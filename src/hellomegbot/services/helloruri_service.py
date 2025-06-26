from .gacha_service import GachaService


HELLORURI_MESSAGE_MEDIUM = """
＿人人人人人人人人＿
＞　ハロるりー！　＜
￣Y^Y^Y^Y^Y^Y^Y￣
"""

HELLORURI_MESSAGE_LARGE = """
​           
   ■       
   ■   ■   
   ■   ■   
    ■■     
           
  ■■■■■   
      ■    
    ■■     
      ■    
  ■■■■■   
           
    ■      
   ■■      
    ■      
    ■      
  ■■■■■   
           
  ■   ■■   
  ■  ■ ■   
  ■ ■  ■   
  ■■   ■   
  ■    ■   
           
■          
■          
■          
■          
■■■■■■■■■ 
           
   ■       
  ■        
■■■■■■■■■ 
  ■        
   ■       
           
    ■      
    ■      
   ■■      
  ■ ■      
■■  ■■■■■ 
           
           
   ■■■■■  
    ■  ■   
   ■■■■■  
   ■    ■  
   ■    ■  
"""

HELLORURI_JSON_URL = "https://hellomeg-assets.pages.dev/public/hellomegbot/helloruri.json"


class HelloRuriService(GachaService):
    """HelloRuriコマンドのビジネスロジック"""
    
    def __init__(
        self,
        fever_minute: int = 30,
        ur_probability: float = 0.03,
        sr_probability: float = 0.18,
    ):
        super().__init__(
            message_medium=HELLORURI_MESSAGE_MEDIUM,
            message_large=HELLORURI_MESSAGE_LARGE,
            json_url=HELLORURI_JSON_URL,
            fever_minute=fever_minute,
            ur_probability=ur_probability,
            sr_probability=sr_probability,
        )