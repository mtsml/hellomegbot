import glob
import os
import random
from typing import Optional, List, Tuple
from enum import Enum


class KeibaResult(Enum):
    """競馬の結果"""
    WIN = "ハロめぐー！"
    LOSE = "バイめぐ〜"
    DRAW = "めぐ"


class KeibaResultService:
    """競馬結果表示のビジネスロジック"""
    
    def __init__(
        self,
        win_image_dir: str = "assets/keibaresult/win/",
        lose_image_dir: str = "assets/keibaresult/lose/",
        draw_image_dir: str = "assets/keibaresult/draw/",
    ):
        self.win_image_dir = win_image_dir
        self.lose_image_dir = lose_image_dir
        self.draw_image_dir = draw_image_dir
        
        self.result_messages = {
            KeibaResult.WIN: "ハロめぐー！",
            KeibaResult.LOSE: "バイめぐ〜",
            KeibaResult.DRAW: "めぐ"
        }
    
    def validate_amount(self, result: str, amount: int) -> Tuple[bool, Optional[str]]:
        """金額のバリデーション
        
        Args:
            result: 競馬の結果
            amount: 金額
            
        Returns:
            (valid, error_message): 有効性とエラーメッセージのタプル
        """
        if result == KeibaResult.WIN.value and amount == 0:
            return False, "amount に 0 より大き値を入れろ"
        if result == KeibaResult.LOSE.value and amount == 0:
            return False, "amount に 0 より大き値を入れろ"
        if result == KeibaResult.DRAW.value and amount != 0:
            return False, "amount に 0 を入れろ"
        return True, None
    
    def get_response(self, result: str, amount: int) -> dict:
        """競馬結果に応じたレスポンスを生成
        
        Args:
            result: 競馬の結果
            amount: 金額
            
        Returns:
            レスポンス情報（content, image_path）
        """
        format_amount = f"{amount:,}"
        
        if result == KeibaResult.WIN.value:
            image_path = self._get_random_image(self.win_image_dir)
            return {
                "content": f"{KeibaResult.WIN.value} (+{format_amount})",
                "image_path": image_path
            }
        elif result == KeibaResult.LOSE.value:
            image_path = self._get_random_image(self.lose_image_dir)
            return {
                "content": f"{KeibaResult.LOSE.value} (-{format_amount})",
                "image_path": image_path
            }
        else:  # DRAW
            return {
                "content": f"{KeibaResult.DRAW.value} (±0)",
                "image_path": None
            }
    
    def _get_random_image(self, directory: str) -> Optional[str]:
        """指定ディレクトリからランダムに画像を選択
        
        Args:
            directory: 画像ディレクトリパス
            
        Returns:
            選択された画像のパス
        """
        filepaths = glob.glob(os.path.join(directory, "*.png"))
        return random.choice(filepaths) if filepaths else None
    
    def get_available_results(self) -> List[str]:
        """利用可能な結果のリストを返す"""
        return [result.value for result in KeibaResult]