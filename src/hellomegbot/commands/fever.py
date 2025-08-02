import discord
import io
from ..services import FeverService


FEVER_COMMAND_NAME = "999"
FEVER_COMMAND_DESC = "何かが999倍の画像をつくる"
FEVER_MESSAGE_TOO_LONG_INPUT = "ちょっとちょっと！\nそんな長いセリフ、めぐちゃん覚えられえないよ！\n（それぞれ全角5文字以内で入力してください）"
FEVER_TEXT_SEND_FILENAME = "fever.png"


class Fever:
    """999倍画像生成のDiscordコマンドインターフェース"""
    
    def __init__(self, service: FeverService = None):
        self.service = service or FeverService()
        self.command_name = FEVER_COMMAND_NAME
        self.command_description = FEVER_COMMAND_DESC
    
    def _log(self, *args):
        """ログ出力"""
        print(" | ".join(args))
    
    def register_command(self, tree):
        """コマンドをコマンドツリーに登録する"""
        @tree.command(name=self.command_name, description=self.command_description)
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
            self._log(str(interaction.guild_id), "command", f"/{self.command_name}", f"一行目: {一行目}, 二行目: {二行目}")
            
            # バリデーション
            valid, error_msg = self.service.validate_text(一行目, 二行目)
            if not valid:
                await interaction.response.send_message(FEVER_MESSAGE_TOO_LONG_INPUT, ephemeral=True)
                return
            
            # 画像生成
            image_data = self.service.generate_image(一行目, 二行目)
            
            # Discordファイルとして送信
            file = discord.File(io.BytesIO(image_data), filename=FEVER_TEXT_SEND_FILENAME)
            await interaction.response.send_message(file=file)