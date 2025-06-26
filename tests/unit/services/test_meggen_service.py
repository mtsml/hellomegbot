import pytest
from unittest.mock import Mock, patch, mock_open
from PIL import Image
from hellomegbot.services import MeggenService


class TestMeggenService:
    """MeggenServiceのユニットテスト"""
    
    @pytest.fixture
    def service(self):
        """MeggenServiceのフィクスチャ"""
        return MeggenService()
    
    def test_initialization(self):
        """初期化テスト"""
        service = MeggenService()
        assert service is not None
        assert hasattr(service, 'IMG_CONFIGS')
    
    def test_get_image_config_valid(self, service):
        """有効な画像タイプの設定取得テスト"""
        config = service.get_image_config('fever')
        assert config is not None
        assert config['rows'] == 3
        assert config['label'] == "（5文字まで）"
        
        config = service.get_image_config('damon')
        assert config is not None
        assert config['rows'] == 2
    
    def test_get_image_config_invalid(self, service):
        """無効な画像タイプの設定取得テスト"""
        config = service.get_image_config('invalid_type')
        assert config is None
    
    def test_get_available_image_types(self, service):
        """利用可能な画像タイプのリスト取得テスト"""
        types = service.get_available_image_types()
        
        assert len(types) == 6
        assert types[0] == {"name": "フィーバー", "value": "fever"}
        assert types[1] == {"name": "ハロめぐだもん", "value": "damon"}
        assert types[2] == {"name": "ハクチュー", "value": "hkc"}
        assert types[3] == {"name": "宇宙猫", "value": "universe"}
        assert types[4] == {"name": "蓮ノ空しかないんすよ", "value": "hasunosorashikanainsuyo"}
        assert types[5] == {"name": "ドヤめぐ", "value": "doya"}
    
    @patch("hellomegbot.services.meggen_service.Image.open")
    @patch("hellomegbot.services.meggen_service.ImageFont.truetype")
    def test_generate_image_valid_type(self, mock_truetype, mock_open, service):
        """有効な画像タイプでの画像生成テスト"""
        # モックの設定
        mock_img = Mock(spec=Image.Image)
        mock_open.return_value = mock_img
        mock_font = Mock()
        mock_truetype.return_value = mock_font
        
        # _draw_textメソッドをモック化
        with patch.object(service, '_draw_text', return_value=mock_img):
            result = service.generate_image('fever', ['テスト1', 'テスト2', 'テスト3'])
            
            # バイナリデータが返されることを確認
            assert isinstance(result, bytes)
    
    def test_generate_image_invalid_type(self, service):
        """無効な画像タイプでの画像生成テスト"""
        with pytest.raises(ValueError, match="Unknown image type: invalid"):
            service.generate_image('invalid', ['テスト'])
    
    @patch("hellomegbot.services.meggen_service.Image.new")
    @patch("hellomegbot.services.meggen_service.ImageDraw.Draw")
    @patch("hellomegbot.services.meggen_service.ImageFont.truetype")
    @patch("hellomegbot.services.meggen_service.Image.open")
    def test_draw_text_without_stroke(self, mock_open, mock_truetype, mock_draw_class, mock_new, service):
        """ストロークなしのテキスト描画テスト"""
        # モックの設定
        mock_text_img = Mock(spec=Image.Image)
        mock_new.return_value = mock_text_img
        mock_draw = Mock()
        mock_draw_class.return_value = mock_draw
        mock_font = Mock()
        mock_truetype.return_value = mock_font
        mock_rotated = Mock()
        mock_text_img.rotate.return_value = mock_rotated
        mock_base_img = Mock(spec=Image.Image)
        mock_open.return_value = mock_base_img
        
        # fever設定（ストロークなし）でテスト
        config = service.IMG_CONFIGS['fever']
        result = service._draw_text("テスト\nテキスト", config)
        
        # 新しい画像が作成されたことを確認
        mock_new.assert_called_once_with("RGBA", (600, 500), (0, 0, 0, 0))
        
        # テキストが描画されたことを確認（ストロークなし）
        mock_draw.text.assert_called_once()
        call_args = mock_draw.text.call_args[1]
        assert call_args['xy'] == (30, 15)
        assert call_args['text'] == "テスト\nテキスト"
        assert call_args['fill'] == "#764c4d"
        assert 'stroke_width' not in call_args
        
        # 画像が回転されたことを確認
        mock_text_img.rotate.assert_called_once_with(16)
    
    @patch("hellomegbot.services.meggen_service.Image.new")
    @patch("hellomegbot.services.meggen_service.ImageDraw.Draw")
    @patch("hellomegbot.services.meggen_service.ImageFont.truetype")
    @patch("hellomegbot.services.meggen_service.Image.open")
    def test_draw_text_with_stroke(self, mock_open, mock_truetype, mock_draw_class, mock_new, service):
        """ストロークありのテキスト描画テスト"""
        # モックの設定
        mock_text_img = Mock(spec=Image.Image)
        mock_new.return_value = mock_text_img
        mock_draw = Mock()
        mock_draw_class.return_value = mock_draw
        mock_font = Mock()
        mock_truetype.return_value = mock_font
        mock_rotated = Mock()
        mock_text_img.rotate.return_value = mock_rotated
        mock_base_img = Mock(spec=Image.Image)
        mock_open.return_value = mock_base_img
        
        # damon設定（ストロークあり）でテスト
        config = service.IMG_CONFIGS['damon']
        result = service._draw_text("テスト", config)
        
        # テキストが描画されたことを確認（ストロークあり）
        mock_draw.text.assert_called_once()
        call_args = mock_draw.text.call_args[1]
        assert call_args['stroke_width'] == 20
        assert call_args['stroke_fill'] == '#633539'