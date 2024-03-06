import io
import os
import random
import unicodedata

import discord
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont


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


HELLOMEG_COMMAND_NAME = "hellomeg"
HELLOMEG_COMMAND_DESC = "ハロめぐー！"
HELLOMEG_MESSAGE_MEDIUM = """
＿人人人人人人人人＿
＞　ハロめぐー！　＜
￣Y^Y^Y^Y^Y^Y^Y￣
"""
HEELOMEG_MESSAGE_LARGE = """
​           
   ■       
   ■   ■   
   ■   ■   
  ■■   ■   
  ■     ■  
  ■     ■  
 ■      ■■ 
 ■       ■ 
           
　■■■■■■■■  
　■       ■ 
　■       ■ 
　■       ■ 
　■       ■ 
　■       ■ 
　■       ■ 
　■■■■■■■■■ 
         
      ■     
  ■   ■     
  ■■■ ■■■   
  ■■  ■ ■■  
 ■ ■ ■   ■  
 ■ ■ ■   ■  
 ■  ■    ■  
 ■ ■■   ■   
 ■■■   ■    
         
      ■    
     ■■    
   ■■      
  ■■  ■ ■  
 ■     ■   
 ■■        
  ■■       
    ■■     
     ■■    
         
     ■■
     ■■
     ■■
     ■■
     ■■
     ■■
     ■■
       
     ■■
"""
HELLOMEG_FEVER_PNG_PATH = "assets/hellomeg/fever.png"
HELLOMEG_LOSER_PNG_PATH = "assets/hellomeg/loser.png"
HELLOMEG_STAND_PNG_PATH = "assets/hellomeg/stand.png"


@tree.command(name=HELLOMEG_COMMAND_NAME, description=HELLOMEG_COMMAND_DESC)
async def hellomeg(interaction: discord.Interaction):
    """多様なハロめぐー！を返答するスラッシュコマンド

    それぞれの確率にもとづきアスキーアートや画像をユーザーに返答する。
    """
    log(str(interaction.guild_id), "command", f"/{HELLOMEG_COMMAND_NAME}")

    rand_num = random.random()
    message = { "content": HELLOMEG_MESSAGE_MEDIUM }

    if rand_num < 0.03:
        message = { "content": HEELOMEG_MESSAGE_LARGE }
    elif rand_num < 0.09:
        message = { "file": discord.File(HELLOMEG_FEVER_PNG_PATH)}
    elif rand_num < 0.15:
        message = { "file": discord.File(HELLOMEG_LOSER_PNG_PATH)}
    elif rand_num < 0.21:
        message = { "file": discord.File(HELLOMEG_STAND_PNG_PATH)}
    
    await interaction.response.send_message(**message)


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
    print(str(interaction.guild_id), "command", f"/{FEVER_COMMAND_NAME}", f"一行目: {一行目}, 二行目: {二行目}")

    if len_half_width(一行目) > 10 or len_half_width(二行目) > 10:
        await interaction.response.send_message(FEVER_MESSAGE_TOO_LONG_INPUT, ephemeral=True)
        print("/{FEVER_COMMAND_NAME} | warning | too long input")
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


if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("DISCORD_BOT_TOKEN")
    client.run(token)
