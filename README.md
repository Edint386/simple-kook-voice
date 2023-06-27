# simple-kook-voice
- - -
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
睡了 明天再写
```

