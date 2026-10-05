# app.py
# Проект: Школьный Помощник
# Школа: РЖД Лицей № 14, г. Иркутск

import streamlit as st
import requests
import datetime
import pandas as pd

# --- НАСТРОЙКИ ---
SCHOOL_NAME = "РЖД Лицей № 14, г. Иркутск"
SCHOOL_LAT = 52.28717
SCHOOL_LON = 104.25592
SCHOOL_URL = "https://licey-14.ru"

# Координаты дома (запасной вариант, если геолокация не сработает)
HOME_LAT = 52.29000
HOME_LON = 104.26000

# --- НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(
    page_title="Школьный Помощник",
    page_icon="🎒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- КРАСИВЫЙ CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    .main-header {
        text-align: center;
        padding: 2rem 1rem;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 24px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        margin-bottom: 2rem;
        animation: slideDown 0.6s ease-out;
    }
    
    .main-header h1 {
        font-size: 2.8rem;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .main-header p {
        color: #666;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    .card {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 20px;
        padding: 1.8rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin-bottom: 1rem;
        animation: fadeIn 0.6s ease-out;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
    }
    
    .card-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #333;
        margin-bottom: 1rem;
    }
    
    .metric-card {
        border-radius: 16px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        transition: transform 0.3s ease;
        margin-bottom: 1rem;
    }
    
    .metric-card:hover {
        transform: scale(1.05);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .metric-label {
        font-size: 0.95rem;
        opacity: 0.95;
        margin-top: 0.3rem;
    }
    
    .metric-blue { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    .metric-green { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
    .metric-orange { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
    .metric-purple { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: rgba(255, 255, 255, 0.15);
        padding: 0.5rem;
        border-radius: 16px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        color: white;
        font-size: 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #667eea !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    [data-testid="stMetricValue"] {
        color: #667eea;
        font-size: 2rem;
        font-weight: 800;
    }
    
    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- ФУНКЦИИ ---
def get_weather(lat, lon):
    """Погода через Open-Meteo (бесплатно, без ключа)."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None


def get_route(start_lat, start_lon, end_lat, end_lon):
    """Маршрут через OSRM (бесплатно, без ключа)."""
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


def get_location_by_ip():
    """Определяет примерную локацию по IP-адресу."""
    try:
        r = requests.get("http://ip-api.com/json/", timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get('status') == 'success':
                return {
                    'lat': data['lat'],
                    'lon': data['lon'],
                    'city': data.get('city', ''),
                    'region': data.get('regionName', '')
                }
    except:
        pass
    return None


def get_user_location():
    """
    Гибридное определение локации:
    1. Браузерная геолокация (точно)
    2. IP-адрес (примерно)
    3. Координаты из кода (запасной)
    """
    # Способ 1: браузер
    try:
        from streamlit_js_eval import get_geolocation
        loc = get_geolocation()
        if loc and 'coords' in loc:
            return {
                'lat': loc['coords']['latitude'],
                'lon': loc['coords']['longitude'],
                'source': '📍 Твоя геолокация (точно)'
            }
    except:
        pass
    
    # Способ 2: IP
    ip_loc = get_location_by_ip()
    if ip_loc:
        return {
            'lat': ip_loc['lat'],
            'lon': ip_loc['lon'],
            'source': f"📍 По IP: {ip_loc['city']}"
        }
    
    # Способ 3: запасной
    return {
        'lat': HOME_LAT,
        'lon': HOME_LON,
        'source': '📍 Координаты дома (по умолчанию)'
    }


# --- ЗАГОЛОВОК ---
st.markdown(f"""
<div class="main-header">
    <h1>🎒 Школьный Помощник</h1>
    <p>{SCHOOL_NAME}</p>
</div>
""", unsafe_allow_html=True)


# --- ВКЛАДКИ ---
tab1, tab2, tab3 = st.tabs(["🏠 Главная", "📊 Мои оценки", "📅 Расписание"])


# ============ ВКЛАДКА 1: ГЛАВНАЯ ============
with tab1:
    # === ПОГОДА ===
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">☀️ Погода утром</div>', unsafe_allow_html=True)
    
    weather = get_weather(SCHOOL_LAT, SCHOOL_LON)
    if weather:
        current = weather['current_weather']
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card metric-blue">
                <p class="metric-value">{current['temperature']}°C</p>
                <p class="metric-label">🌡 Температура</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card metric-green">
                <p class="metric-value">{current['windspeed']}</p>
                <p class="metric-label">💨 Ветер (км/ч)</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card metric-orange">
                <p class="metric-value">{current['winddirection']}°</p>
                <p class="metric-label">🧭 Направление</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("Не удалось загрузить погоду.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
      # === МАРШРУТ С ГЕОЛОКАЦИЕЙ ===
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🗺️ Дорога до школы</div>', unsafe_allow_html=True)
    
    # Кнопка "Определить моё местоположение"
    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn2:
        detect = st.button("📍 Определить", key="btn_detect_location")
    
    # Определяем локацию
    if detect:
        with st.spinner("Определяем твоё местоположение..."):
            user_loc = get_user_location()
        
        st.info(user_loc['source'])
        
        duration, distance = get_route(
            user_loc['lat'], user_loc['lon'],
            SCHOOL_LAT, SCHOOL_LON
        )
    else:
        st.caption("Нажми «Определить», чтобы построить маршрут от твоего текущего местоположения. Пока используется адрес из настроек.")
        duration, distance = get_route(HOME_LAT, HOME_LON, SCHOOL_LAT, SCHOOL_LON)
    
    if duration:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="metric-card metric-purple">
                <p class="metric-value">{duration:.0f} мин</p>
                <p class="metric-label">⏱ Время в пути</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card metric-orange">
                <p class="metric-value">{distance:.1f} км</p>
                <p class="metric-label">📏 Расстояние</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("Не удалось построить маршрут.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Кнопка "Определить моё местоположение"
    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn2:
        if st.button("📍 Определить", key="detect_location"):
            st.session_state.detect_location = True
    
    # Определяем локацию
    use_geolocation = st.session_state.get('detect_location', False)
    
    if use_geolocation:
        with st.spinner("Определяем твоё местоположение..."):
            user_loc = get_user_location()
        
        st.info(user_loc['source'])
        
        duration, distance = get_route(
            user_loc['lat'], user_loc['lon'],
            SCHOOL_LAT, SCHOOL_LON
        )
    else:
        st.caption("Нажми «Определить», чтобы построить маршрут от твоего текущего местоположения. Пока используется адрес из настроек.")
        duration, distance = get_route(HOME_LAT, HOME_LON, SCHOOL_LAT, SCHOOL_LON)
    
    if duration:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="metric-card metric-purple">
                <p class="metric-value">{duration:.0f} мин</p>
                <p class="metric-label">⏱ Время в пути</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card metric-orange">
                <p class="metric-value">{distance:.1f} км</p>
                <p class="metric-label">📏 Расстояние</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("Не удалось построить маршрут.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<p style="text-align:center;color:white;">🔗 <a href="{SCHOOL_URL}" target="_blank" style="color:white;">Сайт школы</a></p>',
        unsafe_allow_html=True
    )


# ============ ВКЛАДКА 2: МОИ ОЦЕНКИ ============
with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📊 Добавить оценку</div>', unsafe_allow_html=True)
    
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
            st.success(f"✅ Оценка {grade} по {subject} добавлена!")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if 'grades' in st.session_state and st.session_state.grades:
        df = pd.DataFrame(st.session_state.grades)
        df['date'] = pd.to_datetime(df['date'])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Статистика
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📈 Статистика</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card metric-purple">
                <p class="metric-value">{df['grade'].mean():.2f}</p>
                <p class="metric-label">⭐ Средний балл</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card metric-blue">
                <p class="metric-value">{len(df)}</p>
                <p class="metric-label">📝 Всего оценок</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            best = df.groupby('subject')['grade'].mean().idxmax()
            st.markdown(f"""
            <div class="metric-card metric-green">
                <p class="metric-value" style="font-size:1.5rem;">{best}</p>
                <p class="metric-label">🏆 Лучший предмет</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Графики
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📉 Динамика по предметам</div>', unsafe_allow_html=True)
        pivot = df.pivot_table(index='date', columns='subject', values='grade', aggfunc='mean')
        st.line_chart(pivot)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📋 Все оценки</div>', unsafe_allow_html=True)
        st.dataframe(df.sort_values('date', ascending=False), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("💡 Пока нет оценок. Добавь первую!")


# ============ ВКЛАДКА 3: РАСПИСАНИЕ ============
with tab3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📅 Моё расписание</div>', unsafe_allow_html=True)
    
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
    
    if 'schedule' not in st.session_state:
        st.session_state.schedule = {day: [] for day in days}
    
    selected_day = st.selectbox("Выбери день недели", days)
    
    with st.form("lesson_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            subject = st.text_input("Предмет", placeholder="Математика")
        with col2:
            time = st.text_input("Время", placeholder="08:30")
        with col3:
            room = st.text_input("Кабинет", placeholder="204")
        
        submitted = st.form_submit_button(f"➕ Добавить в {selected_day}")
        
        if submitted and subject:
            st.session_state.schedule[selected_day].append({
                'subject': subject, 'time': time, 'room': room
            })
            st.success(f"✅ {subject} добавлен")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Показ расписания
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📖 Твоё расписание</div>', unsafe_allow_html=True)
    
    for day in days:
        if st.session_state.schedule[day]:
            with st.expander(f"**{day}** — {len(st.session_state.schedule[day])} уроков", expanded=(day == selected_day)):
                for i, lesson in enumerate(st.session_state.schedule[day], 1):
                    st.write(f"**{i}.** 🕐 `{lesson['time']}` — **{lesson['subject']}** (каб. {lesson['room']})")
        else:
            st.write(f"📭 **{day}** — нет уроков")
    st.markdown('</div>', unsafe_allow_html=True)


# --- ФУТЕР ---
st.markdown("""
<div style="text-align:center; color:white; padding:2rem; opacity:0.8;">
    <p>Проект «Школьный Помощник» © 2026</p>
    <p style="font-size:0.85rem;">Streamlit + Open-Meteo + OSRM</p>
</div>
""", unsafe_allow_html=True)
