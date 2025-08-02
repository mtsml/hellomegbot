import discord
import io
from ..services.meggen_service import MeggenService


MEGGEN_COMMAND_NAME = "meggen"
MEGGEN_COMMAND_DESC = "ハロめぐイラスト作成"


class MeggenModal(discord.ui.Modal, title="テキスト入力"):
    """テキスト入力用のモーダル"""
    
    def __init__(self, service: MeggenService, img_type: str):
        super().__init__()
        self.service = service
        self.img_type = img_type
        self.img_config = service.get_image_config(img_type)
        
        if not self.img_config:
            raise ValueError(f"Unknown image type: {img_type}")
        
        self.text_inputs = []
        for i in range(self.img_config["rows"]):
            text_input = discord.ui.TextInput(
                label=f"{i+1}行目{self.img_config['label']}",
                style=discord.TextStyle.short,
                required=False
            )
            self.text_inputs.append(text_input)
            self.add_item(text_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        # テキスト行を収集（空でないもののみ）
        text_lines = [t.value for t in self.text_inputs if t.value]
        
        # 画像生成
        image_data = self.service.generate_image(self.img_type, text_lines)
        
        # Discordファイルとして送信
        file = discord.File(
            io.BytesIO(image_data), 
            filename=self.img_config["send_filename"]
        )
        await interaction.response.send_message(file=file)


class Meggen:
    """めぐちゃんイラスト生成のDiscordコマンドインターフェース"""
    
    def __init__(self, service: MeggenService = None):
        self.service = service or MeggenService()
        self.command_name = MEGGEN_COMMAND_NAME
        self.command_description = MEGGEN_COMMAND_DESC
    
    def _log(self, *args):
        """ログ出力"""
        print(" | ".join(args))
    
    def register_command(self, tree):
        """コマンドをコマンドツリーに登録する"""
        # 利用可能な画像タイプから選択肢を生成
        image_types = self.service.get_available_image_types()
        choices = [
            discord.app_commands.Choice(name=img["name"], value=img["value"])
            for img in image_types
        ]
        
        @tree.command(name=self.command_name, description=self.command_description)
        @discord.app_commands.choices(img=choices)
        @discord.app_commands.describe(img="ハロめぐを選んでください")
        @discord.app_commands.rename(img="イラスト")
        async def meggen(interaction: discord.Interaction, img: str):
            """任意のテキストを入れたハロめぐのイラストをつくる"""
            self._log(str(interaction.guild_id), "command", f"/{self.command_name}", img)
            
            # モーダルを表示
            modal = MeggenModal(self.service, img)
            await interaction.response.send_modal(modal)