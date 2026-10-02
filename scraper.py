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

        for attempt in range(1, 11):
            url_now = driver.current_url
            print(f"  Попытка {attempt}: URL = {url_now}")

            if "SecurityWarning" not in url_now:
                print("  ✅ Уже не на предупреждении")
                break

            if attempt == 1:
                with open("debug_warning.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print("  💾 debug_warning.html сохранён")

            clicked = False

            try:
                links = driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    text = (link.text or "").strip()
                    if "Продолжить" in text or "Continue" in text:
                        href = link.get_attribute("href") or ""
                        print(f"  Найдена ссылка '{text}', href='{href}'")
                        if href and href.startswith("http") and "javascript" not in href:
                            driver.get(href)
                            clicked = True
                            time.sleep(8)
                            break
                        else:
                            driver.execute_script("arguments[0].click();", link)
                            clicked = True
                            time.sleep(8)
                            break
            except:
                pass

            if not clicked:
                try:
                    btn = driver.find_element(By.XPATH, "//input[@value='Продолжить']")
                    driver.execute_script("arguments[0].click();", btn)
                    clicked = True
                    time.sleep(8)
                except:
                    pass

            if not clicked:
                try:
                    elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Продолжить')]")
                    if elements:
                        driver.execute_script("arguments[0].click();", elements[0])
                        clicked = True
                        time.sleep(8)
                except:
                    pass

            if not clicked:
                try:
                    body = driver.find_element(By.TAG_NAME, "body")
                    body.send_keys(Keys.ENTER)
                    time.sleep(5)
                except:
                    pass

            time.sleep(2)

        print(f"--- После предупреждения URL: {driver.current_url}")

        with open("debug_after_login.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        if "Неправильный пароль или логин" in driver.page_source:
            print("❌ ОШИБКА АВТОРИЗАЦИИ!")
            return

            # === РАБОТА С ОТЧЁТАМИ ===
        print("--- Мы в /reports/, ищем конкретный отчёт ---")
        time.sleep(10)

        with open("debug_reports_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("💾 debug_reports_page.html сохранён")

        # Собираем все ссылки для отладки
        report_links = driver.find_elements(By.TAG_NAME, "a")
        print(f"Всего ссылок на /reports/: {len(report_links)}")
        for link in report_links:
            try:
                text = (link.text or "").strip()
                href = link.get_attribute("href") or ""
                onclick = link.get_attribute("onclick") or ""
                if text:
                    print(f"  «{text}» | href={href} | onclick={onclick[:60]}")
            except:
                continue

        # Смотрим таблицы
        print("--- Таблицы на странице /reports/ ---")
        tables = driver.find_elements(By.CSS_SELECTOR, "table")
        for i, table in enumerate(tables):
            print(f"Таблица {i+1}:")
            rows = table.find_elements(By.TAG_NAME, "tr")
            for j, row in enumerate(rows):
                row_text = row.text.strip()
                if row_text:
                    print(f"  [{j}] {row_text[:180]}")

        # Ищем отчёт «Успеваемость»
        print("--- Ищем 'Успеваемость' / 'Итоговые' ---")
        report_opened = False
        report_kw = ["успеваемост", "итогов", "оценк", "табель", "сводн", "четверт", "текущ"]

        # Способ 1: клик по ссылке
        for link in report_links:
            try:
                text = (link.text or "").strip().lower()
                for kw in report_kw:
                    if kw in text:
                        print(f"✅ Найдена ссылка '{link.text}'. Кликаем через JS...")
                        driver.execute_script("arguments[0].click();", link)
                        report_opened = True
                        time.sleep(10)
                        break
                if report_opened:
                    break
            except:
                continue

        # Способ 2: клик по ячейке таблицы
        if not report_opened:
            print("--- Пробуем кликнуть по строкам таблицы ---")
            for table in tables:
                rows = table.find_elements(By.TAG_NAME, "tr")
                for row in rows:
                    row_text = row.text.lower()
                    for kw in report_kw:
                        if kw in row_text:
                            try:
                                cells = row.find_elements(By.TAG_NAME, "td")
                                if cells:
                                    print(f"✅ Кликаем ячейку: {row.text[:100]}")
                                    driver.execute_script("arguments[0].click();", cells[0])
                                    report_opened = True
                                    time.sleep(10)
                                    break
                            except:
                                pass
                    if report_opened:
                        break
                if report_opened:
                    break

        if not report_opened:
            print("⚠️ Не нашли отчёт для клика")

        # Сохраняем HTML после клика
        with open("debug_grades_final.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"💾 debug_grades_final.html | URL: {driver.current_url}")

        # Ищем кнопку "Сформировать"
        print("--- Ищем кнопку 'Сформировать' ---")
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        all_buttons += driver.find_elements(By.TAG_NAME, "a")
        all_buttons += driver.find_elements(By.TAG_NAME, "input")

        for btn in all_buttons:
            try:
                text = (btn.text or btn.get_attribute("value") or "").strip().lower()
                if any(w in text for w in ["сформир", "показат", "построит", "получить", "вывести"]):
                    print(f"✅ Кликаем '{btn.text}'. Ждём отчёт...")
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(15)
                    break
            except:
                continue

        # Сохраняем финальный HTML
        with open("debug_grades_result.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"💾 debug_grades_result.html | URL: {driver.current_url}")

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
            print("\n❌ Оценки не найдены. Смотри debug_reports_page.html и debug_grades_final.html")

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
