import discord
import spotipy
import youtube_dl

from discord.ext import commands

# Configurações do bot
TOKEN = 'MTA2ODIwNTc2NzA4NzM1Nzk4Mg.GVln6-.OxMC7T9u-07FKLvkKYemYvbARJA6qKf0K4qej0'
SPOTIFY_CLIENT_ID = '0c88316be51540e0bdd25144257e10b9'
SPOTIFY_CLIENT_SECRET = '38a469c8e1994460968a2dd47bd607bd'

# Configurações do YouTube-DL
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'noplaylist': True,
    'quiet': True
}

intents = discord.Intents.default()
intents.typing = True
intents.presences = True

permissions = discord.Permissions(permissions=41779360956272)

bot = commands.Bot(command_prefix='!', intents=intents, permissions=permissions)


@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')


@bot.command()
async def play(ctx, *, url):
    voice_channel = ctx.author.voice.channel
    voice_client = await voice_channel.connect()

    if 'spotify.com' in url:
        track_id = get_spotify_track_id(url)
        if track_id:
            url = get_youtube_url_from_track_id(track_id)
        else:
            await ctx.send('Não foi possível obter o ID da faixa do Spotify.')
            await voice_client.disconnect()
            return

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            voice_client.play(discord.FFmpegPCMAudio(url2))
    except Exception as e:
        print(f'Erro ao reproduzir música: {e}')
        await ctx.send('Ocorreu um erro ao reproduzir a música.')


@bot.command()
async def stop(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client.is_playing():
        voice_client.stop()
    await voice_client.disconnect()


def get_spotify_track_id(url):
    sp = spotipy.Spotify(auth_manager=spotipy.oauth2.SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    ))
    try:
        track_id = sp.track(url)['id']
        return track_id
    except Exception as e:
        print(f'Erro ao obter ID da faixa do Spotify: {e}')
        return None


def get_youtube_url_from_track_id(track_id):
    search_query = f'{track_id} official audio'
    youtube_dl_opts = {
        'default_search': 'ytsearch',
        'quiet': True
    }
    with youtube_dl.YoutubeDL(youtube_dl_opts) as ydl:
        try:
            info = ydl.extract_info(search_query, download=False)
            url = info['entries'][0]['formats'][0]['url']
            return url
        except Exception as e:
            print(f'Erro ao obter URL do YouTube: {e}')
            return None


@bot.command()
async def hello(ctx):
    await ctx.send('Oi!')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.lower() == '!hello':
        await bot.process_commands(message)
        return

    await bot.process_commands(message)


bot.run(TOKEN)



