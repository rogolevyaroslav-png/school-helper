# scraper.py
# Парсер оценок из Сетевого Город (drzd.ru) — финальная версия

import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
        print("--- Обрабатываем предупреждение ---")
        time.sleep(3)

        warning_handled = False
        for attempt in range(1, 11):
            url_now = driver.current_url
            print(f"  Попытка {attempt}: URL = {url_now}")

            if "SecurityWarning" not in url_now:
                print("  ✅ Уже не на предупреждении")
                warning_handled = True
                break

            if attempt == 1:
                with open("debug_warning.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print("  💾 debug_warning.html сохранён")

            # === Ищем ссылку "Продолжить" ===
            clicked = False

            # Способ 1: найти <a> с текстом "Продолжить" и взять href
            try:
                links = driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    text = (link.text or "").strip()
                    if "Продолжить" in text or "Continue" in text:
                        href = link.get_attribute("href") or ""
                        print(f"  Найдена ссылка '{text}', href='{href}'")
                        if href and href.startswith("http") and "javascript" not in href:
                            print(f"  ✅ Переходим по href: {href}")
                            driver.get(href)
                            clicked = True
                            time.sleep(8)
                            break
                        else:
                            print("  ✅ Кликаем ссылку через JS")
                            driver.execute_script("arguments[0].click();", link)
                            clicked = True
                            time.sleep(8)
                            break
            except Exception as e:
                print(f"  Способ 1 ошибка: {e}")

            # Способ 2: input[value='Продолжить']
            if not clicked:
                try:
                    btn = driver.find_element(By.XPATH, "//input[@value='Продолжить']")
                    print("  ✅ Кликнули input через JS")
                    driver.execute_script("arguments[0].click();", btn)
                    clicked = True
                    time.sleep(8)
                except:
                    pass

            # Способ 3: любые элементы с текстом
            if not clicked:
                try:
                    elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Продолжить')]")
                    if elements:
                        print(f"  ✅ Кликнули элемент #{len(elements)} через JS")
                        driver.execute_script("arguments[0].click();", elements[0])
                        clicked = True
                        time.sleep(8)
                except:
                    pass

            # Способ 4: submit формы
            if not clicked:
                try:
                    forms = driver.find_elements(By.TAG_NAME, "form")
                    if forms:
                        print("  ✅ Отправили форму через JS")
                        driver.execute_script("arguments[0].submit();", forms[0])
                        clicked = True
                        time.sleep(8)
                except:
                    pass

            # Способ 5: Enter
            if not clicked:
                try:
                    body = driver.find_element(By.TAG_NAME, "body")
                    body.send_keys(Keys.ENTER)
                    print("  ✅ Нажали Enter")
                    time.sleep(5)
                except:
                    pass

            time.sleep(2)

        print(f"--- После предупреждения URL: {driver.current_url}")

        with open("debug_after_login.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"💾 debug_after_login.html")

        if "Неправильный пароль или логин" in driver.page_source:
            print("❌ ОШИБКА АВТОРИЗАЦИИ!")
            return

        # === ОТЧЁТЫ ===
           # === ИЩЕМ ОЦЕНКИ ЧЕРЕЗ МЕНЮ ===
        print("--- Ищем меню дневника ---")
        time.sleep(5)

        # Собираем все ссылки на странице для отладки
        all_links = driver.find_elements(By.TAG_NAME, "a")
        print(f"Всего ссылок на странице: {len(all_links)}")
        
        menu_links = []
        for link in all_links:
            try:
                text = (link.text or "").strip()
                href = link.get_attribute("href") or ""
                if text:
                    menu_links.append((text, href))
            except:
                continue
        
        print("=== ССЫЛКИ В МЕНЮ ===")
        for text, href in menu_links:
            print(f"  «{text}» → {href}")
        print("====================")

        # Ищем ссылку на отчёты
        print("--- Ищем 'Отчёты' / 'Успеваемость' ---")
        report_clicked = False
        
        keywords = ["отчёт", "отчет", "успеваем", "оценк", "итогов"]
        
        for link in all_links:
            try:
                text = (link.text or "").strip().lower()
                for kw in keywords:
                    if kw in text:
                        print(f"✅ Нашли ссылку: '{link.text}'. Кликаем...")
                        driver.execute_script("arguments[0].click();", link)
                        report_clicked = True
                        time.sleep(8)
                        break
                if report_clicked:
                    break
            except:
                continue

        if not report_clicked:
            print("⚠️ Ссылка на отчёты не найдена — пробуем прямой URL")

        # Сохраняем HTML после клика
        with open("debug_grades.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"💾 debug_grades.html | URL: {driver.current_url}")

        # Если попали на страницу отчётов — нужно найти кнопку "Сформировать" или похожую
        print("--- Ищем кнопку 'Сформировать' / 'Показать' ---")
        try:
            buttons = driver.find_elements(By.TAG_NAME, "button")
            buttons += driver.find_elements(By.TAG_NAME, "a")
            
            for btn in buttons:
                text = (btn.text or "").strip().lower()
                if "сформир" in text or "показат" in text or "построит" in text:
                    print(f"✅ Нашли кнопку: '{btn.text}'. Кликаем...")
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(10)
                    break
        except Exception as e:
            print(f"⚠️ Ошибка поиска кнопки: {e}")

        # Сохраняем итоговый HTML
        with open("debug_grades_final.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"💾 debug_grades_final.html | URL: {driver.current_url}")

        # === СОБИРАЕМ ОЦЕНКИ ===
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
