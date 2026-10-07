from flask import Flask, render_template, request, redirect, url_for, session
import requests
import os
from datetime import datetime
from urllib.parse import quote

app = Flask(__name__)
app.secret_key = "weather-app-student-project"

API_KEY = os.getenv("OPENWEATHER_API_KEY")
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


def get_current_weather(city):
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    response = requests.get(WEATHER_URL, params=params, timeout=10)
    if response.status_code != 200:
        return None
    data = response.json()
    return {
        "city": data["name"],
        "country": data["sys"].get("country", ""),
        "temperature": round(data["main"]["temp"], 1),
        "feels_like": round(data["main"]["feels_like"], 1),
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "wind": data["wind"]["speed"],
        "condition": data["weather"][0]["description"].title(),
        "main_condition": data["weather"][0]["main"],
        "visibility": round(data.get("visibility", 0) / 1000, 1),
        "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%I:%M %p"),
        "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%I:%M %p"),
        "lat": data["coord"]["lat"],
        "lon": data["coord"]["lon"]
    }


def get_forecast(city):
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    response = requests.get(FORECAST_URL, params=params, timeout=10)
    if response.status_code != 200:
        return None
    return response.json()


def icon_for(condition):
    condition = condition.lower()
    icons = {
        "clear": "☀️", "cloud": "☁️", "rain": "🌧️", "drizzle": "🌦️",
        "thunderstorm": "⛈️", "snow": "❄️", "mist": "🌫️", "fog": "🌫️", "haze": "🌫️"
    }
    for key, icon in icons.items():
        if key in condition:
            return icon
    return "☁️"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/weather")
def weather():
    city = request.args.get("city", "").strip()
    if not city:
        return render_template("weather.html", error="Please enter a city name.", city="")
    data = get_current_weather(city)
    if not data:
        return render_template("weather.html", error="City not found", city=city)
    return render_template("weather.html", **data)


@app.route("/forecast")
def forecast():
    city = request.args.get("city", "").strip()
    if not city:
        return render_template("forecast.html", error="Please enter a city name.", city="")
    data = get_forecast(city)
    if not data:
        return render_template("forecast.html", error="City not found", city=city)
    forecast_data, used_dates = [], set()
    for item in data["list"]:
        dt = datetime.fromtimestamp(item["dt"])
        date_key = dt.strftime("%Y-%m-%d")
        if date_key not in used_dates:
            used_dates.add(date_key)
            forecast_data.append({
                "date": dt.strftime("%a, %d %b"),
                "temperature": round(item["main"]["temp"], 1),
                "condition": item["weather"][0]["description"].title(),
                "humidity": item["main"]["humidity"],
                "wind": item["wind"]["speed"],
                "icon": icon_for(item["weather"][0]["main"])
            })
        if len(forecast_data) == 5:
            break
    return render_template("forecast.html", city=data["city"]["name"], forecast=forecast_data)


@app.route("/hourly")
def hourly():
    city = request.args.get("city", "").strip()
    if not city:
        return render_template("hourly.html", error="Please enter a city name.", city="")
    data = get_forecast(city)
    if not data:
        return render_template("hourly.html", error="City not found", city=city)
    hourly_data = []
    for item in data["list"][:8]:
        hourly_data.append({
            "time": datetime.fromtimestamp(item["dt"]).strftime("%I:%M %p"),
            "temperature": round(item["main"]["temp"], 1),
            "condition": item["weather"][0]["description"].title(),
            "humidity": item["main"]["humidity"],
            "wind": item["wind"]["speed"],
            "icon": icon_for(item["weather"][0]["main"])
        })
    return render_template("hourly.html", city=data["city"]["name"], hourly=hourly_data)


@app.route("/details")
def details():
    city = request.args.get("city", "").strip()
    if not city:
        return render_template("details.html", error="Please enter a city name.", city="")
    data = get_current_weather(city)
    if not data:
        return render_template("details.html", error="City not found", city=city)
    return render_template("details.html", **data)


@app.route("/explore")
def explore():
    city = request.args.get("city", "").strip()
    data = get_current_weather(city) if city else None
    return render_template("explore.html", city=city, data=data, error=("City not found" if city and not data else None))


@app.route("/map")
def weather_map():
    city = request.args.get("city", "").strip()
    if not city:
        return render_template("map.html", error="Please enter a city name.", city="")
    data = get_current_weather(city)
    if not data:
        return render_template("map.html", error="City not found", city=city)
    lat, lon = data["lat"], data["lon"]
    delta = 0.08
    bbox = f"{lon-delta},{lat-delta},{lon+delta},{lat+delta}"
    map_url = f"https://www.openstreetmap.org/export/embed.html?bbox={quote(bbox)}&layer=mapnik&marker={lat}%2C{lon}"
    return render_template("map.html", **data, map_url=map_url)


@app.route("/favorites")
def favorites():
    favorites = session.get("favorites", [])
    return render_template("favorites.html", favorites=favorites, message=request.args.get("message"))


@app.route("/favorite/add")
def favorite_add():
    city = request.args.get("city", "").strip()
    if city:
        favorites = session.get("favorites", [])
        if city.title() not in favorites:
            favorites.append(city.title())
            session["favorites"] = favorites[:8]
    return redirect(url_for("favorites", message="City added to favorites."))


@app.route("/favorite/remove")
def favorite_remove():
    city = request.args.get("city", "").strip()
    favorites = session.get("favorites", [])
    session["favorites"] = [item for item in favorites if item.lower() != city.lower()]
    return redirect(url_for("favorites", message="City removed from favorites."))


@app.route("/alerts")
def alerts():
    city = request.args.get("city", "").strip()
    if not city:
        return render_template("alerts.html", error="Please enter a city name.", city="")
    data = get_current_weather(city)
    if not data:
        return render_template("alerts.html", error="City not found", city=city)
    alerts_list = []
    condition = data["main_condition"].lower()
    if data["temperature"] >= 35:
        alerts_list.append(("High Temperature", "The current temperature is quite high. Stay hydrated and avoid prolonged direct sunlight."))
    if data["wind"] >= 10:
        alerts_list.append(("Strong Wind", "Wind speed is elevated. Take care around open areas and unsecured objects."))
    if "thunder" in condition:
        alerts_list.append(("Thunderstorm", "Thunderstorm conditions are currently reported."))
    elif "rain" in condition or "drizzle" in condition:
        alerts_list.append(("Rain Alert", "Rain is currently reported. Carry suitable protection when travelling."))
    if not alerts_list:
        alerts_list.append(("No Major Alert", "No major condition-based alert was detected from the current weather data."))
    return render_template("alerts.html", **data, alerts=alerts_list)


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)
