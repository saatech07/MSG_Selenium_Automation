import re
import sqlite3
from open_w import send_whatsapp_message
from check_new_msg import checking_msg_received


def check_new_msgs():
    checking_msg_received()

def check_new_row():
    conn = sqlite3.connect('WA_Automation.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS WA_data(id INTEGER PRIMARY KEY AUTOINCREMENT,number text, message text, url text)''')
    cursor.execute("SELECT COUNT(*) FROM WA_data")
    original_count = cursor.fetchone()[0]
    main(conn, cursor)
    cursor.execute("SELECT COUNT(*) FROM WA_data")
    new_count = cursor.fetchone()[0]
    if new_count > original_count:
        my_last_row = get_last_added_row(cursor)
        number, message, url = my_last_row
        send_whatsapp_message(number,message, url)
    else:
        pass
def get_last_added_row(cursor):
    cursor.execute("SELECT number, message, url FROM WA_data ORDER BY rowid DESC LIMIT 1")
    last_row = cursor.fetchone()
    return last_row
def main(conn, cursor):
    numb = input("Enter Your Mobile number (No spaces, Must start with country code): ")
    number = re.sub(r"[ \-]", "", numb)
    message = input("Enter the message to send: ")
    url = input("Enter document url: ")
    row_data = [(number,message,url)]
    cursor.executemany("INSERT OR IGNORE INTO WA_data(number, message, url) VALUES (?,?,?)", row_data)
    conn.commit()
if __name__ == '__main__':
    user_checking = input("Do you wanna check for new row (0) or new messages received (1): ")
    if user_checking == '0':
        check_new_row()
    elif user_checking == '1':
        check_new_msgs()
    else:
        print(f"Choose either 0 or 1!")