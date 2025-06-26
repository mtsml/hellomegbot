import unicodedata
from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
import io


class FeverService:
    """999倍画像生成のビジネスロジック"""
    
    def __init__(
        self,
        template_path: str = "assets/fever/template.png",
        text_color: str = "#764c4d",
        text_size: int = 100,
        font_family: str = "MPLUSRounded1c-Black.ttf",
        max_half_width: int = 10,
    ):
        self.template_path = template_path
        self.text_color = text_color
        self.text_size = text_size
        self.font_family = font_family
        self.max_half_width = max_half_width
    
    def validate_text(self, line1: str, line2: str) -> Tuple[bool, Optional[str]]:
        """テキストのバリデーション
        
        Args:
            line1: 1行目のテキスト
            line2: 2行目のテキスト
            
        Returns:
            (valid, error_message): 有効性とエラーメッセージのタプル
        """
        if self._len_half_width(line1) > self.max_half_width:
            return False, f"1行目が長すぎます（全角{self.max_half_width // 2}文字以内）"
        if self._len_half_width(line2) > self.max_half_width:
            return False, f"2行目が長すぎます（全角{self.max_half_width // 2}文字以内）"
        return True, None
    
    def generate_image(self, line1: str, line2: str) -> bytes:
        """999倍画像を生成
        
        Args:
            line1: 1行目のテキスト
            line2: 2行目のテキスト
            
        Returns:
            生成された画像のバイナリデータ
        """
        text = f"{line1}\n{line2}"
        img = Image.open(self.template_path)
        self._draw_text(text, img, (80, 280))
        
        # バイナリデータに変換
        arr = io.BytesIO()
        img.save(arr, format="PNG")
        arr.seek(0)
        return arr.getvalue()
    
    def _len_half_width(self, text: str) -> int:
        """半角で何文字かを数える"""
        return sum([(1, 2)[unicodedata.east_asian_width(char) in "FWA"] for char in text])
    
    def _draw_text(self, text: str, target_img: Image.Image, xy: Tuple[int, int]):
        """target_img に text を画像として埋め込む"""
        text_img = Image.new("RGBA", (600, 330), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_img)
        font = ImageFont.truetype(self.font_family, self.text_size)
        text_draw.text((20, 15), text, self.text_color, font=font)
        text_img = text_img.rotate(14)
        target_img.paste(text_img, xy, text_img)