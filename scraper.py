# scraper.py
# Парсер оценок из Сетевой Город (drzd.ru)
# Запускается на GitHub Actions

import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- НАСТРОЙКИ ---
URL = "http://drzd.ru/"
SCHOOL_NAME = "РЖД лицей №14"

def main():
    # 1. Получаем логин и пароль из секретов GitHub
    login = os.environ.get("DNEVNIK_LOGIN")
    password = os.environ.get("DNEVNIK_PASSWORD")

    if not login or not password:
        print("❌ Ошибка: логин или пароль не найдены в секретах.")
        return

    # 2. Настраиваем браузер для работы на сервере GitHub
    print("Настраиваем браузер...")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-gpu')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)

    try:
        # 3. Открываем сайт
        print("Открываем сайт дневника...")
        driver.get(URL)
        time.sleep(3)

        # 4. Нажимаем красную кнопку (выбор организации)
        print("Нажимаем на кнопку выбора организации...")
        try:
            red_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn.red')))
            red_btn.click()
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ Красная кнопка не найдена: {e}")

        # 5. Выбираем организацию
        print(f"Выбираем организацию: {SCHOOL_NAME}...")
        try:
            # Открываем выпадающий список
            dropdown = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '.select2-selection.select2-selection--single')
            ))
            dropdown.click()
            time.sleep(1)
            
            # Вводим название школы
            search_field = driver.find_element(By.CLASS_NAME, 'select2-search__field')
            search_field.send_keys(SCHOOL_NAME)
            time.sleep(2)
            
            # Кликаем на найденную школу
            org = driver.find_element(By.CLASS_NAME, 'org-name-data')
            org.click()
            time.sleep(1)
            print("✅ Организация выбрана")
        except Exception as e:
            print(f"⚠️ Не удалось выбрать организацию: {e}")

        # 6. Вводим логин
        print("Вводим логин...")
        login_field = wait.until(EC.presence_of_element_located((By.NAME, 'loginname')))
        login_field.clear()
        login_field.send_keys(login)
        time.sleep(1)

        # 7. Вводим пароль
        print("Вводим пароль...")
        password_field = driver.find_element(By.NAME, 'password')
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(1)

        # 8. Нажимаем кнопку "Войти"
        print("Нажимаем 'Войти'...")
        submit_btn = driver.find_element(By.CLASS_NAME, 'primary-button')
        submit_btn.click()
        time.sleep(5)

        # 9. Проверяем, что вошли (если уже был вход — выходим)
        try:
            driver.find_element(By.CLASS_NAME, 'icon-signout').click()
            print("Сессия была активна — вышли, чтобы войти заново")
            time.sleep(3)
        except:
            pass

        # 10. Переходим в отчёты
        print("Переходим в отчёты...")
        nav = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.nav.navbar-nav')
        ))
        links = nav.find_elements(By.TAG_NAME, 'a')
        if len(links) > 6:
            links[6].click()
            time.sleep(3)
        
        # 11. Выбираем отчёт со всеми оценками
        print("Выбираем отчёт с оценками...")
        report_links = driver.find_elements(By.CLASS_NAME, 'ng-binding')
        if len(report_links) > 7:
            report_links[7].click()
            time.sleep(3)

        # 12. Нажимаем "Сформировать"
        print("Нажимаем 'Сформировать'...")
        try:
            form_btn = driver.find_element(By.CSS_SELECTOR, '.btn-default')
            form_btn.click()
            time.sleep(5)
        except Exception as e:
            print(f"⚠️ Кнопка 'Сформировать' не найдена: {e}")

        # 13. Собираем оценки из таблицы
        print("Собираем оценки...")
        grades_data = []
        
        try:
            table_rows = driver.find_element(By.CLASS_NAME, 'table-print').find_elements(By.TAG_NAME, 'tr')
            cell_texts = driver.find_elements(By.CLASS_NAME, 'cell-text')
            
            n = 0
            for row in table_rows[2:]:  # Пропускаем 2 строки заголовков
                tds = row.find_elements(By.TAG_NAME, 'td')
                subject = ""
                grades_row = []
                
                for idx, td in enumerate(tds):
                    text = td.text.strip()
                    if idx == 0:
                        subject = text
                    elif text:
                        grades_row.append(text)
                
                if subject and n < len(cell_texts):
                    subject_name = cell_texts[n].text.strip() if n < len(cell_texts) else subject
                    grades_str = " ".join(grades_row)
                    print(f"{subject_name}: {grades_str}")
                    
                    # Извлекаем последнюю оценку (число 2-5)
                    for g in grades_row:
                        if g.strip().isdigit() and 2 <= int(g.strip()) <= 5:
                            grades_data.append({
                                "subject": subject_name,
                                "grade": int(g.strip()),
                                "date": ""
                            })
                    n += 1
        except Exception as e:
            print(f"⚠️ Ошибка при парсинге таблицы: {e}")

        # 14. Сохраняем в CSV
        if grades_data:
            df = pd.DataFrame(grades_data)
            df.to_csv("grades.csv", index=False, encoding="utf-8-sig")
            print(f"\n✅ Сохранено {len(grades_data)} оценок в grades.csv")
        else:
            print("\n❌ Оценки не найдены")
            # Сохраняем HTML для отладки
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("Сохранён debug_page.html для отладки")

    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        try:
            driver.save_screenshot("error_screenshot.png")
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("Сохранены скриншот и HTML для отладки")
        except:
            pass

    finally:
        print("Закрываем браузер...")
        driver.quit()


if __name__ == "__main__":
    main()
