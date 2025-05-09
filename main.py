import glob
import io
import os
import random
import unicodedata

import discord
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

import meggen
from src.hellomegbot.commands import hellomeg
from src.hellomegbot.commands.helloruri import HelloRuri

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


FEVER_COMMAND_NAME = "999"
FEVER_COMMAND_DESC = "何かが999倍の画像をつくる"
FEVER_MESSAGE_TOO_LONG_INPUT = "ちょっとちょっと！\nそんな長いセリフ、めぐちゃん覚えられえないよ！\n（それぞれ全角5文字以内で入力してください）"
FEVER_TEMPLATE_PNG_PATH = "assets/fever/template.png"
FEVER_TEXT_COLOR = "#764c4d"
FEVER_TEXT_SIZE = 100
FEVER_TEXT_FONT_FAMILY = "MPLUSRounded1c-Black.ttf"
FEVER_TEXT_SEND_FILENAME = "fever.png"


@tree.command(name=FEVER_COMMAND_NAME, description=FEVER_COMMAND_DESC)
async def fever(interaction: discord.Interaction, 一行目: str, 二行目: str):
    """999倍の画像を作成するスラッシュコマンド

    ユーザーが引数として与えた二つの文字列をテンプレート画像に埋め込んで画像を生成する。
    
    テンプレート画像には最大で一行あたり全角5文字を埋め込むスペースがある。
    実装上は len_half_width で全角5文字と同数としてカウントされる半角10文字をバリデーションの基準としている。
    バリデーションに抵触した場合、スラッシュコマンドを利用したユーザーにのみ見える警告メッセージを表示する。
    このとき画像は生成しない。

    半角10文字はバリデーションに抵触しないが、これをテンプレート画像に埋め込むと文字列の表示領域をはみ出す。
    埋め込みに利用しているフォントの半角文字の幅が、全角文字の半分よりも大きいため、この現象が発生する。
    等幅フォントではなく制限が難しいこと、ユースケースとして半角文字の使用は少ないと考えられることから、この現象を許容する。
    """
    log(str(interaction.guild_id), "command", f"/{FEVER_COMMAND_NAME}", f"一行目: {一行目}, 二行目: {二行目}")

    if len_half_width(一行目) > 10 or len_half_width(二行目) > 10:
        await interaction.response.send_message(FEVER_MESSAGE_TOO_LONG_INPUT, ephemeral=True)
        return

    text = f"{一行目}\n{二行目}"
    img = Image.open(FEVER_TEMPLATE_PNG_PATH)
    draw_text(text, img, (80, 280))

    arr = io.BytesIO()
    img.save(arr, format="PNG")
    arr.seek(0)
    file = discord.File(arr, filename=FEVER_TEXT_SEND_FILENAME)

    await interaction.response.send_message(file=file)


def len_half_width(text: str) -> int:
    """半角で何文字かを数える
    """
    return sum([(1, 2)[unicodedata.east_asian_width(char) in "FWA"] for char in text])


def draw_text(text: str, targetImg, xy):
    """targetImg に text を画像として埋め込む
    """
    textImg = Image.new("RGBA", (600, 330), (0, 0, 0, 0))
    textDraw = ImageDraw.Draw(textImg)
    font = ImageFont.truetype(FEVER_TEXT_FONT_FAMILY, FEVER_TEXT_SIZE)
    textDraw.text((20, 15), text, FEVER_TEXT_COLOR, font=font)
    textImg = textImg.rotate(14)
    targetImg.paste(textImg, xy, textImg)


KEIBA_RESULT_COMMAND_NAME = "keibaresult"
KEIBA_RESULT_COMMAND_DESC = "競馬の結果を報告する"
KEIBA_RESULT_WIN_PNG_DIR = "assets/keibaresult/win/"
KEIBA_RESULT_LOSE_PNG_DIR = "assets/keibaresult/lose/"
KEIBA_RESULT_DRAW_PNG_DIR = "assets/keibaresult/draw/"
KEIBA_RESULT_WIN_MESSAGE = "ハロめぐー！"
KEIBA_RESULT_LOSE_MESSAGE = "バイめぐ〜"
KEIBA_RESULT_DRAW_MESSAGE = "めぐ"
KEIBA_RESULT_ERROR_REQUIRE_MORE_THAN_ZERO = "amount に 0 より大き値を入れろ"
KEIBA_RESULT_ERROR_REQUIRE_ZERO = "amount に 0 を入れろ"

@tree.command(name=KEIBA_RESULT_COMMAND_NAME, description=KEIBA_RESULT_COMMAND_DESC)
@discord.app_commands.choices(
    result=[
        discord.app_commands.Choice(name=KEIBA_RESULT_WIN_MESSAGE, value=KEIBA_RESULT_WIN_MESSAGE),
        discord.app_commands.Choice(name=KEIBA_RESULT_LOSE_MESSAGE, value=KEIBA_RESULT_LOSE_MESSAGE),
        discord.app_commands.Choice(name=KEIBA_RESULT_DRAW_MESSAGE, value=KEIBA_RESULT_DRAW_MESSAGE)
    ]
)
@discord.app_commands.describe(
    result="今日の競馬の結果は？",
    amount="いくら？"
)
async def keibaresult(interaction: discord.Interaction, result: str, amount: discord.app_commands.Range[int, 0, None]):
    """競馬の結果に対して返答するスラッシュコマンド

    - 収支がプラスの場合は「ハロめぐー！」と勝利イラストを返答する
    - 収支がマイナスの場合は「バイめぐ〜」と敗北イラストを返答する
    - 収支がプラマイゼロの場合は「めぐ」とドローイラストを返答する
    """
    log(str(interaction.guild_id), "command", f"/{KEIBA_RESULT_COMMAND_NAME}", f"result: {result}, amount: {amount}")

    # かった
    if result == KEIBA_RESULT_WIN_MESSAGE:
        if amount == 0:
            await interaction.response.send_message(KEIBA_RESULT_ERROR_REQUIRE_MORE_THAN_ZERO, ephemeral=True)
            return
        filepaths = [f for f in glob.glob(os.path.join(KEIBA_RESULT_WIN_PNG_DIR, "*.png"))]
        format_amount = f"{amount:,}"
        message = {
            "content": f"{KEIBA_RESULT_WIN_MESSAGE} (+{format_amount})",
            "file": discord.File(random.choice(filepaths))
        }
    # まけた
    if result == KEIBA_RESULT_LOSE_MESSAGE:
        if amount == 0:
            await interaction.response.send_message(KEIBA_RESULT_ERROR_REQUIRE_MORE_THAN_ZERO, ephemeral=True)
            return
        filepaths = [f for f in glob.glob(os.path.join(KEIBA_RESULT_LOSE_PNG_DIR, "*.png"))]
        format_amount = f"{amount:,}"
        message = {
            "content": f"{KEIBA_RESULT_LOSE_MESSAGE} (-{format_amount})",
            "file": discord.File(random.choice(filepaths))
        }
    # どろー
    if result == KEIBA_RESULT_DRAW_MESSAGE:
        if amount != 0:
            await interaction.response.send_message(KEIBA_RESULT_ERROR_REQUIRE_ZERO, ephemeral=True)
            return
        message = {
            "content": f"{KEIBA_RESULT_DRAW_MESSAGE} (±0)"
        }

    await interaction.response.send_message(**message)


@tree.command(name=meggen.COMMAND_NAME, description=meggen.COMMAND_DESC)
@discord.app_commands.choices(**meggen.COMMAND_CHOICES)
@discord.app_commands.describe(**meggen.COMMAND_CHOICES_DESCRIBE)
@discord.app_commands.rename(**meggen.COMMAND_CHOICES_RENAME)
async def hundle_meggen(interaction: discord.Interaction, img: str) -> None:
    """任意のテキストを入れたハロめぐのイラストをつくる
    """
    log(str(interaction.guild_id), "command", f"/{meggen.COMMAND_NAME}", img)
    await meggen.command(interaction, img)


if __name__ == "__main__":
    load_dotenv()

    # /hellomegu
    hellomeg.setup_hellomeg()
    hellomeg_fever_minute = int(os.getenv("HELLOMEG_FEVER_MINUTE", hellomeg.hellomeg_fever_minute))
    hellomeg_ur_probability = float(os.getenv("HELLOMEG_UR_PROBABILITY", hellomeg.hellomeg_ur_probability))
    hellomeg_sr_probability = float(os.getenv("HELLOMEG_SR_PROBABILITY", hellomeg.hellomeg_sr_probability))
    hellomeg.set_config(hellomeg_fever_minute, hellomeg_ur_probability, hellomeg_sr_probability)
    hellomeg.register_command(tree)

    # /helloruri
    helloruri = HelloRuri()
    helloruri.setup()
    helloruri.register_command(tree)

    token = os.getenv("DISCORD_BOT_TOKEN")
    client.run(token)
