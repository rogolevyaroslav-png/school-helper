# app.py
# Проект: Школьный Помощник

import streamlit as st
import requests
import datetime
import pandas as pd

# --- НАСТРОЙКИ ---
SCHOOL_NAME = "РЖД Лицей № 14, г. Иркутск"
SCHOOL_LAT = 52.28717
SCHOOL_LON = 104.25592
SCHOOL_URL = "https://licey-14.ru"

HOME_LAT = 52.29000
HOME_LON = 104.26000

# --- НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(
    page_title="Школьный Помощник",
    page_icon="🎒",
    layout="wide"
)

# --- ЭЛЕГАНТНЫЙ CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    /* Мягкий фон */
    .stApp {
        background: #f7f8fc;
    }
    
    .main .block-container {
        animation: fadeIn 0.5s ease-out;
        padding-top: 2rem;
        max-width: 1150px;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-12px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes scaleIn {
        from { opacity: 0; transform: scale(0.97); }
        to { opacity: 1; transform: scale(1); }
    }
    
    /* Заголовок */
    .main-header {
        background: white;
        padding: 2rem 2rem;
        border-radius: 16px;
        border: 1px solid #e8eaf0;
        box-shadow: 0 1px 3px rgba(16, 24, 40, 0.04);
        margin-bottom: 1.5rem;
        animation: slideIn 0.6s ease-out;
    }
    
    .main-header h1 {
        font-size: 1.75rem;
        font-weight: 700;
        color: #1a1f36;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .main-header p {
        color: #697386;
        font-size: 0.9rem;
        margin-top: 0.35rem;
    }
    
    /* Заголовки секций */
    .section-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #1a1f36;
        margin: 1.5rem 0 1rem 0;
        letter-spacing: -0.01em;
        animation: slideIn 0.5s ease-out;
    }
    
    /* Карточки */
    .stat-box {
        background: white;
        border: 1px solid #e8eaf0;
        border-radius: 12px;
        padding: 1.35rem 1.25rem;
        text-align: left;
        animation: scaleIn 0.5s ease-out;
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.03);
    }
    
    .stat-box:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(59, 91, 219, 0.08);
        border-color: #c7d0ff;
    }
    
    .stat-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #3b5bdb;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .stat-label {
        font-size: 0.78rem;
        color: #697386;
        margin-top: 0.4rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    
    /* Акцентная полоска сверху карточки */
    .stat-box::before {
        content: '';
        display: block;
        width: 32px;
        height: 3px;
        background: #3b5bdb;
        border-radius: 2px;
        margin-bottom: 0.9rem;
    }
    
    /* Вкладки */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem;
        background: white;
        padding: 0.35rem;
        border-radius: 10px;
        border: 1px solid #e8eaf0;
        animation: fadeIn 0.5s ease-out;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 7px;
        padding: 0.5rem 1.1rem;
        font-weight: 500;
        color: #697386;
        font-size: 0.9rem;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #3b5bdb;
        background: #f0f3ff;
    }
    
    .stTabs [aria-selected="true"] {
        background: #3b5bdb !important;
        color: white !important;
    }
    
    /* Кнопки */
    .stButton > button {
        background: #3b5bdb;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.55rem 1.35rem;
        font-weight: 500;
        font-size: 0.9rem;
        transition: all 0.25s ease;
        box-shadow: 0 1px 2px rgba(59, 91, 219, 0.2);
    }
    
    .stButton > button:hover {
        background: #2f4bc4;
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(59, 91, 219, 0.28);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Поля ввода */
    .stTextInput input,
    .stDateInput input,
    .stSelectbox div[data-baseweb="select"] > div {
        border-radius: 8px !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    
    .stTextInput input:focus,
    .stDateInput input:focus {
        border-color: #3b5bdb !important;
        box-shadow: 0 0 0 3px rgba(59, 91, 219, 0.12) !important;
    }
    
    /* Инфо-блоки */
    .stAlert {
        border-radius: 10px;
        border: 1px solid #e8eaf0;
    }
    
    /* Графики */
    .stLineChart {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid #e8eaf0;
    }
    
    /* Скрываем меню */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- ФУНКЦИИ ---
def get_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None


def get_route(start_lat, start_lon, end_lat, end_lon):
    url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=false"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data['code'] == 'Ok':
                duration = data['routes'][0]['duration'] / 60
                distance = data['routes'][0]['distance'] / 1000
                return duration, distance
    except:
        pass
    return None, None


def get_user_location():
    try:
        from streamlit_js_eval import get_geolocation
        loc = get_geolocation()
        if loc and 'coords' in loc and loc['coords']:
            return {
                'lat': loc['coords']['latitude'],
                'lon': loc['coords']['longitude'],
                'source': 'Точная геолокация'
            }
    except:
        pass
    return {
        'lat': HOME_LAT,
        'lon': HOME_LON,
        'source': 'Координаты дома (из настроек)'
    }


# --- ЗАГОЛОВОК ---
st.markdown(f"""
<div class="main-header">
    <h1>🎒 Школьный Помощник</h1>
    <p>{SCHOOL_NAME}</p>
</div>
""", unsafe_allow_html=True)


# --- ВКЛАДКИ ---
tab1, tab2, tab3 = st.tabs(["🏠 Главная", "📊 Оценки", "📅 Расписание"])


# ============ ВКЛАДКА 1: ГЛАВНАЯ ============
with tab1:
    st.markdown('<div class="section-title">☀️ Погода</div>', unsafe_allow_html=True)
    
    weather = get_weather(SCHOOL_LAT, SCHOOL_LON)
    if weather:
        current = weather['current_weather']
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="stat-box">
                <p class="stat-value">{current['temperature']}°C</p>
                <p class="stat-label">Температура</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stat-box">
                <p class="stat-value">{current['windspeed']}</p>
                <p class="stat-label">Ветер, км/ч</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="stat-box">
                <p class="stat-value">{current['winddirection']}°</p>
                <p class="stat-label">Направление</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("Не удалось загрузить погоду.")
    
    st.write("")
    st.markdown('<div class="section-title">🗺️ Дорога до школы</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([4, 1])
    with col2:
        detect = st.button("📍 Определить", key="btn_detect_location")
    
    if detect:
        with st.spinner("Определяем местоположение..."):
            user_loc = get_user_location()
        st.caption(f"Источник: {user_loc['source']}")
        duration, distance = get_route(user_loc['lat'], user_loc['lon'], SCHOOL_LAT, SCHOOL_LON)
    else:
        st.caption("Используются координаты дома из настроек. Нажми «📍 Определить» для точной геолокации.")
        duration, distance = get_route(HOME_LAT, HOME_LON, SCHOOL_LAT, SCHOOL_LON)
    
    if duration:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="stat-box">
                <p class="stat-value">{duration:.0f} мин</p>
                <p class="stat-label">Время в пути</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stat-box">
                <p class="stat-value">{distance:.1f} км</p>
                <p class="stat-label">Расстояние</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("Не удалось построить маршрут.")
    
    st.write("")
    st.markdown(f"🔗 [Сайт школы]({SCHOOL_URL})")


# ============ ВКЛАДКА 2: ОЦЕНКИ ============
with tab2:
    st.markdown('<div class="section-title">📝 Добавить оценку</div>', unsafe_allow_html=True)
    
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
        
        submitted = st.form_submit_button("Добавить")
        
        if submitted:
            if 'grades' not in st.session_state:
                st.session_state.grades = []
            st.session_state.grades.append({
                'subject': subject,
                'grade': grade,
                'date': str(date)
            })
            st.success(f"Оценка {grade} по предмету «{subject}» добавлена.")
    
    if 'grades' in st.session_state and st.session_state.grades:
        df = pd.DataFrame(st.session_state.grades)
        df['date'] = pd.to_datetime(df['date'])
        
        st.write("")
        st.markdown('<div class="section-title">📈 Статистика</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="stat-box">
                <p class="stat-value">{df['grade'].mean():.2f}</p>
                <p class="stat-label">Средний балл</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stat-box">
                <p class="stat-value">{len(df)}</p>
                <p class="stat-label">Всего оценок</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            best = df.groupby('subject')['grade'].mean().idxmax()
            st.markdown(f"""
            <div class="stat-box">
                <p class="stat-value" style="font-size:1.2rem;">{best}</p>
                <p class="stat-label">Лучший предмет</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.write("")
        st.markdown('<div class="section-title">📉 Динамика</div>', unsafe_allow_html=True)
        pivot = df.pivot_table(index='date', columns='subject', values='grade', aggfunc='mean')
        st.line_chart(pivot)
        
        st.write("")
        st.markdown('<div class="section-title">📋 Все оценки</div>', unsafe_allow_html=True)
        st.dataframe(df.sort_values('date', ascending=False), use_container_width=True)
    else:
        st.info("💡 Пока нет оценок. Добавь первую!")


# ============ ВКЛАДКА 3: РАСПИСАНИЕ ============
with tab3:
    st.markdown('<div class="section-title">📅 Моё расписание</div>', unsafe_allow_html=True)
    
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
    
    if 'schedule' not in st.session_state:
        st.session_state.schedule = {day: [] for day in days}
    
    selected_day = st.selectbox("День недели", days)
    
    with st.form("lesson_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            subject = st.text_input("Предмет", placeholder="Математика")
        with col2:
            time = st.text_input("Время", placeholder="08:30")
        with col3:
            room = st.text_input("Кабинет", placeholder="204")
        
        submitted = st.form_submit_button("Добавить")
        
        if submitted and subject:
            st.session_state.schedule[selected_day].append({
                'subject': subject, 'time': time, 'room': room
            })
            st.success(f"Добавлено: {subject}")
    
    st.write("")
    st.markdown('<div class="section-title">📖 Текущее расписание</div>', unsafe_allow_html=True)
    
    for day in days:
        if st.session_state.schedule[day]:
            with st.expander(f"**{day}** — {len(st.session_state.schedule[day])} уроков", expanded=(day == selected_day)):
                for i, lesson in enumerate(st.session_state.schedule[day], 1):
                    st.write(f"**{i}.** 🕐 `{lesson['time']}` — **{lesson['subject']}** (каб. {lesson['room']})")
        else:
            st.write(f"📭 **{day}** — нет уроков")


# --- ФУТЕР ---
st.markdown("---")
st.caption("Школьный Помощник · Streamlit + Open-Meteo + OSRM")
