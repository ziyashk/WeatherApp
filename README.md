# 🌦️ WeatherApp

A college field project weather application developed using Python Flask, HTML and CSS.

The application allows users to search for a city and view current weather information, forecasts, weather details, favorite cities, alerts and map information using the OpenWeather API.

## 👩‍💻 Developer

**Ziya Shaikh**

BCA – 2nd Year  
Abeda Inamdar Senior College

## ✨ Features

- 🌤️ Current Weather
- 📅 5-Day Forecast
- 🕐 Hourly Forecast
- 🌡️ Weather Details
- 🔎 Explore/Search Cities
- 🗺️ Weather Map
- ⭐ Favorite Cities
- ⚠️ Weather Alerts
- ℹ️ About/Help

## 🛠️ Technologies Used

- Python
- Flask
- HTML
- CSS
- Requests
- OpenWeather API
- JSON

## 🏗️ Project Architecture

```text
User
  ↓
Browser
  ↓ HTTP Request
Flask / Python Application
  ↓ HTTP GET
OpenWeather API
  ↓ JSON Response
Flask / Python
  ↓
HTML + CSS
  ↓
User