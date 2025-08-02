import random
import requests
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class GachaRarity(Enum):
    UR = "ur"
    SR = "sr"
    NORMAL = "normal"


@dataclass
class GachaImage:
    filepath: str
    twitter_id: str


@dataclass
class GachaResult:
    rarity: GachaRarity
    message: str
    image: Optional[GachaImage] = None


class GachaService:
    """ガチャのビジネスロジックを管理するサービス"""
    
    def __init__(
        self,
        message_medium: str,
        message_large: str,
        json_url: str,
        fever_minute: int = 0,
        ur_probability: float = 0.03,
        sr_probability: float = 0.18,
    ):
        self.message_medium = message_medium
        self.message_large = message_large
        self.json_url = json_url
        self.fever_minute = fever_minute
        self.ur_probability = ur_probability
        self.sr_probability = sr_probability
        self.images: List[Dict] = []
        self.image_data: Dict[str, bytes] = {}
    
    def _log(self, *args):
        """ログ出力"""
        print(" | ".join(args))
    
    def _load_images_from_json(self) -> bool:
        """JSONファイルから画像情報を読み込む"""
        try:
            response = requests.get(self.json_url)
            response.raise_for_status()
            self.images = response.json()
            self._log(f"Loaded {len(self.images)} images from JSON")
            return True
        except Exception as e:
            self._log("Error loading images from JSON:", str(e))
            return False
    
    def _download_image(self, image: Dict) -> Optional[Tuple[str, bytes]]:
        """1つの画像をダウンロードする"""
        filepath = image["filepath"]
        twitter_id = image["twitter_id"]
        
        try:
            image_url = f"https://hellomeg-assets.pages.dev/{filepath}"
            response = requests.get(image_url)
            response.raise_for_status()
            
            key = f"{filepath}_{twitter_id}"
            self._log(f"Loaded image into memory: {filepath}")
            return key, response.content
        except Exception as e:
            self._log(f"Error loading image {filepath}:", str(e))
            return None
    
    def _load_all_images(self):
        """すべての画像を並列にダウンロードしてメモリに保存する"""
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_image = {
                executor.submit(self._download_image, image): image 
                for image in self.images
            }
            
            for future in concurrent.futures.as_completed(future_to_image):
                result = future.result()
                if result:
                    key, content = result
                    self.image_data[key] = content
    
    def initialize(self):
        """サービスの初期化を行う"""
        if self._load_images_from_json():
            self._load_all_images()
    
    def _calculate_rarity(self, rand_num: float) -> GachaRarity:
        """確率値からレアリティを計算"""
        if rand_num < self.ur_probability:
            return GachaRarity.UR
        elif rand_num < self.ur_probability + self.sr_probability:
            return GachaRarity.SR
        else:
            return GachaRarity.NORMAL
    
    def draw(self, minute: Optional[int] = None) -> GachaResult:
        """ガチャを引く
        
        Args:
            minute: 現在の分（フィーバー判定用）
            
        Returns:
            GachaResult: ガチャの結果
        """
        rand_num = random.random()
        
        # フィーバータイム判定
        if minute == self.fever_minute:
            # フィーバー時はURまたはSRのみ
            rand_num = random.uniform(0, self.ur_probability + self.sr_probability)
        
        rarity = self._calculate_rarity(rand_num)
        
        if rarity == GachaRarity.UR:
            return GachaResult(
                rarity=rarity,
                message=self.message_large
            )
        elif rarity == GachaRarity.SR:
            if self.images:
                image_data = random.choice(self.images)
                return GachaResult(
                    rarity=rarity,
                    message=self.message_medium,
                    image=GachaImage(
                        filepath=image_data["filepath"],
                        twitter_id=image_data["twitter_id"]
                    )
                )
            else:
                # 画像がない場合はメッセージのみ
                return GachaResult(
                    rarity=rarity,
                    message=self.message_medium
                )
        else:
            return GachaResult(
                rarity=rarity,
                message=self.message_medium
            )
    
    def get_image_data(self, image: GachaImage) -> Optional[bytes]:
        """画像データを取得"""
        key = f"{image.filepath}_{image.twitter_id}"
        return self.image_data.get(key)