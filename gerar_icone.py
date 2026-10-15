"""Gera assets/icon.ico (microfone branco em fundo azul). Requer Pillow (só dev)."""
from PIL import Image, ImageDraw

T = 1024  # desenha grande e reduz
img = Image.new("RGBA", (T, T), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.rounded_rectangle([0, 0, T - 1, T - 1], radius=200, fill=(25, 118, 210, 255))
b = (255, 255, 255, 255)
d.rounded_rectangle([370, 150, 654, 570], radius=142, fill=b)          # corpo
d.arc([250, 330, 774, 760], start=0, end=180, fill=b, width=64)        # suporte
d.rectangle([480, 745, 544, 850], fill=b)                              # haste
d.rounded_rectangle([340, 830, 684, 894], radius=32, fill=b)           # base
img.save("assets/icon.ico", sizes=[(16, 16), (32, 32), (48, 48), (256, 256)])
img.resize((256, 256), Image.LANCZOS).save("assets/icon.png")
