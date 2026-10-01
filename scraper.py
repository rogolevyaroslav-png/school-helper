# scraper.py
# Этот скрипт запускается на GitHub Actions и обновляет файл grades.csv

import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def main():
    # 1. Получаем логин и пароль из "секретов" GitHub (мы настроим их позже)
    login = os.environ.get("DNEVNIK_LOGIN")
    password = os.environ.get("DNEVNIK_PASSWORD")

    if not login or not password:
        print("❌ Ошибка: логин или пароль не найдены в секретах.")
        return

    # 2. Настраиваем браузер для работы в фоне (headless)
    print("Настраиваем браузер...")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Работаем без открытия окна браузера
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # 3. Открываем сайт дневника и логинимся
        print("Открываем сайт дневника...")
        driver.get("https://drzd.ru") # !!! ПРОВЕРЬ URL !!!
        time.sleep(5)
        
        # !!! ЭТИ СЕЛЕКТОРЫ НУЖНО УТОЧНИТЬ !!!
        print("Вводим логин и пароль...")
        driver.find_element(By.NAME, "username").send_keys(login)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        print("Ждём загрузки страницы с оценками...")
        time.sleep(10)

        # 4. Собираем оценки (селекторы тоже нужно уточнить!)
        print("Собираем оценки...")
        grades_data = []
        # Найди правильные селекторы для своего дневника!
        rows = driver.find_elements(By.CSS_SELECTOR, ".grades-table tr")
        for row in rows:
            try:
                subject = row.find_element(By.CSS_SELECTOR, ".subject-cell").text
                grade = row.find_element(By.CSS_SELECTOR, ".grade-cell").text
                date = row.find_element(By.CSS_SELECTOR, ".date-cell").text
                if subject and grade:
                    grades_data.append({"subject": subject, "grade": int(grade), "date": date})
            except:
                continue

        # 5. Сохраняем данные в CSV-файл
        if grades_data:
            df = pd.DataFrame(grades_data)
            df.to_csv("grades.csv", index=False, encoding="utf-8-sig")
            print(f"✅ Успешно сохранено {len(grades_data)} оценок в grades.csv")
        else:
            print("❌ Не удалось найти оценки. Проверь селекторы.")

    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
