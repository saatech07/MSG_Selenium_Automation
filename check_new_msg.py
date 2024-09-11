import os
import sqlite3
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_auto_update.chrome_app_utils import ChromeAppUtils
from webdriver_auto_update.webdriver_manager import WebDriverManager


def update_chromedriver():
    chrome_app_utils = ChromeAppUtils()
    chrome_app_utils.get_chrome_version()
    driver_directory = ""
    driver_manager = WebDriverManager(driver_directory)
    driver_manager.main()


def create_user_data_dir(dir_name):
    user_data_dir = os.path.join(os.path.expanduser('~'), dir_name)
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)
    return user_data_dir


def checking_msg_received():
    update_chromedriver()
    user_profile_dir = "whatsapp_automation_profile"
    user_data_dir = create_user_data_dir(user_profile_dir)
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={user_data_dir}")
    chromedriver_path = 'chromedriver.exe'
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://web.whatsapp.com/")
    driver.maximize_window()
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "canvas")))
    except TimeoutException as e:
        print("QR code element not found. Assuming login is complete.")
    finally:
        WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.ID, "side")))
        new_message(driver)
def new_message(driver):
    new_msg_element = WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//div[@id='side']//span[contains(@aria-label, 'unread message')]")))
    new_msg_text = new_msg_element.text
    new_msg_element.click()
    senders_number = get_sender_number(driver)
    new_messages = get_the_message(driver, new_msg_text)
    conn = sqlite3.connect('WA_Automation.db')
    cursor = conn.cursor()
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS new_msgs_received(id INTEGER PRIMARY KEY AUTOINCREMENT, number text, received_message text)''')
    for message in new_messages:
        row_data_received = [(senders_number, message)]
        cursor.executemany("INSERT OR IGNORE INTO new_msgs_received(number, received_message) VALUES (?,?)",
                           row_data_received)
        conn.commit()

def get_sender_number(driver):
    title_header_element = WebDriverWait(driver, 50).until(
        EC.presence_of_element_located((By.XPATH, "//div[@title='Profile details']")))
    title_header_element.click()
    sender_number_element = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//span[@class='x1jchvi3 x1fcty0u x40yjcy']")))
    sender_number = sender_number_element.text
    sender_number = ''.join(sender_number.split())
    close_span = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Close']")))
    close_span.click()
    return sender_number

def get_the_message(driver, num):
    div_elements = driver.find_elements(By.XPATH, "//div[@role='row']")
    div_elements.reverse()
    all_unread_messages = []
    for div_element in div_elements:
        message_element = div_element.find_element(By.XPATH, ".//span[@dir='ltr']/span[text()]")
        message_text = message_element.text
        if len(all_unread_messages) >= int(num):
            break
        else:
            all_unread_messages.append(message_text)
    return all_unread_messages