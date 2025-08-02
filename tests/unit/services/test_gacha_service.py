import pytest
from unittest.mock import Mock, patch, MagicMock
from hellomegbot.services import GachaService, GachaResult, GachaRarity, GachaImage


class TestGachaService:
    """GachaServiceのユニットテスト"""
    
    def setup_method(self):
        """各テストメソッドの前に実行"""
        self.service = GachaService(
            message_medium="Medium Message",
            message_large="Large Message",
            json_url="https://example.com/images.json",
            fever_minute=30,
            ur_probability=0.1,
            sr_probability=0.3
        )
    
    def test_initialization(self):
        """初期化のテスト"""
        assert self.service.message_medium == "Medium Message"
        assert self.service.message_large == "Large Message"
        assert self.service.json_url == "https://example.com/images.json"
        assert self.service.fever_minute == 30
        assert self.service.ur_probability == 0.1
        assert self.service.sr_probability == 0.3
        assert self.service.images == []
        assert self.service.image_data == {}
    
    @patch('requests.get')
    def test_load_images_from_json_success(self, mock_get):
        """JSON読み込み成功のテスト"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"filepath": "image1.png", "twitter_id": "user1"},
            {"filepath": "image2.png", "twitter_id": "user2"}
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.service._load_images_from_json()
        
        assert result is True
        assert len(self.service.images) == 2
        assert self.service.images[0]["filepath"] == "image1.png"
        mock_get.assert_called_once_with("https://example.com/images.json")
    
    @patch('requests.get')
    def test_load_images_from_json_failure(self, mock_get):
        """JSON読み込み失敗のテスト"""
        mock_get.side_effect = Exception("Network error")
        
        result = self.service._load_images_from_json()
        
        assert result is False
        assert self.service.images == []
    
    @patch('requests.get')
    def test_download_image_success(self, mock_get):
        """画像ダウンロード成功のテスト"""
        mock_response = Mock()
        mock_response.content = b"fake image data"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        image = {"filepath": "test.png", "twitter_id": "testuser"}
        result = self.service._download_image(image)
        
        assert result is not None
        key, content = result
        assert key == "test.png_testuser"
        assert content == b"fake image data"
        mock_get.assert_called_once_with("https://hellomeg-assets.pages.dev/test.png")
    
    @patch('requests.get')
    def test_download_image_failure(self, mock_get):
        """画像ダウンロード失敗のテスト"""
        mock_get.side_effect = Exception("Download failed")
        
        image = {"filepath": "test.png", "twitter_id": "testuser"}
        result = self.service._download_image(image)
        
        assert result is None
    
    def test_calculate_rarity(self):
        """レアリティ計算のテスト"""
        # UR range
        assert self.service._calculate_rarity(0.05) == GachaRarity.UR
        
        # SR range
        assert self.service._calculate_rarity(0.2) == GachaRarity.SR
        
        # NORMAL range
        assert self.service._calculate_rarity(0.5) == GachaRarity.NORMAL
    
    @patch('random.random')
    def test_draw_ur_result(self, mock_random):
        """UR結果の抽選テスト"""
        mock_random.return_value = 0.05  # UR range
        
        result = self.service.draw()
        
        assert isinstance(result, GachaResult)
        assert result.rarity == GachaRarity.UR
        assert result.message == "Large Message"
        assert result.image is None
    
    @patch('random.random')
    @patch('random.choice')
    def test_draw_sr_result_with_images(self, mock_choice, mock_random):
        """SR結果（画像あり）の抽選テスト"""
        mock_random.return_value = 0.2  # SR range
        self.service.images = [
            {"filepath": "test.png", "twitter_id": "testuser"}
        ]
        mock_choice.return_value = self.service.images[0]
        
        result = self.service.draw()
        
        assert isinstance(result, GachaResult)
        assert result.rarity == GachaRarity.SR
        assert result.message == "Medium Message"
        assert result.image is not None
        assert result.image.filepath == "test.png"
        assert result.image.twitter_id == "testuser"
    
    @patch('random.random')
    def test_draw_sr_result_without_images(self, mock_random):
        """SR結果（画像なし）の抽選テスト"""
        mock_random.return_value = 0.2  # SR range
        self.service.images = []  # No images
        
        result = self.service.draw()
        
        assert isinstance(result, GachaResult)
        assert result.rarity == GachaRarity.SR
        assert result.message == "Medium Message"
        assert result.image is None
    
    @patch('random.random')
    def test_draw_normal_result(self, mock_random):
        """NORMAL結果の抽選テスト"""
        mock_random.return_value = 0.5  # NORMAL range
        
        result = self.service.draw()
        
        assert isinstance(result, GachaResult)
        assert result.rarity == GachaRarity.NORMAL
        assert result.message == "Medium Message"
        assert result.image is None
    
    @patch('random.uniform')
    def test_draw_fever_time(self, mock_uniform):
        """フィーバータイム時の抽選テスト"""
        mock_uniform.return_value = 0.2  # SR range
        
        # フィーバータイムの分を指定
        result = self.service.draw(minute=30)
        
        # uniform が 0 から ur_probability + sr_probability の範囲で呼ばれることを確認
        mock_uniform.assert_called_once_with(0, 0.4)
        assert result.rarity in [GachaRarity.UR, GachaRarity.SR]
    
    def test_get_image_data(self):
        """画像データ取得のテスト"""
        # テストデータをセット
        self.service.image_data["test.png_testuser"] = b"fake image data"
        
        image = GachaImage(filepath="test.png", twitter_id="testuser")
        data = self.service.get_image_data(image)
        
        assert data == b"fake image data"
    
    def test_get_image_data_not_found(self):
        """存在しない画像データ取得のテスト"""
        image = GachaImage(filepath="notfound.png", twitter_id="nobody")
        data = self.service.get_image_data(image)
        
        assert data is None
    
    @patch('hellomegbot.services.gacha_service.ThreadPoolExecutor')
    @patch.object(GachaService, '_download_image')
    def test_load_all_images(self, mock_download, mock_executor):
        """全画像の並列ダウンロードのテスト"""
        # モックの設定
        self.service.images = [
            {"filepath": "image1.png", "twitter_id": "user1"},
            {"filepath": "image2.png", "twitter_id": "user2"}
        ]
        
        # ダウンロード結果のモック
        future1 = MagicMock()
        future1.result.return_value = ("image1.png_user1", b"data1")
        future2 = MagicMock()
        future2.result.return_value = ("image2.png_user2", b"data2")
        
        # ThreadPoolExecutorのモック設定
        mock_executor_instance = MagicMock()
        mock_executor_instance.__enter__.return_value = mock_executor_instance
        mock_executor_instance.submit.side_effect = [future1, future2]
        mock_executor.return_value = mock_executor_instance
        
        # as_completedのモック
        with patch('concurrent.futures.as_completed', return_value=[future1, future2]):
            self.service._load_all_images()
        
        # 結果の確認
        assert len(self.service.image_data) == 2
        assert self.service.image_data["image1.png_user1"] == b"data1"
        assert self.service.image_data["image2.png_user2"] == b"data2"