import os
import sys
import traceback
import re
import asyncio
import requests
import subprocess
import urllib.parse
import urllib.request

import nextcord
import yt_dlp
from nextcord.ext import commands

import config
import embed_msg

sys.path.append('.')
yt_dlp.utils.bug_reports_message = lambda: ''
intents = nextcord.Intents().default()
intents.members = True
bot = commands.Bot(command_prefix=config.PREFIX, intents=intents)
connected_to_vc = False

ytdl_format_options = {'format': 'bestaudio',
                       'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
                       'restrictfilenames': True,
                       'no-playlist': True,
                       'nocheckcertificate': True,
                       'ignoreerrors': False,
                       'logtostderr': False,
                       'geo-bypass': True,
                       'quiet': True,
                       'no_warnings': True,
                       'default_search': 'auto',
                       'source_address': '0.0.0.0'}
ffmpeg_options = {'options': '-vn'}
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)
play_queue = []
player_obj_queue = []
servers = []
current_server = None


@bot.event
async def on_ready():
    print('Logged on as {0}!'.format(bot.user))


@bot.event
async def on_message(msg: nextcord.Message):
    """Автомодерация чата"""
    if msg.author.bot:
        return
    word_list = msg.content.split()
    for word in word_list:
        if config.BAD_WORDS.__contains__(word):
            await msg.channel.send(embed=embed_msg.restricted_words(word, msg.author))
            await msg.delete()
    await bot.process_commands(msg)


@bot.event
async def on_raw_reaction_add(payload: nextcord.RawReactionActionEvent):
    if payload.message_id == config.POST_ID:
        member: nextcord.Member = payload.member
        if member.bot:
            return
        message = await member.guild.get_channel(payload.channel_id).fetch_message(payload.message_id)

        for emoji in config.ROLES:
            await message.add_reaction(emoji)

        try:
            emoji = str(payload.emoji)  # эмоджик который выбрал юзер
            role = member.guild.get_role(config.ROLES[emoji])  # объект выбранной роли (если есть)
            await member.add_roles(role)

            game_role = member.guild.get_role(853383668512194560)
            if not member.roles.__contains__(game_role):
                await member.add_roles(game_role)
            print('[SUCCESS] User {0.display_name} has been granted with role {1.name}'.format(member, role))

        except KeyError as e:
            print('[ERROR] KeyError, no role found for ' + emoji)
        except Exception as e:
            print(repr(e))


@bot.event
async def on_raw_reaction_remove(payload: nextcord.RawReactionActionEvent):
    if payload.message_id == config.POST_ID:
        member: nextcord.Member = await bot.get_guild(payload.guild_id).fetch_member(payload.user_id)

        # ВОТ ЗДЕСЬ ПРОБЛЕМА
        # member = utils.get(message.guild.members,
        #                   id=payload.user_id)  # получаем объект пользователя который поставил реакцию
        # КТО НАПИСАЛ ЭТОТ КОД - НЕ ЖАЛЕЕТ ЛЮДЕЙ ^

        try:
            emoji = str(payload.emoji)  # эмоджик который выбрал юзер
            role = member.guild.get_role(config.ROLES[emoji])  # объект выбранной роли (если есть)

            await member.remove_roles(role)
            print('[SUCCESS] Role {1.name} has been remove for user {0.display_name}'.format(member, role))

        except KeyError as e:
            print('[ERROR] KeyError, no role found for ' + emoji)
        except Exception as e:
            print(repr(e))


@bot.event
async def on_member_join(member: nextcord.Member):
    print("Member joined")
    if member.guild.system_channel is not None:
        await member.guild.system_channel.send(embed=embed_msg.show_log_info(member, member.guild))
    await member.add_roles(member.guild.get_role(config.ASSIGN_ROLE))


@bot.event
async def on_member_remove(member: nextcord.Member):
    print("Member left")
    if member.guild.system_channel is not None:
        await member.guild.system_channel.send(embed=embed_msg.show_out_info(member))


@bot.event
async def on_command_error(ctx, error):
    send_help = (
        commands.MissingRequiredArgument, commands.BadArgument, commands.TooManyArguments, commands.UserInputError)

    if isinstance(error, commands.CommandNotFound):  # fails silently
        pass

    elif isinstance(error, send_help):
        _help = await send_cmd_help(ctx)
        await ctx.send(embed=_help)

    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'This command is on cooldown. Please wait {error.retry_after:.2f}s')

    elif isinstance(error, commands.errors.CheckAnyFailure):
        await ctx.send(embed=embed_msg.invalid_permissions())

    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(embed=embed_msg.invalid_permissions())
    # If any other error occurs, prints to console.
    else:
        await ctx.send(f'{ctx.author}\'s message "{ctx.message.content}" triggered error:\n{error}')
        print(''.join(traceback.format_exception(type(error), error, error.__traceback__)))


async def send_cmd_help(ctx):
    cmd = ctx.command
    em = nextcord.Embed(title=f'Usage: {ctx.prefix + cmd.signature}')
    em.color = nextcord.Color.green()
    em.description = cmd.help
    return em


@bot.command()
@commands.check_any(commands.has_guild_permissions(kick_members=True),
                    commands.has_guild_permissions(administrator=True),
                    commands.has_guild_permissions(ban_members=True),
                    commands.has_guild_permissions(mute_members=True))
async def info(ctx, member_fullname):
    """Получает информацию о пользователе. Mods only"""
    try:
        member_name = member_fullname.split("#")[0]
        member_discriminator = member_fullname.split("#")[-1]
        list_member_names = []
        for member in ctx.guild.members:
            if member.name == member_name:
                list_member_names.append(member)
        member = nextcord.utils.find(lambda m: m.discriminator == member_discriminator, list_member_names)
        await ctx.send(embed=embed_msg.show_info(member))
    except AttributeError as e:
        await ctx.send(embed=embed_msg.invalid_member())
        print(e)


@bot.command()
async def ping(ctx):
    """Возвращает время отклика бота"""
    em = nextcord.Embed(color=nextcord.Color.green())
    em.title = "Pong!"
    em.description = f'{bot.latency * 1000} ms'
    await ctx.send(embed=em)


@bot.command()
@commands.check_any(commands.has_guild_permissions(kick_members=True),
                    commands.has_guild_permissions(administrator=True),
                    commands.has_guild_permissions(ban_members=True),
                    commands.has_guild_permissions(mute_members=True))
async def purge(ctx, delete_amount):
    """Удаляет n последних сообщений в канале. Mods only"""
    try:
        await ctx.message.channel.purge(limit=int(delete_amount) + 1)
        print(f"{delete_amount} message(s) were successfully deleted!")
    except ValueError as e:
        await ctx.send(embed=embed_msg.invalid_command_purge())
        print(e)


@bot.command()
async def translit(ctx, rus_to_eng):
    """Пишет сообщение пользователя транслитом"""
    for key in config.TRANSLIT:
        rus_to_eng = rus_to_eng.replace(key, config.TRANSLIT[key])
    await ctx.send(rus_to_eng)
    await ctx.message.delete()


@bot.command(aliases=['ri', 'role'])
async def roleinfo(ctx, *, role: nextcord.Role):
    """Показывает инфо о конкретной роли"""
    guild = ctx.guild
    since_created = (ctx.message.created_at - role.created_at).days
    role_created = role.created_at.strftime("%d %b %Y %H:%M")
    created_on = "{} ({} days ago)".format(role_created, since_created)
    users = len([x for x in guild.members if role in x.roles])
    await ctx.send(embed=embed_msg.role_info(role, created_on, users))


@bot.command()
async def fox(ctx):
    """Отправляет рандомную картинку лисы"""
    await ctx.message.delete()
    r = requests.get('https://randomfox.ca/floof/').json()  # TODO: same with cakes
    em = nextcord.Embed(title="Random fox image", color=16202876)
    em.set_image(url=r["image"])
    await ctx.send(embed=em)


for file in os.listdir():
    if file.endswith('.webm'):
        os.remove(file)


def get_res_path(relative_path):
    """Получает абсолютный путь к ресурсу, работает для dev и для PyInstaller
     Относительный путь всегда будет извлечен в root"""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
    if os.path.isfile(os.path.join(base_path, relative_path)):
        return os.path.join(base_path, relative_path)
    else:
        raise FileNotFoundError(f'Embedded file {os.path.join(base_path, relative_path)} is not found!')


nextcord.opus.load_opus(get_res_path('libopus-0.dll'))


class YTDLSource(nextcord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(nextcord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


@bot.command()
@commands.is_owner()
async def debug(ctx, *, code):
    """Только хозяин бота может использовать, evaluates code"""
    await ctx.send(eval(code))


async def connect_to_voice_channel(ctx, channel):
    global voice_client, connected_to_vc
    voice_client = await channel.connect()
    if voice_client.is_connected():
        connected_to_vc = True
        await ctx.send(f'Connected to {voice_client.channel.name}')
    else:
        connected_to_vc = False
        await ctx.send(f'Failed to connect to voice channel {ctx.author.voice.channel.name}')


@bot.command()
async def disconnect(ctx):
    """Отключает бота от голосового канала"""
    global connected_to_vc, play_queue, player_obj_queue, current_server
    if connected_to_vc:
        await voice_client.disconnect()
        await ctx.send(f'Disconnected from {voice_client.channel.name}')
        connected_to_vc = False
        play_queue = []
        player_obj_queue = []
        current_server = None


@bot.command()
async def pause(ctx):
    """Останавливает текущую песню"""
    if connected_to_vc and voice_client.is_playing():
        voice_client.pause()
        await ctx.send('Paused')


@bot.command()
async def resume(ctx):
    """Возобновляет текущую песню"""
    if connected_to_vc and voice_client.is_paused():
        voice_client.resume()
        await ctx.send('Resumed')


@bot.command()
async def skip(ctx):
    """Пропускает текущую песню"""
    if connected_to_vc and voice_client.is_playing():
        voice_client.stop()
        await play_next(ctx)


@bot.command()
async def queue(ctx):
    """Показывает текущую очередь"""
    if connected_to_vc:
        await ctx.send(f'{play_queue}')


@bot.command()
async def remove(ctx, id: int):
    """Убирает песню из очереди по индексу (1...)"""
    if connected_to_vc:
        if id == 0:
            await ctx.send('Cannot remove current playing song')
        else:
            await ctx.send(f'Removed {play_queue[id]}')
            play_queue.pop(id)
            player_obj_queue.pop(id)


@bot.command()
async def clear(ctx):
    """Очищает очередь и останавливает текущую песню"""
    global play_queue, player_obj_queue
    if connected_to_vc and voice_client.is_playing():
        voice_client.stop()
        play_queue = []
        player_obj_queue = []
        await ctx.send('Queue cleared.')


@bot.command()
async def song(ctx):
    """Показывает текущую песню"""
    if connected_to_vc:
        await ctx.send(f'Currently playing {play_queue[0]}')


async def play_next(ctx):
    print('\nPlaying next...')
    if play_queue:
        await play_song(ctx, player_obj_queue[0])
    else:
        await ctx.send('Reached end of queue')


def callback(e):
    if e:
        print(f'Error: {e}')
    else:
        # finished playing prev song without error so removing entry from queue here
        print('\nPlaying next...')
        if play_queue:
            play_queue.pop(0)
        if player_obj_queue:
            player_obj_queue.pop(0)
            voice_client.play(player_obj_queue[0], after=callback)
        else:
            print('Reached end of queue')


async def play_song(ctx, link):
    async with ctx.typing():
        try:
            player = await YTDLSource.from_url(link, loop=bot.loop, stream=False)
        except Exception as e:
            print('Error encountered. Attempting to clear cache and retry...')
            subprocess.call('yt-dlp --rm-cache-dir', shell=True)
            player = await YTDLSource.from_url(link, loop=bot.loop, stream=False)
        player_obj_queue.append(player)
        if not voice_client.is_playing():
            voice_client.play(player_obj_queue[0], after=callback)
            await ctx.send(f'Now playing: {player_obj_queue[0].title}')


@bot.command()
async def play(ctx, *, song: str):
    """Воспроизведение видео YouTube по URL, если задан URL,
    или ищет песню и воспроизводит первое видео в результате поиска."""
    global connected_to_vc, current_server
    if current_server and current_server != ctx.guild:
        await ctx.send('The bot is currently being used in another server.')
        return
    elif current_server is None:
        current_server = ctx.guild
    if not connected_to_vc:
        if ctx.author.voice is None:
            connected_to_vc = False
            await ctx.send(f'You are not connected to any voice channel!')
        else:
            await connect_to_voice_channel(ctx, ctx.author.voice.channel)
    elif voice_client.channel != ctx.author.voice.channel:
        await voice_client.move_to(ctx.author.voice.channel)
    if connected_to_vc:
        try:
            requests.get(song)
        except (requests.ConnectionError, requests.exceptions.MissingSchema):
            URL = False
        else:
            URL = True
        if URL:
            link = song
        else:
            # Search up the query and play the first video in search result
            query_string = urllib.parse.urlencode({"search_query": song})
            format_url = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)
            search_results = re.findall(r"watch\?v=(\S{11})", format_url.read().decode())
            link = f'https://www.youtube.com/watch?v={search_results[0]}'
        play_queue.append(link)
        if voice_client.is_playing():
            await ctx.send(f'Added to queue: {song}')
        await play_song(ctx, link)


bot.run(config.TOKEN)
