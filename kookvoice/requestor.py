import aiohttp


class VoiceRequestor:
    def __init__(self, token):
        self.token = token

    async def request(self, method, api, **kwargs):
        header = {'Authorization': f'Bot {self.token}'}
        async with aiohttp.ClientSession(headers=header) as r:
            res = await r.request(method, f'https://www.kookapp.cn/api/v3/{api}', **kwargs)
            resj = await res.json()
        if resj['code'] != 0:
            raise RuntimeError(resj['message'])
        return resj['data']

    async def join(self, cid):
        return await self.request('POST', 'voice/join', json={'channel_id': cid})

    async def leave(self, cid):
        return await self.request('POST', 'voice/leave', json={'channel_id': cid})

    async def list(self):
        return await self.request('GET', 'voice/list')

    async def keep_alive(self, cid):
        return await self.request('POST', 'voice/keep-alive', json={'channel_id': cid})

