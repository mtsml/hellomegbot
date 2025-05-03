import discord
import random
import os
import requests
import sqlite3
import tempfile

# HELLOMEG コマンドの定数と設定
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
# 外部データベースのURL
HELLOMEG_PNG_MESSAGE = "イラスト："
TWITTER_PROFILE_URL = "https://twitter.com/"
HELLOMEG_DB_URL = "https://hellomeg-assets.pages.dev/data.sqlite"

# グローバル変数
hellomeg_images = []  # (filepath, twitter_id) のタプルのリスト
hellomeg_fever_minute = 0
hellomeg_ur_probability = 0.03
hellomeg_sr_probability = 0.18

def log(*args):
    """ログ出力"""
    print(" | ".join(args))

def download_database():
    """SQLiteデータベースをダウンロードして一時ファイルに保存する"""
    try:
        temp_dir = tempfile.gettempdir()
        db_path = os.path.join(temp_dir, "hellomeg_assets.sqlite")
        
        response = requests.get(HELLOMEG_DB_URL)
        with open(db_path, 'wb') as f:
            f.write(response.content)
        
        return db_path
    except Exception as e:
        log("Error", f"Failed to download database: {e}")
        return None

def get_images_from_db(db_path):
    """データベースから画像情報を取得する"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT filepath, twitter_id FROM images")
        images = cursor.fetchall()
        conn.close()
        
        return images
    except Exception as e:
        log("Error", f"Failed to read database: {e}")
        return []

def setup_hellomeg():
    """hellomegコマンドの初期化を行う"""
    global hellomeg_images
    
    try:
        db_path = download_database()
        if db_path:
            images = get_images_from_db(db_path)
            hellomeg_images = images
            log("Info", f"Loaded {len(images)} images from database")
        else:
            log("Error", "Failed to download database")
            hellomeg_images = []
    except Exception as e:
        log("Error", f"Error setting up hellomeg from database: {e}")
        hellomeg_images = []

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
            filepath, twitter_id = random.choice(hellomeg_images)
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
