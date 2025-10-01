#!/bin/bash

# Discord Webhook Server - GCP Deployment Script
set -e

# gcloud PATH 설정
export PATH="$PATH:/home/codespace/google-cloud-sdk/bin"

echo "🚀 Deploying Discord Webhook Server to Google Cloud Functions..."

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI not found. Please install Google Cloud SDK"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Error: Not authenticated. Run 'gcloud auth login' first"
    exit 1
fi

# Get current project
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [[ -z "$PROJECT_ID" ]]; then
    echo "❌ Error: No project set. Run 'gcloud config set project YOUR_PROJECT_ID'"
    exit 1
fi

echo "📋 Deployment Configuration:"
echo "   Project ID: $PROJECT_ID"
echo "   Function Name: discord-webhook-server"
echo "   Runtime: python311"
echo "   Memory: 512MB"
echo "   Timeout: 60s"
echo ""

# Prompt for webhook URLs (optional)
read -p "🔗 Enter WEBHOOK_GENERAL URL (or press Enter to skip): " WEBHOOK_GENERAL_URL
read -p "🔗 Enter WEBHOOK_ALERTS URL (or press Enter to skip): " WEBHOOK_ALERTS_URL
read -p "🔗 Enter WEBHOOK_LOGS URL (or press Enter to skip): " WEBHOOK_LOGS_URL

# Build environment variables argument
ENV_VARS=""
if [[ -n "$WEBHOOK_GENERAL_URL" ]]; then
    ENV_VARS="$ENV_VARS --set-env-vars WEBHOOK_GENERAL=$WEBHOOK_GENERAL_URL"
fi
if [[ -n "$WEBHOOK_ALERTS_URL" ]]; then
    ENV_VARS="$ENV_VARS --set-env-vars WEBHOOK_ALERTS=$WEBHOOK_ALERTS_URL"
fi
if [[ -n "$WEBHOOK_LOGS_URL" ]]; then
    ENV_VARS="$ENV_VARS --set-env-vars WEBHOOK_LOGS=$WEBHOOK_LOGS_URL"
fi

echo "🔧 Deploying function..."

# Deploy to Cloud Functions
gcloud functions deploy discord-webhook-server \
    --source . \
    --entry-point discord_webhook \
    --runtime python311 \
    --trigger http \
    --allow-unauthenticated \
    --memory 512MB \
    --timeout 60s \
    --max-instances 100 \
    --min-instances 0 \
    $ENV_VARS

echo ""
echo "✅ Deployment completed successfully!"

# Get the function URL
FUNCTION_URL=$(gcloud functions describe discord-webhook-server --format="value(httpsTrigger.url)")
echo "🌐 Function URL: $FUNCTION_URL"

echo ""
echo "🧪 Testing deployment..."
curl -s "$FUNCTION_URL" | jq .

echo ""
echo "📚 Next steps:"
echo "1. Test your webhook: curl -X POST $FUNCTION_URL/api/webhook/general -H 'Content-Type: application/json' -d '{\"content\":\"Test message\"}'"
echo "2. View logs: gcloud functions logs read discord-webhook-server"
echo "3. Update environment variables: gcloud functions deploy discord-webhook-server --update-env-vars KEY=value"