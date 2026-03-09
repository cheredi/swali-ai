"""Remote execution sandbox integration (Piston)."""

from __future__ import annotations

import httpx


class CodeSandbox:
    """Executes user code against Piston API."""

    def __init__(self, base_url: str = "https://emkc.org/api/v2/piston"):
        self.base_url = base_url.rstrip("/")

    async def execute(self, language: str, version: str, code: str, stdin: str = "") -> dict:
        payload = {
            "language": language,
            "version": version,
            "files": [{"name": "main", "content": code}],
            "stdin": stdin,
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(f"{self.base_url}/execute", json=payload)
            response.raise_for_status()
            return response.json()


_sandbox: CodeSandbox | None = None


def get_sandbox() -> CodeSandbox:
    global _sandbox
    if _sandbox is None:
        _sandbox = CodeSandbox()
    return _sandbox
