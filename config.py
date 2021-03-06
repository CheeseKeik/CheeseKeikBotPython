import os

TOKEN = os.environ["DISCORD_TOKEN"]
PREFIX = "!"
BOT_ID = 976072881329025045

ASSIGN_ROLE = 836478496820822116

ROLES = {
    '🟢': 836478868721500230,
    '🟡': 836478958409220186,
    '<:Paimon_knife:851563052863324160>': 844429845634875432,
}
BAD_WORDS = [
    "блядь", "пидор", "пиздабол", "лузер", "чмо", "идиот", "придурок",
    "тупица", "еблан", "гандон", "соси", "быдло", "пиздуй", "шлюха",
    "test"
]
TRANSLIT = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
            'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h',
            'ц': 'c', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e',
            'ю': 'u', 'я': 'ya', 'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
            'Ж': 'ZH', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
            'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H',
            'Ц': 'C', 'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SHCH', 'Ъ': '', 'Ы': 'y', 'Ь': '', 'Э': 'E',
            'Ю': 'U', 'Я': 'YA'}

POST_ID = 977591363795296266

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
