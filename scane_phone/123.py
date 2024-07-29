import logging
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

logging.basicConfig(level=logging.DEBUG)

options = Options()
options.headless = True
driver_path = '/usr/local/bin/geckodriver'

try:
    logging.debug("Starting Firefox WebDriver")
    driver = webdriver.Firefox(service=Service(driver_path), options=options)
    driver.get('https://www.google.com')
    print("Page title is:", driver.title)
    driver.quit()
except Exception as e:
    logging.error(f"Error: {e}")
