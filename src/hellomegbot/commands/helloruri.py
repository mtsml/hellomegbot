from .gacha_base import GachaBase


HELLORURI_COMMAND_NAME = "helloruri"
HELLORURI_COMMAND_DESC = "ハロるりー！"
HELLORURI_MESSAGE_MEDIUM = """
＿人人人人人人人人＿
＞　ハロるりー！　＜
￣Y^Y^Y^Y^Y^Y^Y￣
"""
HELLORURI_MESSAGE_LARGE = """
​           
   ■       
   ■   ■   
   ■   ■   
  ■■   ■   
  ■     ■  
  ■     ■  
 ■      ■■ 
 ■       ■ 
           
　■■■■■■■■  
　■       ■ 
　■       ■ 
　■       ■ 
　■       ■ 
　■       ■ 
　■       ■ 
　■■■■■■■■■ 
         
　■■■■■■　　　　
　　　　　■　　　　　
　　　■■　　　　　　
　　■■■■■　　　　
　■■　　　　■　　　
　　　　　　　　■　　
　　■■　　　　■　　
　　■　　■　■　　　
　　■■■■　　
         
　■　　　　　　　　
　■　　　　　■　　
　■　　　　　■　　
　■　　　　　■　　
　■　　　　　■　　
　■　■　　　■　　
　■■　　　■　　　
　　　　　■　　　
　　　　　■　　　
　　　　■　　　
         
    ■■
    ■■
    ■■
    ■■
    ■■
    ■■
    ■■
      
    ■■
"""
HELLORURI_JSON_URL = "https://hellomeg-assets.pages.dev/public/hellomegbot/helloruri.json"


class HelloRuri(GachaBase):
    def __init__(
        self,
        ur_probability,
        sr_probability,
    ):
        kwargs = {}
        if ur_probability is not None:
            kwargs["ur_probability"] = ur_probability
        if sr_probability is not None:
            kwargs["sr_probability"] = sr_probability
        super().__init__(
            command_name=HELLORURI_COMMAND_NAME,
            command_description=HELLORURI_COMMAND_DESC,
            message_medium=HELLORURI_MESSAGE_MEDIUM,
            message_large=HELLORURI_MESSAGE_LARGE,
            json_url=HELLORURI_JSON_URL,
            **kwargs,
        )
