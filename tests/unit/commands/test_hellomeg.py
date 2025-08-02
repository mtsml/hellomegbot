import pytest
from unittest.mock import Mock, AsyncMock
from hellomegbot.commands.hellomeg import Hellomeg
from hellomegbot.commands.hellomeg import (
    HELLOMEG_COMMAND_NAME,
    HELLOMEG_COMMAND_DESC
)


class TestHellomeg:
    """Hellomegコマンドのユニットテスト"""
    
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
        hellomeg = Hellomeg()
        assert hellomeg.command_name == HELLOMEG_COMMAND_NAME
        assert hellomeg.command_description == HELLOMEG_COMMAND_DESC
        assert hellomeg.service is not None
    
    def test_command_initialization_with_mock_service(self, mock_service):
        """モックサービスでの初期化テスト"""
        hellomeg = Hellomeg(service=mock_service)
        assert hellomeg.command_name == HELLOMEG_COMMAND_NAME
        assert hellomeg.command_description == HELLOMEG_COMMAND_DESC
        assert hellomeg.service == mock_service
    
    def test_setup_calls_service_initialize(self, mock_service):
        """setupがサービスのinitializeを呼ぶことを確認"""
        hellomeg = Hellomeg(service=mock_service)
        hellomeg.setup()
        mock_service.initialize.assert_called_once()
    
    def test_register_command_creates_command(self, mock_service):
        """register_commandがコマンドを作成することを確認"""
        hellomeg = Hellomeg(service=mock_service)
        mock_tree = Mock()
        
        hellomeg.register_command(mock_tree)
        
        # tree.commandが正しいパラメータで呼ばれたことを確認
        mock_tree.command.assert_called_once_with(
            name=HELLOMEG_COMMAND_NAME,
            description=HELLOMEG_COMMAND_DESC
        )
    
