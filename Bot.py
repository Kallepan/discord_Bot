import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import youtube_dl
import nacl
import datetime
import requests
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD')

queues = {}

client = commands.Bot(command_prefix="!", description="This is a Helper Bot")
#TODO Änderung ab hier.
def check_queue(ctx, id):
    if queues[id] != []:
        voice = ctx.guild.voice_client
        source = queues[id].pop(0)
        player = voice.play(source)

def downloadYoutube(videoURL):
    ydl_opts = {
        'format':'bestaudio/best',
        'outtmpl' : r'audios/temp.mp3',
        'keepVideo' : False,
        'preferredcodec' : [{
            'key' : 'FFmpegExtractAudio',
            'preferredcodec' : 'mp3',
            'preferredquality' : '192',
         }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            request.get(videoURL)
        except:
            videoURL = ydl.extract_info(f"ytsearch:{videoURL}", download = False)['entries'][0]['webpage_url']
        else:
            if("youtube" in videoURL):
                videoURL = ydl.extract_info(videoURL, download = False)['webpage_url']
            else:
                return ""
        queryId = videoURL.split('watch?v=')[1]
        queryId = queryId.split('&')[0]
        filename = r"audios/"+queryId+'.mp3'
        if(os.path.isfile(filename)):
            return filename
        ydl.download([videoURL])

    os.rename(r"audios/temp.mp3",filename)
    
    return filename

#info
@client.command(pass_context = True)
async def info(ctx):
    embed = discord.Embed(title=f"{ctx.guild.name}", timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    embed.add_field(name="Server created at", value=f"{ctx.guild.created_at}")
    embed.add_field(name="Server Owner", value=f"{ctx.guild.owner}")
    embed.add_field(name="Server Region", value=f"{ctx.guild.region}")
    embed.add_field(name="Server ID", value=f"{ctx.guild.id}")
    # embed.set_thumbnail(url=f"{ctx.guild.icon}")
    embed.set_thumbnail(url="https://pluralsight.imgix.net/paths/python-7be70baaac.png")

    await ctx.send(embed=embed)

#behavior commands
@client.command(pass_context = True)
async def join(ctx):
    if(ctx.voice_client):
        await ctx.send("The bot is already present.")
    elif(ctx.author.voice):
        await ctx.message.author.voice.channel.connect()
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        source = FFmpegPCMAudio('join.wav')
        player = voice.play(source)
    else:
        await ctx.send("You need to be in a channel to call the bot.")

#basic youtube commands
@client.command(pass_context = True)
async def play(ctx, url : str):
    if(not ctx.voice_client):
        if(ctx.author.voice):
            await ctx.message.author.voice.channel.connect()
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    guildId = ctx.message.guild.id
   
    song = downloadYoutube(url)
    if(song == ""):
        ctx.send("This URL was not correctly detected.")
        return;
    source = FFmpegPCMAudio(song)

    if guildId in queues:
        queues[guildId].append(source)
    else:
        queues[guildId] = [source]
    
    await ctx.send("Added to the queue")

    if(not voice.is_playing()):
        voice.play(queues[guildId].pop(0), after=lambda x=None: check_queue(ctx, guildId))

@client.command(pass_context = True)
async def leave(ctx):
    if ctx.voice_client:
        await stop(ctx)
        await ctx.guild.voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")

#control the songs
@client.command(pass_context = True)
async def pause(ctx):
    if(not ctx.voice_client):
        return;
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    if(voice.is_playing()):
        voice.pause()
    else:
        await ctx.send("Nothing there to pause.")

@client.command(pass_context = True)
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    if(voice.is_paused()):
        voice.resume()
    else:
        await ctx.send("Nothing there to start")

@client.command(pass_context = True)
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    voice.stop()


#purge the chat
@client.command(pass_context = True)
async def purge(ctx, limit : int):
    await ctx.channel.purge(limit = limit)

# debugcommands
@client.event
async def on_ready():
    print(f'{client.user} is conncected to the following guilds:\n')

    for guild in client.guilds:
        print(f'{guild.name}(id: {guild.id})')

@client.listen()
async def on_message(message):
    message.content = message.content.lower()

    if message.author == client.user:
        return

    if (message.content == "hi") or (message.content == "hallo") or (message.content == "hello"):
        await message.channel.send(f"Hello {message.author}!")

client.run(TOKEN)