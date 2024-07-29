import argparse
import sys
import os
import asyncio
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from concurrent.futures import ThreadPoolExecutor
import traceback

# Функция для проверки номера телефона на сайте
def check_phone_number_on_site(phone_number, site_url):
    try:
        options = Options()
        options.headless = True
        # Укажите путь к локально установленному geckodriver
        driver_path = '/usr/local/bin/geckodriver'
        driver = webdriver.Firefox(service=Service(driver_path), options=options)
        driver.get(site_url)
        
        # Найдите поле ввода телефона и введите номер (нужно изменить под структуру конкретного сайта)
        phone_input = driver.find_element(By.ID, 'phone_input_field')
        phone_input.send_keys(phone_number)
        phone_input.send_keys(Keys.RETURN)
        
        # Обработайте ответ сайта (нужно изменить под структуру конкретного сайта)
        try:
            error_message = driver.find_element(By.ID, 'error_message')
            result = False  # Номер не зарегистрирован
        except:
            result = True  # Номер зарегистрирован
        driver.quit()
        return (phone_number, site_url, result)
    except Exception as e:
        print(f"Error checking phone number {phone_number} on site {site_url}: {e}")
        traceback.print_exc()
        return (phone_number, site_url, None)

# Асинхронная функция для обработки номеров телефонов
async def process_phone_numbers(phone_numbers, sites, log_dir, max_workers):
    # Создание директории для логов, если она не существует
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Создание пула потоков
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        tasks = []
        for phone_number in phone_numbers:
            for site_url in sites:
                tasks.append(loop.run_in_executor(executor, check_phone_number_on_site, phone_number, site_url))
        results = await asyncio.gather(*tasks)

    # Запись результатов в лог-файлы
    for phone_number, site_url, is_registered in results:
        log_file_path = os.path.join(log_dir, f"{phone_number}.txt")
        with open(log_file_path, 'a') as log_file:
            if is_registered is None:
                log_file.write(f"Site: {site_url} - Error occurred\n")
            else:
                log_file.write(f"Site: {site_url} - Registered: {is_registered}\n")
            print(f"Phone number {phone_number} registered on {site_url}: {is_registered}")

# Основная функция
def main(phone_file, site_file, log_dir, max_workers):
    # Чтение номеров телефонов из файла
    with open(phone_file, 'r') as f:
        phone_numbers = [line.strip() for line in f.readlines()]
    
    # Чтение URL сайтов из файла
    with open(site_file, 'r') as f:
        sites = [line.strip() for line in f.readlines()]

    # Запуск асинхронной обработки
    asyncio.run(process_phone_numbers(phone_numbers, sites, log_dir, max_workers))

# Функция для отображения помощи
def display_help():
    print("Usage: python script.py --phones PHONES_FILE --sites SITES_FILE --log_dir LOG_DIRECTORY --workers MAX_WORKERS")
    print("Arguments:")
    print("  --phones PHONES_FILE  Path to the file containing phone numbers")
    print("  --sites SITES_FILE    Path to the file containing site URLs")
    print("  --log_dir LOG_DIRECTORY    Path to the directory for log files")
    print("  --workers MAX_WORKERS  Maximum number of concurrent threads")

# Настройка аргументов командной строки
parser = argparse.ArgumentParser(description="Phone number registration checker")
parser.add_argument('--phones', type=str, required=True, help="Path to the file containing phone numbers")
parser.add_argument('--sites', type=str, required=True, help="Path to the file containing site URLs")
parser.add_argument('--log_dir', type=str, required=True, help="Path to the directory for log files")
parser.add_argument('--workers', type=int, default=4, help="Maximum number of concurrent threads")
args = parser.parse_args()

# Если запрашивается помощь, отображаем ее
if '--help' in sys.argv:
    display_help()
else:
    # Запуск основной функции
    main(args.phones, args.sites, args.log_dir, args.workers)
