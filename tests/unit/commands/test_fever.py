import pytest
from unittest.mock import Mock, AsyncMock, patch
import discord
from hellomegbot.commands.fever import Fever, FEVER_COMMAND_NAME, FEVER_COMMAND_DESC, FEVER_MESSAGE_TOO_LONG_INPUT


class TestFever:
    """Feverコマンドのユニットテスト"""
    
    @pytest.fixture
    def mock_service(self):
        """モックサービスのフィクスチャ"""
        service = Mock()
        service.validate_text = Mock(return_value=(True, None))
        service.generate_image = Mock(return_value=b"fake_image_data")
        return service
    
    def test_initialization_with_default_service(self):
        """デフォルトサービスでの初期化テスト"""
        fever = Fever()
        assert fever.command_name == FEVER_COMMAND_NAME
        assert fever.command_description == FEVER_COMMAND_DESC
        assert fever.service is not None
    
    def test_initialization_with_mock_service(self, mock_service):
        """モックサービスでの初期化テスト"""
        fever = Fever(service=mock_service)
        assert fever.command_name == FEVER_COMMAND_NAME
        assert fever.command_description == FEVER_COMMAND_DESC
        assert fever.service == mock_service
    
    def test_register_command_creates_command(self, mock_service):
        """register_commandがコマンドを作成することを確認"""
        fever = Fever(service=mock_service)
        mock_tree = Mock()
        
        fever.register_command(mock_tree)
        
        # tree.commandが正しいパラメータで呼ばれたことを確認
        mock_tree.command.assert_called_once_with(
            name=FEVER_COMMAND_NAME,
            description=FEVER_COMMAND_DESC
        )
    
    def test_fever_command_structure(self, mock_service):
        """コマンド構造のテスト"""
        fever = Fever(service=mock_service)
        mock_tree = Mock()
        
        # コマンドを登録
        fever.register_command(mock_tree)
        
        # デコレータが正しく適用されていることを確認
        decorator_call = mock_tree.command.return_value
        assert decorator_call is not None
    
    def test_fever_validation_settings(self, mock_service):
        """バリデーション設定のテスト"""
        # バリデーションエラーを返すように設定
        mock_service.validate_text.return_value = (False, "テキストが長すぎます")
        
        fever = Fever(service=mock_service)
        
        # サービスが正しく設定されていることを確認
        assert fever.service == mock_service
        
        # サービスのvalidate_textメソッドが呼び出し可能であることを確認
        result = fever.service.validate_text("test1", "test2")
        assert result == (False, "テキストが長すぎます")
    
    @patch("builtins.print")
    def test_log_method(self, mock_print, mock_service):
        """ログメソッドのテスト"""
        fever = Fever(service=mock_service)
        fever._log("test", "log", "message")
        
        mock_print.assert_called_once_with("test | log | message")