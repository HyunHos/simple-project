#!/bin/bash

# GCP 설정 및 API 활성화 스크립트
set -e

export PATH="$PATH:/home/codespace/google-cloud-sdk/bin"

echo "🚀 Discord Webhook Server - GCP 초기 설정"

# 인증 상태 확인
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ 인증이 필요합니다. 다음 명령어를 실행하세요:"
    echo "   gcloud auth login"
    exit 1
fi

# 프로젝트 설정 확인
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [[ -z "$PROJECT_ID" ]]; then
    echo "❌ 프로젝트가 설정되지 않았습니다."
    echo "📋 사용 가능한 프로젝트:"
    gcloud projects list --format="table(projectId,name,projectNumber)"
    echo ""
    read -p "🔧 사용할 프로젝트 ID를 입력하세요: " PROJECT_ID
    gcloud config set project $PROJECT_ID
fi

echo "📋 현재 설정:"
echo "   프로젝트 ID: $PROJECT_ID"
echo "   계정: $(gcloud auth list --filter=status:ACTIVE --format='value(account)')"
echo ""

# 필요한 API 활성화
echo "🔧 필요한 API 활성화 중..."

# Cloud Functions API
echo "  📦 Cloud Functions API 활성화..."
gcloud services enable cloudfunctions.googleapis.com

# Cloud Build API (Functions 배포에 필요)
echo "  📦 Cloud Build API 활성화..."
gcloud services enable cloudbuild.googleapis.com

# Cloud Run API (Functions Gen2에 필요)
echo "  📦 Cloud Run API 활성화..."
gcloud services enable run.googleapis.com

# Cloud Logging API
echo "  📦 Cloud Logging API 활성화..."
gcloud services enable logging.googleapis.com

# Artifact Registry API
echo "  📦 Artifact Registry API 활성화..."
gcloud services enable artifactregistry.googleapis.com

echo ""
echo "✅ GCP 설정 완료!"
echo ""
echo "📚 다음 단계:"
echo "1. Discord 웹훅 URL 준비"
echo "2. 배포 스크립트 실행: ./deploy.sh"
echo "3. 또는 직접 배포: gcloud functions deploy discord-webhook-server --source . --entry-point discord_webhook --runtime python311 --trigger http --allow-unauthenticated"