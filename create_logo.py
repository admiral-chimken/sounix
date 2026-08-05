from PIL import Image, ImageDraw, ImageFont

image = Image.new("RGB", (900, 300), "black")

draw = ImageDraw.Draw(image)

try:
    font = ImageFont.truetype(
        "DejaVuSans-Bold.ttf",
        140
    )
except:
    font = ImageFont.load_default()

draw.text(
    (230, 40),
    "SOUNIX",
    font=font,
    fill="white",
)

try:
    small_font = ImageFont.truetype(
        "DejaVuSans.ttf",
        45
    )
except:
    small_font = ImageFont.load_default()

draw.text(
    (260, 190),
    "Linux System Assistant",
    font=small_font,
    fill="white",
)

image.save("assets/sounix_logo.png")
