import asyncio
import json
import random
import time
from typing import List
from .voice_json import voice_json

import aiohttp
from aiohttp import ClientWebSocketResponse


class Voice:
    token = ''
    channel_id = ''
    rtp_url = ''
    ws_clients: List[ClientWebSocketResponse] = []
    wait_handler_msgs = []
    is_exit = False

    def __init__(self, token: str):
        self.token = token
        self.ws_clients = []
        self.wait_handler_msgs = []

    async def get_gateway(self, channel_id: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://www.kaiheila.cn/api/v3/gateway/voice?channel_id={channel_id}',
                                   headers={'Authorization': f'Bot {self.token}'}) as res:
                return (await res.json())['data']['gateway_url']

    async def connect_ws(self):
        gateway = await self.get_gateway(self.channel_id)
        print(gateway)
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=64,verify_ssl=False)) as session:
            async with session.ws_connect(gateway) as ws:
                self.ws_clients.append(ws)
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        if len(self.ws_clients) != 0 and self.ws_clients[0] == ws:
                            self.wait_handler_msgs.append(msg.data)
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        break
                    else:
                        return

    async def ws_msg(self):
        while True:
            if self.is_exit:
                return
            if len(self.ws_clients) != 0:
                break
            await asyncio.sleep(0.1)
        # with open('voice.json', 'r') as f:
        #     a = json.loads(f.read())
        a = voice_json
        a['1']['id'] = random.randint(1000000, 9999999)
        print('1:', a['1'])
        await self.ws_clients[0].send_json(a['1'])
        now = 1
        ip = ''
        port = 0
        rtcp_port = 0
        while True:
            if self.is_exit:
                return
            if len(self.wait_handler_msgs) != 0:
                data = json.loads(self.wait_handler_msgs.pop(0))
                if now == 1:
                    print('1:', data)
                    a['2']['id'] = random.randint(1000000, 9999999)
                    print('2:', a['2'])
                    await self.ws_clients[0].send_json(a['2'])
                    now = 2
                elif now == 2:
                    print('2:', data)
                    a['3']['id'] = random.randint(1000000, 9999999)
                    print('3:', a['3'])
                    await self.ws_clients[0].send_json(a['3'])
                    now = 3
                elif now == 3:
                    print('3:', data)
                    transport_id = data['data']['id']
                    ip = data['data']['ip']
                    port = data['data']['port']
                    rtcp_port = data['data']['rtcpPort']
                    a['4']['data']['transportId'] = transport_id
                    a['4']['id'] = random.randint(1000000, 9999999)
                    print('4:', a['4'])
                    await self.ws_clients[0].send_json(a['4'])
                    now = 4
                elif now == 4:
                    print('4:', data)
                    print(f'ssrc=1357 ffmpeg rtp url: rtp://{ip}:{port}?rtcpport={rtcp_port}')
                    self.rtp_url = f'rtp://{ip}:{port}?rtcpport={rtcp_port}'
                    now = 5
                else:
                    if 'notification' in data and 'method' in data and data['method'] == 'disconnect':
                        print('The connection had been disconnected', data)
                    else:
                        pass
            await asyncio.sleep(0.1)

    async def ws_ping(self):
        while True:
            if self.is_exit:
                return
            if len(self.ws_clients) != 0:
                break
            await asyncio.sleep(0.1)
        ping_time = 0.0
        while True:
            if self.is_exit:
                return
            await asyncio.sleep(0.1)
            if len(self.ws_clients) == 0:
                return
            now_time = time.time()
            if now_time - ping_time >= 30:
                await self.ws_clients[0].ping()
                ping_time = now_time

    async def main(self):
        await asyncio.wait([self.ws_msg(), self.connect_ws(), self.ws_ping()], return_when='FIRST_COMPLETED')
        self.is_exit = False
        self.channel_id = ''
        self.rtp_url = ''
        self.ws_clients.clear()
        self.wait_handler_msgs.clear()

    async def handler(self):
        while True:
            if len(self.channel_id) != 0:
                await self.main()
            await asyncio.sleep(0.1)