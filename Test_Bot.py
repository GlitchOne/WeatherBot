import json
import os
import time
import epd7in5
import requests
from cairosvg import svg2png
from PIL import Image,ImageDraw,ImageFont,ImageOps

url = "https://api.openweathermap.org/data/2.5/weather?id=YOURCITYID&appid=YOURAPIKEY&units=metric"
response = requests.post(url)

currentWeather = response.json()["main"]["temp"]
prettierWeather = str(int(currentWeather))+"°C"

svg2png(url="wi-thermometer.svg", write_to="timeIcon.png", parent_width=200,parent_height=200)

screenCanvas = Image.new('RGBA', (640,384), (255,255,255,255))
timeIcon = Image.open("timeIcon.png")
timeIcon.convert("RGBA")
screenCanvas.paste(timeIcon, box=(0,0), mask=timeIcon)

drawCanvas = ImageDraw.Draw(screenCanvas)
currentTempFont = ImageFont.truetype(r'Fonts/OpenSans-ExtraBold.ttf', 100)
drawCanvas.text((200, 10), prettierWeather, fill="black", font=currentTempFont)

screenCanvas.save("testWeatherImage.png", format="PNG")

epd = epd7in5.EPD()
epd.init()
epd.Clear(0xFF)
InitialImage = Image.open("testWeatherImage.png")
ShownImage = InitialImage.rotate(180)
epd.display(epd.getbuffer(ShownImage))
epd.sleep()