코드 리뷰 API (FastAPI + Gemini)

개요
- GitHub Actions에서 전달한 Pull Request 정보를 받아 Gemini로 코드 리뷰를 생성하는 FastAPI 기반 서비스입니다.
- `curl` 또는 간단한 GitHub Actions 스텝으로 쉽게 연동할 수 있습니다.

엔드포인트
- `GET /healthz` — 헬스 체크
- `POST /v1/review` — 코드 리뷰 생성

요청 스키마 (`POST /v1/review`)
- `repo` (string): `owner/repo` 형식의 저장소 식별자
- `pr_number` (int): PR 번호
- `title` (string): PR 제목
- `description` (string): PR 본문/설명
- `base_sha` (string, optional): 베이스 커밋 SHA
- `head_sha` (string, optional): 헤드 커밋 SHA
- `author` (string, optional): PR 작성자
- `changed_files` (array): 변경 파일 목록(파일별 unified diff 포함 가능)
  - `path` (string): 파일 경로
  - `status` (string): `added|modified|removed|renamed`
  - `patch` (string, optional): 해당 파일의 unified diff

응답 스키마
- `summary` (string): 리뷰 요약
- `comments` (array of objects): 인라인 코멘트 목록
  - `path` (string): 파일 경로
  - `line` (int, optional): 라인 번호
  - `comment` (string): 코멘트 내용
  - `severity` (string, optional): `nit|suggestion|warning|error`
- `suggestions` (array of strings): 추가 제안 사항
- `model` (string): 사용 모델명
- `tokens_used` (int, optional): 사용 토큰 수(옵션)

로컬 실행
1) 파이썬 환경 및 패키지
   - Python 3.10+
   - 의존성 설치: `pip install -r requirements.txt`

2) 환경 변수
   - `GEMINI_API_KEY`: Gemini API 키(없으면 개발 편의를 위한 mock 응답 반환)
   - 선택 사항: `GEMINI_MODEL`(기본 `gemini-1.5-flash`), `GEMINI_TEMPERATURE`(기본 `0.2`), `GEMINI_MAX_OUTPUT_TOKENS`(기본 `2048`)
   - 선택 인증: 서버에 `AUTH_TOKEN`을 설정하면 요청 헤더에 `X-Auth-Token`이 필요합니다.
   - 예시 파일: `.env.example`

3) 서버 실행
   - 개발 실행: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
   - 헬스 체크: `curl http://localhost:8000/healthz`

예시 요청
curl -sS -X POST http://localhost:8000/v1/review \
  -H 'Content-Type: application/json' \
  -d '{
        "repo": "acme/widgets",
        "pr_number": 42,
        "title": "파싱 개선 및 테스트 추가",
        "description": "보다 엄격한 파싱과 유닛 테스트를 추가합니다.",
        "base_sha": "abc123",
        "head_sha": "def456",
        "author": "octocat",
        "changed_files": [
          {
            "path": "src/parser.py",
            "status": "modified",
            "patch": "@@ -10,6 +10,8 @@ def parse(x):\n-  return x\n+  if x is None: raise ValueError\n+  return str(x)\n"
          }
        ]
      }' | jq .

GitHub Actions 예시
다음 워크플로우는 PR 컨텍스트 수집 후 API에 POST합니다. 러너에서 API에 접근 가능해야 합니다(자가 호스팅 또는 공개 URL).

저장소에 `.github/workflows/code-review.yml` 생성:

name: Code Review (Gemini)
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Collect changed files (with patch)
        id: diff
        run: |
          base_sha="${{ github.event.pull_request.base.sha }}"
          head_sha="${{ github.event.pull_request.head.sha }}"
          # 변경된 파일의 diff 수집 (unified 형식)
          git fetch --no-tags --depth=2 origin "+refs/pull/${{ github.event.pull_request.number }}/merge"
          git diff --unified=0 "$base_sha"..."$head_sha" > full.diff || true
          # 파일별 패치(hunks)를 포함한 JSON 배열을 GITHUB_OUTPUT으로 내보내기
          python - << 'PY' >> "$GITHUB_OUTPUT"
import json, re
from pathlib import Path

diff = Path('full.diff').read_text(encoding='utf-8', errors='ignore') if Path('full.diff').exists() else ''
files = {}
cur = None
for line in diff.splitlines():
    if line.startswith('diff --git'):
        m = re.findall(r" a\/([^ ]+) b\/([^ ]+)", line)
        if m:
            _, path = m[0]
            cur = path
            files[cur] = {'path': cur, 'status': 'modified', 'patch': ''}
        continue
    if cur is not None:
        files[cur]['patch'] += line + '\n'

arr = list(files.values())
print('files=' + json.dumps(arr))
PY

      - name: Call Review API
        env:
          API_URL: ${{ secrets.REVIEW_API_URL }}  # 예: https://review.example.com
        run: |
          payload=$(jq -n \
            --arg repo "${{ github.repository }}" \
            --argjson pr_number ${{ github.event.pull_request.number }} \
            --arg title "${{ github.event.pull_request.title }}" \
            --arg description "${{ github.event.pull_request.body }}" \
            --arg base_sha "${{ github.event.pull_request.base.sha }}" \
            --arg head_sha "${{ github.event.pull_request.head.sha }}" \
            --arg author "${{ github.event.pull_request.user.login }}" \
            --argjson changed_files "${{ steps.diff.outputs.files }}" \
            '{repo:$repo, pr_number:$pr_number, title:$title, description:$description, base_sha:$base_sha, head_sha:$head_sha, author:$author, changed_files:$changed_files}')

          curl -sS -X POST "$API_URL/v1/review" \
            -H 'Content-Type: application/json' \
            -H "X-Auth-Token: ${{ secrets.REVIEW_API_TOKEN }}" \
            -d "$payload" | tee review.json

비고
- 서버에서 `GEMINI_API_KEY`가 설정되지 않은 경우, 개발 편의를 위한 모의(mock) 리뷰가 반환됩니다.
- GitHub에 인라인 코멘트를 실제로 등록하려면, `review.json`을 파싱해 GitHub REST API 또는 `gh api`로 리뷰 코멘트를 생성하세요.
