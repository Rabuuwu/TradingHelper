from __future__ import annotations

from dataclasses import dataclass

import requests


@dataclass(frozen=True)
class NtfyPublisher:
    server: str
    topic: str
    timeout_seconds: float = 10.0

    def publish(self, title: str, body: str, priority: str = "default", tags: str = "") -> None:
        if not self.topic:
            raise ValueError("ntfy topic is empty")
        headers = {"Title": title, "Priority": priority}
        if tags:
            headers["Tags"] = tags
        response = requests.post(f"{self.server.rstrip('/')}/{self.topic}", data=body.encode("utf-8"), headers=headers, timeout=self.timeout_seconds)
        response.raise_for_status()
