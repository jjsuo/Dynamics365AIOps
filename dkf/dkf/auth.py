"""Dataverse 认证：Service Principal (client credentials) 获取 OAuth2 token。

前置：在 Entra ID 注册一个应用，并在 Dataverse 里把该应用作为
"应用程序用户(Application User)"加入，赋予一个只读的安全角色
(建议自建一个 "DKF Reader" 角色，只给元数据/系统表的读权限)。
"""
from __future__ import annotations

import time
import requests


class DataverseAuth:
    def __init__(self, tenant_id: str, client_id: str, client_secret: str, resource_url: str):
        # resource_url 形如 https://yourorg.crm5.dynamics.com (无尾斜杠)
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.resource_url = resource_url.rstrip("/")
        self._token: str | None = None
        self._expires_at: float = 0.0

    def token(self) -> str:
        # 提前 60s 续期
        if self._token and time.time() < self._expires_at - 60:
            return self._token
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": f"{self.resource_url}/.default",
        }
        resp = requests.post(url, data=data, timeout=30)
        resp.raise_for_status()
        payload = resp.json()
        self._token = payload["access_token"]
        self._expires_at = time.time() + int(payload.get("expires_in", 3600))
        return self._token
