import discord
from ..services.keibaresult_service import KeibaResultService, KeibaResult


KEIBA_RESULT_COMMAND_NAME = "keibaresult"
KEIBA_RESULT_COMMAND_DESC = "競馬の結果を報告する"


class Keibaresult:
    """競馬結果のDiscordコマンドインターフェース"""
    
    def __init__(self, service: KeibaResultService = None):
        self.service = service or KeibaResultService()
        self.command_name = KEIBA_RESULT_COMMAND_NAME
        self.command_description = KEIBA_RESULT_COMMAND_DESC
    
    def _log(self, *args):
        """ログ出力"""
        print(" | ".join(args))
    
    def register_command(self, tree):
        """コマンドをコマンドツリーに登録する"""
        @tree.command(name=self.command_name, description=self.command_description)
        @discord.app_commands.choices(
            result=[
                discord.app_commands.Choice(name=KeibaResult.WIN.value, value=KeibaResult.WIN.value),
                discord.app_commands.Choice(name=KeibaResult.LOSE.value, value=KeibaResult.LOSE.value),
                discord.app_commands.Choice(name=KeibaResult.DRAW.value, value=KeibaResult.DRAW.value)
            ]
        )
        @discord.app_commands.describe(
            result="今日の競馬の結果は？",
            amount="いくら？"
        )
        async def keibaresult(interaction: discord.Interaction, result: str, amount: discord.app_commands.Range[int, 0, None]):
            """競馬の結果に対して返答するスラッシュコマンド

            - 収支がプラスの場合は「ハロめぐー！」と勝利イラストを返答する
            - 収支がマイナスの場合は「バイめぐ〜」と敗北イラストを返答する
            - 収支がプラマイゼロの場合は「めぐ」とドローイラストを返答する
            """
            self._log(str(interaction.guild_id), "command", f"/{self.command_name}", f"result: {result}, amount: {amount}")
            
            # バリデーション
            valid, error_msg = self.service.validate_amount(result, amount)
            if not valid:
                await interaction.response.send_message(error_msg, ephemeral=True)
                return
            
            # レスポンス生成
            response = self.service.get_response(result, amount)
            
            # Discord用メッセージ構築
            message = {"content": response["content"]}
            if response["image_path"]:
                message["file"] = discord.File(response["image_path"])
            
            await interaction.response.send_message(**message)