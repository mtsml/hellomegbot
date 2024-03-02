from PIL import Image, ImageDraw, ImageFont


TEMPLATE_PNG_PATH = 'assets/fever/template.png'
TEXT_COLOR = '#764c4d'
TEXT_SIZE = 100
TEXT_FONT_FAMILY = 'MPLUSRounded1c-Black.ttf'


font = ImageFont.truetype(TEXT_FONT_FAMILY, TEXT_SIZE)


def draw_text(text: str, targetImg, xy):
    textImg = Image.new('RGBA', (600, 330), (0, 0, 0, 0))
    textDraw = ImageDraw.Draw(textImg)
    textDraw.text((20, 15), text, TEXT_COLOR, font=font)
    textImg = textImg.rotate(14)
    targetImg.paste(textImg, xy, textImg)


def generate_fever_png(text: str):
    img = Image.open(TEMPLATE_PNG_PATH)
    draw_text(text, img, (80, 280))
    return img