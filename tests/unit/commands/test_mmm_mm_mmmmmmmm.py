import pytest
from unittest.mock import Mock
from hellomegbot.commands.mmm_mm_mmmmmmmm import MmmMmMmmmmmmm
from hellomegbot.commands.mmm_mm_mmmmmmmm import (
    MMM_MM_MMMMMMMM_COMMAND_NAME,
    MMM_MM_MMMMMMMM_COMMAND_DESC
)


class TestMmmMmMmmmmmmmm:
    """MmmMmMmmmmmmコマンドのユニットテスト"""
    
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
        mmm = MmmMmMmmmmmmm()
        assert mmm.command_name == MMM_MM_MMMMMMMM_COMMAND_NAME
        assert mmm.command_description == MMM_MM_MMMMMMMM_COMMAND_DESC
        assert mmm.service is not None
    
    def test_command_initialization_with_mock_service(self, mock_service):
        """モックサービスでの初期化テスト"""
        mmm = MmmMmMmmmmmmm(service=mock_service)
        assert mmm.command_name == MMM_MM_MMMMMMMM_COMMAND_NAME
        assert mmm.command_description == MMM_MM_MMMMMMMM_COMMAND_DESC
        assert mmm.service == mock_service
    
    def test_setup_calls_service_initialize(self, mock_service):
        """setupがサービスのinitializeを呼ぶことを確認"""
        mmm = MmmMmMmmmmmmm(service=mock_service)
        mmm.setup()
        mock_service.initialize.assert_called_once()
    
    def test_register_command_creates_command(self, mock_service):
        """register_commandがコマンドを作成することを確認"""
        mmm = MmmMmMmmmmmmm(service=mock_service)
        mock_tree = Mock()
        
        mmm.register_command(mock_tree)
        
        # tree.commandが正しいパラメータで呼ばれたことを確認
        mock_tree.command.assert_called_once_with(
            name=MMM_MM_MMMMMMMM_COMMAND_NAME,
            description=MMM_MM_MMMMMMMM_COMMAND_DESC
        )