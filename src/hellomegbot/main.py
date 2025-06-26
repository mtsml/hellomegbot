import os

import discord
from dotenv import load_dotenv

from .services import HelloRuriService, MmmMmMmmmmmmmService, HellomegService, KeibaResultService, MeggenService
from .commands import hellomeg
from .commands.helloruri import HelloRuri
from .commands.mmm_mm_mmmmmmmm import MmmMmMmmmmmmm
from .commands.fever import Fever
from .commands.keibaresult import Keibaresult
from .commands.meggen import Meggen

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)


def log(*args):
    """ログ出力

    TODO: logging に書き換える
    """
    print(" | ".join(args))


LOG_READY = """
---------------------
| HelloMegBot running
---------------------
"""


@client.event
async def on_ready():
    log(LOG_READY)
    log((f"server len: {len(client.guilds)}"))
    await client.change_presence(activity=discord.CustomActivity(name="アンケート実施中"))
    await tree.sync()


ON_MESSAGE_LOG = "on_message"
ON_MESSAGE_REPLY = "バイめぐー！"


@client.event
async def on_message(message):
    if message.author.bot: return
    if not isinstance(message.channel, discord.DMChannel): return
    # DM は guild_id 取得不可。DM オブジェクトを文字列に変換して渡す
    log(str(message.channel), ON_MESSAGE_LOG)
    await message.reply(ON_MESSAGE_REPLY)



if __name__ == "__main__":
    load_dotenv()

    # /999
    fever_cmd = Fever()
    fever_cmd.register_command(tree)

    # /hellomegu
    hellomeg_service = HellomegService(
        fever_minute=int(os.getenv("HELLOMEG_FEVER_MINUTE", "0")),
        ur_probability=float(os.getenv("HELLOMEG_UR_PROBABILITY", "0.03")),
        sr_probability=float(os.getenv("HELLOMEG_SR_PROBABILITY", "0.18"))
    )
    hellomeg_cmd = hellomeg.Hellomeg(service=hellomeg_service)
    hellomeg_cmd.setup()
    hellomeg_cmd.register_command(tree)

    # /helloruri
    helloruri_service = HelloRuriService(
        ur_probability=float(os.getenv("HELLORURI_UR_PROBABILITY", "0.03")),
        sr_probability=float(os.getenv("HELLORURI_SR_PROBABILITY", "0.18"))
    )
    helloruri = HelloRuri(service=helloruri_service)
    helloruri.setup()
    helloruri.register_command(tree)

    # /mmm-mm-mmmmmmmm
    mmm_service = MmmMmMmmmmmmmService(
        ur_probability=float(os.getenv("MMM_MM_MMMMMMMM_UR_PROBABILITY", "0.012345679")),
        sr_probability=float(os.getenv("MMM_MM_MMMMMMMM_SR_PROBABILITY", "0.18"))
    )
    mmm_mm_mmmmmmmm = MmmMmMmmmmmmm(service=mmm_service)
    mmm_mm_mmmmmmmm.setup()
    mmm_mm_mmmmmmmm.register_command(tree)

    # /keibaresult
    keibaresult_service = KeibaResultService()
    keibaresult_cmd = Keibaresult(service=keibaresult_service)
    keibaresult_cmd.register_command(tree)

    # /meggen
    meggen_service = MeggenService()
    meggen_cmd = Meggen(service=meggen_service)
    meggen_cmd.register_command(tree)

    token = os.getenv("DISCORD_BOT_TOKEN")
    client.run(token)
