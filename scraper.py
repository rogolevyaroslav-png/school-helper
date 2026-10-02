# scraper.py
# Парсер оценок из Сетевого Город (drzd.ru) — финальная версия

import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def select_by_js(driver, select_id, value):
    js = f"""
    var $sel = jQuery('#{select_id}');
    $sel.val('{value}');
    $sel.trigger('change');
    """
    driver.execute_script(js)
    print(f"✅ #{select_id} = {value}")


def main():
    login = os.environ.get("DNEVNIK_LOGIN", "").strip()
    password = os.environ.get("DNEVNIK_PASSWORD", "").strip()

    if not login or not password:
        print("❌ Ошибка: логин или пароль не найдены.")
        return

    print(f"Логин: {login[:3]}***")

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 30)

    try:
        print("Открываем сайт...")
        driver.get("http://drzd.ru/")
        time.sleep(5)

        print("--- Выбираем регион/город/школу ---")
        time.sleep(3)
        select_by_js(driver, "states", "38")
        time.sleep(3)
        select_by_js(driver, "provinces", "-19")
        time.sleep(4)
        select_by_js(driver, "cities", "19")
        time.sleep(3)
        select_by_js(driver, "schools", "3")
        time.sleep(3)

        with open("debug_after_region.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("💾 debug_after_region.html")

        print("--- Вводим логин/пароль ---")
        form_block = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".box-form.visible")
        ))
        login_field = form_block.find_element(By.NAME, "UN")
        password_field = form_block.find_element(By.NAME, "PW")
        login_field.clear()
        login_field.send_keys(login)
        time.sleep(1)
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(1)
        print("✅ Данные введены")

        print("--- Нажимаем 'Войти' ---")
        submit_btn = form_block.find_element(By.CSS_SELECTOR, ".button-login-marker")
        submit_btn.click()
        time.sleep(10)

        # === ОБРАБОТКА ПРЕДУПРЕЖДЕНИЯ ===
        print("--- Ждём появления предупреждения (5 сек) ---")
        time.sleep(5)

        warning_handled = False
        for attempt in range(1, 11):  # 10 попыток по 2 секунды = 20 секунд
            print(f"  Попытка {attempt}: проверяем URL и кнопки...")
            current_url = driver.current_url
            print(f"  URL: {current_url}")

            # Если URL содержит SecurityWarning — значит мы на странице предупреждения
            if "SecurityWarning" in current_url or "securityWarning" in current_url.lower():
                print("  ⚠️ Обнаружена страница предупреждения!")
                
                # Пробуем найти кнопку "Продолжить"
                try:
                    continue_btn = driver.find_element(
                        By.XPATH, "//input[@value='Продолжить']"
                    )
                    print("  ✅ Нашли 'Продолжить'. Нажимаем...")
                    continue_btn.click()
                    warning_handled = True
                    time.sleep(10)
                    print(f"  ✅ После нажатия URL: {driver.current_url}")
                    break
                except:
                    pass

                # Если не нашли — пробуем "Выход"
                try:
                    exit_btn = driver.find_element(
                        By.XPATH, "//input[@value='Выход']"
                    )
                    print("  ⚠️ 'Продолжить' не нашли, нажимаем 'Выход'...")
                    exit_btn.click()
                    warning_handled = True
                    time.sleep(10)
                    # После "Выход" нужно залогиниться заново
                    print("  Повторный логин...")
                    form_block = wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".box-form.visible")
                    ))
                    login_field = form_block.find_element(By.NAME, "UN")
                    password_field = form_block.find_element(By.NAME, "PW")
                    login_field.clear()
                    login_field.send_keys(login)
                    password_field.clear()
                    password_field.send_keys(password)
                    submit_btn = form_block.find_element(By.CSS_SELECTOR, ".button-login-marker")
                    submit_btn.click()
                    time.sleep(10)
                    break
                except:
                    pass

            # Если URL не похож на предупреждение — возможно, мы уже вошли
            if "SecurityWarning" not in current_url and "about" not in current_url:
                print("  ✅ Похоже, мы уже вошли. Идём дальше.")
                warning_handled = True
                break

            time.sleep(2)

        if not warning_handled:
            print("⚠️ Предупреждение не обнаружено — возможно, всё в порядке")

        # Сохраняем HTML после входа
        with open("debug_after_login.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"💾 debug_after_login.html | URL: {driver.current_url}")

        # Проверяем на ошибку авторизации
        if "Неправильный пароль или логин" in driver.page_source:
            print("❌ ОШИБКА АВТОРИЗАЦИИ!")
            return

        # === ИЩЕМ ССЫЛКИ В МЕНЮ ===
        print("--- Ищем меню дневника ---")
        time.sleep(5)

        # Сначала попробуем прямой URL
        print("Пробуем прямой URL отчётов...")
        driver.get("http://drzd.ru/angular/school/reports/studenttotal")
        time.sleep(10)

        with open("debug_grades.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"💾 debug_grades.html | URL: {driver.current_url}")

        # Собираем оценки
        print("--- Собираем оценки ---")
        grades_data = []

        selectors = [".table-print tr", "table tr", ".report-table tr", "tbody tr"]
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
            print("\n❌ Оценки не найдены")

    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        try:
            with open("debug_error.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
        except:
            pass
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
