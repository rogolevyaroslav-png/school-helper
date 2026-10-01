# app.py
# Проект: Школьный Помощник
# Школа: РЖД Лицей № 14, г. Иркутск

import streamlit as st
import requests
import datetime
import pandas as pd
import json

# --- НАСТРОЙКИ ---
SCHOOL_NAME = "РЖД Лицей № 14, г. Иркутск"
SCHOOL_LAT = 52.28717
SCHOOL_LON = 104.25592
SCHOOL_URL = "https://licey-14.ru"

HOME_LAT = 52.29000   # <-- ЗАМЕНИ НА СВОИ
HOME_LON = 104.26000  # <-- ЗАМЕНИ НА СВОИ

# --- ФУНКЦИИ ---

def get_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def get_route(start_lat, start_lon, end_lat, end_lon):
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

# --- ВКЛАДКИ ---
tab1, tab2, tab3 = st.tabs(["🏠 Главная", "📊 Мои оценки", "🤖 Аналитика"])

# ============ ВКЛАДКА 1: ГЛАВНАЯ ============
with tab1:
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
        st.warning("Не удалось загрузить погоду.")
    
    st.header("🗺️ Дорога до школы")
    duration, distance = get_route(HOME_LAT, HOME_LON, SCHOOL_LAT, SCHOOL_LON)
    if duration:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("⏱ Время в пути", f"{duration:.0f} мин")
        with col2:
            st.metric("📏 Расстояние", f"{distance:.1f} км")
    else:
        st.warning("Не удалось построить маршрут.")
    
    st.divider()
    st.markdown(f"🔗 [Сайт школы]({SCHOOL_URL})")

# ============ ВКЛАДКА 2: МОИ ОЦЕНКИ ============
with tab2:
    st.header("📊 Мои оценки")
    st.write("Внеси свои оценки — система построит график прогресса.")
    
    # Форма ввода
    with st.form("grade_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            subject = st.selectbox("Предмет", [
                "Математика", "Русский язык", "Физика", "Химия", 
                "История", "Биология", "География", "Английский", 
                "Информатика", "Литература"
            ])
        with col2:
            grade = st.slider("Оценка", 2, 5, 4)
        with col3:
            date = st.date_input("Дата", datetime.date.today())
        
        submitted = st.form_submit_button("➕ Добавить оценку")
        
        if submitted:
            if 'grades' not in st.session_state:
                st.session_state.grades = []
            st.session_state.grades.append({
                'subject': subject,
                'grade': grade,
                'date': str(date)
            })
            st.success(f"Оценка {grade} по {subject} добавлена!")
    
    # Показ оценок
    if 'grades' in st.session_state and st.session_state.grades:
        df = pd.DataFrame(st.session_state.grades)
        st.dataframe(df, use_container_width=True)
        
        # График
        st.subheader("📈 График по предметам")
        pivot = df.pivot_table(index='date', columns='subject', values='grade', aggfunc='mean')
        st.line_chart(pivot)
        
        # Скачать данные
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "💾 Скачать мои оценки (CSV)",
            csv,
            "my_grades.csv",
            "text/csv"
        )
    else:
        st.info("Пока нет оценок. Добавь первую!")

# ============ ВКЛАДКА 3: АНАЛИТИКА ============
with tab3:
    st.header("🤖 Аналитика через ИИ")
    st.write("Здесь будет MAML — модель, которая предсказывает твои будущие оценки.")
    
    if 'grades' in st.session_state and len(st.session_state.grades) >= 5:
        st.success("✅ Данных достаточно для анализа!")
        st.write("Следующий шаг: подключим MAML.")
        
        # Простая статистика пока без MAML
        df = pd.DataFrame(st.session_state.grades)
        st.subheader("📊 Твоя статистика")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Средний балл", f"{df['grade'].mean():.2f}")
        with col2:
            st.metric("Всего оценок", len(df))
        with col3:
            best_subject = df.groupby('subject')['grade'].mean().idxmax()
            st.metric("Лучший предмет", best_subject)
        
        # Прогноз (заглушка)
        st.subheader("🔮 Прогноз")
        st.info("После подключения MAML здесь появится прогноз твоих оценок на следующий месяц.")
    else:
        st.warning("Добавь хотя бы 5 оценок во вкладке 'Мои оценки', чтобы увидеть аналитику.")

st.divider()
st.caption("Проект «Школьный Помощник». Streamlit + Open-Meteo + OSRM.")
