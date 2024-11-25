from pyrogram import Client, filters

import requests

from utils.misc import prefix, modules_help


BASE_URL = "https://www.samirxpikachu.run.place/weather/"


def get_weather_data(city):
    """Fetches weather data from the API."""
    url = f"{BASE_URL}{city}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None


def format_weather_data(data):
    """Formats weather data into a readable string."""
    if not data:
        return "No weather data available."

    city = data.get("city", "N/A")
    region = data.get("region", "N/A")
    country = data.get("country", "N/A")
    temperature = data.get("temperature", {})
    condition = data.get("condition", {})
    wind = data.get("wind", {})
    pressure = data.get("pressure", {})
    precipitation = data.get("precipitation", {})
    humidity = data.get("humidity", "N/A")
    feels_like = data.get("feels_like", {})
    visibility = data.get("visibility", {})
    uv_index = data.get("uv_index", "N/A")
    gust = data.get("gust", {})
    air_quality = data.get("air_quality", {})

    weather_info = (
        f"Weather in {city}, {region}, {country}:\n"
        f"Temperature: {temperature.get('celsius', 'N/A')}°C ({temperature.get('fahrenheit', 'N/A')}°F)\n"
        f"Condition: {condition.get('text', 'N/A')} {condition.get('icon', '')}\n"
        f"Wind: {wind.get('speed_kph', 'N/A')} kph ({wind.get('speed_mph', 'N/A')} mph), "
        f"Direction: {wind.get('direction', 'N/A')}\n"
        f"Pressure: {pressure.get('mb', 'N/A')} mb ({pressure.get('in', 'N/A')} in)\n"
        f"Precipitation: {precipitation.get('mm', 'N/A')} mm ({precipitation.get('inches', 'N/A')} in)\n"
        f"Humidity: {humidity}%\n"
        f"Feels Like: {feels_like.get('celsius', 'N/A')}°C ({feels_like.get('fahrenheit', 'N/A')}°F)\n"
        f"Visibility: {visibility.get('km', 'N/A')} km ({visibility.get('miles', 'N/A')} miles)\n"
        f"UV Index: {uv_index}\n"
        f"Gust: {gust.get('kph', 'N/A')} kph ({gust.get('mph', 'N/A')} mph)\n"
        f"Air Quality:\n"
        f"  CO: {air_quality.get('co', 'N/A')} mg/m³\n"
        f"  NO2: {air_quality.get('no2', 'N/A')} µg/m³\n"
        f"  O3: {air_quality.get('o3', 'N/A')} µg/m³\n"
        f"  SO2: {air_quality.get('so2', 'N/A')} µg/m³\n"
        f"  PM2.5: {air_quality.get('pm2_5', 'N/A')} µg/m³\n"
        f"  PM10: {air_quality.get('pm10', 'N/A')} µg/m³\n"
        f"  US EPA Index: {air_quality.get('us_epa_index', 'N/A')}\n"
        f"  GB DEFRA Index: {air_quality.get('gb_defra_index', 'N/A')}\n"
    )
    return weather_info


@Client.on_message(filters.command("forecast", prefix) & filters.me)
async def weather(client, message):
    if len(message.text.split()) < 2:
        await message.edit_text("Please provide a search query.")
        return

    await message.edit_text("Fetching weather data...")
    city = message.text.split(None, 1)[1]  # Extract the query from the command

    data = get_weather_data(city)  # Changed from generate_image

    weather_info = format_weather_data(data)
    await message.edit_text(weather_info)


modules_help["forecast"] = {"forecast": "Get the weather forecast for a city."}
