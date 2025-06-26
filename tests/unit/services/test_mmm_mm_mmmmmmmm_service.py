import pytest
from hellomegbot.services import MmmMmMmmmmmmmService
from hellomegbot.services.mmm_mm_mmmmmmmm_service import (
    MMM_MM_MMMMMMMM_MESSAGE_MEDIUM,
    MMM_MM_MMMMMMMM_MESSAGE_LARGE,
    MMM_MM_MMMMMMMM_JSON_URL
)


class TestMmmMmMmmmmmmmService:
    """MmmMmMmmmmmmmServiceのユニットテスト"""
    
    def test_initialization_with_defaults(self):
        """デフォルト値での初期化テスト"""
        service = MmmMmMmmmmmmmService()
        
        assert service.message_medium == MMM_MM_MMMMMMMM_MESSAGE_MEDIUM
        assert service.message_large == MMM_MM_MMMMMMMM_MESSAGE_LARGE
        assert service.json_url == MMM_MM_MMMMMMMM_JSON_URL
        assert service.fever_minute == 0
        assert service.ur_probability == 0.012345679
        assert service.sr_probability == 0.18
    
    def test_initialization_with_custom_values(self):
        """カスタム値での初期化テスト"""
        service = MmmMmMmmmmmmmService(
            fever_minute=15,
            ur_probability=0.02,
            sr_probability=0.20
        )
        
        assert service.message_medium == MMM_MM_MMMMMMMM_MESSAGE_MEDIUM
        assert service.message_large == MMM_MM_MMMMMMMM_MESSAGE_LARGE
        assert service.json_url == MMM_MM_MMMMMMMM_JSON_URL
        assert service.fever_minute == 15
        assert service.ur_probability == 0.02
        assert service.sr_probability == 0.20
    
    def test_inheritance_from_gacha_service(self):
        """GachaServiceからの継承確認テスト"""
        service = MmmMmMmmmmmmmService()
        
        # GachaServiceのメソッドが使えることを確認
        assert hasattr(service, 'draw')
        assert hasattr(service, 'initialize')
        assert hasattr(service, 'get_image_data')
        assert hasattr(service, '_calculate_rarity')