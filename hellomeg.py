import os, io, random, unicodedata
from dotenv import load_dotenv
import discord
from discord import app_commands
from fever import generate_fever_png


load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
HELLO_MEG_SMALL = "ハロめぐー！"
HELLO_MEG_MEDIUM = '''
＿人人人人人人人人＿
＞　ハロめぐー！　＜
￣Y^Y^Y^Y^Y^Y^Y￣
'''
HEELO_MEG_LARGE = '''
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
'''


intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    print("running")
    await tree.sync()


@tree.command(name="hellomeg",description="ハロめぐー！")
async def hellomeg(interaction: discord.Interaction):
    rand_num = random.random()
    message = HELLO_MEG_MEDIUM
    if rand_num < 0.1:
        message = HEELO_MEG_LARGE
    await interaction.response.send_message(message)


@tree.command(name="999",description="何かが999倍の画像をつくる")
async def fever(interaction: discord.Interaction, 一行目: str, 二行目: str):
    if len_half_width(一行目) > 10 or len_half_width(二行目) > 10:
        await interaction.response.send_message("ちょっとちょっと！\nそんな長いセリフ、めぐちゃん覚えられえないよ！\n（それぞれ全角5文字以内で入力してください）", ephemeral=True)
        return
    img = generate_fever_png(f"{一行目}\n{二行目}")
    arr = io.BytesIO()
    img.save(arr, format='PNG')
    arr.seek(0)
    file = discord.File(arr, filename="fever.png")
    await interaction.response.send_message(file=file)


def len_half_width(text):
    return sum([(1, 2)[unicodedata.east_asian_width(char) in 'FWA'] for char in text])


client.run(TOKEN)
