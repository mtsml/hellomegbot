import discord
import random
import os
import requests
import io
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor


PNG_MESSAGE = "イラスト："
TWITTER_PROFILE_URL = "https://twitter.com/"


class GachaBase:
    def __init__(
        self,
        command_name,
        command_description,
        message_medium,
        message_large,
        json_url,
        fever_minute=0,
        ur_probability=0.03,
        sr_probability=0.18
    ):
        self.command_name = command_name
        self.command_description = command_description
        self.message_medium = message_medium
        self.message_large = message_large
        self.json_url = json_url
        self.fever_minute = fever_minute
        self.ur_probability = ur_probability
        self.sr_probability = sr_probability
        self.images = []
        self.image_data = {}

    def _log(self, *args):
        """ログ出力"""
        print(" | ".join(args))

    def _load_images_from_json(self):
        """JSONファイルから画像情報を読み込む"""
        try:
            # JSONファイルをダウンロード
            response = requests.get(self.json_url)
            response.raise_for_status()
            
            # JSONをパース
            self.images = response.json()
            self._log(f"Loaded {len(self.images)} images from JSON")
            return True
        except Exception as e:
            self._log("Error loading images from JSON:", str(e))
            return False

    def _download_image(self, image):
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

            self._log(f"Loaded image into memory: {filepath}")
            return key, response.content
        except Exception as e:
            self._log(f"Error loading image {filepath}:", str(e))
            return None

    def _load_all_images(self):
        """すべての画像を並列にダウンロードしてメモリに保存する"""
        # スレッドプールを作成
        with ThreadPoolExecutor(max_workers=10) as executor:
            # 並列でダウンロードを実行
            future_to_image = {executor.submit(self._download_image, image): image for image in self.images}
            
            # 結果を収集
            for future in concurrent.futures.as_completed(future_to_image):
                result = future.result()
                if result:
                    key, content = result
                    self.image_data[key] = content

    def setup(self):
        """コマンドの初期化を行う"""
        # JSONファイルから画像情報を読み込む
        if self._load_images_from_json():
            # すべての画像をメモリにロード
            self._load_all_images()

    def register_command(self, tree):
        """コマンドをコマンドツリーに登録する"""
        @tree.command(name=self.command_name, description=self.command_description)
        async def helloruri(interaction: discord.Interaction):
            """アスキーアートや画像を返答するスラッシュコマンド
            """
            self._log(str(interaction.guild_id), "command", f"/{self.command_name}")

            rand_num = random.random()
            if interaction.created_at.minute == self.fever_minute:
                # FEVER している時は UR または SR のみ排出する
                rand_num = random.uniform(0, self.ur_probability + self.sr_probability)

            if rand_num < self.ur_probability:
                message = { "content": self.message_large }
            elif rand_num < self.ur_probability + self.sr_probability:
                if self.images:
                    image = random.choice(self.images)
                    filepath = image["filepath"]
                    twitter_id = image["twitter_id"]
                    twitter_profile_url = TWITTER_PROFILE_URL + twitter_id
                    
                    # キーを生成
                    key = f"{filepath}_{twitter_id}"
                    
                    if key in self.image_data:
                        # メモリ上の画像データを使用
                        img_binary = self.image_data[key]
                        
                        # バイナリデータからファイルライクオブジェクトを作成
                        img_file = io.BytesIO(img_binary)
                        img_file.seek(0)
                        
                        # ファイル名を取得（パスの最後の部分）
                        filename = os.path.basename(filepath)
                        
                        message = {
                            # <> で URL を囲むことで Discord で OGP が表示されなくなる
                            "content": f"{PNG_MESSAGE}[@{twitter_id}](<{twitter_profile_url}>)",
                            "file": discord.File(fp=img_file, filename=filename)
                        }
                    else:
                        # 画像データがない場合はテキストで返す
                        self._log(f"Image data not found for {key}")
                        message = { "content": self.message_medium }
                else:
                    # 画像が読み込めなかった場合はテキストで返す
                    message = { "content": self.message_medium }
            else:
                message = { "content": self.message_medium }

            await interaction.response.send_message(**message)
