# Discord Webhook Server - Google Cloud Functions 배포용
# FastAPI + Functions Framework로 구현

import functions_framework
from fastapi import FastAPI, HTTPException
import requests.exceptions
from webhook import WebhookMessage, webhook_manager

# Google Cloud Functions는 환경변수를 자동으로 로드하므로 dotenv 불필요

# FastAPI 앱 생성
app = FastAPI(
    title="Discord Webhook Server",
    version="2.0.0",
    description="Google Cloud Functions 기반 Discord 웹훅 서버"
)

# 헬스 체크 엔드포인트
@app.get("/")
async def health_check():
    return {
        "status": "healthy",
        "message": "Discord Webhook Server is running",
        "version": "2.0.0",
        "platform": "Google Cloud Functions",
        "registered_webhooks_count": len(webhook_manager.registered_webhooks)
    }

# 등록된 웹훅 목록 조회
@app.get("/api/webhooks")
async def list_webhooks():
    return {
        "registered_webhooks": list(webhook_manager.registered_webhooks.keys()),
        "total_count": len(webhook_manager.registered_webhooks)
    }

# 웹훅 메시지 전송 (메인 기능)
@app.post("/api/webhook/{identifier}")
async def send_webhook(identifier: str, message: WebhookMessage):
    try:
        result = await webhook_manager.send_webhook(identifier, message)
        return result
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Discord API 요청 실패: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"서버 내부 오류: {str(e)}"
        )

# 런타임 웹훅 등록
@app.post("/api/webhooks/{name}/register")
async def register_webhook(name: str, webhook_data: dict):
    if "webhook_url" not in webhook_data:
        raise HTTPException(
            status_code=400, 
            detail="webhook_url 필드가 필요합니다"
        )
    
    webhook_manager.register_webhook(name, webhook_data["webhook_url"])
    return {
        "message": f"웹훅 '{name}'이 성공적으로 등록되었습니다",
        "webhook_name": name
    }

# Google Cloud Functions 엔트리포인트
@functions_framework.http
def discord_webhook(request):
    """
    Google Cloud Functions 진입점
    모든 HTTP 요청을 FastAPI 앱으로 라우팅
    """
    from fastapi.testclient import TestClient
    
    # TestClient로 FastAPI 앱 테스트
    client = TestClient(app)
    
    # 요청 정보 추출
    method = request.method.lower()
    path = request.path if hasattr(request, 'path') else '/'
    headers = dict(request.headers) if hasattr(request, 'headers') else {}
    
    # JSON 데이터 처리
    json_data = None
    if hasattr(request, 'get_json'):
        try:
            json_data = request.get_json(silent=True)
        except Exception:
            pass
    
    # Content-Type 헤더 정리
    headers.pop('host', None)  # TestClient가 자체 host를 사용
    
    try:
        # HTTP 메서드별 요청 처리
        if method == 'post':
            response = client.post(path, json=json_data, headers=headers)
        elif method == 'get':
            response = client.get(path, headers=headers)
        elif method == 'put':
            response = client.put(path, json=json_data, headers=headers)
        elif method == 'delete':
            response = client.delete(path, headers=headers)
        else:
            response = client.get(path, headers=headers)
        
        # Cloud Functions 응답 형식으로 반환
        return (
            response.json(),
            response.status_code,
            {'Content-Type': 'application/json'}
        )
        
    except Exception as e:
        # 에러 발생 시 기본 응답
        return (
            {"error": f"요청 처리 중 오류 발생: {str(e)}"},
            500,
            {'Content-Type': 'application/json'}
        )