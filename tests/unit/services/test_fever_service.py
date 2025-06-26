import pytest
from unittest.mock import Mock, patch, mock_open
from io import BytesIO
from PIL import Image
from hellomegbot.services import FeverService


class TestFeverService:
    """FeverServiceのユニットテスト"""
    
    @pytest.fixture
    def service(self):
        """FeverServiceのフィクスチャ"""
        return FeverService()
    
    def test_initialization_with_defaults(self):
        """デフォルト値での初期化テスト"""
        service = FeverService()
        assert service.template_path == "assets/fever/template.png"
        assert service.text_color == "#764c4d"
        assert service.text_size == 100
        assert service.font_family == "MPLUSRounded1c-Black.ttf"
        assert service.max_half_width == 10
    
    def test_initialization_with_custom_values(self):
        """カスタム値での初期化テスト"""
        service = FeverService(
            template_path="custom/path.png",
            text_color="#000000",
            text_size=150,
            font_family="custom-font.ttf",
            max_half_width=20
        )
        assert service.template_path == "custom/path.png"
        assert service.text_color == "#000000"
        assert service.text_size == 150
        assert service.font_family == "custom-font.ttf"
        assert service.max_half_width == 20
    
    def test_validate_text_valid(self, service):
        """有効なテキストのバリデーションテスト"""
        # 全角5文字以内
        valid, error = service.validate_text("あいうえお", "かきくけこ")
        assert valid is True
        assert error is None
        
        # 半角10文字以内
        valid, error = service.validate_text("1234567890", "abcdefghij")
        assert valid is True
        assert error is None
        
        # 空文字
        valid, error = service.validate_text("", "")
        assert valid is True
        assert error is None
    
    def test_validate_text_invalid_line1(self, service):
        """1行目が長すぎる場合のバリデーションテスト"""
        valid, error = service.validate_text("あいうえおか", "かきくけこ")
        assert valid is False
        assert "1行目が長すぎます" in error
    
    def test_validate_text_invalid_line2(self, service):
        """2行目が長すぎる場合のバリデーションテスト"""
        valid, error = service.validate_text("あいうえお", "かきくけこさ")
        assert valid is False
        assert "2行目が長すぎます" in error
    
    def test_len_half_width(self, service):
        """半角文字数カウントのテスト"""
        # 全角のみ
        assert service._len_half_width("あいうえお") == 10
        
        # 半角のみ
        assert service._len_half_width("abcde") == 5
        
        # 混在
        assert service._len_half_width("あいabc") == 7
        
        # 空文字
        assert service._len_half_width("") == 0
    
    @patch("hellomegbot.services.fever_service.Image")
    @patch("hellomegbot.services.fever_service.ImageDraw")
    @patch("hellomegbot.services.fever_service.ImageFont.truetype")
    def test_generate_image(self, mock_truetype, mock_draw_module, mock_image_module, service):
        """画像生成のテスト"""
        # モックの設定
        mock_img = Mock(spec=Image.Image)
        mock_image_module.open.return_value = mock_img
        
        # _draw_textメソッドをモック化
        with patch.object(service, '_draw_text') as mock_draw_text:
            # 画像生成
            result = service.generate_image("テスト1", "テスト2")
            
            # Image.openが呼ばれたことを確認
            mock_image_module.open.assert_called_once_with("assets/fever/template.png")
            
            # _draw_textが呼ばれたことを確認
            mock_draw_text.assert_called_once_with("テスト1\nテスト2", mock_img, (80, 280))
            
            # バイナリデータが返されることを確認
            assert isinstance(result, bytes)
    
    @patch("hellomegbot.services.fever_service.Image.new")
    @patch("hellomegbot.services.fever_service.ImageDraw.Draw")
    @patch("hellomegbot.services.fever_service.ImageFont.truetype")
    def test_draw_text(self, mock_truetype, mock_draw_class, mock_new, service):
        """テキスト描画のテスト"""
        # モックの設定
        mock_text_img = Mock(spec=Image.Image)
        mock_new.return_value = mock_text_img
        mock_draw = Mock()
        mock_draw_class.return_value = mock_draw
        mock_font = Mock()
        mock_truetype.return_value = mock_font
        mock_rotated = Mock()
        mock_text_img.rotate.return_value = mock_rotated
        
        # ターゲット画像のモック
        mock_target_img = Mock(spec=Image.Image)
        
        # テキスト描画
        service._draw_text("テスト\nテキスト", mock_target_img, (80, 280))
        
        # 新しい画像が作成されたことを確認
        mock_new.assert_called_once_with("RGBA", (600, 330), (0, 0, 0, 0))
        
        # テキストが描画されたことを確認
        mock_draw.text.assert_called_once_with(
            (20, 15), 
            "テスト\nテキスト", 
            "#764c4d", 
            font=mock_font
        )
        
        # 画像が回転されたことを確認
        mock_text_img.rotate.assert_called_once_with(14)
        
        # 画像が貼り付けられたことを確認
        mock_target_img.paste.assert_called_once_with(
            mock_rotated, 
            (80, 280), 
            mock_rotated
        )