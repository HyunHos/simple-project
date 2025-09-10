# Discord Webhook Server

Google Cloud Functions 기반 Discord 웹훅 서버 🚀

## 🌟 주요 기능

- **리치 메시지 지원**: 텍스트, 임베드, 이미지, TTS 등 다양한 형태
- **환경변수 관리**: 안전한 웹훅 URL 관리
- **서버리스**: Google Cloud Functions로 무료 운영 가능
- **자동 배포**: GitHub 연동으로 푸시 시 자동 배포
- **200만 요청/월** 무료 제공

## 🚀 빠른 시작

### 1. 로컬 테스트

```bash
# 의존성 설치
pip install -r requirements.txt

# 로컬에서 Functions Framework로 테스트
functions-framework --target=discord_webhook --port=8080

# 테스트 요청
curl http://localhost:8080/ 
```

### 2. Google Cloud 배포

```bash
# gcloud CLI 설치 후 로그인
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Cloud Functions 배포
gcloud functions deploy discord-webhook-server \
  --source . \
  --entry-point discord_webhook \
  --runtime python311 \
  --trigger http \
  --allow-unauthenticated \
  --memory 512MB \
  --set-env-vars WEBHOOK_GENERAL="your-discord-webhook-url"

# 배포된 URL 확인
gcloud functions describe discord-webhook-server
```

## 📡 API 사용법

### 헬스 체크
```bash
GET /
```

### 웹훅 전송
```bash
POST /api/webhook/{identifier}
Content-Type: application/json

{
  "content": "안녕하세요! 테스트 메시지입니다.",
  "username": "봇 이름",
  "embeds": [{
    "title": "제목",
    "description": "설명",
    "color": 65280
  }]
}
```

### 등록된 웹훅 조회
```bash
GET /api/webhooks
```

### 새 웹훅 등록
```bash
POST /api/webhooks/{name}/register
Content-Type: application/json

{
  "webhook_url": "https://discord.com/api/webhooks/..."
}
```

## 🎨 메시지 예시

### 기본 텍스트
```json
{
  "content": "간단한 메시지입니다"
}
```

### 리치 임베드
```json
{
  "embeds": [{
    "title": "🚀 배포 완료",
    "description": "성공적으로 배포되었습니다!",
    "color": 65280,
    "fields": [
      {
        "name": "버전",
        "value": "v2.0.0",
        "inline": true
      }
    ],
    "footer": {
      "text": "CI/CD Bot"
    }
  }]
}
```

### 이미지 포함
```json
{
  "content": "⚠️ 시스템 경고",
  "embeds": [{
    "title": "모니터링 알림",
    "image": {
      "url": "https://example.com/graph.png"
    }
  }]
}
```

## ⚙️ 환경변수

Google Cloud Console에서 환경변수 설정:

```
WEBHOOK_GENERAL=https://discord.com/api/webhooks/123/abc
WEBHOOK_ALERTS=https://discord.com/api/webhooks/456/def
WEBHOOK_LOGS=https://discord.com/api/webhooks/789/ghi
```

## 🔄 자동 배포 설정

1. Google Cloud Build API 활성화
2. GitHub 저장소 연결
3. Cloud Build 트리거 생성
4. 환경변수 설정
5. 푸시 시 자동 배포 🎉

## 📊 비용

- **무료**: 월 200만 요청까지
- **예상 비용**: 일반적인 사용량에서는 **완전 무료**
- **확장성**: 자동 스케일링으로 트래픽 급증에도 대응

## 🛠️ 개발

### 프로젝트 구조
```
├── main.py           # FastAPI 앱 + Cloud Functions 엔트리포인트
├── webhook.py        # 웹훅 처리 로직
├── requirements.txt  # 의존성
├── cloudbuild.yaml   # 자동 배포 설정
└── README.md        # 문서
```

### 로컬 개발
```bash
# Functions Framework로 로컬 서버 실행
functions-framework --target=discord_webhook --debug

# API 테스트
curl -X POST localhost:8080/api/webhook/general \
  -H "Content-Type: application/json" \
  -d '{"content": "테스트 메시지"}'
```

## 🔗 유용한 링크

- [Discord Webhook 가이드](https://discord.com/developers/docs/resources/webhook)
- [Google Cloud Functions 문서](https://cloud.google.com/functions/docs)
- [FastAPI 문서](https://fastapi.tiangolo.com/)

## 📝 라이센스

MIT License