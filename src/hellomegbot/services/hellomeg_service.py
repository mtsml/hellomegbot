from .gacha_service import GachaService


HELLOMEG_MESSAGE_MEDIUM = """
＿人人人人人人人人＿
＞　ハロめぐー！　＜
￣Y^Y^Y^Y^Y^Y^Y￣
"""

HELLOMEG_MESSAGE_LARGE = """
​           
   ■       
   ■   ■   
   ■   ■   
  ■■   ■   
  ■     ■  
  ■     ■  
 ■      ■■ 
 ■       ■ 
           
　■■■■■■■■  
　■       ■ 
　■       ■ 
　■       ■ 
　■       ■ 
　■       ■ 
　■       ■ 
　■■■■■■■■■ 
         
      ■     
  ■   ■     
  ■■■ ■■■   
  ■■  ■ ■■  
 ■ ■ ■   ■  
 ■ ■ ■   ■  
 ■  ■    ■  
 ■ ■■   ■   
 ■■■   ■    
         
      ■    
     ■■    
   ■■      
  ■■  ■ ■  
 ■     ■   
 ■■        
  ■■       
    ■■     
     ■■    
         
     ■■
     ■■
     ■■
     ■■
     ■■
     ■■
     ■■
       
     ■■
"""

HELLOMEG_JSON_URL = "https://hellomeg-assets.pages.dev/public/hellomegbot/hellomeg.json"


class HellomegService(GachaService):
    """Hellomegコマンドのビジネスロジック"""
    
    def __init__(
        self,
        fever_minute: int = 0,
        ur_probability: float = 0.03,
        sr_probability: float = 0.18,
    ):
        super().__init__(
            message_medium=HELLOMEG_MESSAGE_MEDIUM,
            message_large=HELLOMEG_MESSAGE_LARGE,
            json_url=HELLOMEG_JSON_URL,
            fever_minute=fever_minute,
            ur_probability=ur_probability,
            sr_probability=sr_probability,
        )