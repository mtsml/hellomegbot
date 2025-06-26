import pytest
from hellomegbot.services import HellomegService
from hellomegbot.services.hellomeg_service import (
    HELLOMEG_MESSAGE_MEDIUM,
    HELLOMEG_MESSAGE_LARGE,
    HELLOMEG_JSON_URL
)


class TestHellomegService:
    """HellomegServiceのユニットテスト"""
    
    def test_initialization_with_defaults(self):
        """デフォルト値での初期化テスト"""
        service = HellomegService()
        
        assert service.message_medium == HELLOMEG_MESSAGE_MEDIUM
        assert service.message_large == HELLOMEG_MESSAGE_LARGE
        assert service.json_url == HELLOMEG_JSON_URL
        assert service.fever_minute == 0
        assert service.ur_probability == 0.03
        assert service.sr_probability == 0.18
    
    def test_initialization_with_custom_values(self):
        """カスタム値での初期化テスト"""
        service = HellomegService(
            fever_minute=59,
            ur_probability=0.05,
            sr_probability=0.25
        )
        
        assert service.message_medium == HELLOMEG_MESSAGE_MEDIUM
        assert service.message_large == HELLOMEG_MESSAGE_LARGE
        assert service.json_url == HELLOMEG_JSON_URL
        assert service.fever_minute == 59
        assert service.ur_probability == 0.05
        assert service.sr_probability == 0.25
    
    def test_inheritance_from_gacha_service(self):
        """GachaServiceからの継承確認テスト"""
        service = HellomegService()
        
        # GachaServiceのメソッドが使えることを確認
        assert hasattr(service, 'draw')
        assert hasattr(service, 'initialize')
        assert hasattr(service, 'get_image_data')
        assert hasattr(service, '_calculate_rarity')