import pytest
from unittest.mock import patch, Mock
from hellomegbot.services import KeibaResultService, KeibaResult


class TestKeibaResultService:
    """KeibaResultServiceのユニットテスト"""
    
    @pytest.fixture
    def service(self):
        """KeibaResultServiceのフィクスチャ"""
        return KeibaResultService()
    
    def test_initialization_with_defaults(self):
        """デフォルト値での初期化テスト"""
        service = KeibaResultService()
        assert service.win_image_dir == "assets/keibaresult/win/"
        assert service.lose_image_dir == "assets/keibaresult/lose/"
        assert service.draw_image_dir == "assets/keibaresult/draw/"
    
    def test_initialization_with_custom_values(self):
        """カスタム値での初期化テスト"""
        service = KeibaResultService(
            win_image_dir="custom/win/",
            lose_image_dir="custom/lose/",
            draw_image_dir="custom/draw/"
        )
        assert service.win_image_dir == "custom/win/"
        assert service.lose_image_dir == "custom/lose/"
        assert service.draw_image_dir == "custom/draw/"
    
    def test_validate_amount_win_valid(self, service):
        """勝利時の有効な金額バリデーション"""
        valid, error = service.validate_amount(KeibaResult.WIN.value, 1000)
        assert valid is True
        assert error is None
    
    def test_validate_amount_win_invalid(self, service):
        """勝利時の無効な金額バリデーション"""
        valid, error = service.validate_amount(KeibaResult.WIN.value, 0)
        assert valid is False
        assert error == "amount に 0 より大き値を入れろ"
    
    def test_validate_amount_lose_valid(self, service):
        """敗北時の有効な金額バリデーション"""
        valid, error = service.validate_amount(KeibaResult.LOSE.value, 5000)
        assert valid is True
        assert error is None
    
    def test_validate_amount_lose_invalid(self, service):
        """敗北時の無効な金額バリデーション"""
        valid, error = service.validate_amount(KeibaResult.LOSE.value, 0)
        assert valid is False
        assert error == "amount に 0 より大き値を入れろ"
    
    def test_validate_amount_draw_valid(self, service):
        """引き分け時の有効な金額バリデーション"""
        valid, error = service.validate_amount(KeibaResult.DRAW.value, 0)
        assert valid is True
        assert error is None
    
    def test_validate_amount_draw_invalid(self, service):
        """引き分け時の無効な金額バリデーション"""
        valid, error = service.validate_amount(KeibaResult.DRAW.value, 100)
        assert valid is False
        assert error == "amount に 0 を入れろ"
    
    @patch("hellomegbot.services.keibaresult_service.glob.glob")
    @patch("hellomegbot.services.keibaresult_service.random.choice")
    def test_get_response_win(self, mock_choice, mock_glob, service):
        """勝利時のレスポンス生成テスト"""
        mock_glob.return_value = ["win1.png", "win2.png"]
        mock_choice.return_value = "win1.png"
        
        response = service.get_response(KeibaResult.WIN.value, 10000)
        
        assert response["content"] == "ハロめぐー！ (+10,000)"
        assert response["image_path"] == "win1.png"
        mock_glob.assert_called_once_with("assets/keibaresult/win/*.png")
    
    @patch("hellomegbot.services.keibaresult_service.glob.glob")
    @patch("hellomegbot.services.keibaresult_service.random.choice")
    def test_get_response_lose(self, mock_choice, mock_glob, service):
        """敗北時のレスポンス生成テスト"""
        mock_glob.return_value = ["lose1.png", "lose2.png"]
        mock_choice.return_value = "lose2.png"
        
        response = service.get_response(KeibaResult.LOSE.value, 5000)
        
        assert response["content"] == "バイめぐ〜 (-5,000)"
        assert response["image_path"] == "lose2.png"
        mock_glob.assert_called_once_with("assets/keibaresult/lose/*.png")
    
    def test_get_response_draw(self, service):
        """引き分け時のレスポンス生成テスト"""
        response = service.get_response(KeibaResult.DRAW.value, 0)
        
        assert response["content"] == "めぐ (±0)"
        assert response["image_path"] is None
    
    @patch("hellomegbot.services.keibaresult_service.glob.glob")
    def test_get_random_image_no_files(self, mock_glob, service):
        """画像ファイルが存在しない場合のテスト"""
        mock_glob.return_value = []
        
        result = service._get_random_image("assets/test/")
        
        assert result is None
    
    def test_get_available_results(self, service):
        """利用可能な結果のリスト取得テスト"""
        results = service.get_available_results()
        
        assert len(results) == 3
        assert KeibaResult.WIN.value in results
        assert KeibaResult.LOSE.value in results
        assert KeibaResult.DRAW.value in results