import discord
import random
import os
import requests
import io
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

def log(*args):
    """ログ出力"""
    print(" | ".join(args))

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
HELLOMEG_PNG_DIR = "assets/hellomeg/"
HELLOMEG_PNG_MESSAGE = "イラスト："
TWITTER_PROFILE_URL = "https://twitter.com/"
HELLOMEG_JSON_URL = "https://hellomeg-assets.pages.dev/public/hellomegbot/hellomeg.json"

# グローバル変数
hellomeg_images = []  # {filepath, twitter_id} のリスト
hellomeg_fever_minute = 0
hellomeg_ur_probability = 0.03
hellomeg_sr_probability = 0.18
image_data = {}  # メモリ上に保存された画像のバイナリデータを保持する辞書

def load_images_from_json():
    """JSONファイルから画像情報を読み込む"""
    global hellomeg_images
    
    try:
        # JSONファイルをダウンロード
        response = requests.get(HELLOMEG_JSON_URL)
        response.raise_for_status()
        
        # JSONをパース
        hellomeg_images = response.json()
        log(f"Loaded {len(hellomeg_images)} images from JSON")
        return True
    except Exception as e:
        log("Error loading images from JSON:", str(e))
        return False

def download_image(image):
    """1つの画像をダウンロードする関数"""
    filepath = image["filepath"]
    twitter_id = image["twitter_id"]
    
    try:
        # 画像URLを構築
        image_url = f"https://hellomeg-assets.pages.dev/{filepath}"
        
        # 画像をダウンロード
        response = requests.get(image_url)
        response.raise_for_status()
        
        # キーを生成
        key = f"{filepath}_{twitter_id}"
        
        log(f"Loaded image into memory: {filepath}")
        return key, response.content
    except Exception as e:
        log(f"Error loading image {filepath}:", str(e))
        return None

def load_all_images():
    """すべての画像を並列にダウンロードしてメモリに保存する"""
    global image_data
    
    # スレッドプールを作成
    with ThreadPoolExecutor(max_workers=10) as executor:
        # 並列でダウンロードを実行
        future_to_image = {executor.submit(download_image, image): image for image in hellomeg_images}
        
        # 結果を収集
        for future in concurrent.futures.as_completed(future_to_image):
            result = future.result()
            if result:
                key, content = result
                image_data[key] = content

def setup_hellomeg():
    """hellomegコマンドの初期化を行う"""
    # JSONファイルから画像情報を読み込む
    if load_images_from_json():
        # すべての画像をメモリにロード
        load_all_images()

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
            if hellomeg_images:
                image = random.choice(hellomeg_images)
                filepath = image["filepath"]
                twitter_id = image["twitter_id"]
                twitter_profile_url = TWITTER_PROFILE_URL + twitter_id
                
                # キーを生成
                key = f"{filepath}_{twitter_id}"
                
                if key in image_data:
                    # メモリ上の画像データを使用
                    img_binary = image_data[key]
                    
                    # バイナリデータからファイルライクオブジェクトを作成
                    img_file = io.BytesIO(img_binary)
                    img_file.seek(0)
                    
                    # ファイル名を取得（パスの最後の部分）
                    filename = os.path.basename(filepath)
                    
                    message = {
                        # <> で URL を囲むことで Discord で OGP が表示されなくなる
                        "content": f"{HELLOMEG_PNG_MESSAGE}[@{twitter_id}](<{twitter_profile_url}>)",
                        "file": discord.File(fp=img_file, filename=filename)
                    }
                else:
                    # 画像データがない場合はテキストで返す
                    log(f"Image data not found for {key}")
                    message = { "content": HELLOMEG_MESSAGE_MEDIUM }
            else:
                # 画像が読み込めなかった場合はテキストで返す
                message = { "content": HELLOMEG_MESSAGE_MEDIUM }
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
