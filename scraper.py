# scraper.py
import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 20)

    try:
        print("Открываем сайт дневника...")
        driver.get("http://drzd.ru/")
        time.sleep(5)

        # Ищем поле логина — пробуем разные варианты
        print("Ищем поле логина...")
        login_field = None
        for by, value in [
            (By.CSS_SELECTOR, "input[placeholder='Логин']"),
            (By.CSS_SELECTOR, "input[type='text']"),
            (By.NAME, "username"),
            (By.NAME, "login"),
        ]:
            try:
                login_field = driver.find_element(by, value)
                print(f"✅ Поле логина найдено: {by} = {value}")
                break
            except:
                continue
        
        if not login_field:
            raise Exception("Не нашли поле логина")

        # Ищем поле пароля
        print("Ищем поле пароля...")
        password_field = None
        for by, value in [
            (By.CSS_SELECTOR, "input[placeholder='Пароль']"),
            (By.CSS_SELECTOR, "input[type='password']"),
            (By.NAME, "password"),
        ]:
            try:
                password_field = driver.find_element(by, value)
                print(f"✅ Поле пароля найдено: {by} = {value}")
                break
            except:
                continue
        
        if not password_field:
            raise Exception("Не нашли поле пароля")

        # Вводим данные
        print("Вводим логин и пароль...")
        login_field.clear()
        login_field.send_keys(login)
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(1)

        # Ищем кнопку "Войти"
        print("Ищем кнопку 'Войти'...")
        submit_button = None
        for by, value in [
            (By.XPATH, "//button[contains(text(), 'Войти')]"),
            (By.XPATH, "//*[contains(text(), 'Войти')]"),
            (By.CSS_SELECTOR, "button[type='submit']"),
        ]:
            try:
                submit_button = driver.find_element(by, value)
                print(f"✅ Кнопка найдена: {by} = {value}")
                break
            except:
                continue
        
        if not submit_button:
            raise Exception("Не нашли кнопку 'Войти'")

        submit_button.click()
        print("Нажали 'Войти'. Ждём загрузки...")
        time.sleep(10)

        # Переходим на страницу с оценками
        print("Переходим на страницу с оценками...")
        driver.get("http://drzd.ru/angular/school/reports/studenttotal")
        time.sleep(10)

        # Сохраняем HTML страницы в лог, чтобы понять структуру
        print("=" * 60)
        print("HTML СТРАНИЦЫ С ОЦЕНКАМИ (первые 5000 символов):")
        print("=" * 60)
        html = driver.page_source
        print(html[:5000])
        print("=" * 60)
        print(f"Всего символов в HTML: {len(html)}")

        # Пробуем найти таблицы
        print("\nИщем таблицы на странице...")
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"Найдено таблиц: {len(tables)}")
        
        for i, table in enumerate(tables):
            print(f"\n--- Таблица {i+1} ---")
            print(table.text[:500])

        # Пробуем собрать строки с оценками
        print("\nСобираем данные...")
        grades_data = []
        
        rows = driver.find_elements(By.CSS_SELECTOR, "tr")
        print(f"Найдено строк <tr>: {len(rows)}")
        
        for row in rows:
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 3:
                    subject = cells[0].text.strip()
                    grade_text = cells[1].text.strip()
                    date = cells[2].text.strip()
                    if grade_text.isdigit() and 2 <= int(grade_text) <= 5:
                        grades_data.append({
                            "subject": subject,
                            "grade": int(grade_text),
                            "date": date
                        })
            except:
                continue

        if grades_data:
            df = pd.DataFrame(grades_data)
            df.to_csv("grades.csv", index=False, encoding="utf-8-sig")
            print(f"\n✅ Сохранено {len(grades_data)} оценок в grades.csv")
        else:
            print("\n❌ Оценки не найдены. Смотри HTML выше.")

    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        # Сохраняем скриншот и HTML для отладки
        try:
            driver.save_screenshot("error_screenshot.png")
            with open("error_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("Сохранён скриншот и HTML для отладки")
        except:
            pass
    finally:
        print("Закрываем браузер...")
        driver.quit()

if __name__ == "__main__":
    main()
