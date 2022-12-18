import os
import base64


def generate_unique_code() -> str:
    return base64.b32encode(os.urandom(3))[:5].decode("utf-8")

def get_token_by_webhook(webhook_url: str) -> str:
    return webhook_url.replace('https://discord.com/api/webhooks/', 'WEBHOOK::')
