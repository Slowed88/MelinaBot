import discord
from discord.ext import commands
from urllib.parse import urlparse, parse_qs
import asyncio
import pytube
import random
import subprocess
import os
from discord.ui import Button, View 
from discord import ButtonStyle
import re
import urllib.request
import urllib.parse
import sys
import locale

sys.stdout.reconfigure(encoding="utf-8")
locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

bot = commands.Bot(command_prefix="$$", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")

class MyView(discord.ui.View):
    @discord.ui.button(label="stop",row=0, style = discord.ButtonStyle.red)
    async def first_button_callback(self,button,interaction):
        await stop(interaction)

    @discord.ui.button(label = "skip", row=0, style=discord.ButtonStyle.primary)
    async def second_button_callback(self,button,interaction):
        await skip(interaction)

    @discord.ui.button(label="shuffle", row = 0, style = discord.ButtonStyle.primary)
    async def third_button_callback(self,button,interaction):
        await shuffle(interaction)

    @discord.ui.button(label="pause", row = 0, style = discord.ButtonStyle.primary)
    async def fourth_button_callback(self,button,interaction):
        await pause(interaction)

    @discord.ui.button(label="clean", row=0, style= discord.ButtonStyle.primary)
    async def fifth_button_callback(self,button,interaction):
        await clean(interaction)
    
    @discord.ui.button(label="loop",row = 1, style= discord.ButtonStyle.primary)
    async def sixth_button_callback(self,button,interaction):
        await loopsongi(interaction)

@bot.command()
async def botoninho(ctx):

    view = MyView()
    await ctx.send(f"", view=view)

loop = False
@bot.command()
async def loopsongi(ctx):
    global loop
    loop = not loop
    if loop == True: await ctx.send("Temaiken")
    if loop == False: await ctx.send("Reanudadno la programacion predeterminada")

queue =[]


def extract_video_id(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    video_id=query_params.get("v")
    if video_id:
        return video_id[0]
    return None

@bot.command()
async def play(ctx,url):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)


    queue.append(url)

    voice_channel = ctx.author.voice.channel
    if not voice_channel:
        await ctx.send("Metete a un canal de voz primero capo")
        return

    if voice_client and voice_client.is_connected():
        await voice_client.move_to(voice_channel)
    else:
        voice_client = await voice_channel.connect()

    while len (queue)>0:
        if len(queue)>= 1:
            while voice_client.is_playing():
                await asyncio.sleep(1)

            print(queue)


        if "playlist" in url:
            try:
                queue.pop(0)
                queue.pop(0)
            finally:
                await playlist_url (ctx,url)
        url = queue [0]
        video_id = extract_video_id(url)
        if video_id:
            video = pytube.YouTube(url)

            audio_url = video.streams.get_audio_only().url
            output_file = "output.mp3"

            try: os.remove(output_file)

            finally: subprocess.run(["ffmpeg","-i", audio_url, "-b:a","64k","-bufsize","10000k","-fs","10M", output_file])
            audio_file = discord.FFmpegPCMAudio(source = output_file)
            voice_client.play(audio_file)
            await ctx.send(f"Now playing: {url}")
            await botoninho(ctx)
            await asyncio.sleep(10)
            while loop:
                while voice_client.is_playing():
                    await asyncio.sleep(2)
                audio_file2 = discord.FFmpegPCMAudio (source = output_file)
                voice_client.play(audio_file2)
                await ctx.send(f"Now playing: {url}")
                await botoninho(ctx)

            queue.pop(0)
        else:
            await queue.clear()
            await ctx.send("Y si pones un link de youtube quizas te pueda poner una cancion maestro")

async def playlist_url(ctx,url):
    playlist = pytube.Playlist(url)
    await ctx.send(f"Agregando lista de reproducción: {playlist.title}")

    for video_url in playlist.video_urls:
        queue.append(video_url)
    queue.pop(0)
    random.shuffle(queue)
    for video_url in playlist.video_urls:
        await play(ctx,queue[0])


@bot.event
async def on_command_error(ctx,error):

    if isinstance(error,commands.CommandNotFound):
        return
    
    print(f"An error ocurred: {error}")

@bot.command()
async def loopsong(ctx):

    if loop== False:
        loop = True
        await ctx.send("Temaiken")
    if loop == True:
        loop = False
        await ctx.send("Prosiguiendo con la queue")

@bot.command()
async def resume(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild = ctx.guild)

    if voice_client.is_paused():
        voice_client.resume()

    await ctx.send(":)")

@bot.command()
async def skip(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild = ctx.guild)

    if voice_client.is_playing():
        voice_client.stop()
        if len(queue)==0:
            await ctx.send("Playlist vacia")
        else:
            await ctx.send("Skipping the current song.")

@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await ctx.send("OMW")
    await channel.connect()
    await asyncio.sleep(1)
    voice_client = discord.utils.get(bot.voice_clients, guild = ctx.guild)
    audio_source4 = "/root/oyahoo.mp3"
    audio_file4 = discord.FFmpegPCMAudio(source = audio_source4)
    voice_client.play(audio_file4)


@bot.command()
async def stop(ctx):
    await ctx.send("Cya")
    voice_client = discord.utils.get(bot.voice_clients, guild = ctx.guild)
    if voice_client.is_playing():
        voice_client.stop()
    audio_source3 = "/root/sayonara.mp3"
    audio_file3 = discord.FFmpegPCMAudio(source = audio_source3)
    voice_client.play(audio_file3)
    await asyncio.sleep(4)
    await voice_client.disconnect()
    await queue.clear()
    if len(queue)==0:
        await ctx.send("Playlist vacia")

@bot.command()
async def lista(ctx):
    await ctx.send(str(queue))

@bot.command()
async def clean(ctx):
    await ctx.send("playlist vacia")
    await queue.clear()


@bot.command()
async def shuffle(ctx):
    random.shuffle(queue)
    await ctx.send("No")

@bot.command()
async def pause (ctx):
    await ctx.send("dale dale ahi hago lo que vos me digas")

async def searchsongis(ctx,input):

    html = urllib.request.rulopen("https://www.youtube.com/results?search_query="+input)
    global video_ids3
    video_ids3 = re.findall(r"watch\?v=(S{11})",html.read().decode())
    for i in range(0,6,2):
        await ctx.send(f"https://youtube.com/watch?v="+video_ids3[i])
    await botoninho3(ctx)


@bot.command()
async def search(ctx,*,args):

    if " "in args:
        global termino
        termino = args.replace (" ", "%20").replace("\xf1","n")
    await searchsongis(ctx,termino)

    await asyncio.sleep(10)

    if len(queue)>0:
        await ctx.send("starting soon")
        await play(ctx,queue[0])

class MyView2(discord.ui.View):
    @discord.ui.button(label = "opcion 1", row=0, style = discord.ButtonStyle.primary)
    async def first_button_callback(self,button,interaction):
        queue.append("https://www.youtube.com/watch?v="+video_ids3[0])

    @discord.ui.button(label = "opcion 2", row=0, style = discord.ButtonStyle.primary)
    async def first_button_callback(self,button,interaction):
        queue.append("https://www.youtube.com/watch?v="+video_ids3[2])

    @discord.ui.button(label = "opcion 3", row=0, style = discord.ButtonStyle.primary)
    async def first_button_callback(self,button,interaction):
        queue.append("https://www.youtube.com/watch?v="+video_ids3[4])

async def botoninho3(ctx):
    view=MyView2()
    await ctx.send(f"", view = view)

class MyView4(discord.ui.View):
    @discord.ui.button(label="1v9", row = 0, style= discord.Button.Style.red)
    async def afirst_button_callback(self,button,interaction):
        queue.append("playlist1")

    @discord.ui.button(label="hidden rat", row = 0, style= discord.Button.Style.red)
    async def afirst_button_callback(self,button,interaction):
        queue.append("ratirl playlist")

    @discord.ui.button(label="try harder", row = 0, style= discord.Button.Style.red)
    async def afirst_button_callback(self,button,interaction):
        queue.append("frenchcore")

async def hidden_choice(ctx):
    view=MyView4()
    await ctx.send(f"", view = view)

@bot.command()
async def hidden(ctx):
    await hidden_choice(ctx)
    while len(queue)==0:
        await asyncio.sleep(10)
    if len(queue)>0:
        await play(ctx,queue[0])












bot.run("bot-key")






























