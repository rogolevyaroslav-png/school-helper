# scraper.py
# Парсер оценок из Сетевого Город (drzd.ru)

import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "http://drzd.ru/"
SCHOOL_NAME = "РЖД лицей"

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

        # 2. Сохраняем HTML главной страницы для отладки
        with open("debug_main.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("💾 Сохранён debug_main.html")

        # 3. Ищем поле Логин по placeholder
        print("Ищем поле логина...")
        login_field = None
        selectors_login = [
            (By.CSS_SELECTOR, "input[placeholder='Логин']"),
            (By.CSS_SELECTOR, "input[placeholder='Login']"),
            (By.CSS_SELECTOR, "input[ng-model*='login']"),
            (By.CSS_SELECTOR, "input[name='loginname']"),
            (By.CSS_SELECTOR, "input[name='username']"),
            (By.CSS_SELECTOR, "input[type='text']"),
        ]
        for by, sel in selectors_login:
            try:
                login_field = driver.find_element(by, sel)
                print(f"✅ Поле логина найдено: {sel}")
                break
            except:
                continue
        
        if not login_field:
            raise Exception("Не нашли поле логина")

        # 4. Ищем поле Пароль
        print("Ищем поле пароля...")
        password_field = None
        selectors_pass = [
            (By.CSS_SELECTOR, "input[placeholder='Пароль']"),
            (By.CSS_SELECTOR, "input[type='password']"),
            (By.CSS_SELECTOR, "input[name='password']"),
        ]
        for by, sel in selectors_pass:
            try:
                password_field = driver.find_element(by, sel)
                print(f"✅ Поле пароля найдено: {sel}")
                break
            except:
                continue
        
        if not password_field:
            raise Exception("Не нашли поле пароля")

        # 5. Вводим данные
        print("Вводим логин и пароль...")
        login_field.clear()
        login_field.send_keys(login)
        time.sleep(1)
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(1)

        # 6. Ищем кнопку "Войти"
        print("Ищем кнопку 'Войти'...")
        submit_btn = None
        selectors_btn = [
            (By.XPATH, "//button[contains(text(), 'Войти')]"),
            (By.XPATH, "//*[contains(text(), 'Войти')]"),
            (By.CSS_SELECTOR, "button.primary-button"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.CSS_SELECTOR, ".btn-primary"),
        ]
        for by, sel in selectors_btn:
            try:
                submit_btn = driver.find_element(by, sel)
                print(f"✅ Кнопка найдена: {sel}")
                break
            except:
                continue

        if not submit_btn:
            raise Exception("Не нашли кнопку 'Войти'")

        submit_btn.click()
        print("Нажали 'Войти'. Ждём загрузки (15 сек)...")
        time.sleep(15)

        # 7. Сохраняем HTML после входа
        with open("debug_after_login.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("💾 Сохранён debug_after_login.html")

        print(f"Текущий URL: {driver.current_url}")

        # 8. Переходим на страницу с отчётами
        print("Переходим к отчётам...")
        driver.get("http://drzd.ru/angular/school/reports/studenttotal")
        time.sleep(10)

        # 9. Сохраняем HTML страницы с оценками
        with open("debug_grades.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("💾 Сохранён debug_grades.html")

        # 10. Пробуем найти таблицы
        print("Ищем таблицы на странице...")
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"Найдено таблиц: {len(tables)}")
        
        for i, table in enumerate(tables):
            rows = table.find_elements(By.TAG_NAME, "tr")
            print(f"Таблица {i+1}: {len(rows)} строк")

        # 11. Пробуем собрать данные
        print("Собираем оценки...")
        grades_data = []
        
        all_rows = driver.find_elements(By.CSS_SELECTOR, "tr")
        print(f"Всего строк <tr>: {len(all_rows)}")
        
        for row in all_rows:
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 2:
                    subject = cells[0].text.strip()
                    # Ищем оценки в остальных ячейках
                    grades_in_row = []
                    for cell in cells[1:]:
                        text = cell.text.strip()
                        if text and text.isdigit() and 2 <= int(text) <= 5:
                            grades_in_row.append(int(text))
                    
                    if subject and grades_in_row:
                        for g in grades_in_row:
                            grades_data.append({
                                "subject": subject,
                                "grade": g,
                                "date": ""
                            })
            except:
                continue

        if grades_data:
            df = pd.DataFrame(grades_data)
            df.to_csv("grades.csv", index=False, encoding="utf-8-sig")
            print(f"\n✅ Сохранено {len(grades_data)} оценок в grades.csv")
        else:
            print("\n❌ Оценки не найдены. Смотри debug_grades.html")

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
