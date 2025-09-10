# simple-project
test project

## 개발 기록
- 2025-09-09
  - `main` 브랜치 최신화 (`git pull`)
  - 기능 브랜치(feature branch) 사용 목적 학습
  - 신규 기능 브랜치 `feature/taekhwan` 생성

## AI 코드 리뷰어 프로젝트

### 수정된 1단계: MVP 개발 - VS Code 확장 프로그램

**목표:** VS Code에서 사용자가 선택한 코드 블록을 AI가 리뷰하고, 그 결과를 VS Code 내의 별도 패널에 보여주는 간단한 확장 프로그램을 만듭니다.

#### 기술 스택 추천
*   **개발 언어:** **TypeScript** (VS Code 확장 프로그램 개발의 표준)
*   **핵심 로직:** **Node.js** (VS Code의 런타임 환경)
*   **AI 모델:** **대규모 언어 모델(LLM) API**

#### 개발 순서 (단계별 계획)
1.  **VS Code 확장 프로그램 프로젝트 생성:**
    *   Node.js 환경에서 `yo code` 라는 공식 도구를 사용해 기본적인 VS Code 확장 프로그램 프로젝트 구조를 자동으로 생성합니다.
2.  **명령(Command) 등록:**
    *   `package.json` 파일에 `AI Code Review` 같은 이름의 명령을 등록하여 명령 팔레트에서 실행할 수 있게 합니다.
3.  **코드 가져오기:**
    *   사용자가 명령을 실행했을 때, VS Code API를 사용하여 현재 편집기에서 **선택된 텍스트(코드)**를 가져오는 로직을 구현합니다.
4.  **AI 모델 호출:**
    *   가져온 코드를 프롬프트와 조합하여, Node.js 환경에서 LLM API로 전송하고 응답을 받습니다.
5.  **결과 표시:**
    *   AI가 생성한 리뷰 결과를 **웹뷰(Webview) 패널**을 사용해 VS Code 내의 새 탭이나 분할 창에 마크다운 형식으로 보기 좋게 출력합니다.


## 개발일지

### 2025-09-10

*   프로젝트 초기 설정 및 디버깅 세션 진행.
*   `npm run build`를 통해 `dist` 폴더에 빌드 결과물이 생성되지 않아 명령어가 활성화되지 않는 문제 해결.
*   Google Gemini API 연동을 위한 초기 코드 작성.
*   `Only absolute URLs are supported` 에러 해결: `YOUR_API_ENDPOINT`를 실제 Gemini API 주소로 변경.
*   `models/gemini-pro is not found` 에러 해결: API 모델을 `gemini-1.5-pro-latest`로 변경.
*   세션 간 대화 내용을 기억하기 위한 `save_memory` 도구 설정 완료.
*   세션 종료 시 `README.md`에 개발일지를 작성하는 프로세스 정립.
*   Gemini API 할당량 초과 시 'flash' 모델로 자동 재시도 기능 추가.