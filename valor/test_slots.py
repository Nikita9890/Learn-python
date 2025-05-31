import time
import os
import cv2
import pyautogui
import requests
import random
import logging
from faker import Faker
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# === Настроим логирование ===
logging.basicConfig(
    filename="test_log.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

faker = Faker()

# === Пути к папкам ===
BASE_SCREENSHOTS_PATH = "screenshots"
# Преобразуем в абсолютный путь
BASE_SCREENSHOTS_PATH = os.path.abspath(BASE_SCREENSHOTS_PATH)

# Создаем основную папку, если её нет
if not os.path.exists(BASE_SCREENSHOTS_PATH):
    os.makedirs(BASE_SCREENSHOTS_PATH)
    print(f"Создана папка: {BASE_SCREENSHOTS_PATH}")
else:
    print(f"Папка уже существует: {BASE_SCREENSHOTS_PATH}")

SITE_URL = "https://valor.bet"

# === Список тестируемых ГЕО ===
geo_list = ["india", "columbia"]

# === Функция генерации уникальных данных для регистрации ===
def generate_user_data(geo):
    """Генерирует уникальные данные для регистрации на основе гео."""
    email = f"user_{geo.lower()}_{random.randint(1000, 9999)}@example.com"
    password = f"Pass_{geo}_{random.randint(1000, 9999)}!"
    phone = faker.phone_number()

    return {"email": email, "password": password, "phone": phone}

# === Настройки браузера ===
def get_driver():
    """Запускает Chrome в режиме мобильного устройства"""
    logger = logging.getLogger(__name__)

    options = Options()
    mobile_emulation = {"deviceName": "iPhone 12 Pro"}
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless")  # Закомментировать если нужно видеть браузер

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    logger.info("Запущен браузер в мобильном режиме (iPhone 12 Pro)")

    return driver

# === Создание папки для скриншотов текущего ГЕО ===
def create_geo_screenshot_folder(geo_name):
    """Создает папку для текущего ГЕО и проверяет, была ли она создана."""
    geo_screenshot_path = os.path.join(BASE_SCREENSHOTS_PATH, geo_name)

    try:
        os.makedirs(geo_screenshot_path, exist_ok=True)  # Создаём папку
        if os.path.exists(geo_screenshot_path):
            print(f"✅ Папка создана: {geo_screenshot_path}")
        else:
            print(f"❌ Ошибка: папка {geo_screenshot_path} не была создана!")
    except Exception as e:
        print(f"❌ Ошибка при создании папки {geo_screenshot_path}: {e}")

    return geo_screenshot_path  # Возвращаем путь к папке текущего ГЕО


# Тестируем создание папки
for geo in ["india", "columbia"]:
    create_geo_screenshot_folder(geo)

# === Запуск Surfshark ===
def start_surfshark():
    """Открывает приложение Surfshark"""
    os.system(r'start "" "C:\Program Files\Surfshark\Surfshark.exe"')
    time.sleep(5)

# === Регистрация на сайте с ожиданием полей ===
def register_on_site(driver, user_data):
    """Выполняет регистрацию с дополнительным ожиданием полей"""
    driver.get(SITE_URL)

    # Ждем полной загрузки страницы
    WebDriverWait(driver, 15).until(lambda d: d.execute_script("return document.readyState") == "complete")
    time.sleep(8)

    try:
        email_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        email_field.send_keys(user_data["email"])
    except:
        print("Поле email отсутствует или не загрузилось")

    try:
        password_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_field.send_keys(user_data["password"])
    except:
        print("Поле password отсутствует или не загрузилось")

    try:
        phone_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//*[@data-testid="phone-input"]'))
        )
        phone_field.send_keys(user_data["phone"])
    except:
        print("Поле phone отсутствует или не загрузилось")

    try:
        submit_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@data-testid="submit-button"]'))
        )
        submit_btn.click()
        time.sleep(10)
    except:
        print("Кнопка отправки не найдена или не активна")

# === Получение списка игр через API ===
def get_game_ids():
    """Получение ID игр с двух категорий через API"""
    all_games_url = "https://valor.bet/s-api/v1/games?page=1&per_page=12&category=all_games&is_mobile=1"
    live_games_url = "https://valor.bet/s-api/v1/games?page=1&per_page=12&category=live&is_mobile=1"

    # Получаем игры из двух категорий
    all_games_response = requests.get(all_games_url)
    live_games_response = requests.get(live_games_url)

    if all_games_response.status_code == 200 and live_games_response.status_code == 200:
        all_games = all_games_response.json()["data"]
        live_games = live_games_response.json()["data"]

        all_game_ids = [game["id"] for game in all_games]
        live_game_ids = [game["id"] for game in live_games]

        return all_game_ids + live_game_ids  # Слияние обоих списков
    else:
        print("Ошибка при получении списка игр")
        return []

# === Открытие игры и снятие скриншота ===
def open_game_and_take_screenshot(driver, geo_name, game_id, screenshot_folder):
    """Открывает игру по ID и делает скриншот"""
    game_url = f"https://valor.bet/de/casino/current/{game_id}"
    driver.get(game_url)
    time.sleep(3)

    logging.info(f"Открыта игра с ID {game_id} в регионе {geo_name}")

    try:
        # Ждем появления возможного модального окна и закрываем его
        try:
            close_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@data-cy="close-modal-button"]'))
            )
            close_button.click()
            logging.info(f"Модалка закрыта для игры с ID {game_id}.")
            time.sleep(2)  # Даем время на закрытие модалки
        except Exception:
            logging.info(f"Модалка не появилась для игры с ID {game_id}, продолжаем без её закрытия.")

        # Даем время на загрузку игры
        time.sleep(20)

        # Сохраняем скриншот в папку текущего ГЕО
        screenshot_name = f"{game_id}.png"
        screenshot_path = os.path.join(screenshot_folder, screenshot_name)
        driver.save_screenshot(screenshot_path)
        logging.info(f"Скриншот сохранён: {screenshot_path}")

    except Exception as e:
        logging.error(f"Ошибка при открытии игры с ID {game_id}: {e}")

# === Основной тест ===
def run_test():
    """Запуск теста для всех ГЕО"""
    for geo in geo_list:
        print(f"\nТестируем ГЕО: {geo}")

        # Шаг 1: Открытие Surfshark и выбор гео
        start_surfshark()

        # Создаем папку для скриншотов текущего ГЕО
        screenshot_folder = create_geo_screenshot_folder(geo)

        # Шаг 2: Запуск теста для данного гео
        driver = get_driver()

        try:
            user_data = generate_user_data(geo)  # Уникальные данные для каждого гео
            register_on_site(driver, user_data)

            game_ids = get_game_ids()

            # Шаг 3: Открытие игры и сохранение скриншота
            for game_id in game_ids:
                open_game_and_take_screenshot(driver, geo, game_id, screenshot_folder)

        finally:
            driver.quit()

if __name__ == "__main__":
    run_test()
