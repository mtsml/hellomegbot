import discord
import random
import glob
import os

# HELLOMEG コマンドの定数
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
   ■   ■   
   ■   ■   
  ■■   ■   
  ■     ■  
  ■     ■  
 ■      ■■ 
 ■       ■ 
           
　■■■■■■■■  
　■       ■ 
　■       ■ 
　■       ■ 
　■       ■ 
　■       ■ 
　■       ■ 
　■■■■■■■■■ 
         
      ■     
  ■   ■     
  ■■■ ■■■   
  ■■  ■ ■■  
 ■ ■ ■   ■  
 ■ ■ ■   ■  
 ■  ■    ■  
 ■ ■■   ■   
 ■■■   ■    
         
      ■    
     ■■    
   ■■      
  ■■  ■ ■  
 ■     ■   
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
HELLOMEG_PNG_DIR = "assets/hellomeg/"
HELLOMEG_PNG_MESSAGE = "イラスト："
TWITTER_PROFILE_URL = "https://twitter.com/"

# グローバル変数
hellomeg_png_filepaths = []
hellomeg_fever_minute = 0
hellomeg_ur_probability = 0.03
hellomeg_sr_probability = 0.18

def log(*args):
    """ログ出力"""
    print(" | ".join(args))

def setup_hellomeg():
    """hellomegコマンドの初期化を行う"""
    global hellomeg_png_filepaths
    hellomeg_png_filepaths = [f for f in glob.glob(os.path.join(HELLOMEG_PNG_DIR, "*", "*.png"))]

def register_command(tree):
    """ハロめぐコマンドをコマンドツリーに登録する"""
    @tree.command(name=HELLOMEG_COMMAND_NAME, description=HELLOMEG_COMMAND_DESC)
    async def hellomeg(interaction: discord.Interaction):
        """多様なハロめぐー！を返答するスラッシュコマンド

        それぞれの確率にもとづきアスキーアートや画像をユーザーに返答する。
        """
        log(str(interaction.guild_id), "command", f"/{HELLOMEG_COMMAND_NAME}")

        rand_num = random.random()
        if interaction.created_at.minute == hellomeg_fever_minute:
            # FEVER している時は UR または SR のみ排出する
            rand_num = random.uniform(0, hellomeg_ur_probability + hellomeg_sr_probability)

        if rand_num < hellomeg_ur_probability:
            message = { "content": HEELOMEG_MESSAGE_LARGE }
        elif rand_num < hellomeg_ur_probability + hellomeg_sr_probability:
            filepath = random.choice(hellomeg_png_filepaths)
            twitter_id = filepath.split("/")[2]
            twiiter_profile_url = TWITTER_PROFILE_URL + twitter_id
            message = {
                # <> で URL を囲むことで Discord で OGP が表示されなくなる
                "content": f"{HELLOMEG_PNG_MESSAGE}[@{twitter_id}](<{twiiter_profile_url}>)",
                "file": discord.File(filepath)
            }
        else:
            message = { "content": HELLOMEG_MESSAGE_MEDIUM }

        await interaction.response.send_message(**message)

def set_config(fever_minute=None, ur_prob=None, sr_prob=None):
    """設定値を更新する"""
    global hellomeg_fever_minute, hellomeg_ur_probability, hellomeg_sr_probability
    
    if fever_minute is not None:
        hellomeg_fever_minute = fever_minute
    if ur_prob is not None:
        hellomeg_ur_probability = ur_prob
    if sr_prob is not None:
        hellomeg_sr_probability = sr_prob
