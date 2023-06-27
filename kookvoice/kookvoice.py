import asyncio
import os
import threading
import time
import traceback
from enum import Enum, unique
from typing import Dict, Union, List

from .voice import Voice

ffmpeg_bin = os.environ.get('FFMPEG_BIN', 'ffmpeg')


@unique
class Status(Enum):
    STOP = 0
    WAIT = 1
    SKIP = 2
    END = 3
    PLAYING = 10
    EMPTY = 11


guild_status = {}
play_list: Dict[str, Dict[str, Union[str, Dict, List[Dict]]]] = {}
play_list_example = {"机器人token":
                         {'服务器id':
                              {'token': '机器人token',
                               'voice_channel': '语音频道id',
                               'text_channel': '最后一次执行指令的文字频道id',
                               'now_playing': {'file': '歌曲文件', 'ss': 0, 'start': 0},
                               'play_list': [
                                   {'file': '路径', 'ss': 0}]}}}

playlist_handle_status = {}


class Player:
    def __init__(self, guild_id, voice_channel_id=None, token=None):
        """
            :param str guild_id: 推流服务器id
            :param str voice_channel_id: 推流语音频道id
            :param str token: 推流机器人token
        """
        self.guild_id = str(guild_id)

        if self.guild_id in play_list:
            if token is None:
                token = play_list[self.guild_id]['token']
            else:
                if token != play_list[self.guild_id]['token']:
                    raise ValueError('播放歌曲过程中无法更换token')
            if voice_channel_id is None:
                voice_channel_id = play_list[self.guild_id]['voice_channel']
            else:
                if voice_channel_id != play_list[self.guild_id]['voice_channel']:
                    raise ValueError('播放歌曲过程中无法更换语音频道')
                # 将会支持切换频道
        self.token = str(token)
        self.voice_channel_id = str(voice_channel_id)

    # def join(self):
    #     not finished

    def add_music(self, music: str):
        """Adding music to the playlist
            :param str music: music_file_path or music_url
        """

        if self.voice_channel_id is None:
            raise ValueError('第一次启动推流时，你需要指定语音频道id')
        if self.token is None:
            raise ValueError('第一次启动推流时，你需要指定机器人token')
        if self.guild_id not in play_list:
            play_list[self.guild_id] = {'token': self.token,
                                        'now_playing': None,
                                        'play_list': []}

        if not 'http' in music:
            if not os.path.exists(music):
                # print(real_path)
                raise ValueError('文件不存在')
        play_list[self.guild_id]['voice_channel'] = self.voice_channel_id
        play_list[self.guild_id]['play_list'].append({'file': music, 'ss': 0})
        # print(play_list)

    def stop(self):
        global guild_status
        if self.guild_id not in play_list:
            raise ValueError('该服务器没有正在播放的歌曲')
        guild_status[self.guild_id] = Status.STOP

    def skip(self):
        global guild_status
        if self.guild_id not in play_list:
            raise ValueError('该服务器没有正在播放的歌曲')
        guild_status[self.guild_id] = Status.SKIP

    def list(self, json=True):
        if self.guild_id not in play_list:
            raise ValueError('该服务器没有正在播放的歌曲')
        if json:
            return [play_list[self.guild_id]['now_playing'], *play_list[self.guild_id]['play_list']]
        else:
            ...
            # 懒得写


class PlayHandler(threading.Thread):
    channel_id: str = None

    def __init__(self, guild_id: str, token: str):
        threading.Thread.__init__(self)
        self.token = token
        self.guild = guild_id
        self.voice = Voice(token)
        # self.zmq_port = str(get_free_port())

    def run(self):
        print("开始处理：" + self.guild)
        loop_t = asyncio.new_event_loop()
        loop_t.run_until_complete(self.main())
        print("处理完成：" + self.guild)

    async def main(self):
        task1 = self.push()
        task2 = self.voice.handler()
        task3 = self.stop()

        try:
            # 等待前两个任务任一结束
            await asyncio.wait(
                [task1, task2],
                return_when=asyncio.FIRST_COMPLETED
            )
        except:
            print(traceback.format_exc())
        # finally:
        #     # 取消前两个任务
        #     for task in [task1, task2]:
        #         if not task.done():
        #             task.cancel()

        await task3

    async def stop(self):
        global playlist_handle_status

        if self.guild in play_list:
            del play_list[self.guild]
        if self.guild in playlist_handle_status and playlist_handle_status[self.guild]:
            playlist_handle_status[self.guild] = False

    async def push(self):
        global playlist_handle_status
        playlist_handle_status[self.guild] = True
        if True:
            await asyncio.sleep(1)
            new_channel = play_list[self.guild]['voice_channel']
            last_voice_channel = new_channel
            self.voice.channel_id = new_channel
            while True:
                if len(self.voice.rtp_url) != 0:
                    rtp_url = self.voice.rtp_url
                    break
                await asyncio.sleep(0.2)
            command = f'{ffmpeg_bin} -re -loglevel level+info -nostats -i - -map 0:a:0 -acodec libopus -ab 128k -ac 2 -ar 48000 -f tee [select=a:f=rtp:ssrc=1357:payload_type=100]{rtp_url}'
            p = await asyncio.create_subprocess_shell(
                command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )

            while True:
                await asyncio.sleep(0.5)
                if play_list[self.guild]['now_playing'] and not play_list[self.guild]['play_list']:
                    music_info = play_list[self.guild]['now_playing']
                else:
                    music_info = play_list[self.guild]['play_list'].pop(0)
                    music_info['start'] = time.time()
                    play_list[self.guild]['now_playing'] = music_info
                file = music_info['file']
                # start = time.time()
                # -filter:a "loudnorm=i=-27:tp=0.0"
                command2 = f'{ffmpeg_bin}  -nostats -i "{file}" -filter:a volume=0.4 -ss {music_info["ss"]} -format pcm_s16le -ac 2  -ar 48000 -f wav -'

                p2 = await asyncio.create_subprocess_shell(
                    command2,
                    stdin=asyncio.subprocess.DEVNULL,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.DEVNULL
                )
                print('正在播放', file)
                sleep_control = 1
                every_shard_bytes = 192000 * sleep_control
                sleep_control -= 0.004
                i = 0
                total_audio = b''
                need_break = False
                first_music_start_time = 0
                while True:
                    start_time = time.time()
                    new_audio = await p2.stdout.read()
                    total_audio = total_audio + new_audio
                    audio_slice = total_audio[i * every_shard_bytes:(i + 1) * every_shard_bytes]
                    if need_break:
                        break
                    if not new_audio:
                        if not audio_slice:
                            break
                        if len(audio_slice) < every_shard_bytes:
                            need_break = True
                    elif len(audio_slice) < every_shard_bytes:
                        await asyncio.sleep(0.01)
                        continue
                    p.stdin.write(audio_slice)
                    if first_music_start_time == 0:
                        first_music_start_time = time.time()
                    play_list[self.guild]['now_playing']['ss'] = first_music_start_time - time.time()
                    i += 1
                    flag = 0
                    while True:
                        if self.guild not in guild_status:
                            guild_status[self.guild] = Status.END

                        if guild_status[self.guild] != Status.PLAYING:
                            state = guild_status[self.guild]
                            if state == Status.END:
                                guild_status[self.guild] = Status.PLAYING
                            elif state == Status.SKIP:
                                flag = 1
                                break
                            elif state == Status.STOP:
                                flag = 1
                                play_list[self.guild]['play_list'] = []
                                break
                        elif time.time() - start_time > sleep_control:
                            # flag = 1
                            break
                        else:
                            await asyncio.sleep(0.001)

                    if flag == 1:
                        break
                guild_status[self.guild] = Status.END
                if len(play_list[self.guild]['play_list']) == 0:
                    p.kill()
                    del play_list[self.guild]
                    playlist_handle_status[self.guild] = False
                    break


async def start():
    while True:
        try:
            for guild in play_list.keys():
                self_token = play_list[guild]['token']
                if guild not in playlist_handle_status and len(play_list[guild]) != 0:
                    playlist_handle_status[guild] = True
                    PlayHandler(guild, self_token).start()
                elif guild in playlist_handle_status and not playlist_handle_status[guild] and len(
                        play_list[guild]) != 0:
                    playlist_handle_status[guild] = True
                    PlayHandler(guild, self_token).start()
            await asyncio.sleep(0.1)
        except:
            print(traceback.format_exc())


def run():
    asyncio.run(start())
