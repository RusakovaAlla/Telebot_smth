import requests
import googletrans
from datetime import datetime, timedelta


def extract_city_weather_info(some_city):
    """ввод на русском, в любом регистре"""
    translator = googletrans.Translator()
    city = translator.translate(some_city.lower(), src="ru")
    r = requests.get(
        f'http://api.openweathermap.org/data/2.5/weather?q={city.text}&appid=4321a3d417b53045aa1b6617c529c910&units=metric&lang=ru')

    return r.json()


def useful_weather_info(city):
    """на вход подаем созданный json файл с погодой и разбираем его"""
    test = extract_city_weather_info(city)
    descr = test['weather'][0]['description'][0].title() + test['weather'][0]['description'][
                                                           1:]  # чтобы было кравиво написано с болшой буквы
    temps = [int(test['main']['temp']), int(test['main']['feels_like'])]
    atm_pr = test['main']['pressure']
    hum = test['main']['humidity']
    what_sun_does = [datetime.fromtimestamp(test['sys']['sunrise']),
                     datetime.fromtimestamp(test['sys']['sunset'])]

    return f"Погода в {city}\n{descr}, облачность {test['clouds']['all']}%\nTемпература воздуха {temps[0]} \u00B0C, " \
           f"ощущается как {temps[1]} \u00B0C, влажность {hum}%\n" \
           f"Атмосферное давление {atm_pr} мм.рт.ст\nВосход - {what_sun_does[0]}, " \
           f"заход - {what_sun_does[1]} (по вашему времени)\n"
