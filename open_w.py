import os
import time
import pyautogui
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_auto_update.chrome_app_utils import ChromeAppUtils
from webdriver_auto_update.webdriver_manager import WebDriverManager

def update_chromedriver():
    chrome_app_utils = ChromeAppUtils()
    chrome_app_version = chrome_app_utils.get_chrome_version()
    driver_directory = ""
    driver_manager = WebDriverManager(driver_directory)
    driver_manager.main()
def access_number(driver,number):
    driver.get(f'https://wa.me/{number}')
    time.sleep(5)
    pyautogui.press('enter')
    continue_chat = WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.XPATH, '//span[contains(text(),"Continue to Chat")]')))
    continue_chat.click()
    time.sleep(5)
    web_use = WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.XPATH, '//span[contains(text(),"use WhatsApp Web")]')))
    web_use.click()


def create_user_data_dir(dir_name):
    user_data_dir = os.path.join(os.path.expanduser('~'), dir_name)
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)
    return user_data_dir
def send_whatsapp_message(number, message, url_file_link):
    update_chromedriver()
    user_profile_dir = "whatsapp_automation_profile"
    user_data_dir = create_user_data_dir(user_profile_dir)
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={user_data_dir}")
    chromedriver_path = 'chromedriver.exe'
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service,options = chrome_options)
    driver.get("https://web.whatsapp.com/")
    my_downloaded_file = save_pdf(url_file_link, driver)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "canvas")))
    except TimeoutException as e:
        print("QR code element not found. Assuming login is complete.")
    finally:
        WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.ID, "side")))
        access_number(driver, number)
        send_msg_pdf(driver, my_downloaded_file, message)
        os.remove(my_downloaded_file)

def send_msg_pdf(driver,my_file,my_message):
    clipper_icon = WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.XPATH, "//span[@data-icon = 'plus']")))
    clipper_icon.click()
    document_click = WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Document')]")))
    document_click.click()
    time.sleep(5)
    pyautogui.write(my_file)
    pyautogui.press('enter')
    caption_bar = WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.XPATH, "//div[@aria-placeholder = 'Add a caption']")))
    caption_bar.click()
    caption_bar.send_keys(my_message)
    caption_bar.send_keys(Keys.ENTER)
    time.sleep(10)
    driver.close()

def save_pdf(url, driver):
    original_handle = driver.current_window_handle
    driver.execute_script("window.open('');")
    handles = driver.window_handles
    driver.switch_to.window(handles[-1])
    driver.get(url)
    pdf_down = WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '.pdf')]")))
    href = pdf_down.get_attribute('href')
    filename = href.split('/')[-1]
    pdf_down.click()
    WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Downloaded')]")))
    time.sleep(20)
    download_path = os.path.join(os.path.expanduser('~'), 'Downloads')
    downloaded_file = os.path.join(download_path, filename)
    driver.close()
    driver.switch_to.window(original_handle)
    return downloaded_file


