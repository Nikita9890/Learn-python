import pyautogui
import subprocess
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Функция для запуска Surfshark
def launch_surfshark():
    surfshark_path = r"C:\Program Files\Surfshark\Surfshark.exe"
    subprocess.Popen([surfshark_path])
    time.sleep(10)

# Функция для поиска и нажатия кнопки с прокруткой клавишами
def find_and_click_with_scroll(image_path, max_scrolls=10):
    for _ in range(max_scrolls):
        button_location = pyautogui.locateOnScreen(image_path, confidence=0.8)
        if button_location:
            pyautogui.click(button_location)
            print(f"Изображение {image_path} найдено и клик выполнен.")
            return True
        # Прокрутка клавишей вниз
        pyautogui.press("pagedown")
        time.sleep(1)
    print(f"Изображение {image_path} не найдено после прокрутки.")
    return False

# Функция для регистрации пользователя
def register_user(driver, phone, email, password):
    try:
        driver.find_element(By.XPATH, '//*[@data-testid="phone-input"]').send_keys(phone)  # Ввод телефона
        driver.find_element(By.XPATH, '//*[@name="email"]').send_keys(email)  # Ввод email
        driver.find_element(By.XPATH, '//*[@name="password"]').send_keys(password)  # Ввод пароля
        driver.find_element(By.XPATH, '//*[@data-testid="submit-button"]').click()  # Нажимаем на кнопку регистрации
        print(f"Регистрация выполнена: {email}")
        time.sleep(10)  # Ожидание завершения регистрации
    except Exception as e:
        print(f"Ошибка при регистрации: {e}")

# Функция для открытия игры, создания скриншота и возврата на главную
def open_game_and_screenshot(driver, game_alt_text, wait_time, screenshot_name):
    try:
        # Ждем появления элемента с заданным alt текстом
        game_image = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f'//img[@alt="{game_alt_text}"]'))
        )
        # Скроллим к элементу
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", game_image)
        # Кликаем на элемент
        driver.execute_script("arguments[0].click();", game_image)
        print(f"Открыта игра: {game_alt_text}")

        # Ждем указанное время
        time.sleep(wait_time)

        # Создаем скриншот
        screenshot_path = f"{screenshot_name}.png"
        driver.save_screenshot(screenshot_path)
        print(f"Скриншот сохранён: {screenshot_path}")

        # Возвращаемся на главную через селектор `_back_tf7f2_15`
        back_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "_back_tf7f2_15"))
        )
        driver.execute_script("arguments[0].click();", back_button)
        time.sleep(2)

    except Exception as e:
        print(f"Ошибка при открытии игры {game_alt_text}: {e}")

# Основной код для запуска тестов с Selenium
def run_selenium_test(games_list, registration_data):
    # Настройки для мобильного режима
    chrome_options = Options()
    mobile_emulation = {
        "deviceName": "iPhone X"
    }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

    # Инициализация драйвера
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # 1. Открываем сайт
        driver.get("https://valor.bet/")
        time.sleep(10)

        # 2. Регистрируем пользователя с уникальными данными
        register_user(
            driver,
            phone=registration_data["phone"],
            email=registration_data["email"],
            password=registration_data["password"]
        )

        # Переход на главную
        driver.find_element(By.CSS_SELECTOR, '._logo-icon_de94n_8').click()
        time.sleep(2)

        # Открытие каждой игры из списка
        for game in games_list:
            open_game_and_screenshot(
                driver,
                game_alt_text=game["alt_text"],
                wait_time=game["wait_time"],
                screenshot_name=game["screenshot_name"]
            )
    except Exception as e:
        print(f"Общая ошибка: {e}")
    finally:
        driver.quit()

# Основной код
if __name__ == "__main__":
    # Список ГЕО с регистрационными данными и списками игр
    geo_data = {
        "india.png": {
            "registration": {"phone": "6756747628", "email": "user_india@exawdawample.com", "password": "password_india"},
            "games": [
                {"alt_text": "Aviator", "wait_time": 10, "screenshot_name": "aviator_india"},
                {"alt_text": "Diver", "wait_time": 10, "screenshot_name": "diver_india"},
                {"alt_text": "Wheel", "wait_time": 10, "screenshot_name": "Wheel_india"},
                {"alt_text": "Mines", "wait_time": 10, "screenshot_name": "Mines_india"},
                {"alt_text": "Crash", "wait_time": 10, "screenshot_name": "Crash_india"},
                {"alt_text": "Chicken Road", "wait_time": 10, "screenshot_name": "Chicken Road_india"},
                {"alt_text": "Plinko 1000", "wait_time": 10, "screenshot_name": "Plinko 1000_india"},
                {"alt_text": "Crime Empire", "wait_time": 10, "screenshot_name": "Crime Empire_india"},
                {"alt_text": "AVIAMASTERS Mobile", "wait_time": 10, "screenshot_name": "AVIAMASTERS Mobile_india"},
                {"alt_text": "Air Jet", "wait_time": 10, "screenshot_name": "Air Jet_india"},
                {"alt_text": "Roulette", "wait_time": 10, "screenshot_name": "Roulette_india"},
                {"alt_text": "Diver", "Tropicana": 10, "screenshot_name": "Tropicana_india"},
            ]
        },
        "azerbaijan.png": {
            "registration": {"phone": "1237416090", "email": "user_azerbaijan@exawadwdwample.com", "password": "111111"},
            "games": [
                {"alt_text": "Aviator", "wait_time": 10, "screenshot_name": "Aviator_azerbaijan"},
                {"alt_text": "Air Jet", "wait_time": 10, "screenshot_name": "Air Jet_azerbaijan"},
                {"alt_text": "Sugar Rush Mobile", "wait_time": 10, "screenshot_name": "Sugar Rush Mobile_azerbaijan"},
                {"alt_text": "Sun of Egypt 3", "wait_time": 10, "screenshot_name": "Sun of Egypt 3_azerbaijan"},
                {"alt_text": "Hell Hot 100", "wait_time": 10, "screenshot_name": "Hell Hot 100_azerbaijan"},
                {"alt_text": "2021 Hit Slot", "wait_time": 10, "screenshot_name": "A2021 Hit Slot_azerbaijan"},
                {"alt_text": "9 Coins Grand Platinum Edition Mobile", "wait_time": 10, "screenshot_name": "9 Coins Grand Platinum Edition Mobile_azerbaijan"},
                {"alt_text": "Big Wild Buffalo", "wait_time": 10, "screenshot_name": "Big Wild Buffalo_azerbaijan"},
                {"alt_text": "Big Bass Bonanza Mobile", "wait_time": 10, "screenshot_name": "Big Bass Bonanza Mobile_azerbaijan"},
                {"alt_text": "777 Coins", "wait_time": 10, "screenshot_name": "777 Coins_azerbaijan"},
                {"alt_text": "Lucky Streak 3", "wait_time": 10, "screenshot_name": "Lucky Streak 3_azerbaijan"},
                {"alt_text": "Fortune Crash", "wait_time": 10, "screenshot_name": "Fortune Crash_azerbaijan"},
            ]
        },

        # Добавьте аналогично другие ГЕО
    }

    # Шаг 1: Запускаем Surfshark
    launch_surfshark()

    # Перебираем каждое ГЕО из списка
    for geo_image_path, data in geo_data.items():
        print(f"Тестирование для ГЕО: {geo_image_path}")
        success = find_and_click_with_scroll(rf"E:\GEO\{geo_image_path}")
        if not success:
            print(f"Не удалось выбрать ГЕО: {geo_image_path}. Переходим к следующему.")
            continue
        else:
            # Ждём 5 секунд после выбора ГЕО
            time.sleep(5)
            # Шаг 2: Запускаем Selenium тест для текущего списка игр и данных регистрации
            run_selenium_test(
                games_list=data["games"],
                registration_data=data["registration"]
            )
            print(f"Тест для {geo_image_path} завершён.\n")
