import os
import discord
from PIL import Image, ImageDraw, ImageFont


async def text_to_image(message, text, number):
    img = Image.new("RGB", (900, 250), color=(255, 255, 255))
    fnt = ImageFont.truetype(os.path.abspath(
        os.path.join((os.getcwd()), './fonts/meiryo.ttc')), 128)
    d = ImageDraw.Draw(img)
    d.text((30, 30), "{num}. {kanji}".format(
        num=number, kanji=text), font=fnt, fill=(0, 0, 0))
    filedir = os.path.abspath(os.path.join(
        os.getcwd(), "./modules/cache/temp.png"))
    img.save(filedir)
    await message.channel.send(file=discord.File(filedir))
