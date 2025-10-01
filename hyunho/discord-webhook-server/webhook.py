# Discord 웹훅 처리 전용 모듈
# 웹훅 URL 관리와 메시지 전송 로직을 분리하여 관심사 분리 구현

import os
import requests
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

# Discord Embed 필드 모델
class EmbedField(BaseModel):
    name: str  # 필드 제목
    value: str  # 필드 내용
    inline: Optional[bool] = False  # 인라인 표시 여부

# Discord Embed 푸터 모델
class EmbedFooter(BaseModel):
    text: str  # 푸터 텍스트
    icon_url: Optional[str] = None  # 푸터 아이콘 URL

# Discord Embed 작성자 모델
class EmbedAuthor(BaseModel):
    name: str  # 작성자 이름
    url: Optional[str] = None  # 작성자 링크
    icon_url: Optional[str] = None  # 작성자 아이콘 URL

# Discord Embed 모델
class Embed(BaseModel):
    title: Optional[str] = None  # 임베드 제목
    description: Optional[str] = None  # 임베드 설명
    url: Optional[str] = None  # 임베드 링크
    color: Optional[int] = None  # 임베드 색상 (0x000000 형태)
    timestamp: Optional[str] = None  # 타임스탬프 (ISO 8601 형식)
    footer: Optional[EmbedFooter] = None  # 푸터
    image: Optional[Dict[str, str]] = None  # 이미지 {"url": "image_url"}
    thumbnail: Optional[Dict[str, str]] = None  # 썸네일 {"url": "thumbnail_url"}
    author: Optional[EmbedAuthor] = None  # 작성자
    fields: Optional[List[EmbedField]] = []  # 필드 목록

# 웹훅 메시지 데이터 모델 (확장된 버전)
class WebhookMessage(BaseModel):
    # 기본 메시지
    content: Optional[str] = None  # 메시지 내용 (임베드만 사용할 경우 선택사항)
    username: Optional[str] = None  # 웹훅 봇의 표시명
    avatar_url: Optional[str] = None  # 웹훅 봇의 아바타 이미지 URL
    
    # 리치 메시지
    embeds: Optional[List[Embed]] = []  # 임베드 목록 (최대 10개)
    
    # TTS (Text-to-Speech)
    tts: Optional[bool] = False  # 음성 읽기 여부

class DiscordWebhookManager:
    """Discord 웹훅 관리 클래스"""
    
    def __init__(self):
        # 환경변수에서 기본 웹훅 URL들을 로드
        # 여러 웹훅을 미리 등록해두고 이름으로 사용 가능
        self.registered_webhooks = {}
        self._load_webhooks_from_env()
    
    def _load_webhooks_from_env(self):
        """환경변수에서 웹훅 URL들을 로드"""
        # 환경변수 패턴: WEBHOOK_채널명=전체_웹훅_URL
        for key, value in os.environ.items():
            if key.startswith("WEBHOOK_"):
                webhook_name = key.replace("WEBHOOK_", "").lower()
                self.registered_webhooks[webhook_name] = value
    
    def register_webhook(self, name: str, webhook_url: str):
        """런타임에 새 웹훅 등록"""
        self.registered_webhooks[name] = webhook_url
    
    def get_webhook_url(self, identifier: str) -> str:
        """웹훅 URL 반환 - 등록된 이름 또는 직접 webhook_id 사용"""
        # 등록된 웹훅 이름인지 확인
        if identifier in self.registered_webhooks:
            return self.registered_webhooks[identifier]
        
        # webhook_id 형태로 간주하고 Discord API URL 구성
        # Discord 웹훅 URL 형태: https://discord.com/api/webhooks/ID/TOKEN
        if "/" in identifier:
            # 이미 완전한 webhook_id/token 형태
            return f"https://discord.com/api/webhooks/{identifier}"
        else:
            # 단순 ID만 제공된 경우 (보안상 권장하지 않음)
            return f"https://discord.com/api/webhooks/{identifier}"
    
    def build_payload(self, message: WebhookMessage) -> Dict[str, Any]:
        """웹훅 페이로드 구성"""
        payload = {}
        
        # 기본 메시지 필드들
        if message.content:
            payload["content"] = message.content
        if message.username:
            payload["username"] = message.username
        if message.avatar_url:
            payload["avatar_url"] = message.avatar_url
        if message.tts:
            payload["tts"] = message.tts
        
        # 임베드 처리
        if message.embeds:
            embeds_data = []
            for embed in message.embeds:
                embed_dict = {}
                
                # 기본 임베드 필드들
                if embed.title:
                    embed_dict["title"] = embed.title
                if embed.description:
                    embed_dict["description"] = embed.description
                if embed.url:
                    embed_dict["url"] = embed.url
                if embed.color:
                    embed_dict["color"] = embed.color
                if embed.timestamp:
                    embed_dict["timestamp"] = embed.timestamp
                
                # 복합 객체들
                if embed.footer:
                    footer_dict = {"text": embed.footer.text}
                    if embed.footer.icon_url:
                        footer_dict["icon_url"] = embed.footer.icon_url
                    embed_dict["footer"] = footer_dict
                
                if embed.author:
                    author_dict = {"name": embed.author.name}
                    if embed.author.url:
                        author_dict["url"] = embed.author.url
                    if embed.author.icon_url:
                        author_dict["icon_url"] = embed.author.icon_url
                    embed_dict["author"] = author_dict
                
                if embed.image:
                    embed_dict["image"] = embed.image
                if embed.thumbnail:
                    embed_dict["thumbnail"] = embed.thumbnail
                
                # 필드 목록
                if embed.fields:
                    fields_data = []
                    for field in embed.fields:
                        fields_data.append({
                            "name": field.name,
                            "value": field.value,
                            "inline": field.inline
                        })
                    embed_dict["fields"] = fields_data
                
                embeds_data.append(embed_dict)
            
            payload["embeds"] = embeds_data
        
        return payload
    
    async def send_webhook(self, identifier: str, message: WebhookMessage) -> Dict[str, str]:
        """웹훅 메시지 전송"""
        webhook_url = self.get_webhook_url(identifier)
        payload = self.build_payload(message)
        
        # Discord API 호출
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        # HTTP 에러 체크
        response.raise_for_status()
        
        return {
            "status": "success", 
            "message": f"Webhook sent successfully to {identifier}",
            "webhook_url": webhook_url.split("/webhooks/")[0] + "/webhooks/***"  # 보안을 위해 URL 마스킹
        }

# 전역 웹훅 매니저 인스턴스
webhook_manager = DiscordWebhookManager()