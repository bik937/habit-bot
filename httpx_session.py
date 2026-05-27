"""
Custom aiogram session using httpx instead of aiohttp.
Needed because aiohttp's async TCP (ProactorEventLoop) fails on this Windows machine,
while httpx works fine.
"""
from typing import AsyncGenerator, Dict, Optional, Any, cast

import httpx
import certifi

from aiogram.client.session.base import BaseSession
from aiogram.exceptions import TelegramNetworkError
from aiogram.methods.base import TelegramMethod, TelegramType
from aiogram.client.bot import Bot
from aiogram.types import InputFile


class HttpxSession(BaseSession):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._client: Optional[httpx.AsyncClient] = None

    async def create_session(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                verify=certifi.where(),
                timeout=httpx.Timeout(self.timeout),
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def make_request(
        self,
        bot: Bot,
        method: TelegramMethod[TelegramType],
        timeout: Optional[int] = None,
    ) -> TelegramType:
        client = await self.create_session()
        url = self.api.api_url(token=bot.token, method=method.__api_method__)

        form_data: Dict[str, Any] = {}
        input_files: Dict[str, InputFile] = {}

        for key, value in method.model_dump(warnings=False).items():
            prepared = self.prepare_value(value, bot=bot, files=input_files)
            if prepared is None:
                continue
            form_data[key] = prepared

        files_data = {}
        for file_key, input_file in input_files.items():
            chunks = []
            async for chunk in input_file.read(bot):
                chunks.append(chunk)
            files_data[file_key] = (input_file.filename or file_key, b"".join(chunks))

        try:
            req_timeout = httpx.Timeout(timeout if timeout is not None else self.timeout)
            if files_data:
                resp = await client.post(url, data=form_data, files=files_data, timeout=req_timeout)
            else:
                resp = await client.post(url, data=form_data, timeout=req_timeout)
        except httpx.TimeoutException:
            raise TelegramNetworkError(method=method, message="Request timeout error")
        except httpx.NetworkError as e:
            raise TelegramNetworkError(method=method, message=f"{type(e).__name__}: {e}")

        response = self.check_response(
            bot=bot, method=method, status_code=resp.status_code, content=resp.text
        )
        return cast(TelegramType, response.result)

    async def stream_content(
        self,
        url: str,
        headers: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
        chunk_size: int = 65536,
        raise_for_status: bool = True,
    ) -> AsyncGenerator[bytes, None]:
        if headers is None:
            headers = {}
        client = await self.create_session()
        async with client.stream("GET", url, headers=headers, timeout=timeout) as resp:
            if raise_for_status:
                resp.raise_for_status()
            async for chunk in resp.aiter_bytes(chunk_size):
                yield chunk

    async def __aenter__(self) -> "HttpxSession":
        await self.create_session()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
