# simple-kook-voice

Python SDK for kook music bot  
希望做成一款开箱即用的推流sdk  
遇到问题/功能建议/代码贡献都可以来 [KOOK服务器](https://kook.top/5KOq5I) 找我

# Special Thanks
hank9999： 提供了voice.py 以及 大部分推流底层逻辑

# 安装依赖
需要自备ffmpeg且配置好全局变量  
不配置全局变量的话需要在代码中指定ffmpeg路径  如下：
```python
import kookvoice

kookvoice.ffmpeg_bin = "F:/ffmpeg/bin/ffmpeg.exe"
```
其余python依赖已写在reqirements.txt中  
当然你可以可以直接
`pip install enum`  
~~因为就这一个依赖~~



# 使用教程
先放一个最基础的推流体验一下
```python
import kookvoice

music_path_or_link = "https://api.kookbot.cn/static/Ulchero,Couple%20N-LoveTrip.mp3"  # 仅示例音频，侵权请联系删除
player = kookvoice.Player('服务器id', '语音频道id', '机器人token')
player.add_music(music_path_or_link)

kookvoice.run()
```

   
看过了基础的使用教程，但是如何与机器人(khl.py)实现结合呢？

```python
import asyncio
import kookvoice
from khl import *

bot_token = 'your_kook_bot_token'
kookvoice.ffmpeg_bin = "F:/ffmpeg/bin/ffmpeg.exe"  # ffmpeg路径，如果已经配置环境变量可以不用填写

bot = Bot(token=bot_token)


async def find_user(gid, aid):
    global current_voice_channel
    # 调用接口查询用户所在的语音频道
    voice_channel_ = await bot.client.gate.request('GET', 'channel-user/get-joined-channel',
                                                   params={'guild_id': gid, 'user_id': aid})
    voice_channel = voice_channel_["items"]
    if voice_channel:
        vcid = voice_channel[0]['id']
        return vcid


# 让点歌机加入频道
# 这条指令其实完全没用，因为点歌了会自动加入语音频道
# 但是还是写了，万一有人要呢
# 指令： /join
@bot.command(name='join')
async def join_vc(msg:Message):
    # 获取用户所在频道
    voice_channel_id = await find_user(msg.ctx.guild.id, msg.author_id)
    if voice_channel_id is None:
        await msg.ctx.channel.send('请先加入语音频道')
        return
    player = kookvoice.Player(msg.ctx.guild.id, voice_channel_id, bot_token)
    player.join()
    voice_channel = await bot.client.fetch_public_channel(voice_channel_id)
    await msg.ctx.channel.send(f'已加入语音频道 #{voice_channel.name}')


# 播放直链或本地歌曲
# 指令： /播放 https://api.kookbot.cn/static/Ulchero,Couple%20N-LoveTrip.mp3
@bot.command(name='播放')
async def play(msg: Message, music_url: str):
    # 第一步：获取用户所在的语音频道
    voice_channel_id = await find_user(msg.ctx.guild.id, msg.author_id)
    # 如果不在语音频道就提示加入语音频道后点歌
    if voice_channel_id is None:
        await msg.ctx.channel.send('请先加入语音频道')
        return

    # 如果用户发了音乐直链，会被kook转为链接的kmd，要拆一下
    if 'http' in music_url and '[' in music_url:
        music_url = music_url.split('[')[1].split(']')[0]

    # 这时候只需要为他添加歌曲即可
    # 构建一个player，首次使用需要填写服务器id，语音频道id以及token
    player = kookvoice.Player(msg.ctx.guild.id, voice_channel_id, bot_token)

    # 这里的extra data是歌曲的备注信息，你可以在这里存入播放列表
    # 而后在播放列表里以及歌曲切换时获取到这些信息
    # 当然想不填也完全没问题
    extra_data = {"音乐名字": "未知", "点歌人": msg.author_id, "文字频道": msg.ctx.channel.id}

    # 注：如果填写的为本地播放路径，建议填写绝对路径
    player.add_music(music_url, extra_data)

    # 机器人提示点歌成功
    await msg.ctx.channel.send(f'添加音乐成功 {music_url}')


# 既然能够添加歌曲 那也得有控制选项
# 指令： /跳过
@bot.command(name='跳过')
async def skip(msg: Message):
    # 在当前服务器歌单有歌曲的时候，你可以直接填入guild_id来获取player
    player = kookvoice.Player(msg.ctx.guild.id)
    player.skip()
    await msg.ctx.channel.send(f'已跳过当前歌曲')


# 指令： /停止
@bot.command(name='停止')
async def stop(msg: Message):
    player = kookvoice.Player(msg.ctx.guild.id)
    player.stop()
    await msg.ctx.channel.send(f'播放已停止')


from khl.card import Module, Card, CardMessage


# 指令： /列表
@bot.command(name="列表")
async def list(msg: Message):
    player = kookvoice.Player(msg.ctx.guild.id)
    music_list = player.list()
    c = Card(color='#FFA4A4')
    c.append(Module.Context('正在播放'))
    c.append(Module.Header(f"{music_list.pop(0)['file']}"))
    c.append(Module.Divider())
    for index, i in enumerate(music_list):
        # 这里的extra data 便是点歌的时候放入的东西
        c.append(Module.Context(f"{index + 1}. {i['file']} 点歌人：(met){i['extra_data']['点歌人']}(met)"))
    await msg.ctx.channel.send(CardMessage(c))


# 指令： /跳转 120
# 注：120是秒数
@bot.command(name="跳转")
async def seek(msg: Message, time: int):
    player = kookvoice.Player(msg.ctx.guild.id)
    player.seek(time)
    await msg.ctx.channel.send(f'已跳转到 {time} 秒')


# 切歌时触发事件便于发送开始的消息
@kookvoice.on_event(kookvoice.Status.START)
async def on_music_start(play_info: kookvoice.PlayInfo):
    guild_id = play_info.guild_id
    voice_channel_id = play_info.voice_channel_id
    music_bot_token = play_info.token
    extra_data = play_info.extra_data  # 你可以在这里获取到歌曲的备注信息
    text_channel_id = extra_data['文字频道']
    text_channel = await bot.client.fetch_public_channel(text_channel_id)
    await text_channel.send(f"正在播放 {play_info.file}")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # 使用gather同时启动机器人与推流
    loop.run_until_complete(asyncio.gather(bot.start(), kookvoice.start()))
```


# Contribute

在保证 **简单易用** 的宗旨下，十分欢迎大家的pr！


- - -
对了家人们有没有会pypi的教教我怎么发包（）  太蠢了整不明白





