import discord
import os
import io
from ..services import MmmMmMmmmmmmmService, GachaRarity


MMM_MM_MMMMMMMM_COMMAND_NAME = "mmm-mm-mmmmmmmm"
MMM_MM_MMMMMMMM_COMMAND_DESC = "萌萌萌・萌萌・萌萌萌萌萌萌萌萌"
PNG_MESSAGE = "イラスト："
TWITTER_PROFILE_URL = "https://twitter.com/"


class MmmMmMmmmmmmm:
    """MmmMmMmmmmmmmのDiscordコマンドインターフェース"""
    
    def __init__(self, service: MmmMmMmmmmmmmService = None):
        self.service = service or MmmMmMmmmmmmmService()
        self.command_name = MMM_MM_MMMMMMMM_COMMAND_NAME
        self.command_description = MMM_MM_MMMMMMMM_COMMAND_DESC
    
    def _log(self, *args):
        """ログ出力"""
        print(" | ".join(args))
    
    def setup(self):
        """コマンドの初期化を行う"""
        self.service.initialize()
    
    def register_command(self, tree):
        """コマンドをコマンドツリーに登録する"""
        @tree.command(name=self.command_name, description=self.command_description)
        async def command_handler(interaction: discord.Interaction):
            self._log(str(interaction.guild_id), "command", f"/{self.command_name}")
            
            # ガチャを実行
            result = self.service.draw(minute=interaction.created_at.minute)
            
            # Discord用のメッセージを作成
            if result.rarity == GachaRarity.UR:
                message = {"content": result.message}
            elif result.rarity == GachaRarity.SR and result.image:
                # 画像データを取得
                image_data = self.service.get_image_data(result.image)
                if image_data:
                    # バイナリデータからファイルライクオブジェクトを作成
                    img_file = io.BytesIO(image_data)
                    img_file.seek(0)
                    
                    # ファイル名を取得
                    filename = os.path.basename(result.image.filepath)
                    
                    # Twitter URLを作成
                    twitter_profile_url = TWITTER_PROFILE_URL + result.image.twitter_id
                    
                    message = {
                        "content": f"{PNG_MESSAGE}[@{result.image.twitter_id}](<{twitter_profile_url}>)",
                        "file": discord.File(fp=img_file, filename=filename)
                    }
                else:
                    # 画像データがない場合はテキストで返す
                    self._log(f"Image data not found for {result.image.filepath}")
                    message = {"content": result.message}
            else:
                message = {"content": result.message}
            
            await interaction.response.send_message(**message)