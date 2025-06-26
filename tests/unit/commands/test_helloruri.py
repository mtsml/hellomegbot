import pytest
from unittest.mock import Mock, AsyncMock
from hellomegbot.commands.helloruri import HelloRuri
from hellomegbot.commands.helloruri import (
    HELLORURI_COMMAND_NAME,
    HELLORURI_COMMAND_DESC
)
from hellomegbot.services import GachaResult, GachaRarity


class TestHelloRuri:
    """HelloRuriコマンドのユニットテスト"""
    
    @pytest.fixture
    def mock_service(self):
        """モックサービスのフィクスチャ"""
        service = Mock()
        service.initialize = Mock()
        service.draw = Mock()
        service.get_image_data = Mock()
        return service
    
    def test_command_initialization_with_default_service(self):
        """デフォルトサービスでの初期化テスト"""
        helloruri = HelloRuri()
        assert helloruri.command_name == HELLORURI_COMMAND_NAME
        assert helloruri.command_description == HELLORURI_COMMAND_DESC
        assert helloruri.service is not None
    
    def test_command_initialization_with_mock_service(self, mock_service):
        """モックサービスでの初期化テスト"""
        helloruri = HelloRuri(service=mock_service)
        assert helloruri.command_name == HELLORURI_COMMAND_NAME
        assert helloruri.command_description == HELLORURI_COMMAND_DESC
        assert helloruri.service == mock_service
    
    def test_setup_calls_service_initialize(self, mock_service):
        """setupがサービスのinitializeを呼ぶことを確認"""
        helloruri = HelloRuri(service=mock_service)
        helloruri.setup()
        mock_service.initialize.assert_called_once()
    
    def test_register_command_creates_command(self, mock_service):
        """register_commandがコマンドを作成することを確認"""
        helloruri = HelloRuri(service=mock_service)
        mock_tree = Mock()
        
        helloruri.register_command(mock_tree)
        
        # tree.commandが正しいパラメータで呼ばれたことを確認
        mock_tree.command.assert_called_once_with(
            name=HELLORURI_COMMAND_NAME,
            description=HELLORURI_COMMAND_DESC
        )
    
