#!/bin/bash

# Discord Webhook Server - Local Test Commands
# Run these commands after starting the local server

echo "🧪 Testing Discord Webhook Server locally..."
echo "Make sure the server is running on http://localhost:8080"
echo ""

# 1. Health check
echo "1. Health Check:"
curl -s http://localhost:8080/ | jq .
echo -e "\n"

# 2. List webhooks
echo "2. List registered webhooks:"
curl -s http://gcp/api/webhooks | jq .
echo -e "\n"

# 3. Send simple message
# echo "3. Send simple text message:"
# curl -X POST http://localhost:8080/api/webhook/general \
#   -H "Content-Type: application/json" \
#   -d '{
#     "content": "🧪 로컬 테스트 메시지입니다!"
#   }' | jq .
# echo -e "\n"

# 4. Send rich embed message
echo "4. Send rich embed message:"
curl -X POST http://localhost:8080/api/webhook/general \
  -H "Content-Type: application/json" \
  -d '{
    "content": "웹훅 메시지 테스트",
    "embeds": [{
      "title": "🚀 로컬 테스트 성공!",
      "description": "Discord Webhook Server가 정상적으로 작동합니다.",
      "color": 65280,
      "fields": [
        {
          "name": "환경",
          "value": "로컬 개발",
          "inline": true
        },
        {
          "name": "포트",
          "value": "8080",
          "inline": true
        }
      ],
      "footer": {
        "text": "테스트 완료"
      }
    }]
  }' | jq .
echo -e "\n"

# 5. Register new webhook (runtime)
echo "5. Register new webhook at runtime:"
curl -X POST http://localhost:8080/api/webhooks/test/register \
  -H "Content-Type: application/json" \
  -d '{
    "webhook_url": "https://discord.com/api/webhooks/test-webhook-url"
  }' | jq .
echo -e "\n"

echo "✅ All tests completed!"