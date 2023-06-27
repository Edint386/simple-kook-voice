# simple-kook-voice
Python SDK for kook music bot

# Minimal Example

```python
import kookvoice

kookvoice.ffmpeg_bin = "F:/ffmpeg/bin/ffmpeg.exe" # ffmpeg路径，如果已经配置环境变量可以不用填写
music_path_or_link = "https://api.kookbot.cn/static/Ulchero,Couple%20N-LoveTrip.mp3" # 仅示例音频，侵权请联系删除
player = kookvoice.Player('服务器id', '语音频道id', '机器人token')
player.add_music(music_path_or_link)

kookvoice.run()
```

# Big Example

```python
import asyncio
import kookvoice
from khl import *
from khl.card import *


bot_token = 'your_kook_bot_token'
kookvoice.ffmpeg_bin = "F:/ffmpeg/bin/ffmpeg.exe" # ffmpeg路径，如果已经配置环境变量可以不用填写


bot = Bot(token=bot_token)


async def find_user(gid, aid):
    global current_voice_channel
    voice_channel_ = await bot.client.gate.request('GET', 'channel-user/get-joined-channel',
                                                   params={'guild_id': gid, 'user_id': aid})
    voice_channel = voice_channel_["items"]
    if voice_channel:
        vcid = voice_channel[0]['id']
        return vcid

# 指令： /播放 https://api.kookbot.cn/static/Ulchero,Couple%20N-LoveTrip.mp3
@bot.command(name='播放')
async def play(msg: Message, music_url: str):
    voice_channel_id = await find_user(msg.ctx.guild.id, msg.author_id)
    if voice_channel_id is None:
        await msg.ctx.channel.send('请先加入语音频道')
        return

    if 'http' in music_url and '[' in music_url:
        music_url = music_url.split('[')[1].split(']')[0]

    player = kookvoice.Player(msg.ctx.guild.id, voice_channel_id, bot_token)
    player.add_music(music_url)
    await msg.ctx.channel.send(f'开始播放 {music_url}')

# 指令： /跳过
@bot.command(name='跳过')
async def skip(msg: Message):
    player = kookvoice.Player(msg.ctx.guild.id)
    player.skip()
    await msg.ctx.channel.send(f'已跳过当前歌曲')

# 指令： /停止
@bot.command(name='停止')
async def stop(msg: Message):
    player = kookvoice.Player(msg.ctx.guild.id)
    player.stop()
    await msg.ctx.channel.send(f'播放已停止')

# 指令： /列表
@bot.command(name="列表")
async def list(msg: Message):
    player = kookvoice.Player(msg.ctx.guild.id)
    music_list = player.list()
    c = Card(color='#FFA4A4')
    c.append(Module.Context('正在播放'))
    c.append(Module.Header(f"{music_list.pop(0)['file']}"))
    c.append(Module.Divider())
    for index,i in enumerate(music_list):
        c.append(Module.Context(f"{index+1}. {i['file']}"))
    await msg.ctx.channel.send(CardMessage(c))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(bot.start(), kookvoice.start()))

```

