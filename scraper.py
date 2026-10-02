# scraper.py
# Парсер оценок из Сетевого Город (drzd.ru) — финальная версия

import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def main():
    login = os.environ.get("DNEVNIK_LOGIN")
    password = os.environ.get("DNEVNIK_PASSWORD")

    if not login or not password:
        print("❌ Ошибка: логин или пароль не найдены.")
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
        driver.get("http://drzd.ru/")
        time.sleep(5)

        # 2. Ищем поля логина и пароля ВНУТРИ блока школы
        print("Ищем поля ввода...")
        form_block = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".box-form.visible")
        ))
        
        login_field = form_block.find_element(By.NAME, "UN")
        password_field = form_block.find_element(By.NAME, "PW")
        print("✅ Поля найдены")

        # 3. Вводим данные
        print("Вводим логин и пароль...")
        login_field.clear()
        login_field.send_keys(login)
        time.sleep(1)
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(1)

        # 4. Нажимаем кнопку "Войти"
        print("Нажимаем 'Войти'...")
        submit_btn = form_block.find_element(By.CSS_SELECTOR, ".button-login-marker")
        submit_btn.click()
        time.sleep(8)

        # 5. Обрабатываем предупреждение "Продолжить"
        print("Проверяем предупреждение...")
        try:
            continue_btn = driver.find_element(By.XPATH, "//input[@value='Продолжить']")
            print("⚠️ Нашли предупреждение. Нажимаем 'Продолжить'...")
            continue_btn.click()
            time.sleep(8)
        except:
            print("✅ Предупреждения нет")

        # 6. Сохраняем HTML после входа
        with open("debug_after_login.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"💾 debug_after_login.html | URL: {driver.current_url}")

        # 7. Переходим к оценкам
        print("Переходим к отчётам...")
        driver.get("http://drzd.ru/angular/school/reports/studenttotal")
        time.sleep(12)

        with open("debug_grades.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"💾 debug_grades.html | URL: {driver.current_url}")

        # 8. Парсим оценки
        print("Собираем оценки...")
        grades_data = []
        
        selectors = [
            ".table-print tr",
            "table tr",
            ".report-table tr",
            "tbody tr",
        ]
        
        all_rows = []
        for sel in selectors:
            rows = driver.find_elements(By.CSS_SELECTOR, sel)
            if len(rows) > len(all_rows):
                all_rows = rows
                print(f"Селектор {sel}: {len(rows)} строк")
        
        print(f"Всего строк: {len(all_rows)}")

        for row in all_rows:
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
