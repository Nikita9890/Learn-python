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

# Получаем корневую папку репозитория
repo_root = os.path.abspath(os.path.join(os.getcwd(), ".."))  # т.к. запускаешь из valor, поднимаемся на уровень вверх

REPORT_PATH = os.path.join(repo_root, "docs")
BASE_SCREENSHOTS_PATH = os.path.join(REPORT_PATH, "screenshots")

os.makedirs(REPORT_PATH, exist_ok=True)

# дальше использовать REPORT_PATH и BASE_SCREENSHOTS_PATH

# === Пути к папкам ===
GEO_IMAGES_PATH = "E:\\GEO"
SITE_URL = "https://valor.bet"

# === Список тестируемых ГЕО ===
geo_list = ["india",
            "columbia",
            "brazil",
            "egipt",
            "pery",
            "mexico",
            "indonezia",
            "korea",
            "malayzia",
]

# === Функция генерации уникальных данных для регистрации ===
def generate_user_data(geo):
    """Генерирует уникальные данные для регистрации на основе гео."""
    email = f"user_{geo.lower()}_{random.randint(1000, 9999)}@example.com"
    password = f"Pass_{geo}_{random.randint(1000, 9999)}!"
    phone = faker.phone_number()

    return {"email": email, "password": password, "phone": phone}
# === Создание папки для текущего ГЕО ===
def create_geo_screenshot_folder(geo_name):
    geo_screenshot_path = os.path.join(BASE_SCREENSHOTS_PATH, geo_name)
    os.makedirs(geo_screenshot_path, exist_ok=True)
    logging.info(f"Создана папка для скриншотов: {geo_screenshot_path}")
    return geo_screenshot_path

# === Настройки браузера ===
def get_driver():
    """Запускает Chrome в режиме мобильного устройства"""
    logger = logging.getLogger(__name__)

    options = Options()
    mobile_emulation = {"deviceName": "iPhone 12 Pro"}
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    options.add_argument("--disable-blink-features=AutomationControlled")
    #options.add_argument("--headless")  # Закомментировать если нужно видеть браузер

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    logger.info("Запущен браузер в мобильном режиме (iPhone 12 Pro)")

    return driver

# === Запуск Surfshark ===
def start_surfshark():
    """Запускает приложение Surfshark"""
    os.system(r'start "" "C:\Program Files\Surfshark\Surfshark.exe"')
    time.sleep(5)

# === Выбор ГЕО по картинке ===
def select_geo(geo_name):
    """Выбирает гео по картинке"""
    image_path = os.path.join(GEO_IMAGES_PATH,  f"{geo_name}.png")
    geo_image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    if geo_image is None:
        print(f"Ошибка: изображение {geo_name} не найдено!")
        return False

    location = pyautogui.locateCenterOnScreen(image_path, confidence=0.8)

    if location:
        pyautogui.click(location)
        print(f"Выбрано гео: {geo_name}")
        time.sleep(5)
        return True
    else:
        print(f"Ошибка: ГЕО {geo_name} не найдено на экране!")
        return False

# === Регистрация на сайте ===
def register_on_site(driver, user_data):
    """Регистрирует пользователя на сайте"""
    driver.get(SITE_URL)
    WebDriverWait(driver, 15).until(lambda d: d.execute_script("return document.readyState") == "complete")
    time.sleep(15)

    try:
        email_field = driver.find_element(By.XPATH, '//*[@name="email"]')
        email_field.send_keys(user_data["email"])
    except:
        print("Поле email отсутствует")

    try:
        password_field = driver.find_element(By.XPATH, '//*[@name="password"]')
        password_field.send_keys(user_data["password"])
    except:
        print("Поле password отсутствует")

    try:
        phone_field = driver.find_element(By.XPATH, '//*[@data-testid="phone-input"]')
        phone_field.send_keys(user_data["phone"])
    except:
        print("Поле phone отсутствует")

    submit_btn = driver.find_element(By.XPATH, '//*[@data-testid="submit-button"]')
    submit_btn.click()

    time.sleep(15)



# === Переход на главную страницу ===
def go_to_main_page(driver):
    """Переход на главную страницу"""
    main_page_element = driver.find_element(By.CSS_SELECTOR, '[aria-label="Valor"]')
    main_page_element.click()
    time.sleep(3)

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
def open_game_and_take_screenshot(driver, geo_name, game_id, geo_screenshot_path):
    """Открывает игру по ID и делает скриншот"""
    game_url = f"https://valor.bet/de/casino/current/{game_id}"
    driver.get(game_url)
    time.sleep(3)

    logging.info(f"Открыта игра с ID {game_id} в регионе {geo_name}")

    try:
        # Ждем появления модального окна депозита и закрываем его
        try:
            close_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@data-cy="close-modal-button"]'))
            )
            close_button.click()
            logging.info(f"Модалка закрыта для игры с ID {game_id}.")
            time.sleep(5)  # Даем время на закрытие модалки
        except Exception:
            logging.info(f"Модалка не появилась для игры с ID {game_id}, продолжаем без её закрытия.")

        # Даем время на загрузку игры
        time.sleep(25)

        # Сохраняем скриншот
        screenshot_name = f"{geo_name} — {game_id}.png"
        screenshot_path = os.path.join(geo_screenshot_path, screenshot_name)
        driver.save_screenshot(screenshot_path)
        logging.info(f"Скриншот сохранён: {screenshot_path}")

    except Exception as e:
        logging.error(f"Ошибка при открытии игры с ID {game_id}: {e}")


# === Основной тест ===
def run_test():
    """Запуск теста для всех ГЕО"""
    start_time = time.time()  # Засекаем время начала
    test_results = []  # Список для отчета

    for geo in geo_list:
        print(f"\nТестируем ГЕО: {geo}")
        test_start = time.time()

        # Шаг 1: Открытие Surfshark и выбор гео
        start_surfshark()
        if not select_geo(geo):
            test_results.append(f"{geo}:  Ошибка выбора GEO")
            continue

        # Шаг 2: Создание папки для скриншотов текущего ГЕО
        geo_screenshot_path = create_geo_screenshot_folder(geo)

        # Шаг 3: Запуск теста для данного гео
        print(" Запускаем браузер...")
        driver = get_driver()
        print(" Браузер запущен")

        try:
            user_data = generate_user_data(geo)  # Уникальные данные для каждого гео
            register_on_site(driver, user_data)
            go_to_main_page(driver)

            # Получаем все игры
            game_ids = get_game_ids()

            if not game_ids:
                test_results.append(f"{geo}: ⚠ Игры не найдены")
            else:
                for game_id in game_ids:
                    open_game_and_take_screenshot(driver, geo, game_id, geo_screenshot_path)

            test_results.append(f"{geo}: ✅ Успешно ({len(game_ids)} игр)")

        except Exception as e:
            test_results.append(f"{geo}: ❌ Ошибка - {str(e)}")
            logging.error(f"Ошибка в GEO {geo}: {e}")

        finally:
            driver.quit()

        test_end = time.time()
        test_duration = round(test_end - test_start, 2)
        print(f"Тест для {geo} завершен за {test_duration} сек")

        # Конец теста
    end_time = time.time()
    total_duration = round(end_time - start_time, 2)

    # === Запись отчета ===
    # === HTML отчет ===
    html_report_path = os.path.join(REPORT_PATH, "index.html")
    with open(html_report_path, "w", encoding="utf-8") as html_file:
        html_file.write("""
        <html>
        <head>
            <title>Тестовый отчет</title>
            <style>
                body { font-family: 'Segoe UI', sans-serif; background-color: #f5f7fa; color: #333; margin: 0; padding: 0; }
                h1 { text-align: center; padding: 20px; background-color: #343a40; color: white; margin: 0; }
                table { border-collapse: collapse; margin: 30px auto; width: 90%; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
                th, td { padding: 12px 20px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #6c757d; color: white; }
                tr:hover { background-color: #f1f1f1; }
                .success { color: green; font-weight: bold; }
                .warning { color: orange; font-weight: bold; }
                .error { color: red; font-weight: bold; }
                .image-container { margin-top: 10px; }
                img { height: 120px; margin-right: 10px; border-radius: 4px; border: 1px solid #ccc; }
            </style>
        </head>
        <body>
            <h1>Результаты тестирования</h1>
            <p style="text-align:center;">Общее время выполнения: """ + str(total_duration) + """ сек</p>
            <table>
                <tr><th>GEO</th><th>Результат</th><th>Скриншоты</th></tr>
        """)

        for result in test_results:
            geo_name, status = result.split(":", 1)
            status = status.strip()

            if "✅" in status:
                status_class = "success"
            elif "⚠️" in status:
                status_class = "warning"
            else:
                status_class = "error"

            # Подгружаем до 24 скриншотов
            geo_folder = os.path.join(BASE_SCREENSHOTS_PATH, geo_name)
            images_html = ""
            if os.path.exists(geo_folder):
                screenshots = [f for f in os.listdir(geo_folder) if f.endswith(".png")]
                for img_file in screenshots[:24]:
                    img_path = f"screenshots/{geo_name}/{img_file}"
                    images_html += f'<img src="{img_path}" alt="{img_file}"/>'

            html_file.write(f"""
                <tr>
                    <td>{geo_name}</td>
                    <td class="{status_class}">{status}</td>
                    <td><div class="image-container">{images_html}</div></td>
                </tr>
            """)

        html_file.write("""
            </table>
        </body>
        </html>
        """)

    print(f"\n Тест завершен! HTML-отчет сохранен в {html_report_path}")

    # После теста для текущего гео можно выключить Surfshark, если необходимо
        # os.system(r'start "" "C:\Program Files\Surfshark\Surfshark.exe" /stop')

if __name__ == "__main__":
    run_test()