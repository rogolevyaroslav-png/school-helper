# scraper.py
# Этот скрипт запускается на GitHub Actions и обновляет файл grades.csv

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
    # 1. Получаем логин и пароль из "секретов" GitHub
    login = os.environ.get("DNEVNIK_LOGIN")
    password = os.environ.get("DNEVNIK_PASSWORD")

    if not login or not password:
        print("❌ Ошибка: логин или пароль не найдены в секретах.")
        return

    # 2. Настраиваем браузер
    print("Настраиваем браузер...")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 20) # Будем ждать до 20 секунд

    try:
        # 3. Открываем сайт дневника
        print("Открываем сайт дневника...")
        driver.get("http://drzd.ru/") # Используем корневой URL
        time.sleep(5)
        
        # 4. Ищем поля для входа (пробуем разные варианты)
        print("Ищем поля для ввода логина и пароля...")
        
        # Сначала попробуем найти поле логина по общим атрибутам
        login_field = None
        for by, value in [(By.NAME, "username"), (By.NAME, "login"), (By.ID, "login"), (By.CSS_SELECTOR, "input[type='text']")]:
            try:
                login_field = wait.until(EC.presence_of_element_located((by, value)))
                print(f"✅ Нашли поле логина: {by}={value}")
                break
            except:
                continue
        
        if not login_field:
            raise Exception("Не удалось найти поле для логина")

        # То же для пароля
        password_field = None
        for by, value in [(By.NAME, "password"), (By.ID, "password"), (By.CSS_SELECTOR, "input[type='password']")]:
            try:
                password_field = driver.find_element(by, value)
                print(f"✅ Нашли поле пароля: {by}={value}")
                break
            except:
                continue
        
        if not password_field:
            raise Exception("Не удалось найти поле для пароля")

        # 5. Вводим данные и логинимся
        print("Вводим данные для входа...")
        login_field.send_keys(login)
        password_field.send_keys(password)
        
        # Ищем кнопку входа
        submit_button = None
        for by, value in [(By.CSS_SELECTOR, "button[type='submit']"), (By.CSS_SELECTOR, "input[type='submit']"), (By.XPATH, "//button[contains(text(), 'Войти')]")]:
            try:
                submit_button = driver.find_element(by, value)
                print(f"✅ Нашли кнопку входа: {by}={value}")
                break
            except:
                continue
        
        if not submit_button:
            raise Exception("Не удалось найти кнопку для входа")

        submit_button.click()
        
        print("Ждём загрузки страницы с оценками...")
        time.sleep(10) # Даём время на загрузку

        # 6. Собираем оценки (селекторы нужно будет уточнить после скриншота!)
        print("Собираем оценки...")
        grades_data = []
        
        # Пытаемся найти таблицу с оценками
        # Это заглушка, точные селекторы мы определим позже
        try:
            # Ищем все строки таблицы
            rows = driver.find_elements(By.CSS_SELECTOR, "table tr")
            print(f"Найдено строк в таблицах: {len(rows)}")
            
            for row in rows:
                try:
                    # Пытаемся извлечь данные из ячеек
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 3:
                        # Предполагаем, что первые три ячейки - это предмет, оценка, дата
                        subject = cells[0].text
                        grade_text = cells[1].text
                        date = cells[2].text
                        
                        # Проверяем, является ли оценка числом
                        if grade_text.strip().isdigit():
                            grades_data.append({
                                "subject": subject,
                                "grade": int(grade_text),
                                "date": date
                            })
                except:
                    continue
        except Exception as e:
            print(f"Ошибка при парсинге таблицы: {e}")

        # 7. Сохраняем данные в CSV
        if grades_data:
            df = pd.DataFrame(grades_data)
            df.to_csv("grades.csv", index=False, encoding="utf-8-sig")
            print(f"✅ Успешно сохранено {len(grades_data)} оценок в grades.csv")
        else:
            print("❌ Не удалось найти оценки. Проверь селекторы.")

    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
    finally:
        print("Закрываем браузер...")
        driver.quit()

if __name__ == "__main__":
    main()
