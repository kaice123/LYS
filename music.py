import discord
from discord.ext import commands
from discord.utils import get

import youtube_dl
import requests
import asyncio
import time
import ffmpeg


class Music(commands.Cog):

    """
    노래듣쟈!
    """
    
    def __init__(self, client):
        self.client = client
        self.song_queue = []
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    def parse_duration(self, duration):
        result = []
        seconds = duration%60
        minutes = duration//60
        hour = minutes//60
        day = hour//24
        
        def parse_duration(self, duration):
            result, suffix = [], ['s', 'min', 'h', 'j']
            seconds = duration%60
            minutes = duration//60
            hour = minutes//60
            day = hour//24
            
            for y, x in zip([x for x in [seconds, minutes, hour, day] if x != 0], suffix):
                result.append(str(y) + x)
            return "".join(result)
    
    def search(self, ctx, arg):
        ydl_opts = {'format': 'bestaudio', 'noplaylist':'True'}
        try:
            temp = "".join(arg[:])
            response = requests.get(temp)
        except:
            arg = " ".join(arg[:])
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{arg}", download=False)
                title = info['entries'][0]['title']
                url = info['entries'][0]['webpage_url']
                source = info['entries'][0]['formats'][0]['url']
                uploader = info['entries'][0]['uploader']
                uploader_url = info['entries'][0]['channel_url']
                duration = self.parse_duration(info['entries'][0]['duration'])
                thumbnail = info['entries'][0]['thumbnail']
        else:
            arg = "".join(arg[:])
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(arg, download=False)
                title = info['title']
                url = info['webpage_url']
                source = info['formats'][0]['url']
                uploader = info['uploader']
                uploader_url = info['channel_url']
                duration = self.parse_duration(info['duration'])
                thumbnail = info['thumbnail']
            
        embed = (discord.Embed(title='🎵 노래하는중:', description=f'{title}', color=discord.Color.blue())
                 .set_thumbnail(url="thumbnail")
                 .add_field(name='이예에', value=ctx.message.author.display_name)
                 .add_field(name='노래 업로더', value=f'[{uploader}]({uploader_url})')
                 .add_field(name='노래 링크', value=f'[클릭!]({url})')
                 .set_footer(text="내 컴 상태가 안좋으면 노래 안나와요.. 미아내ㅜㅜ")
                 .set_thumbnail(url=thumbnail))
        
        return {'embed': embed, 'source': source, 'title': title}

    @commands.command(aliases=['ㅔ'], brief='p', usage="릿! ㄱ <음악 이름> or <링크>" )
    async def play(self, ctx, *arg):
        channel = ctx.message.author.voice.channel
        if not channel:
            await ctx.send("~~노래할 곳에 들어가바~~")
        else:
            voice = get(self.client.voice_clients, guild=ctx.guild)
            if voice and voice.is_connected():
                await voice.move_to(channel)
            else:
                await ctx.send(f'**{channel}** 에서 놀면 되는거야?')
                voice = await channel.connect()
            def play_next(ctx):
                del self.song_queue[0]
                if len(self.song_queue) >= 1:
                    voice = get(self.client.voice_clients, guild=ctx.guild)
                    voice.play(discord.FFmpegPCMAudio(self.song_queue[0]['source'], **self.FFMPEG_OPTIONS), after=lambda e: play_next(ctx))
                    asyncio.run_coroutine_threadsafe(ctx.send(embed=self.song_queue[0]['embed']), self.client.loop).result()
                else:
                    asyncio.sleep(90)
                    voice = get(self.client.voice_clients, guild=ctx.guild)
                    if not voice.is_playing():
                        asyncio.run_coroutine_threadsafe(self.client.voice_clients[0].disconnect(), self.client.loop).result()
                        
            song = self.search(ctx, arg)
            if not voice.is_playing():
                self.song_queue.append(song)
                voice.play(discord.FFmpegPCMAudio(song['source'], **self.FFMPEG_OPTIONS), after=lambda e: play_next(ctx))
                await ctx.send(embed=song['embed'])
                voice.is_playing()
            else:
                self.song_queue.append(song)
                await ctx.send(f"**{song['title']}** 듣는거 마자? ({len(self.song_queue)-1} to go)")

    @commands.command(aliases=['list'], brief='목록')
    async def queue(self, ctx):
        channel = ctx.message.author.voice.channel
        voice = get(self.client.voice_clients, guild=ctx.guild)
        embed = discord.Embed(color=discord.Color.blue(), title="⏱️ 대기열:")
        if voice and voice.is_playing():
            for i in self.song_queue:
                if self.song_queue.index(i) == 0:
                    embed.add_field(name=f'**지금 듣는거 :**', value=f"{i['title']}", inline=False)
                else:
                    embed.add_field(
                        name=f'**🎵 {self.song_queue.index(i)}번째 들을 노래 :**', value=f"{i['title']}", inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("우웅..? 지금 쉬는중인데에...")

    @commands.command(aliases=['pau'], brief='ㄴ')
    async def pause(self, ctx):
        voice = get(self.client.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            if voice.is_playing():
                await ctx.send('⏸️ ㅇ')
                voice.pause()
            else:
                await ctx.send('⏯️ ㅇ')
                voice.resume()
        else:
            await ctx.send("우웅..? 지금 쉬는중인데에...")

    @commands.command(aliases=['스킵'], brief='s')
    async def skip(self, ctx):
        voice = get(self.client.voice_clients, guild=ctx.guild)
        if voice and voice.is_playing():
            await ctx.send('⏭️ ㅇ')
            voice.stop()
        else:
            await ctx.send("지금 노는중임")

def setup(client):
    client.add_cog(Music(client))