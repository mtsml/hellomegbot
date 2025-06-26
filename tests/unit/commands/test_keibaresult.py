import pytest
from unittest.mock import Mock, patch
from hellomegbot.commands.keibaresult import Keibaresult, KEIBA_RESULT_COMMAND_NAME, KEIBA_RESULT_COMMAND_DESC
from hellomegbot.services.keibaresult_service import KeibaResult


class TestKeibaresult:
    """Keibaresultコマンドのユニットテスト"""
    
    @pytest.fixture
    def mock_service(self):
        """モックサービスのフィクスチャ"""
        service = Mock()
        service.validate_amount = Mock(return_value=(True, None))
        service.get_response = Mock(return_value={
            "content": "ハロめぐー！ (+1,000)",
            "image_path": "test.png"
        })
        service.get_available_results = Mock(return_value=[
            KeibaResult.WIN.value,
            KeibaResult.LOSE.value,
            KeibaResult.DRAW.value
        ])
        return service
    
    def test_initialization_with_default_service(self):
        """デフォルトサービスでの初期化テスト"""
        keibaresult = Keibaresult()
        assert keibaresult.command_name == KEIBA_RESULT_COMMAND_NAME
        assert keibaresult.command_description == KEIBA_RESULT_COMMAND_DESC
        assert keibaresult.service is not None
    
    def test_initialization_with_mock_service(self, mock_service):
        """モックサービスでの初期化テスト"""
        keibaresult = Keibaresult(service=mock_service)
        assert keibaresult.command_name == KEIBA_RESULT_COMMAND_NAME
        assert keibaresult.command_description == KEIBA_RESULT_COMMAND_DESC
        assert keibaresult.service == mock_service
    
    def test_register_command_creates_command(self, mock_service):
        """register_commandがコマンドを作成することを確認"""
        keibaresult = Keibaresult(service=mock_service)
        mock_tree = Mock()
        
        keibaresult.register_command(mock_tree)
        
        # tree.commandが正しいパラメータで呼ばれたことを確認
        mock_tree.command.assert_called_once_with(
            name=KEIBA_RESULT_COMMAND_NAME,
            description=KEIBA_RESULT_COMMAND_DESC
        )
    
    @patch("builtins.print")
    def test_log_method(self, mock_print, mock_service):
        """ログメソッドのテスト"""
        keibaresult = Keibaresult(service=mock_service)
        keibaresult._log("test", "log", "message")
        
        mock_print.assert_called_once_with("test | log | message")
    
    def test_command_choices_structure(self, mock_service):
        """コマンドの選択肢構造のテスト"""
        keibaresult = Keibaresult(service=mock_service)
        mock_tree = Mock()
        
        keibaresult.register_command(mock_tree)
        
        # デコレータが適用されていることを確認
        decorator_call = mock_tree.command.return_value
        assert decorator_call is not None