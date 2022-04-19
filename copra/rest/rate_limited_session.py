#!/usr/bin/env python3

# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

import asyncio
import time

from aiohttp import ClientSession


class RateLimitedSession(ClientSession):
    """Rate limited aiohttp.ClientSession.

    idea from: https://gist.github.com/pquentin/5d8f5408cdad73e589d85ba509091741
    explanation: https://quentin.pradet.me/blog/how-do-you-rate-limit-calls-with-aiohttp.html
    """
    def __init__(self, *args, rate=10, burst=15, **kwargs):
        self.rate = rate  # requests per second
        self.burst = burst  # up to 'burst' requests per second in bursts
        self.tokens = self.burst
        self.updated_at = time.monotonic()
        super().__init__(*args, **kwargs)

    def add_new_tokens(self):
        now = time.monotonic()
        time_since_update = now - self.updated_at
        new_tokens = time_since_update * self.rate
        if self.tokens + new_tokens >= 1:
            self.tokens = min(self.tokens + new_tokens, self.burst)
            self.updated_at = now

    async def wait_for_token(self):
        while self.tokens < 1:
            self.add_new_tokens()
            await asyncio.sleep(0.1)
        self.tokens -= 1

    async def get(self, *args, **kwargs):
        await self.wait_for_token()
        resp = await super().get(*args, **kwargs)
        return resp

    async def delete(self, *args, **kwargs):
        await self.wait_for_token()
        resp = await super().delete(*args, **kwargs)
        return resp

    async def post(self, *args, **kwargs):
        await self.wait_for_token()
        resp = await super().post(*args, **kwargs)
        return resp
