# scraper.py
# Парсер оценок из Сетевого Город (drzd.ru)
# Версия 3: с выбором региона, города и школы

import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

URL = "http://drzd.ru/"

# !!! ПРОВЕРЬ НАЗВАНИЯ — они должны ТОЧНО совпадать с текстом в списках !!!
REGION = "Иркутская обл"
MUNICIPALITY = "Городской округ Иркутск"
LOCALITY = "Иркутск, г."
SCHOOL = "РЖД лицей № 14"


def select_by_text(driver, element_id, text, wait_time=5):
    """Выбирает значение в выпадающем списке <select> по видимому тексту."""
    time.sleep(wait_time)  # ждём загрузки опций
    select_elem = Select(driver.find_element(By.ID, element_id))
    for option in select_elem.options:
        if text.lower() in option.text.lower():
            select_elem.select_by_visible_text(option.text)
            print(f"✅ Выбрано в #{element_id}: {option.text}")
            return True
    print(f"⚠️ Не найдено '{text}' в #{element_id}")
    print(f"   Доступные опции: {[o.text for o in select_elem.options][:10]}")
    return False


def main():
    login = os.environ.get("DNEVNIK_LOGIN")
    password = os.environ.get("DNEVNIK_PASSWORD")

    if not login or not password:
        print("❌ Ошибка: логин или пароль не найдены в секретах.")
        return

    print("Настраиваем браузер...")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 30)

    try:
        # 1. Открываем сайт
        print("Открываем сайт...")
        driver.get(URL)
        time.sleep(5)

        # 2. Выбираем РЕГИОН
        print("\n--- Выбираем регион ---")
        select_by_text(driver, "countries", "Россия", wait_time=2)
        select_by_text(driver, "states", REGION, wait_time=3)

        # 3. Выбираем МУНИЦИПАЛЬНЫЙ РАЙОН
        print("\n--- Выбираем городской округ ---")
        select_by_text(driver, "provinces", MUNICIPALITY, wait_time=5)

        # 4. Выбираем НАСЕЛЁННЫЙ ПУНКТ (если есть)
        print("\n--- Выбираем населённый пункт ---")
        try:
            select_by_text(driver, "cities", LOCALITY, wait_time=5)
        except Exception as e:
            print(f"⚠️ Поле 'cities' не найдено: {e}")

        # 5. Сохраняем HTML после выбора региона
        with open("debug_after_region.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("💾 Сохранён debug_after_region.html")

        # 6. Ищем поле организации (может быть select или input)
        print("\n--- Ищем поле организации ---")
        school_selected = False
        
        # Пробуем как select
        for sel_id in ["organizations", "schools", "organization"]:
            try:
                if select_by_text(driver, sel_id, SCHOOL, wait_time=5):
                    school_selected = True
                    break
            except:
                continue
        
        if not school_selected:
            print("⚠️ Не удалось выбрать школу автоматически")

        # 7. Вводим логин
        print("\n--- Вводим логин ---")
        login_field = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[placeholder='Логин']")
        ))
        login_field.clear()
        login_field.send_keys(login)
        time.sleep(1)
        print("✅ Логин введён")

        # 8. Вводим пароль
        print("--- Вводим пароль ---")
        password_field = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Пароль']")
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(1)
        print("✅ Пароль введён")

              # 9. Нажимаем "Войти"
        print("\n--- Нажимаем 'Войти' ---")
        submit_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Войти')]")
        submit_btn.click()
        time.sleep(8)

              # 9.1. Проверяем предупреждение о другом пользователе
        print("--- Проверяем предупреждение ---")
        time.sleep(3)
        
        warning_clicked = False
        # Пробуем разные способы найти кнопку "Продолжить"
        selectors = [
            (By.XPATH, "//input[@value='Продолжить']"),
            (By.XPATH, "//input[@value='Continue']"),
            (By.XPATH, "//button[contains(text(), 'Продолжить')]"),
            (By.XPATH, "//a[contains(text(), 'Продолжить')]"),
            (By.XPATH, "//*[contains(text(), 'Продолжить')]"),
        ]
        
        for by, sel in selectors:
            try:
                btn = driver.find_element(by, sel)
                btn.click()
                print(f"✅ Нажали 'Продолжить' ({sel})")
                warning_clicked = True
                time.sleep(8)
                break
            except:
                continue
        
        if not warning_clicked:
            print("✅ Предупреждения не было — продолжаем")
        
        # Делаем скриншот после нажатия
        with open("debug_after_warning.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("💾 Сохранён debug_after_warning.html")

        # 10. Сохраняем HTML после входа
        with open("debug_after_login.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("💾 Сохранён debug_after_login.html")

        # 11. Переходим к отчётам
        print("\n--- Переходим к отчётам ---")
        driver.get("http://drzd.ru/angular/school/reports/studenttotal")
        time.sleep(10)

        with open("debug_grades.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("💾 Сохранён debug_grades.html")
        print(f"URL страницы с оценками: {driver.current_url}")

        # 12. Парсим таблицы
        print("\n--- Собираем оценки ---")
        grades_data = []
        
        rows = driver.find_elements(By.CSS_SELECTOR, "tr")
        print(f"Всего строк <tr>: {len(rows)}")
        
        for row in rows:
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 2:
                    subject = cells[0].text.strip()
                    for cell in cells[1:]:
                        text = cell.text.strip()
                        if text and text.isdigit() and 2 <= int(text) <= 5:
                            if subject:
                                grades_data.append({
                                    "subject": subject,
                                    "grade": int(text),
                                    "date": ""
                                })
            except:
                continue

        if grades_data:
            df = pd.DataFrame(grades_data)
            df.to_csv("grades.csv", index=False, encoding="utf-8-sig")
            print(f"\n✅ Сохранено {len(grades_data)} оценок в grades.csv")
        else:
            print("\n❌ Оценки не найдены")

    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        try:
            with open("debug_error.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("💾 Сохранён debug_error.html")
        except:
            pass

    finally:
        print("Закрываем браузер...")
        driver.quit()


if __name__ == "__main__":
    main()
