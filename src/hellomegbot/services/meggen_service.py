from typing import Dict, List, Optional, Any
from PIL import Image, ImageDraw, ImageFont
import io


class MeggenService:
    """めぐちゃんイラスト生成のビジネスロジック"""
    
    # イメージ設定の定義
    IMG_CONFIGS = {
        'fever': {
            'rows': 3,
            'label': "（5文字まで）",
            'img_path': "assets/meggen/fever.png",
            'text_img_size': (600, 500),
            'text_color': "#764c4d",
            'text_font_size': 100,
            'text_font_family': "MPLUSRounded1c-Black.ttf",
            'text_start_xy': (30, 15),
            'text_rotate': 16,
            'text_paste_xy': (80, 300),
            'send_filename': 'fever.png',
        },
        'damon': {
            'rows': 2,
            'label': "（10文字まで）",
            'img_path': "assets/meggen/damon.png",
            'text_img_size': (1050, 300),
            'text_color': "#ceaa9e",
            'text_font_size': 100,
            'text_font_family': "MPLUSRounded1c-Black.ttf",
            'text_start_xy': (20, 0),
            'text_rotate': 0,
            'text_paste_xy': (120, 280),
            'stroke_width': 20,
            'stroke_fill': '#633539',
            'send_filename': 'damon.png',
        },
        'hkc': {
            'rows': 1,
            'label': "（7文字まで）",
            'img_path': "assets/meggen/hkc.png",
            'text_img_size': (500, 300),
            'text_color': "#c1e3da",
            'text_font_size': 60,
            'text_font_family': "MPLUSRounded1c-Black.ttf",
            'text_start_xy': (60, 75),
            'text_rotate': 20,
            'text_paste_xy': (20, 80),
            'stroke_width': 15,
            'stroke_fill': '#9fccbf',
            'send_filename': 'hkc.png',
        },
        'universe': {
            'rows': 2,
            'label': "（5文字まで）",
            'img_path': "assets/meggen/universe.png",
            'text_img_size': (350, 260),
            'text_color': "#000000",
            'text_font_size': 50,
            'text_font_family': "MPLUSRounded1c-Black.ttf",
            'text_start_xy': (50, 15),
            'text_rotate': 340,
            'text_paste_xy': (720, 450),
            'send_filename': 'universe.png',
        },
        'hasunosorashikanainsuyo': {
            'rows': 3,
            'label': "（10文字まで）",
            'img_path': "assets/meggen/hasunosorashikanainsuyo.png",
            'text_img_size': (1050, 400),
            'text_color': "#000000",
            'text_font_size': 100,
            'text_font_family': "MPLUSRounded1c-Black.ttf",
            'text_start_xy': (0, 0),
            'text_rotate': 0,
            'text_paste_xy': (150, 50),
            'send_filename': 'hasunosorashikanainsuyo.png',
        },
        'doya': {
            'rows': 5,
            'label': "（10文字まで）",
            'img_path': "assets/meggen/doya.png",
            'text_img_size': (700, 400),
            'text_color': "#ffffff",
            'text_font_size': 70,
            'text_font_family': "MPLUSRounded1c-Black.ttf",
            'text_start_xy': (0, 0),
            'text_rotate': 0,
            'text_paste_xy': (50, 500),
            'send_filename': 'doya.png',
        }
    }
    
    def __init__(self):
        pass
    
    def get_image_config(self, img_type: str) -> Optional[Dict[str, Any]]:
        """指定された画像タイプの設定を取得"""
        return self.IMG_CONFIGS.get(img_type)
    
    def get_available_image_types(self) -> List[Dict[str, str]]:
        """利用可能な画像タイプのリストを返す"""
        return [
            {"name": "フィーバー", "value": "fever"},
            {"name": "ハロめぐだもん", "value": "damon"},
            {"name": "ハクチュー", "value": "hkc"},
            {"name": "宇宙猫", "value": "universe"},
            {"name": "蓮ノ空しかないんすよ", "value": "hasunosorashikanainsuyo"},
            {"name": "ドヤめぐ", "value": "doya"},
        ]
    
    def generate_image(self, img_type: str, text_lines: List[str]) -> bytes:
        """テキスト入りの画像を生成
        
        Args:
            img_type: 画像タイプ
            text_lines: テキスト行のリスト
            
        Returns:
            生成された画像のバイナリデータ
        """
        img_config = self.get_image_config(img_type)
        if not img_config:
            raise ValueError(f"Unknown image type: {img_type}")
        
        # テキストを改行で結合
        text = "\n".join(text_lines)
        
        # 画像を生成
        img = self._draw_text(text, img_config)
        
        # バイナリデータに変換
        arr = io.BytesIO()
        img.save(arr, format="PNG")
        arr.seek(0)
        return arr.getvalue()
    
    def _draw_text(self, text: str, img_config: Dict[str, Any]) -> Image.Image:
        """画像にテキストを描画する
        
        Args:
            text: 描画するテキスト
            img_config: 画像設定
            
        Returns:
            テキストが描画された画像
        """
        # テキスト画像を作成
        text_img = Image.new("RGBA", img_config["text_img_size"], (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_img)
        font = ImageFont.truetype(img_config["text_font_family"], img_config["text_font_size"])
        
        # テキスト描画パラメータ
        text_param = {
            "xy": img_config["text_start_xy"],
            "text": text,
            "fill": img_config["text_color"],
            "font": font
        }
        
        # ストローク設定がある場合は追加
        if "stroke_width" in img_config and "stroke_fill" in img_config:
            text_param['stroke_width'] = img_config["stroke_width"]
            text_param['stroke_fill'] = img_config["stroke_fill"]
        
        text_draw.text(**text_param)
        
        # 回転
        text_img = text_img.rotate(img_config["text_rotate"])
        
        # ベース画像を開いてテキストを貼り付け
        img = Image.open(img_config["img_path"])
        img.paste(text_img, img_config["text_paste_xy"], text_img)
        
        return img