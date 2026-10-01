# app.py
# Проект: Школьный Помощник
# Школа: РЖД Лицей № 14, г. Иркутск

import streamlit as st
import requests
import datetime

# --- НАСТРОЙКИ ---
SCHOOL_NAME = "РЖД Лицей № 14, г. Иркутск"
SCHOOL_LAT = 52.28717   # Широта школы
SCHOOL_LON = 104.25592  # Долгота школы
SCHOOL_URL = "https://licey-14.ru"

# !!! ЗАМЕНИ ЭТИ КООРДИНАТЫ НА СВОИ !!!
# Как найти: Google Maps → правой кнопкой на дом → "Что здесь?" → скопируй числа
HOME_LAT = 52.29000   # <-- ЗАМЕНИ
HOME_LON = 104.26000  # <-- ЗАМЕНИ

# --- ФУНКЦИИ ---

def get_weather(lat, lon):
    """Погода через Open-Meteo (бесплатно, без ключа)."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,precipitation_probability"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def get_route(start_lat, start_lon, end_lat, end_lon):
    """Маршрут через OSRM (бесплатно, без ключа)."""
    url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=false"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 'Ok':
                duration = data['routes'][0]['duration'] / 60
                distance = data['routes'][0]['distance'] / 1000
                return duration, distance
    except:
        pass
    return None, None

# --- ИНТЕРФЕЙС ---

st.set_page_config(page_title="Школьный Помощник", page_icon="🎒")
st.title("🎒 Школьный Помощник")
st.write(f"**{SCHOOL_NAME}** | Твой личный дашборд")

# Погода
st.header("☀️ Погода утром")
weather = get_weather(SCHOOL_LAT, SCHOOL_LON)
if weather:
    current = weather['current_weather']
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Температура", f"{current['temperature']}°C")
    with col2:
        st.metric("Ветер", f"{current['windspeed']} км/ч")
    with col3:
        st.metric("Направление", f"{current['winddirection']}°")
else:
    st.warning("Не удалось загрузить погоду. Проверь интернет.")

# Маршрут
st.header("🗺️ Дорога до школы")
duration, distance = get_route(HOME_LAT, HOME_LON, SCHOOL_LAT, SCHOOL_LON)
if duration:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("⏱ Время в пути", f"{duration:.0f} мин")
    with col2:
        st.metric("📏 Расстояние", f"{distance:.1f} км")
else:
    st.warning("Не удалось построить маршрут. Проверь координаты дома.")

# Ссылка на школу
st.divider()
st.markdown(f"🔗 [Сайт школы]({SCHOOL_URL})")
st.caption("Проект «Школьный Помощник». Streamlit + Open-Meteo + OSRM.")
