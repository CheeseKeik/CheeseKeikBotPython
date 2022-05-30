import nextcord
import datetime
from nextcord.ext import commands
import config

bot = commands.Bot(command_prefix=config.PREFIX)


def show_log_info(member: nextcord.Member, guild: nextcord.Guild):
    """Показывает информацию о пользователе, который только подключился к серверу:
        Логин с тегом, аватар, ID пользователя, время подключения, какой пользователь по счету на сервере"""
    date = (datetime.datetime.now(tz=datetime.timezone.utc) - member.created_at)
    create_date = td_format(date).__str__()
    embed = nextcord.Embed(title="Member joined", colour=nextcord.Colour.green(),
                           description=member.mention + " " + guild.member_count.__str__() + "th to join\ncreated: "
                                       + create_date + " ago",
                           timestamp=datetime.datetime.now(tz=datetime.timezone.utc))

    embed.set_author(name=member.name + "#" + member.discriminator,
                     icon_url=member.avatar.url)
    embed.set_footer(text="ID: " + member.id.__str__())

    return embed


def show_out_info(member: nextcord.Member):
    """Показывает информацию о пользователе, который вышел с сервера:
        Логин с тегом, аватар, ID пользователя, время пребывания на сервере,
        время отключения, бывшие у пользователя роли"""
    roles_mention = map(lambda role: role.mention, reversed(member.roles[1:]))
    roles_mention = str.join(', ', roles_mention)
    date = (datetime.datetime.now(tz=datetime.timezone.utc) - member.joined_at)
    join_date = td_format(date).__str__()
    embed = nextcord.Embed(title="Member left", colour=nextcord.Colour.red(),
                           description=member.mention + " joined: " + join_date + " ago\nRoles: " + roles_mention,
                           timestamp=datetime.datetime.now(tz=datetime.timezone.utc))

    embed.set_author(name=member.name + "#" + member.discriminator,
                     icon_url=member.avatar.url)
    embed.set_footer(text="ID: " + member.id.__str__())

    return embed


def show_info(member: nextcord.Member):
    """Показывает информацию о пользователе:
        Логин с дискриминатором, аватар, ID пользователя, роли, когда аккаунт был создан,
        когда пользователь подключился к серверу"""
    roles_mention = map(lambda role: role.mention, reversed(member.roles[1:]))
    roles_mention = str.join(', ', roles_mention)
    date = (datetime.datetime.now(tz=datetime.timezone.utc) - member.joined_at)
    join_date = td_format(date).__str__()
    date = (datetime.datetime.now(tz=datetime.timezone.utc) - member.created_at)
    create_date = td_format(date).__str__()
    embed = nextcord.Embed(title="Info", colour=member.colour,
                           timestamp=datetime.datetime.now(tz=datetime.timezone.utc))

    embed.add_field(name="Roles:", value=roles_mention, inline=True)

    embed.add_field(name="Created at:",
                    value=member.created_at.strftime("%d/%m/%Y, %H:%M:%S") + "\n" + create_date + " ago",
                    inline=True)

    embed.add_field(name="Joined:",
                    value=member.joined_at.strftime("%d/%m/%Y, %H:%M:%S") + "\n" + join_date + " ago",
                    inline=True)

    embed.set_author(name=member.name + "#" + member.discriminator,
                     icon_url=member.avatar.url)
    embed.set_footer(text="ID: " + member.id.__str__())

    return embed


def invalid_member():
    """Сообщение для команды info, вызываемое при ошибке"""
    embed = nextcord.Embed(title="Member not found", colour=nextcord.Colour.red(),
                           description="Member doesn't exist or invalid input. "
                                       "\nPlease print member name in format: **Member#0000**")
    return embed


def invalid_permissions():
    """Сообщение для команд, требующих особые права"""
    embed = nextcord.Embed(title="У вас недостаточно разрешений на использование этой команды.",
                           colour=nextcord.Colour.red())
    return embed


def invalid_command_purge():
    """Сообщение для команды purge, вызываемое при ошибке"""
    embed = nextcord.Embed(title="Invalid command", colour=nextcord.Colour.red(),
                           description="Please print command in format: \n**!purge [amount of messages to purge]**")
    return embed


def restricted_words(word, member: nextcord.Member):
    """Сообщение появляющееся, когда пользователь использует запрещенные слова"""
    embed = nextcord.Embed(title="Сообщение удалено.", colour=nextcord.Colour.red(),
                           description=f"{member.mention}, ваше сообщение было удалено. "
                                       f"\nПричина удаления: использование запрещенного слова **{word}**"
                                       f"\nПожалуйста, ознакомьтесь с правилами.")
    return embed


def invalid_voice_channel():
    embed = nextcord.Embed(title="Вы не находитесь в голосовом канале.\nНевозможно присоединиться.",
                           colour=nextcord.Colour.red())
    return embed


def left_voice_channel():
    embed = nextcord.Embed(title="Бот отключен от голосового канала",
                           colour=nextcord.Colour.green())
    return embed


def role_info(role, created_on, users):
    """Показывает инфо о конкретной роли"""
    embed = nextcord.Embed(colour=role.color)
    embed.set_author(name=f"Name: {role.name}"
                          f"\nRole ID: {role.id}")
    embed.add_field(name="Users", value=users)
    embed.add_field(name="Mentionable", value=role.mentionable)
    embed.add_field(name="Hoist", value=role.hoist)
    embed.add_field(name="Position", value=role.position)
    embed.add_field(name="Managed", value=role.managed)
    embed.add_field(name="Colour", value=str(role.colour).upper())
    embed.add_field(name='Creation Date', value=created_on)

    return embed


def td_format(td_object):
    seconds = int(td_object.total_seconds())
    periods = [
        ('year', 60 * 60 * 24 * 365),
        ('month', 60 * 60 * 24 * 30),
        ('day', 60 * 60 * 24),
        ('hour', 60 * 60),
        ('minute', 60)
    ]

    strings = []
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            has_s = 's' if period_value > 1 else ''
            strings.append("%s %s%s" % (period_value, period_name, has_s))

    return ", ".join(strings)
