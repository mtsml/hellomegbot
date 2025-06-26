import pytest
from hellomegbot.services import HelloRuriService
from hellomegbot.services.helloruri_service import (
    HELLORURI_MESSAGE_MEDIUM,
    HELLORURI_MESSAGE_LARGE,
    HELLORURI_JSON_URL
)


class TestHelloRuriService:
    """HelloRuriServiceのユニットテスト"""
    
    def test_initialization_with_defaults(self):
        """デフォルト値での初期化テスト"""
        service = HelloRuriService()
        
        assert service.message_medium == HELLORURI_MESSAGE_MEDIUM
        assert service.message_large == HELLORURI_MESSAGE_LARGE
        assert service.json_url == HELLORURI_JSON_URL
        assert service.fever_minute == 30
        assert service.ur_probability == 0.03
        assert service.sr_probability == 0.18
    
    def test_initialization_with_custom_values(self):
        """カスタム値での初期化テスト"""
        service = HelloRuriService(
            fever_minute=45,
            ur_probability=0.05,
            sr_probability=0.25
        )
        
        assert service.message_medium == HELLORURI_MESSAGE_MEDIUM
        assert service.message_large == HELLORURI_MESSAGE_LARGE
        assert service.json_url == HELLORURI_JSON_URL
        assert service.fever_minute == 45
        assert service.ur_probability == 0.05
        assert service.sr_probability == 0.25
    
    def test_inheritance_from_gacha_service(self):
        """GachaServiceからの継承確認テスト"""
        service = HelloRuriService()
        
        # GachaServiceのメソッドが使えることを確認
        assert hasattr(service, 'draw')
        assert hasattr(service, 'initialize')
        assert hasattr(service, 'get_image_data')
        assert hasattr(service, '_calculate_rarity')