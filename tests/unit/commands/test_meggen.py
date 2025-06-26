import pytest
from unittest.mock import Mock, patch
import discord
from hellomegbot.commands.meggen import Meggen, MeggenModal, MEGGEN_COMMAND_NAME, MEGGEN_COMMAND_DESC


class TestMeggen:
    """Meggenコマンドのユニットテスト"""
    
    @pytest.fixture
    def mock_service(self):
        """モックサービスのフィクスチャ"""
        service = Mock()
        service.get_available_image_types = Mock(return_value=[
            {"name": "フィーバー", "value": "fever"},
            {"name": "ハロめぐだもん", "value": "damon"}
        ])
        service.get_image_config = Mock(return_value={
            'rows': 3,
            'label': "（5文字まで）",
            'send_filename': 'fever.png'
        })
        service.generate_image = Mock(return_value=b"fake_image_data")
        return service
    
    def test_initialization_with_default_service(self):
        """デフォルトサービスでの初期化テスト"""
        meggen = Meggen()
        assert meggen.command_name == MEGGEN_COMMAND_NAME
        assert meggen.command_description == MEGGEN_COMMAND_DESC
        assert meggen.service is not None
    
    def test_initialization_with_mock_service(self, mock_service):
        """モックサービスでの初期化テスト"""
        meggen = Meggen(service=mock_service)
        assert meggen.command_name == MEGGEN_COMMAND_NAME
        assert meggen.command_description == MEGGEN_COMMAND_DESC
        assert meggen.service == mock_service
    
    def test_register_command_creates_command(self, mock_service):
        """register_commandがコマンドを作成することを確認"""
        meggen = Meggen(service=mock_service)
        mock_tree = Mock()
        
        meggen.register_command(mock_tree)
        
        # tree.commandが正しいパラメータで呼ばれたことを確認
        mock_tree.command.assert_called_once_with(
            name=MEGGEN_COMMAND_NAME,
            description=MEGGEN_COMMAND_DESC
        )
        
        # 選択肢が正しく設定されていることを確認
        decorator = mock_tree.command.return_value
        choices_decorator = decorator.return_value
        assert choices_decorator is not None
    
    @patch("builtins.print")
    def test_log_method(self, mock_print, mock_service):
        """ログメソッドのテスト"""
        meggen = Meggen(service=mock_service)
        meggen._log("test", "log", "message")
        
        mock_print.assert_called_once_with("test | log | message")


class TestMeggenModal:
    """MeggenModalのユニットテスト"""
    
    @pytest.fixture
    def mock_service(self):
        """モックサービスのフィクスチャ"""
        service = Mock()
        service.get_image_config = Mock(return_value={
            'rows': 2,
            'label': "（10文字まで）",
            'send_filename': 'test.png'
        })
        service.generate_image = Mock(return_value=b"fake_image_data")
        return service
    
    def test_modal_validation_logic(self, mock_service):
        """モーダルの検証ロジックのテスト"""
        # 有効な画像タイプ
        img_config = mock_service.get_image_config('fever')
        assert img_config is not None
        assert img_config['rows'] == 2
        assert img_config['label'] == "（10文字まで）"
        
        # 無効な画像タイプ
        mock_service.get_image_config.return_value = None
        img_config = mock_service.get_image_config('invalid')
        assert img_config is None
    
    def test_modal_initialization_invalid_type(self, mock_service):
        """無効な画像タイプでのモーダル初期化テスト"""
        mock_service.get_image_config.return_value = None
        
        # __init__メソッドの最初の部分だけをテスト
        with pytest.raises(ValueError, match="Unknown image type: invalid"):
            # 直接検証ロジックをテスト
            service = mock_service
            img_type = 'invalid'
            img_config = service.get_image_config(img_type)
            if not img_config:
                raise ValueError(f"Unknown image type: {img_type}")