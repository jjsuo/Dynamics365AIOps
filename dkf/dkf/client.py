"""Dataverse Web API 客户端：自动翻页、统一 header。"""
from __future__ import annotations

from typing import Iterator
import requests

from .auth import DataverseAuth

API_VERSION = "v9.2"


class DataverseClient:
    def __init__(self, auth: DataverseAuth, page_size: int = 500):
        self.auth = auth
        self.base = f"{auth.resource_url}/api/data/{API_VERSION}/"
        self.page_size = page_size

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.auth.token()}",
            "Accept": "application/json",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Prefer": f"odata.maxpagesize={self.page_size}",
        }

    def get_all(self, path: str) -> Iterator[dict]:
        """GET 一个集合，自动跟随 @odata.nextLink 翻页，逐条 yield。"""
        url = self.base + path
        while url:
            resp = requests.get(url, headers=self._headers(), timeout=120)
            resp.raise_for_status()
            data = resp.json()
            for row in data.get("value", []):
                yield row
            url = data.get("@odata.nextLink")  # 已含完整 query，直接用

    def get_one(self, path: str) -> dict:
        resp = requests.get(self.base + path, headers=self._headers(), timeout=120)
        resp.raise_for_status()
        return resp.json()
