import os
import random
from dotenv import load_dotenv
import discord
from discord import app_commands


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


client.run(TOKEN)
