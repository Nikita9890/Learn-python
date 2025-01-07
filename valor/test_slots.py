import pyautogui
import subprocess
import time
from selenium import webdriver
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import pytest


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
        pyautogui.press("page down")
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
def open_game_and_screenshot(driver, game_alt_text, wait_time, screenshot_name, geo_name):
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

        # Создаём папку для скриншотов, если её нет
        geo_folder = os.path.join("screenshots", geo_name)
        os.makedirs(geo_folder, exist_ok=True)

        # Путь для сохранения скриншота
        screenshot_path = os.path.join(geo_folder, f"{screenshot_name}.png")
        driver.save_screenshot(screenshot_path)
        print(f"Скриншот сохранён: {screenshot_path}")

        # Возвращаемся на главную через селектор `_back_tf7f2_15` закрытия игры
        back_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "_back_tf7f2_15"))
        )
        driver.execute_script("arguments[0].click();", back_button)
        time.sleep(2)

        # Проверяем, есть ли кнопка для второго клика закрытия игры
        try:
            back_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "_back_tf7f2_15"))
            )
            # Если кнопка доступна, выполняем второй клик закрытия игры
            driver.execute_script("arguments[0].click();", back_button)
            time.sleep(2)
        except Exception:
            # Кнопка не найдена, продолжаем тест без второго клика
            print("Второй клик закрытия игры не потребовался.")

    except Exception as e:
        print(f"Ошибка при открытии игры {game_alt_text}: {e}")

# Основной код для запуска тестов с Selenium
def run_selenium_test(games_list, registration_data, geo_name):
    # Настройки для мобильного режима
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Безголовый режим
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument("--disable-software-rasterizer")
    # chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument("--start-maximized")
    mobile_emulation = {
        "deviceName": "iPhone X"
    }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

    # Инициализация драйвера
    driver = webdriver.Chrome(options=chrome_options)

    def clear_cache(driver):
        try:
            # Открытие страницы настроек Chrome
            driver.get('chrome://settings/clearBrowserData')
            time.sleep(2)

            # Выполнение команды очистки кэша через JavaScript
            actions = ActionChains(driver)
            actions.send_keys(Keys.TAB * 3 + Keys.DOWN * 3).perform()  # Перемещаемся к кнопке "Очистить данные"
            actions.send_keys(Keys.ENTER).perform()  # Подтверждаем очистку
            time.sleep(5)
            print("Кэш очищен.")
        except Exception as e:
            print(f"Ошибка при очистке кэша: {e}")

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

        # 3 Переход на главную
        driver.find_element(By.CSS_SELECTOR, '._logo-icon_de94n_8').click()
        time.sleep(2)

        # 4 Открытие каждой игры из списка
        for game in games_list:
            open_game_and_screenshot(
                driver,
                game_alt_text=game["alt_text"],
                wait_time=game["wait_time"],
                screenshot_name=game["screenshot_name"],
                geo_name=geo_name
            )

        # 5. Очистка кэша после всех игр
        clear_cache(driver)

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
                {"alt_text": "Aviator", "wait_time": 20, "screenshot_name": "aviator_IN"},
                {"alt_text": "Diver", "wait_time": 20, "screenshot_name": "diver_IN"},
                {"alt_text": "Wheel", "wait_time": 20, "screenshot_name": "Wheel_IN"},
                {"alt_text": "Mines", "wait_time": 20, "screenshot_name": "Mines_IN"},
                {"alt_text": "Crash", "wait_time": 20, "screenshot_name": "Crash_IN"},
                {"alt_text": "Chicken Road", "wait_time": 20, "screenshot_name": "Chicken Road_IN"},
                {"alt_text": "Plinko 1000", "wait_time": 20, "screenshot_name": "Plinko 1000_IN"},
                {"alt_text": "Crime Empire", "wait_time": 20, "screenshot_name": "Crime Empire_IN"},
                {"alt_text": "AVIAMASTERS Mobile", "wait_time": 20, "screenshot_name": "AVIAMASTERS Mobile_IN"},
                {"alt_text": "Air Jet", "wait_time": 20, "screenshot_name": "Air Jet_IN"},
                {"alt_text": "Roulette", "wait_time": 20, "screenshot_name": "Roulette_IN"},
                {"alt_text": "Tropicana", "wait_time": 20, "screenshot_name": "Tropicana_IN"},

                {"alt_text": "Crazy Time", "wait_time": 20, "screenshot_name": "Crazy Time_IN"},
                {"alt_text": "Monopoly Live", "wait_time": 20, "screenshot_name": "Monopoly Live_IN"},
                {"alt_text": "Crazy Pachinko", "wait_time": 20, "screenshot_name": "Crazy Pachinko_IN"},
                {"alt_text": "Dream Catcher", "wait_time": 20, "screenshot_name": "Dream Catcher_IN"},
                {"alt_text": "Lightning Baccarat", "wait_time": 20, "screenshot_name": "Lightning Baccarat_IN"},
                {"alt_text": "Baccarat A", "wait_time": 20, "screenshot_name": "Baccarat A_IN"},
                {"alt_text": "Speed Baccarat D", "wait_time": 20, "screenshot_name": "Speed Baccarat D_IN"},
                {"alt_text": "Baccarat", "wait_time": 20, "screenshot_name": "Baccarat_IN"},
                {"alt_text": "Crazy Coin Flip", "wait_time": 20, "screenshot_name": "Crazy Coin Flip_IN"},
                {"alt_text": "Casino Holdem", "wait_time": 20, "screenshot_name": "Casino Holdem_IN"},
                {"alt_text": "Three Card Poker", "wait_time": 20, "screenshot_name": "Three Card Poker_IN"},
                {"alt_text": "Caribbean Stud Poker", "wait_time": 20, "screenshot_name": "Caribbean Stud Poker_IN"},
            ]
        },
        # "azerbaijan.png": {
        #     "registration": {"phone": "1237416090", "email": "user_azerbaijan@exawadwdwample.com", "password": "111111"},
        #     "games": [
        #         {"alt_text": "Aviator", "wait_time": 10, "screenshot_name": "Aviator_AZ"},
        #         {"alt_text": "Air Jet", "wait_time": 10, "screenshot_name": "Air Jet_AZ"},
        #         {"alt_text": "Sugar Rush Mobile", "wait_time": 10, "screenshot_name": "Sugar Rush Mobile_AZ"},
        #         {"alt_text": "Sun of Egypt 3", "wait_time": 10, "screenshot_name": "Sun of Egypt 3_AZ"},
        #         {"alt_text": "Hell Hot 100", "wait_time": 10, "screenshot_name": "Hell Hot 100_AZ"},
        #         {"alt_text": "2021 Hit Slot", "wait_time": 10, "screenshot_name": "A2021 Hit Slot_AZ"},
        #         {"alt_text": "9 Coins Grand Platinum Edition Mobile", "wait_time": 10, "screenshot_name": "9 Coins Grand Platinum Edition Mobile_AZ"},
        #         {"alt_text": "Big Wild Buffalo", "wait_time": 10, "screenshot_name": "Big Wild Buffalo_AZ"},
        #         {"alt_text": "Big Bass Bonanza Mobile", "wait_time": 10, "screenshot_name": "Big Bass Bonanza Mobile_AZ"},
        #         {"alt_text": "777 Coins", "wait_time": 10, "screenshot_name": "777 Coins_AZ"},
        #         {"alt_text": "Lucky Streak 3", "wait_time": 10, "screenshot_name": "Lucky Streak 3_AZ"},
        #         {"alt_text": "Fortune Crash", "wait_time": 10, "screenshot_name": "Fortune Crash_AZ"},
        #
        #         {"alt_text": "Crazy Time", "wait_time": 10, "screenshot_name": "Fortune Crazy Time_AZ"},
        #         {"alt_text": "Monopoly Live", "wait_time": 10, "screenshot_name": "Monopoly Live_AZ"},
        #         {"alt_text": "Crazy Pachinko", "wait_time": 10, "screenshot_name": "Crazy Pachinko_AZ"},
        #         {"alt_text": "Lightning Roulette", "wait_time": 10, "screenshot_name": "Lightning Roulette_AZ"},
        #         {"alt_text": "Gonzos Treasure Map", "wait_time": 10, "screenshot_name": "Gonzos Treasure Map_AZ"},
        #         {"alt_text": "Gold Vault Roulette", "wait_time": 10, "screenshot_name": "Gold Vault Roulette_AZ"},
        #         {"alt_text": "Dream Catcher", "wait_time": 10, "screenshot_name": "Dream Catcher_AZ"},
        #         {"alt_text": "Football studio", "wait_time": 10, "screenshot_name": "Football studio_AZ"},
        #         {"alt_text": "Golden Wealth Baccarat", "wait_time": 10, "screenshot_name": "Golden Wealth Baccarat_AZ"},
        #         {"alt_text": "Dead or Alive Saloon", "wait_time": 10, "screenshot_name": "Dead or Alive Saloon_AZ"},
        #         {"alt_text": "Football Studio Dice", "wait_time": 10, "screenshot_name": "Football Studio Dice_AZ"},
        #         {"alt_text": "Extra Chilli Epic Spins", "wait_time": 10, "screenshot_name": "Extra Chilli Epic Spins_AZ"},
        #     ]
        # },

        "brazil.png": {
            "registration": {"phone": "1237416095", "email": "user_brazilqqqn@exawadwdwample.com",
                             "password": "111111"},
            "games": [
                {"alt_text": "Aviator", "wait_time": 20, "screenshot_name": "aviator_BR"},
                {"alt_text": "Diver", "wait_time": 20, "screenshot_name": "diver_BR"},
                {"alt_text": "Wheel", "wait_time": 20, "screenshot_name": "Wheel_BR"},
                {"alt_text": "Mines", "wait_time": 20, "screenshot_name": "Mines_BR"},
                {"alt_text": "Crash", "wait_time": 20, "screenshot_name": "Crash_BR"},
                {"alt_text": "Chicken Road", "wait_time": 20, "screenshot_name": "Chicken Road_BR"},
                {"alt_text": "Plinko 1000", "wait_time": 20, "screenshot_name": "Plinko 1000_BR"},
                {"alt_text": "Crime Empire", "wait_time": 20, "screenshot_name": "Crime Empire_BR"},
                {"alt_text": "AVIAMASTERS Mobile", "wait_time": 20, "screenshot_name": "AVIAMASTERS Mobile_BR"},
                {"alt_text": "Air Jet", "wait_time": 20, "screenshot_name": "Air Jet_BR"},
                {"alt_text": "Roulette", "wait_time": 20, "screenshot_name": "Roulette_BR"},
                {"alt_text": "Sweet Bonanza Mobile", "wait_time": 20, "screenshot_name": "Sweet Bonanza Mobile_BR"},

                {"alt_text": "Crazy Time", "wait_time": 20, "screenshot_name": "Crazy Time_BR"},
                {"alt_text": "Monopoly Live", "wait_time": 20, "screenshot_name": "Monopoly Live_BR"},
                {"alt_text": "Crazy Pachinko", "wait_time": 20, "screenshot_name": "Crazy Pachinko_BR"},
                {"alt_text": "Lightning Roulette", "wait_time": 20, "screenshot_name": "Lightning Roulette_BR"},
                {"alt_text": "Gonzos Treasure Map", "wait_time": 20, "screenshot_name": "Gonzos Treasure Map_BR"},
                {"alt_text": "Gold Vault Roulette", "wait_time": 20, "screenshot_name": "Gold Vault Roulette_BR"},
                {"alt_text": "Dream Catcher", "wait_time": 20, "screenshot_name": "Dream Catcher_BR"},
                {"alt_text": "Football studio", "wait_time": 20, "screenshot_name": "Football studio_BR"},
                {"alt_text": "Golden Wealth Baccarat", "wait_time": 20, "screenshot_name": "Golden Wealth Baccarat_BR"},
                {"alt_text": "Dead or Alive Saloon", "wait_time": 20, "screenshot_name": "Dead or Alive Saloon_BR"},
                {"alt_text": "Football Studio Dice", "wait_time": 20, "screenshot_name": "Football Studio Dice_BR"},
                {"alt_text": "Extra Chilli Epic Spins", "wait_time": 20, "screenshot_name": "Extra Chilli Epic Spins_BR"},
            ]
        },
        "chili.png": {
            "registration": {"phone": "1237416044", "email": "user_chiliqqqn@exawadwdwample.com",
                             "password": "111111"},
            "games": [
                {"alt_text": "Aviator", "wait_time": 20, "screenshot_name": "aviator_CL"},
                {"alt_text": "Sugar Rush Mobile", "wait_time": 20, "screenshot_name": "Sugar Rush Mobile_CL"},
                {"alt_text": "Rich Piggies: Bonus Combo", "wait_time": 20, "screenshot_name": "Rich Piggies: Bonus Combo_CL"},
                {"alt_text": "Mines", "wait_time": 20, "screenshot_name": "Mines_CL"},
                {"alt_text": "Plinko 1000", "wait_time": 20, "screenshot_name": "Plinko 1000_CL"},
                {"alt_text": "Wolf Gold Mobile", "wait_time": 20, "screenshot_name": "Wolf Gold Mobile_CL"},
                {"alt_text": "Diver", "wait_time": 20, "screenshot_name": "Diver_CL"},
                {"alt_text": "JetX", "wait_time": 20, "screenshot_name": "JetX_CL"},
                {"alt_text": "Balloon", "wait_time": 20, "screenshot_name": "Balloon_CL"},
                {"alt_text": "Gates of Olympus Mobile", "wait_time": 20, "screenshot_name": "Gates of Olympus Mobile_CL"},
                {"alt_text": "Magic Target Mobile", "wait_time": 20, "screenshot_name": "Magic Target Mobile_CL"},
                {"alt_text": "The Dog House Mobile", "wait_time": 20, "screenshot_name": "The Dog House Mobile_CL"},

                {"alt_text": "Mega Bola", "wait_time": 20, "screenshot_name": "Crazy Time_CL"},
                {"alt_text": "Lightning Roulette", "wait_time": 20, "screenshot_name": "Lightning Roulette_CL"},
                {"alt_text": "Crazy Pachinko", "wait_time": 20, "screenshot_name": "Crazy Pachinko_CL"},
                {"alt_text": "Monopoly Big Baller", "wait_time": 20, "screenshot_name": "Monopoly Big Baller_CL"},
                {"alt_text": "Crazy Time", "wait_time": 20, "screenshot_name": "Crazy Time_CL"},
                {"alt_text": "Dream Catcher", "wait_time": 20, "screenshot_name": "Dream Catcher_CL"},
                {"alt_text": "Monopoly Live", "wait_time": 20, "screenshot_name": "Monopoly Live_CL"},
                {"alt_text": "Baccarat Super 6", "wait_time": 20, "screenshot_name": "Baccarat Super 6_CL"},
                {"alt_text": "Dragon Tiger Mobile", "wait_time": 20, "screenshot_name": "Dragon Tiger Mobile_CL"},
                {"alt_text": "ONE Blackjack Mobile", "wait_time": 20, "screenshot_name": "ONE Blackjack Mobile_CL"},
                {"alt_text": "ONE Blackjack 2 - Ruby Mobile", "wait_time": 20, "screenshot_name": "ONE Blackjack 2 - Ruby Mobile_CL"},
                {"alt_text": "Mega Roulette Mobile", "wait_time": 20, "screenshot_name": "Mega Roulette Mobile_CL"},
            ]
        },

        "pery.png": {
            "registration": {"phone": "1237416044", "email": "user_chiliqqqn@exawadwdwample.com",
                             "password": "111111"},
            "games": [
                {"alt_text": "Aviator", "wait_time": 20, "screenshot_name": "aviator_PE"},
                {"alt_text": "Diver", "wait_time": 20, "screenshot_name": "Diver_PE"},
                {"alt_text": "Plinko 1000", "wait_time": 20, "screenshot_name": "Plinko 1000_PE"},
                {"alt_text": "The Dog House Mobile", "wait_time": 20, "screenshot_name": "The Dog House Mobile_PE"},
                {"alt_text": "Sweet Bonanza Mobile", "wait_time": 20, "screenshot_name": "Sweet Bonanza Mobile_PE"},
                {"alt_text": "Mines", "wait_time": 20, "screenshot_name": "Mines_PE"},
                {"alt_text": "Gates of Olympus Mobile", "wait_time": 20, "screenshot_name": "Gates of Olympus Mobile_PE"},
                {"alt_text": "Penalty Shoot Out", "wait_time": 20, "screenshot_name": "Penalty Shoot Out_PE"},
                {"alt_text": "Sun of Egypt 3", "wait_time": 20, "screenshot_name": "Sun of Egypt 3_PE"},
                {"alt_text": "Tropicana", "wait_time": 20, "screenshot_name": "Tropicana_PE"},
                {"alt_text": "Zeus vs Hades - Gods of War Mobile", "wait_time": 20, "screenshot_name": "Zeus vs Hades - Gods of War Mobile_PE"},
                {"alt_text": "Hot-mines", "wait_time": 20, "screenshot_name": "Hot-mines_PE"},

                {"alt_text": "Mega Bola", "wait_time": 20, "screenshot_name": "Crazy Time_PE"},
                {"alt_text": "Lightning Roulette", "wait_time": 20, "screenshot_name": "Lightning Roulette_PE"},
                {"alt_text": "Crazy Pachinko", "wait_time": 20, "screenshot_name": "Crazy Pachinko_PE"},
                {"alt_text": "Monopoly Live", "wait_time": 20, "screenshot_name": "Monopoly Live_PE"},
                {"alt_text": "Crazy Time", "wait_time": 20, "screenshot_name": "Crazy Time_PE"},
                {"alt_text": "Football studio", "wait_time": 20, "screenshot_name": "Football studio_PE"},
                {"alt_text": "Andar Bahar Mobile", "wait_time": 20, "screenshot_name": "Andar Bahar Mobile_PE"},
                {"alt_text": "Blackjack 9 - Azure Mobile", "wait_time": 20, "screenshot_name": "Blackjack 9 - Azure Mobile_PE"},
                {"alt_text": "Baccarat 8 Mobile", "wait_time": 20, "screenshot_name": "Baccarat 8 Mobile_PE"},
                {"alt_text": "Speed Baccarat 2 Mobile", "wait_time": 20, "screenshot_name": "Speed Baccarat 2 Mobile_PE"},
                {"alt_text": "Speed Baccarat 3 Mobile", "wait_time": 20, "screenshot_name": "Speed Baccarat 3 Mobile_PE"},
                {"alt_text": "Fortune 6 Baccarat Mobile", "wait_time": 20, "screenshot_name": "Fortune 6 Baccarat Mobile_PE"},
            ]
        },

        "columbia.png": {
            "registration": {"phone": "1237416044", "email": "user_chiliqqqn@exawadwdwample.com",
                             "password": "111111"},
            "games": [
                {"alt_text": "Aviator", "wait_time": 20, "screenshot_name": "aviator_CO"},
                {"alt_text": "Diver", "wait_time": 20, "screenshot_name": "Diver_CO"},
                {"alt_text": "Plinko 1000", "wait_time": 20, "screenshot_name": "Plinko 1000_CO"},
                {"alt_text": "Rich Piggies: Bonus Combo", "wait_time": 20, "screenshot_name": "Rich Piggies: Bonus Combo_CO"},
                {"alt_text": "Balloon", "wait_time": 20, "screenshot_name": "Balloon_CO"},
                {"alt_text": "Mines", "wait_time": 20, "screenshot_name": "Mines_CO"},
                {"alt_text": "New Double", "wait_time": 20, "screenshot_name": "New Double_CO"},
                {"alt_text": "Crash", "wait_time": 20, "screenshot_name": "Crash_CO"},
                {"alt_text": "AVIAMASTERS Mobile", "wait_time": 20, "screenshot_name": "AVIAMASTERS Mobile_CO"},
                {"alt_text": "Tropicana", "wait_time": 20, "screenshot_name": "Tropicana_CO"},
                {"alt_text": "Robo dice", "wait_time": 20, "screenshot_name": "Robo dice_CO"},
                {"alt_text": "Roulette", "wait_time": 20, "screenshot_name": "Roulette_CO"},

                {"alt_text": "Gonzos Treasure Map", "wait_time": 20, "screenshot_name": "Crazy Time_CO"},
                {"alt_text": "Lightning Roulette", "wait_time": 20, "screenshot_name": "Lightning Roulette_CO"},
                {"alt_text": "Crazy Pachinko", "wait_time": 20, "screenshot_name": "Crazy Pachinko_CO"},
                {"alt_text": "Monopoly Live", "wait_time": 20, "screenshot_name": "Monopoly Live_CO"},
                {"alt_text": "Crazy Time", "wait_time": 20, "screenshot_name": "Crazy Time_CO"},
                {"alt_text": "Football studio", "wait_time": 20, "screenshot_name": "Football studio_CO"},
                {"alt_text": "Gold Vault Roulette", "wait_time": 20, "screenshot_name": "Gold Vault Roulette_CO"},
                {"alt_text": "Dream Catcher", "wait_time": 20, "screenshot_name": "Dream Catcher_CO"},
                {"alt_text": "Golden Wealth Baccarat", "wait_time": 20, "screenshot_name": "Golden Wealth Baccarat_CO"},
                {"alt_text": "Dead or Alive Saloon", "wait_time": 20, "screenshot_name": "Dead or Alive Saloon_CO"},
                {"alt_text": "Football Studio Dice", "wait_time": 20, "screenshot_name": "Football Studio Dice_CO"},
                {"alt_text": "Extra Chilli Epic Spins", "wait_time": 20, "screenshot_name": "Extra Chilli Epic Spins_CO"},
            ]
        },

        "egipt.png": {
            "registration": {"phone": "1237416044", "email": "user_chiliqqqn@exawadwdwample.com",
                             "password": "111111"},
            "games": [
                {"alt_text": "Aviator", "wait_time": 20, "screenshot_name": "aviator_EG"},
                {"alt_text": "Diver", "wait_time": 20, "screenshot_name": "Diver_EG"},
                {"alt_text": "Plinko 1000", "wait_time": 20, "screenshot_name": "Plinko 1000_EG"},
                {"alt_text": "Battle Trades", "wait_time": 20, "screenshot_name": "Battle Trades_EG"},
                {"alt_text": "Sun of Egypt", "wait_time": 20, "screenshot_name": "Sun of Egypt_EG"},
                {"alt_text": "Book Hotfire Mobile", "wait_time": 20, "screenshot_name": "Book Hotfire Mobile_EG"},
                {"alt_text": "Big Catch Bass Fishing Mobile", "wait_time": 20, "screenshot_name": "Big Catch Bass Fishing Mobile_EG"},
                {"alt_text": "Gates of Olympus Mobile", "wait_time": 20, "screenshot_name": "Gates of Olympus Mobile_EG"},
                {"alt_text": "Dolphin's Pearl deluxe Mobile", "wait_time": 20, "screenshot_name": "Dolphin's Pearl deluxe Mobile_EG"},
                {"alt_text": "Oktoberfest Mobile", "wait_time": 20, "screenshot_name": "Oktoberfest Mobile_EG"},
                {"alt_text": "Dolphin's Pearl Mobile", "wait_time": 20, "screenshot_name": "Dolphin's Pearl Mobile_EG"},
                {"alt_text": "Magic Apple 2", "wait_time": 20, "screenshot_name": "Magic Apple 2_EG"},

                {"alt_text": "Gonzos Treasure Map", "wait_time": 20, "screenshot_name": "Crazy Time_EG"},
                {"alt_text": "Lightning Roulette", "wait_time": 20, "screenshot_name": "Lightning Roulette_EG"},
                {"alt_text": "Crazy Pachinko", "wait_time": 10, "screenshot_name": "Crazy Pachinko_EG"},
                {"alt_text": "Monopoly Live", "wait_time": 20, "screenshot_name": "Monopoly Live_EG"},
                {"alt_text": "Crazy Time", "wait_time": 20, "screenshot_name": "Crazy Time_EG"},
                {"alt_text": "Football studio", "wait_time": 20, "screenshot_name": "Football studio_EG"},
                {"alt_text": "Gold Vault Roulette", "wait_time": 20, "screenshot_name": "Gold Vault Roulette_EG"},
                {"alt_text": "Dream Catcher", "wait_time": 20, "screenshot_name": "Dream Catcher_EG"},
                {"alt_text": "Golden Wealth Baccarat", "wait_time": 20, "screenshot_name": "Golden Wealth Baccarat_EG"},
                {"alt_text": "Dead or Alive Saloon", "wait_time": 20, "screenshot_name": "Dead or Alive Saloon_EG"},
                {"alt_text": "Football Studio Dice", "wait_time": 20, "screenshot_name": "Football Studio Dice_EG"},
                {"alt_text": "Extra Chilli Epic Spins", "wait_time": 20, "screenshot_name": "Extra Chilli Epic Spins_EG"},
            ]
        },

        "argentina.png": {
            "registration": {"phone": "1237416044", "email": "user_chiliqqqn@exawadwdwample.com",
                             "password": "111111"},
            "games": [
                {"alt_text": "Aviator", "wait_time": 20, "screenshot_name": "aviator_AR"},
                {"alt_text": "Diver", "wait_time": 20, "screenshot_name": "Diver_AR"},
                {"alt_text": "Plinko 1000", "wait_time": 20, "screenshot_name": "Plinko 1000_AR"},
                {"alt_text": "Battle Trades", "wait_time": 20, "screenshot_name": "Battle Trades_AR"},
                {"alt_text": "Wheel", "wait_time": 20, "screenshot_name": "Wheel_AR"},
                {"alt_text": "Balloon", "wait_time": 20, "screenshot_name": "Balloon_AR"},
                {"alt_text": "Joker's Jewels Mobile", "wait_time": 20, "screenshot_name": "Joker's Jewels Mobile_AR"},
                {"alt_text": "Gates of Olympus Mobile", "wait_time": 20, "screenshot_name": "Gates of Olympus Mobile_AR"},
                {"alt_text": "Meta Crash", "wait_time": 20, "screenshot_name": "Meta Crash_AR"},
                {"alt_text": "Tropicana", "wait_time": 20, "screenshot_name": "Tropicana_AR"},
                {"alt_text": "StarX", "wait_time": 20, "screenshot_name": "StarX_AR"},
                {"alt_text": "Sweet Bonanza Mobile", "wait_time": 20, "screenshot_name": "Sweet Bonanza Mobile_AR"},

                {"alt_text": "Fortune 6 Baccarat Mobile", "wait_time": 20, "screenshot_name": "Fortune 6 Baccarat Mobile_AR"},
                {"alt_text": "PowerUP Roulette Mobile", "wait_time": 20, "screenshot_name": "PowerUP Roulette Mobile_AR"},
                {"alt_text": "Blackjack 70 - Ruby Mobile", "wait_time": 20, "screenshot_name": "Blackjack 70 - Ruby Mobile_AR"},
                {"alt_text": "32 Cards", "wait_time": 20, "screenshot_name": "32 Cards_AR"},
                {"alt_text": "One Day Teen Patti", "wait_time": 20, "screenshot_name": "One Day Teen Patti_AR"},
                {"alt_text": "Blackjack Salon Privé", "wait_time": 20, "screenshot_name": "Blackjack Salon Privé_AR"},
                {"alt_text": "Sweet Bonanza CandyLand Mobile", "wait_time": 20, "screenshot_name": "Sweet Bonanza CandyLand Mobile_AR"},
                {"alt_text": "Blackjack 9 - Azure Mobile", "wait_time": 10, "screenshot_name": "Blackjack 9 - Azure Mobile_AR"},
                {"alt_text": "Mega Wheel Mobile", "wait_time": 20, "screenshot_name": "Mega Wheel Mobile_AR"},
                {"alt_text": "Blackjack 4 - Azure Mobile", "wait_time": 20, "screenshot_name": "Blackjack 4 - Azure Mobile_AR"},
                {"alt_text": "Mega Baccarat Mobile", "wait_time": 20, "screenshot_name": "Mega Baccarat Mobile_AR"},
                {"alt_text": "Snakes & Ladders Live Mobile", "wait_time": 20, "screenshot_name": "Snakes & Ladders Live Mobile_AR"},
            ]
        },

        "yzbeckistan.png": {
            "registration": {"phone": "1237416044", "email": "user_chiliqqqn@exawadwdwample.com",
                             "password": "111111"},
            "games": [
                {"alt_text": "Aviator", "wait_time": 20, "screenshot_name": "aviator_UZ"},
                {"alt_text": "Diver", "wait_time": 20, "screenshot_name": "Diver_UZ"},
                {"alt_text": "Super Sticky Piggy", "wait_time": 20, "screenshot_name": "Super Sticky Piggy_UZ"},
                {"alt_text": "Slugger Time Mobile", "wait_time": 20, "screenshot_name": "Slugger Time Mobile_UZ"},
                {"alt_text": "Wheel", "wait_time": 20, "screenshot_name": "Wheel_UZ"},
                {"alt_text": "Dice", "wait_time": 20, "screenshot_name": "Dice_UZ"},
                {"alt_text": "Mines", "wait_time": 20, "screenshot_name": "Mines_UZ"},
                {"alt_text": "Gates of Olympus Mobile", "wait_time": 20, "screenshot_name": "Gates of Olympus Mobile_UZ"},
                {"alt_text": "Keno", "wait_time": 20, "screenshot_name": "Keno_UZ"},
                {"alt_text": "Volcano Riches Mobile", "wait_time": 20, "screenshot_name": "Volcano Riches Mobile_UZ"},
                {"alt_text": "Sakura Fortune Mobile", "wait_time": 20, "screenshot_name": "Sakura Fortune Mobile_UZ"},
                {"alt_text": "Hot Sync Mobile", "wait_time": 20, "screenshot_name": "Hot Sync Mobile_UZ"},

                {"alt_text": "Gonzos Treasure Map", "wait_time": 20, "screenshot_name": "Crazy Time_UZ"},
                {"alt_text": "Lightning Roulette", "wait_time": 20, "screenshot_name": "Lightning Roulette_UZ"},
                {"alt_text": "Crazy Pachinko", "wait_time": 20, "screenshot_name": "Crazy Pachinko_UZ"},
                {"alt_text": "Monopoly Live", "wait_time": 20, "screenshot_name": "Monopoly Live_UZ"},
                {"alt_text": "Crazy Time", "wait_time": 20, "screenshot_name": "Crazy Time_UZ"},
                {"alt_text": "Football studio", "wait_time": 20, "screenshot_name": "Football studio_UZ"},
                {"alt_text": "Gold Vault Roulette", "wait_time": 20, "screenshot_name": "Gold Vault Roulette_UZ"},
                {"alt_text": "Dream Catcher", "wait_time": 20, "screenshot_name": "Dream Catcher_UZ"},
                {"alt_text": "Golden Wealth Baccarat", "wait_time": 20, "screenshot_name": "Golden Wealth Baccarat_UZ"},
                {"alt_text": "Dead or Alive Saloon", "wait_time": 20, "screenshot_name": "Dead or Alive Saloon_UZ"},
                {"alt_text": "Football Studio Dice", "wait_time": 20, "screenshot_name": "Football Studio Dice_UZ"},
                {"alt_text": "Extra Chilli Epic Spins", "wait_time": 20, "screenshot_name": "Extra Chilli Epic Spins_UZ"},
            ]
        },

        "venesyela.png": {
            "registration": {"phone": "1237416044", "email": "user_chiliqqqn@exawadwdwample.com",
                             "password": "111111"},
            "games": [
                {"alt_text": "Aviator", "wait_time": 20, "screenshot_name": "aviator_VE"},
                {"alt_text": "Diver", "wait_time": 20, "screenshot_name": "diver_VE"},
                {"alt_text": "Wheel", "wait_time": 20, "screenshot_name": "Wheel_VE"},
                {"alt_text": "Mines", "wait_time": 20, "screenshot_name": "Mines_VE"},
                {"alt_text": "Crash", "wait_time": 20, "screenshot_name": "Crash_VE"},
                {"alt_text": "Chicken Road", "wait_time": 20, "screenshot_name": "Chicken Road_VE"},
                {"alt_text": "Plinko 1000", "wait_time": 20, "screenshot_name": "Plinko 1000_VE"},
                {"alt_text": "Crime Empire", "wait_time": 20, "screenshot_name": "Crime Empire_VE"},
                {"alt_text": "AVIAMASTERS Mobile", "wait_time": 20, "screenshot_name": "AVIAMASTERS Mobile_VE"},
                {"alt_text": "Air Jet", "wait_time": 20, "screenshot_name": "Air Jet_VE"},
                {"alt_text": "Roulette", "wait_time": 20, "screenshot_name": "Roulette_VE"},
                {"alt_text": "Sweet Bonanza Mobile", "wait_time": 20, "screenshot_name": "Sweet Bonanza Mobile_VE"},

                {"alt_text": "Mega Baccarat Mobile", "wait_time": 20, "screenshot_name": "Mega Baccarat Mobile_VE"},
                {"alt_text": "Blackjack 37 - Ruby Mobile", "wait_time": 20, "screenshot_name": "Blackjack 37 - Ruby Mobile_VE"},
                {"alt_text": "Blackjack 49 - Ruby Mobile", "wait_time": 20, "screenshot_name": "Blackjack 49 - Ruby Mobile_VE"},
                {"alt_text": "Andar Bahar Mobile", "wait_time": 20, "screenshot_name": "Andar Bahar Mobile_VE"},
                {"alt_text": "VIP Blackjack 1 Mobile", "wait_time": 20, "screenshot_name": "VIP Blackjack 1 Mobile_VE"},
                {"alt_text": "Baccarat 2 Mobile", "wait_time": 20, "screenshot_name": "Baccarat 2 Mobile_VE"},
                {"alt_text": "Blackjack 46 - Ruby Mobile", "wait_time": 20, "screenshot_name": "Blackjack 46 - Ruby Mobile_VE"},
                {"alt_text": "Speed Baccarat 3 Mobile", "wait_time": 20, "screenshot_name": "Speed Baccarat 3 Mobile_VE"},
                {"alt_text": "Speed Baccarat 2 Mobile", "wait_time": 20, "screenshot_name": "Speed Baccarat 2 Mobile_VE"},
                {"alt_text": "Blackjack 21 - Azure Mobile", "wait_time": 20, "screenshot_name": "Blackjack 21 - Azure Mobile_VE"},
                {"alt_text": "Blackjack 19 - Azure Mobile", "wait_time": 20, "screenshot_name": "Blackjack 19 - Azure Mobile_VE"},
                {"alt_text": "Fortune 6 Baccarat Mobile", "wait_time": 20, "screenshot_name": "Fortune 6 Baccarat Mobile_VE"},
            ]
        },
        "bangladesh.png": {
            "registration": {"phone": "1237416044", "email": "user_chiliqqqn@exawadwdwample.com",
                             "password": "111111"},
            "games": [
                {"alt_text": "Aviator", "wait_time": 20, "screenshot_name": "aviator_BG"},
                {"alt_text": "Diver", "wait_time": 20, "screenshot_name": "diver_BG"},
                {"alt_text": "777 Coins", "wait_time": 20, "screenshot_name": "777 Coins_BG"},
                {"alt_text": "Coin UP: Hot Fire", "wait_time": 20, "screenshot_name": "Coin UP: Hot Fire_BG"},
                {"alt_text": "Hot-mines", "wait_time": 20, "screenshot_name": "Hot-mines_BG"},
                {"alt_text": "Chicken Road", "wait_time": 20, "screenshot_name": "Chicken Road_BG"},
                {"alt_text": "Plinko 1000", "wait_time": 20, "screenshot_name": "Plinko 1000_BG"},
                {"alt_text": "Gates of Olympus Mobile", "wait_time": 20, "screenshot_name": "Gates of Olympus Mobile_BG"},
                {"alt_text": "The Dog House Mobile", "wait_time": 20, "screenshot_name": "The Dog House Mobile_BG"},
                {"alt_text": "Zeus vs Hades - Gods of War Mobile", "wait_time": 20, "screenshot_name": "Zeus vs Hades - Gods of War Mobile_BG"},
                {"alt_text": "Dice", "wait_time": 20, "screenshot_name": "Dice_BG"},
                {"alt_text": "Mines", "wait_time": 20, "screenshot_name": "Mines_BG"},

                {"alt_text": "Gonzos Treasure Map", "wait_time": 20, "screenshot_name": "Crazy Time_BG"},
                {"alt_text": "Lightning Roulette", "wait_time": 20, "screenshot_name": "Lightning Roulette_BG"},
                {"alt_text": "Crazy Pachinko", "wait_time": 20, "screenshot_name": "Crazy Pachinko_BG"},
                {"alt_text": "Monopoly Live", "wait_time": 20, "screenshot_name": "Monopoly Live_BG"},
                {"alt_text": "Crazy Time", "wait_time": 20, "screenshot_name": "Crazy Time_BG"},
                {"alt_text": "Football studio", "wait_time": 20, "screenshot_name": "Football studio_BG"},
                {"alt_text": "Gold Vault Roulette", "wait_time": 20, "screenshot_name": "Gold Vault Roulette_BG"},
                {"alt_text": "Dream Catcher", "wait_time": 20, "screenshot_name": "Dream Catcher_BG"},
                {"alt_text": "Golden Wealth Baccarat", "wait_time": 20, "screenshot_name": "Golden Wealth Baccarat_BG"},
                {"alt_text": "Dead or Alive Saloon", "wait_time": 20, "screenshot_name": "Dead or Alive Saloon_BG"},
                {"alt_text": "Football Studio Dice", "wait_time": 20, "screenshot_name": "Football Studio Dice_BG"},
                {"alt_text": "Extra Chilli Epic Spins", "wait_time": 20, "screenshot_name": "Extra Chilli Epic Spins_BG"},
            ]
        },

        "indonezia.png": {
            "registration": {"phone": "1237416044", "email": "user_chiliqqqn@exawadwdwample.com",
                             "password": "111111"},
            "games": [
                {"alt_text": "Aviator", "wait_time": 20, "screenshot_name": "aviator_ID"},
                {"alt_text": "Diver", "wait_time": 20, "screenshot_name": "diver_ID"},
                {"alt_text": "Wheel", "wait_time": 20, "screenshot_name": "Wheel_ID"},
                {"alt_text": "AVIAMASTERS Mobile", "wait_time": 20, "screenshot_name": "AVIAMASTERS Mobile_ID"},
                {"alt_text": "Crime Empire", "wait_time": 20, "screenshot_name": "Crime Empire_ID"},
                {"alt_text": "Chicken Road", "wait_time": 20, "screenshot_name": "Chicken Road_ID"},
                {"alt_text": "Plinko 1000", "wait_time": 20, "screenshot_name": "Plinko 1000_ID"},
                {"alt_text": "Tropicana", "wait_time": 20, "screenshot_name": "Tropicana_ID"},
                {"alt_text": "Sweet Bonanza Mobile", "wait_time": 20, "screenshot_name": "Sweet Bonanza Mobile_ID"},
                {"alt_text": "Sugar Rush Mobile", "wait_time": 20, "screenshot_name": "Sugar Rush Mobile_ID"},
                {"alt_text": "3 Coins: Egypt", "wait_time": 20, "screenshot_name": "3 Coins: Egypt_ID"},
                {"alt_text": "3 Coins", "wait_time": 20, "screenshot_name": "3 Coins_ID"},

                {"alt_text": "Monopoly Live", "wait_time": 20, "screenshot_name": "Monopoly Live_ID"},
                {"alt_text": "Speed Baccarat 11 Mobile", "wait_time": 20, "screenshot_name": "Speed Baccarat 11 Mobile_ID"},
                {"alt_text": "Bac Bo", "wait_time": 20, "screenshot_name": "Bac Bo_ID"},
                {"alt_text": "Baccarat 2 Mobile", "wait_time": 20, "screenshot_name": "Baccarat 2 Mobile_ID"},
                {"alt_text": "Crazy Time", "wait_time": 20, "screenshot_name": "Crazy Time_ID"},
                {"alt_text": "Dragon Tiger", "wait_time": 20, "screenshot_name": "Dragon Tiger_ID"},
                {"alt_text": "Instant Super Sic Bo", "wait_time": 20, "screenshot_name": "Instant Super Sic Bo_ID"},
                {"alt_text": "VIP Blackjack 1 Mobile", "wait_time": 20, "screenshot_name": "VIP Blackjack 1 Mobile_ID"},
                {"alt_text": "Golden Wealth Baccarat", "wait_time": 20, "screenshot_name": "Golden Wealth Baccarat_ID"},
                {"alt_text": "Sweet Bonanza CandyLand Mobile", "wait_time": 20, "screenshot_name": "Sweet Bonanza CandyLand Mobile_ID"},
                {"alt_text": "Dragon Tiger Mobile", "wait_time": 20, "screenshot_name": "Dragon Tiger Mobile_ID"},
                {"alt_text": "ONE Blackjack Mobile", "wait_time": 20, "screenshot_name": "ONE Blackjack Mobile_ID"},
            ]
        },

        "malayzia.png": {
            "registration": {"phone": "1237416044", "email": "user_chiliqqqn@exawadwdwample.com",
                             "password": "111111"},
            "games": [
                {"alt_text": "Aviator", "wait_time": 20, "screenshot_name": "aviator_ML"},
                {"alt_text": "Diver", "wait_time": 20, "screenshot_name": "diver_ML"},
                {"alt_text": "Wheel", "wait_time": 20, "screenshot_name": "Wheel_ML"},
                {"alt_text": "AVIAMASTERS Mobile", "wait_time": 20, "screenshot_name": "AVIAMASTERS Mobile_ML"},
                {"alt_text": "Balloon", "wait_time": 20, "screenshot_name": "Balloon_ML"},
                {"alt_text": "Battle Trades", "wait_time": 20, "screenshot_name": "Battle Trades_ML"},
                {"alt_text": "Plinko 1000", "wait_time": 20, "screenshot_name": "Plinko 1000_ML"},
                {"alt_text": "Tropicana", "wait_time": 20, "screenshot_name": "Tropicana_ML"},
                {"alt_text": "Sweet Bonanza Mobile", "wait_time": 20, "screenshot_name": "Sweet Bonanza Mobile_ML"},
                {"alt_text": "Sugar Rush Mobile", "wait_time": 20, "screenshot_name": "Sugar Rush Mobile_ML"},
                {"alt_text": "Meta Crash", "wait_time": 20, "screenshot_name": "Meta Crash_ML"},
                {"alt_text": "Zeus vs Hades - Gods of War Mobile", "wait_time": 20, "screenshot_name": "Zeus vs Hades - Gods of War Mobile_ML"},

                {"alt_text": "Monopoly Live", "wait_time": 20, "screenshot_name": "Monopoly Live_ML"},
                {"alt_text": "Speed Baccarat 11 Mobile", "wait_time": 20, "screenshot_name": "Speed Baccarat 11 Mobile_ML"},
                {"alt_text": "Bac Bo", "wait_time": 20, "screenshot_name": "Bac Bo_ML"},
                {"alt_text": "Baccarat 2 Mobile", "wait_time": 20, "screenshot_name": "Baccarat 2 Mobile_ML"},
                {"alt_text": "Crazy Time", "wait_time": 20, "screenshot_name": "Crazy Time_ML"},
                {"alt_text": "Dragon Tiger", "wait_time": 20, "screenshot_name": "Dragon Tiger_ML"},
                {"alt_text": "Instant Super Sic Bo", "wait_time": 20, "screenshot_name": "Instant Super Sic Bo_ML"},
                {"alt_text": "Craps", "wait_time": 20, "screenshot_name": "Craps_ML"},
                {"alt_text": "Golden Wealth Baccarat", "wait_time": 20, "screenshot_name": "Golden Wealth Baccarat_ML"},
                {"alt_text": "Andar Bahar Mobile", "wait_time": 20, "screenshot_name": "Andar Bahar Mobile_ML"},
                {"alt_text": "Dragon Tiger Mobile", "wait_time": 20, "screenshot_name": "Dragon Tiger Mobile_ML"},
                {"alt_text": "ONE Blackjack Mobile", "wait_time": 20, "screenshot_name": "ONE Blackjack Mobile_ML"},
            ]
        },

        "mexico.png": {
            "registration": {"phone": "1237416044", "email": "user_chiliqqqn@exawadwdwample.com",
                             "password": "111111"},
            "games": [
                {"alt_text": "Aviator", "wait_time": 20, "screenshot_name": "aviator_MX"},
                {"alt_text": "Diver", "wait_time": 20, "screenshot_name": "diver_MX"},
                {"alt_text": "Gates of Olympus Mobile", "wait_time": 20, "screenshot_name": "Gates of Olympus Mobile_MX"},
                {"alt_text": "The Dog House Mobile", "wait_time": 20, "screenshot_name": "The Dog House Mobile_MX"},
                {"alt_text": "Starlight Princess Mobile", "wait_time": 20, "screenshot_name": "Starlight Princess Mobile_MX"},
                {"alt_text": "Mines", "wait_time": 20, "screenshot_name": "Mines_MX"},
                {"alt_text": "Dice", "wait_time": 20, "screenshot_name": "Dice_MX"},
                {"alt_text": "Mines", "wait_time": 20, "screenshot_name": "Mines_MX"},
                {"alt_text": "Sweet Bonanza Mobile", "wait_time": 20, "screenshot_name": "Sweet Bonanza Mobile_MX"},
                {"alt_text": "Sugar Rush Mobile", "wait_time": 20, "screenshot_name": "Sugar Rush Mobile_MX"},
                {"alt_text": "Keno", "wait_time": 20, "screenshot_name": "Keno_MX"},
                {"alt_text": "Primal Megaways Mobile", "wait_time": 20, "screenshot_name": "Primal Megaways Mobile_MX"},

                {"alt_text": "Gonzos Treasure Map", "wait_time": 20, "screenshot_name": "Crazy Time_MX"},
                {"alt_text": "Lightning Roulette", "wait_time": 20, "screenshot_name": "Lightning Roulette_MX"},
                {"alt_text": "Crazy Pachinko", "wait_time": 20, "screenshot_name": "Crazy Pachinko_MX"},
                {"alt_text": "Monopoly Live", "wait_time": 20, "screenshot_name": "Monopoly Live_MX"},
                {"alt_text": "Crazy Time", "wait_time": 20, "screenshot_name": "Crazy Time_MX"},
                {"alt_text": "Football studio", "wait_time": 20, "screenshot_name": "Football studio_MX"},
                {"alt_text": "Gold Vault Roulette", "wait_time": 20, "screenshot_name": "Gold Vault Roulette_MX"},
                {"alt_text": "Dream Catcher", "wait_time": 20, "screenshot_name": "Dream Catcher_MX"},
                {"alt_text": "Golden Wealth Baccarat", "wait_time": 20, "screenshot_name": "Golden Wealth Baccarat_MX"},
                {"alt_text": "Dead or Alive Saloon", "wait_time": 20, "screenshot_name": "Dead or Alive Saloon_MX"},
                {"alt_text": "Football Studio Dice", "wait_time": 20, "screenshot_name": "Football Studio Dice_MX"},
                {"alt_text": "Extra Chilli Epic Spins", "wait_time": 20, "screenshot_name": "Extra Chilli Epic Spins_MX"},
            ]
        },





        # Добавьте аналогично другие ГЕО
    }

    # Шаг 1: Запускаем Surfshark
    launch_surfshark()

    # Перебираем каждое ГЕО из списка
    for geo_image_path, data in geo_data.items():
        geo_name = os.path.splitext(geo_image_path)[0]  # Извлекаем имя ГЕО без расширения
        print(f"Тестирование для ГЕО: {geo_name}")
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
                registration_data=data["registration"],
                geo_name=geo_name
            )
            print(f"Тест для {geo_name} завершён.\n")
            print(f"Тест для {geo_image_path} завершён.\n")
