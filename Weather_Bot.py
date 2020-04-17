try:
    from cairosvg import svg2png
except ImportError:
    exit('This script requires the cairo module\nInstall with: sudo apt-get install libcairo2-dev\nsudo python3 -m pip install --upgrade pip\nsudo python3 -m pip install cairosvg')
try:
    from pytz import timezone
except ImportError:
    exit('This script requires the pytz module\nInstall with: sudo python3 -m pip install --upgrade pip\nsudo python3 -m pip install pytz')
try:
    from PIL import Image,ImageDraw,ImageFont,ImageOps
except ImportError:
    exit('This script requires the pillow module\nInstall with: sudo python3 -m pip install --upgrade pip\nsudo python3 -m pip install --upgrade Pillow')
try:
    import pytz
except ImportError:
    exit('This script requires the pytz module\nInstall with: sudo python3 -m pip install --upgrade pip\nsudo python3 -m pip install pytz')
try:
    import requests
except ImportError:
    exit('This script requires the requests module\nInstall with: sudo python3 -m pip install --upgrade pip\nsudo python3 -m pip install requests')
try:
    import epd7in5
except ImportError:
    exit('This script requires the waveshare_epd epd7in5 and epdconfig scripts\nDownload them from: https://github.com/waveshare/e-Paper')
try:
    import RPi.GPIO
except ImportError:
    exit('This script requires the RPi.GPIO module\nInstall with: sudo python3 -m pip install --upgrade pip\nsudo python3 -m pip install RPi.GPIO')

from datetime import datetime, timedelta
import json
import os
import time
import traceback

iconDict = {"Day":{200:"wi-day-storm-showers.svg",
201:"wi-day-storm-showers.svg",
202:"wi-storm-showers.svg",
210:"wi-day-thunderstorm.svg",
211:"wi-thunderstorm.svg",
212:"wi-thunderstorm.svg",
221:"wi-thunderstorm.svg",
230:"wi-day-storm-showers.svg",
231:"wi-day-storm-showers.svg",
232:"wi-day-storm-showers.svg",
300:"wi-day-rain-mix.svg",
301:"wi-day-rain-mix.svg",
302:"wi-day-rain-mix.svg",
310:"wi-day-rain-mix.svg",
311:"wi-rain-mix.svg",
312:"wi-rain-mix.svg",
313:"wi-rain-mix.svg",
314:"wi-showers.svg",
321:"wi-showers.svg",
500:"wi-day-showers.svg",
501:"wi-day-rain.svg",
502:"wi-rain.svg",
503:"wi-rain.svg",
504:"wi-rain.svg",
511:"wi-rain.svg",
520:"wi-day-rain.svg",
521:"wi-rain.svg",
522:"wi-rain-wind.svg",
531:"wi-rain-wind.svg",
600:"wi-day-snow.svg",
601:"wi-day-snow.svg",
602:"wi-snow.svg",
611:"wi-day-sleet.svg",
612:"wi-day-sleet.svg",
613:"wi-day-sleet.svg",
615:"wi-day-rain-mix.svg",
616:"wi-day-rain-mix.svg",
620:"wi-day-rain-mix.svg",
621:"wi-day-rain-mix.svg",
622:"wi-day-rain-mix.svg",
701:"wi-sprinkle.svg",
711:"wi-smoke.svg",
721:"wi-day-haze.svg",
731:"wi-sandstorm.svg",
741:"wi-fog.svg",
751:"wi-sandstorm.svg",
761:"wi-dust.svg",
762:"wi-volcano.svg",
771:"wi-strong-wind.svg",
781:"wi-tornado.svg",
800:"wi-day-sunny.svg",
801:"wi-day-sunny-overcast.svg",
802:"wi-day-cloudy.svg",
803:"wi-cloud.svg",
804:"wi-cloudy.svg"}, 
"Night":{200:"wi-night-alt-storm-showers.svg",
201:"wi-night-alt-storm-showers.svg",
202:"wi-storm-showers.svg",
210:"wi-night-alt-thunderstorm.svg",
211:"wi-thunderstorm.svg",
212:"wi-thunderstorm.svg",
221:"wi-thunderstorm.svg",
230:"wi-night-alt-storm-showers.svg",
231:"wi-night-alt-storm-showers.svg",
232:"wi-night-alt-storm-showers.svg",
300:"wi-night-alt-rain-mix.svg",
301:"wi-night-alt-rain-mix.svg",
302:"wi-night-alt-rain-mix.svg",
310:"wi-night-alt-rain-mix.svg",
311:"wi-rain-mix.svg",
312:"wi-rain-mix.svg",
313:"wi-rain-mix.svg",
314:"wi-showers.svg",
321:"wi-showers.svg",
500:"wi-night-alt-showers.svg",
501:"wi-night-alt-rain.svg",
502:"wi-rain.svg",
503:"wi-rain.svg",
504:"wi-rain.svg",
511:"wi-rain.svg",
520:"wi-night-alt-rain.svg",
521:"wi-rain.svg",
522:"wi-rain-wind.svg",
531:"wi-rain-wind.svg",
600:"wi-night-alt-snow.svg",
601:"wi-night-alt-snow.svg",
602:"wi-snow.svg",
611:"wi-night-alt-sleet.svg",
612:"wi-night-alt-sleet.svg",
613:"wi-night-alt-sleet.svg",
615:"wi-night-alt-rain-mix.svg",
616:"wi-night-alt-rain-mix.svg",
620:"wi-night-alt-rain-mix.svg",
621:"wi-night-alt-rain-mix.svg",
622:"wi-night-alt-rain-mix.svg",
701:"wi-sprinkle.svg",
711:"wi-smoke.svg",
721:"wi-haze.svg",
731:"wi-sandstorm.svg",
741:"wi-fog.svg",
751:"wi-sandstorm.svg",
761:"wi-dust.svg",
762:"wi-volcano.svg",
771:"wi-strong-wind.svg",
781:"wi-tornado.svg",
800:"wi-night-clear.svg",
801:"wi-night-alt-partly-cloudy.svg",
802:"wi-night-clear.svg",
803:"wi-cloud.svg",
804:"wi-cloudy.svg"}}

unitsDict = {"metric":{"temperature":"°C","speed":"m/s"},"imperial":{"temperature":"°F","speed":"mph"}}
timeFormatDict = {24:"%H:%M",12:"%I %p"}
forecastIconPosition = [1,2,3,4]
forecastTempPosition = [1,2,3,4]
forecastTimePosition = [1,2,3,4]

#Load the config file from the specified folder.
config = json.load(open('/home/pi/WeatherBot/config.json'))

def invertImage(filename):
    image = Image.open(filename)

    r,g,b,a = image.split()
    rgb_image = Image.merge('RGB', (r,g,b))
    inverted_image = ImageOps.invert(rgb_image)
    r2,g2,b2 = inverted_image.split()

    final_transparent_image = Image.merge('RGBA', (r2,g2,b2,a))
    final_transparent_image.save(filename)

def getTOD(sunrise=1577858400, sunset=1577901600,time=int(datetime.now().timestamp())):
    #Find out whether the specified time given as an argument is daytime or nighttime based on sunrise/sunset values.
    utc=pytz.utc
    localTimezone = timezone(config["timezone"])

    sunriseDatetime = datetime.fromtimestamp(sunrise)
    sunsetDatetime = datetime.fromtimestamp(sunset)
    currentDatetime = datetime.fromtimestamp(time)

    if(utc.localize(currentDatetime).astimezone(localTimezone).time()>=utc.localize(sunriseDatetime).astimezone(localTimezone).time() and utc.localize(currentDatetime).astimezone(localTimezone).time()<=utc.localize(sunsetDatetime).astimezone(localTimezone).time()):
        return "Day"
    else:
        return "Night"

def getCurrentWeather():
    #Get the current weather from the 'weather' OpenWeatherMap API.
    #The 'weather' OpenWeatherMap API has an access limit of 60 calls/day.
    url = "https://api.openweathermap.org/data/2.5/weather?id="+config["locationID"]+"&appid="+config["APIKEY"]+"&units="+config["units"]
    response = requests.post(url)
    return response.json()

def getForecast():
    #Get the 3 hour / 5 days forecast from the 'forecast' OpenWeatherMap API.
    #The 'forecast' OpenWeatherMap API has an access limit of 60 calls/day.
    url = "https://api.openweathermap.org/data/2.5/forecast?id="+config["locationID"]+"&appid="+config["APIKEY"]+"&units="+config["units"]
    response = requests.post(url)
    return response.json()

def getOneCallWeather():
    #Get the weather and forecast from the 'OneCall' OpenWeatherMap API.
    url = "https://api.openweathermap.org/data/2.5/onecall?lat="+str(config["lat"])+"&lon="+str(config["lon"])+"&appid="+config["APIKEY"]+"&units="+config["units"]
    response = requests.post(url)
    return response.json()

def generateWeather():
    #Generate a single weather / forecast file either by using two separate APIs or the 'OneCall' API.
    #The separate APIs have an access limit of 60 calls/minute.
    #The 'OneCall' API has an access limit of 1000 calls/day.
    weather={}
    forecast=[]
    if (config["APITYPE"] == 0):
        weatherDetails = getCurrentWeather()
        forecastDetails = getForecast()

        weather["time"] = weatherDetails["dt"]
        weather["icon"] = weatherDetails["weather"][0]["id"]
        weather["temp"] = weatherDetails["main"]["temp"]
        weather["windSpeed"] = weatherDetails["wind"]["speed"]
        weather["sunrise"] = weatherDetails["sys"]["sunrise"]
        weather["sunset"] = weatherDetails["sys"]["sunset"]

        for position in range(0,4):
            hourDetails = {}
            hourDetails["time"] = forecastDetails["list"][position]["dt"]
            hourDetails["icon"] = forecastDetails["list"][position]["weather"][0]["id"]
            hourDetails["temp"] = forecastDetails["list"][position]["main"]["temp"]
            forecast.append(hourDetails)
    
    elif (config["APITYPE"] == 1):
        oneCallDetails = getOneCallWeather()

        weather["time"] = oneCallDetails["current"]["dt"]
        weather["icon"] = oneCallDetails["current"]["weather"][0]["id"]
        weather["temp"] = oneCallDetails["current"]["temp"]
        weather["windSpeed"] = oneCallDetails["current"]["wind_speed"]
        weather["sunrise"] = oneCallDetails["current"]["sunrise"]
        weather["sunset"] = oneCallDetails["current"]["sunset"]

        for position in range(0,4):
            hourDetails = {}
            hourDetails["time"] = oneCallDetails["hourly"][position*config["hourSpacing"]+1]["dt"]
            hourDetails["icon"] = oneCallDetails["hourly"][position*config["hourSpacing"]+1]["weather"][0]["id"]
            hourDetails["temp"] = oneCallDetails["hourly"][position*config["hourSpacing"]+1]["temp"]
            forecast.append(hourDetails)

    completeData = {}
    completeData["current"] = weather
    completeData["forecast"] = forecast

    return completeData

def generate_image():
    #Generate the .png image shown on the e-Ink screen.

    utc=pytz.utc
    localTimezone = timezone(config["timezone"])

    weatherData = generateWeather()

    #Use the svg2png module to convert the .svg icons to .png so that they can be added to the image.
    svg2png(url="Icons/"+iconDict[getTOD(weatherData["current"]["sunrise"], weatherData["current"]["sunset"], weatherData["current"]["time"])][weatherData["current"]["icon"]], write_to="weatherIcon.png", parent_width=200,parent_height=200)
    svg2png(url="Icons/wi-time-4.svg", write_to="timeIcon.png", parent_width=60,parent_height=60)
    svg2png(url="Icons/wi-strong-wind.svg", write_to="windIcon.png", parent_width=100,parent_height=100)

    screenCanvas = Image.new('RGBA', (640,384), (255,255,255,255)) #Generate an empty white canvas.

    weatherIcon = Image.open("weatherIcon.png") #Open the icon file.
    windIcon = Image.open("windIcon.png")
    timeIcon = Image.open("timeIcon.png")

    weatherIcon.convert("RGBA") #Convert the icon to RGBA if possible.
    windIcon.convert("RGBA")
    timeIcon.convert("RGBA")

    screenCanvas.paste(weatherIcon, box=(0,0), mask=weatherIcon) #Paste the loaded icons to the specified position via the box argument.
    screenCanvas.paste(windIcon, box=(220,90), mask=windIcon)

    drawCanvas = ImageDraw.Draw(screenCanvas) #Generate a draw canvas so that we can paste text on it.

    currentTempFont = ImageFont.truetype(r'Fonts/OpenSans-ExtraBold.ttf', 90) #Load a font with the specified size.
    windSpeedFont = ImageFont.truetype(r'Fonts/OpenSans-ExtraBold.ttf', 40)
    forecastTempFont = ImageFont.truetype(r'Fonts/OpenSans-Bold.ttf', 40)
    forecastHourFont = ImageFont.truetype(r'Fonts/OpenSans-Light.ttf', 40)

    drawCanvas.text((220, 0), str(int(weatherData["current"]["temp"]))+unitsDict[config["units"]]["temperature"], fill="black", font=currentTempFont) #Draw some text on the canvas, with the specified loaded font.
    drawCanvas.text((320, 115), str(int(weatherData["current"]["windSpeed"]))+unitsDict[config["units"]]["speed"], fill="black", font=windSpeedFont)
    drawCanvas.text((470, 75), utc.localize(datetime.fromtimestamp(weatherData["current"]["time"])).astimezone(localTimezone).strftime('%a'), fill="black", font=forecastTempFont)
    drawCanvas.text((470, 115), utc.localize(datetime.fromtimestamp(weatherData["current"]["time"])).astimezone(localTimezone).strftime('%d %b'), fill="black", font=forecastTempFont)

    for position in range(0,4):
        svg2png(url="Icons/"+iconDict[getTOD(weatherData["current"]["sunrise"], weatherData["current"]["sunset"], weatherData["forecast"][position]["time"])][weatherData["forecast"][position]["icon"]], write_to="weatherIcon.png", parent_width=100,parent_height=100)
        weatherIcon = Image.open("weatherIcon.png")
        screenCanvas.paste(weatherIcon, box=(160*position+30,200), mask=weatherIcon)
        drawCanvas.text((160*position+30, 275), str(int(weatherData["forecast"][position]["temp"]))+unitsDict[config["units"]]["temperature"], fill="black", font=forecastTempFont)
        drawCanvas.text((160*position+30, 315), utc.localize(datetime.fromtimestamp(weatherData["forecast"][position]["time"])).astimezone(localTimezone).strftime(timeFormatDict[config["timeFormat"]]), fill="black", font=forecastHourFont)

    screenCanvas.save("weatherImage.png", format="PNG")
    return 1

def show_image():
    try:
        epd = epd7in5.EPD()
        epd.init()
        epd.Clear(0xFF)
        
        InitialImage = Image.open("weatherImage.png")
        ShownImage = InitialImage.rotate(180)

        epd.display(epd.getbuffer(ShownImage))
        epd.sleep()
    except:
        print('traceback.format_exc():\n%s', traceback.format_exc())
        exit()
        return 1

def run():
    os.chdir(config["workingDirectory"])
    generate_image()
    show_image()

if __name__ == "__main__":
    run()