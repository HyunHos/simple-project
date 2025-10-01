from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .schemas import ReviewRequest, ReviewResponse
from .services.review import ReviewService, ReviewServiceConfig
import os


app = FastAPI(title="Code Review API", version="0.1.0")

# Allow local and GitHub Action runners by default; adjust as needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_review_service() -> ReviewService:
    cfg = ReviewServiceConfig(
        model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
        api_key=os.getenv("GEMINI_API_KEY", ""),
        temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.2")),
        max_output_tokens=int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "2048")),
    )
    return ReviewService.from_env(cfg)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/v1/review", response_model=ReviewResponse)
async def create_review(payload: ReviewRequest, x_auth_token: str | None = Header(default=None)):
    try:
        expected = os.getenv("AUTH_TOKEN")
        if expected:
            if not x_auth_token or x_auth_token != expected:
                raise HTTPException(status_code=401, detail="Unauthorized")
        service = build_review_service()
        result = await service.generate_review(payload)
        return JSONResponse(content=result.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
