import io
import discord
from PIL import Image, ImageDraw, ImageFont


COMMAND_NAME = "meggen"
COMMAND_DESC = "ハロめぐイラスト作成"
COMMAND_CHOICES = {
    "img": [
        discord.app_commands.Choice(name="フィーバー", value="fever"),
        discord.app_commands.Choice(name="ハロめぐだもん", value="damon"),
        discord.app_commands.Choice(name="ハクチュー", value="hkc"),
        discord.app_commands.Choice(name="宇宙猫", value="universe"),
        discord.app_commands.Choice(name="蓮ノ空しかないんすよ", value="hasunosorashikanainsuyo"),
        discord.app_commands.Choice(name="ドヤめぐ", value="doya"),
    ]
}
COMMAND_CHOICES_DESCRIBE = {
    "img": "ハロめぐを選んでください"   
}
COMMAND_CHOICES_RENAME = {
    "img": "イラスト"
}
IMG_FEVER = {
    'rows': 3,
    'label': "（5文字まで）",
    'img_path': "assets/meggen/fever.png",
    'text_img_size': (600, 500),
    'text_color': "#764c4d",
    'text_font_size': 100,
    'text_font_family': "MPLUSRounded1c-Black.ttf",
    'text_start_xy': (30, 15),
    'text_rotate': 16,
    'text_paste_xy': (80, 300),
    'send_filename': 'fever.png',
}
IMG_DAMON = {
    'rows': 2,
    'label': "（10文字まで）",
    'img_path': "assets/meggen/damon.png",
    'text_img_size': (1050, 300),
    'text_color': "#ceaa9e",
    'text_font_size': 100,
    'text_font_family': "MPLUSRounded1c-Black.ttf",
    'text_start_xy': (20, 0),
    'text_rotate': 0,
    'text_paste_xy': (120, 280),
    'stroke_width': 20,
    'stroke_fill': '#633539',
    'send_filename': 'damon.png',
}
IMG_HKC = {
    'rows': 1,
    'label': "（7文字まで）",
    'img_path': "assets/meggen/hkc.png",
    'text_img_size': (500, 300),
    'text_color': "#c1e3da",
    'text_font_size': 60,
    'text_font_family': "MPLUSRounded1c-Black.ttf",
    'text_start_xy': (60, 75),
    'text_rotate': 20,
    'text_paste_xy': (20, 80),
    'stroke_width': 15,
    'stroke_fill': '#9fccbf',
    'send_filename': 'hkc.png',
}
IMG_UNIVERSE = {
    'rows': 2,
    'label': "（5文字まで）",
    'img_path': "assets/meggen/universe.png",
    'text_img_size': (350, 260),
    'text_color': "#000000",
    'text_font_size': 50,
    'text_font_family': "MPLUSRounded1c-Black.ttf",
    'text_start_xy': (50, 15),
    'text_rotate': 340,
    'text_paste_xy': (720, 450),
    'send_filename': 'universe.png',
}
IMG_HASUNOSORASHIKANAINSUYO = {
    'rows': 3,
    'label': "（10文字まで）",
    'img_path': "assets/meggen/hasunosorashikanainsuyo.png",
    'text_img_size': (1050, 400),
    'text_color': "#000000",
    'text_font_size': 100,
    'text_font_family': "MPLUSRounded1c-Black.ttf",
    'text_start_xy': (0, 0),
    'text_rotate': 0,
    'text_paste_xy': (150, 50),
    'send_filename': 'hasunosorashikanainsuyo.png',
}
IMG_DOYA = {
    'rows': 5,
    'label': "（10文字まで）",
    'img_path': "assets/meggen/doya.png",
    'text_img_size': (700, 400),
    'text_color': "#ffffff",
    'text_font_size': 70,
    'text_font_family': "MPLUSRounded1c-Black.ttf",
    'text_start_xy': (0, 0),
    'text_rotate': 0,
    'text_paste_xy': (50, 500),
    'send_filename': 'doya.png',
}
IMG_INFO_MAP = {
    'fever': IMG_FEVER,
    'damon': IMG_DAMON,
    'hkc': IMG_HKC,
    'universe': IMG_UNIVERSE,
    'hasunosorashikanainsuyo': IMG_HASUNOSORASHIKANAINSUYO,
    'doya': IMG_DOYA,
}


class Modal(discord.ui.Modal, title="テキスト入力"):

    def __init__(self, img):
        super().__init__()
        self.img_info = IMG_INFO_MAP[img]
        self.textInputs = []
        for i in range(self.img_info["rows"]):
            self.textInputs.append(discord.ui.TextInput(
                label=f"{i+1}行目{self.img_info['label']}",
                style=discord.TextStyle.short,
                required=False))
            self.add_item(self.textInputs[i])

    async def on_submit(self, interaction: discord.Interaction):
        text = "\n".join(map(lambda t: t.value, self.textInputs))
        img = draw_text(text, self.img_info)

        arr = io.BytesIO()
        img.save(arr, format="PNG")
        arr.seek(0)
        file = discord.File(arr, filename=self.img_info["send_filename"])

        await interaction.response.send_message(file=file)


def draw_text(text: str, img_info):
    """targetImg に text を画像として埋め込む
    """

    textImg = Image.new("RGBA", img_info["text_img_size"], (0, 0, 0, 0))
    textDraw = ImageDraw.Draw(textImg)
    font = ImageFont.truetype(img_info["text_font_family"], img_info["text_font_size"])
    text_param = {
        "xy": img_info["text_start_xy"],
        "text": text,
        "fill": img_info["text_color"],
        "font": font
    }
    if ("stroke_width" in img_info.keys() and "stroke_fill" in img_info.keys()):
        text_param['stroke_width'] = img_info["stroke_width"]
        text_param['stroke_fill'] = img_info["stroke_fill"]
    textDraw.text(**text_param)
    textImg = textImg.rotate(img_info["text_rotate"])

    img = Image.open(img_info["img_path"])
    img.paste(textImg, img_info["text_paste_xy"], textImg)

    return img


async def command(interaction: discord.Interaction, img: str):
    """任意のテキストを入れたハロめぐのイラストをつくる
    """
    await interaction.response.send_modal(Modal(img))
