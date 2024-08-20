import os
import re
import sys
import platform
from time import sleep

from consolemenu import *
from consolemenu.items import *
from pwinput import pwinput
from dotenv import load_dotenv, set_key

import ascii_text
from helpers import clear_scr
from rmit_login import login as rmit_login
from AEL import AEL

# Init AEL class
ael = AEL()
# Credentials file which stores the user's email and password
if not os.path.exists("credentials.txt"):
    with open("credentials.txt", "w") as file:
        file.write("EMAIL=\nPASSWORD=\n")
credentials_file = "credentials.txt"


# Wait for Keypress
if platform.system() == "Windows":
    import msvcrt
else:
    import tty
    import termios


def await_keypress(message):
    if message is None:
        message = "Ấn nút bất kì để tiếp tục..."
    print(message)
    if platform.system() == "Windows":  # For Windows
        msvcrt.getch()
    else:  # For Unix-like systems (Linux, macOS)
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def login_credentials(is_change=False):
    # Check for credentials.txt
    load_dotenv(credentials_file)
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    if (email == "" and password == "") or is_change:
        email = input("Email đăng nhập tài khoản \033[91mRMIT\033[0m: ")
        password = pwinput("Nhập mật khẩu: ")
    else:
        print(
            "Hình như bạn đăng nhập trước đó rồi\nSẽ load thông tin đăng nhập từ credentials.txt...\n"
        )

    clear_scr()
    print(
        "Trình duyệt Chrome sẽ mở, sau khi xong sẽ tự động tắt, "
        + "\033[33m"
        + "don't intefere with it"
        + "\033[0m"
    )
    print("\033[1m" + "Đang login..." + "\033[0m")
    if rmit_login(email, password):
        # Save to credentials.txt
        with open(credentials_file, "w") as file:
            set_key(credentials_file, "EMAIL", email)
            set_key(credentials_file, "PASSWORD", password)

        print("\033[92m" + "Thành công!" + "\033[0m")
        print(
            "\nĐăng nhập thành công! Đã lưu thông tin đăng nhập vào credentials.txt\nCookies đã được lưu vào cookies.json để được sử dụng tải sách\n\n"
        )
        await_keypress()

        return email, password
    else:
        # Clear credentials.txt i.e. Replace the values of EMAIL and PASSWORD with empty strings
        with open("credentials.txt", "r") as file:
            content = file.read()
        content = re.sub(r"(EMAIL=')[^']*(')", r"\1\2", content)
        content = re.sub(r"(PASSWORD=')[^']*(')", r"\1\2", content)
        with open("credentials.txt", "w") as file:
            file.write(content)

        print("\033[91m" + "Thất bại!" + "\033[0m")
        print(
            "Đăng nhập không được rồi, chắc sai pass thì phải? or Chrome was intefered...\n\n"
        )
        await_keypress()
        clear_scr()
        return None, None


def download_book():
    # Check if cookies are valid
    if not ael.validate_cookies():
        print(
            "\033[91m"
            + "Cookies không có hoặc hết hạn"
            + "\033[0m"
        )
        print("\033[1m" + "Phải đăng nhập mới tải được sách.\n" + "\033[0m")
        print("Bạn có muốn đăng nhập ngay bây giờ không? (nhập ký tự Y hoặc N)")
        print("[Y] Đăng nhập\n[N] Thoát")
        choice = input(">> ").lower()
        if choice == "y":
            clear_scr()
            if login_credentials() == (None, None):
                return
        else:
            return

    clear_scr()
    # Check cookie
    if ael.validate_cookies():
        print("\033[92m" + "Cookies sử dụng được!" + "\033[0m")
    userInput = input(
        "Nhập link sách, hoặc ID sách\nVí dụ: "
        + "\033[1m"
        + "https://www.accessengineeringlibrary.com/content/book/9781260457223"
        + "\033[0m"
        + " hoặc "
        + "\033[1m"
        + "9781260457223"
        + "\033[0m"
        + "\n\n>> "
    )

    # Check whether the URL is from accessengineeringlibrary.com
    book_title = ael.get_title(userInput)
    if type(book_title) == str:
        print("Đã tìm được sách!")
        print(f"Title: {book_title}")
        print("Đang tải từng chapters...")
    else:
        print(
            "Không tìm thấy sách, có thể là do link không hợp lệ hoặc ID sách không đúng"
        )
        await_keypress()
        exit()

    # Get the book's number of chapters
    ael.get_chapters()

    # Download the chapters using threading
    ael.download_chapters(use_threading=True)

    # Merge the chapters
    response_ael = ael.merge_chapters()
    if response_ael[0]:
        print("Merge sách thành công!")
        print(response_ael[1])
        await_keypress()
    else:
        await_keypress("Merge sách thất bại.")


def clean_up():
    ael.clean_up()
    print("\033[92m" + "Thành công!" + "\033[0m")
    await_keypress("Đã dọn xong rác, ấn nút bất kì để tiếp tục...")


if __name__ == "__main__":

    def say_hello():
        print("Hello!")

    menu = ConsoleMenu(
        ascii_text.title,
        ascii_text.description,
        prologue_text="Chọn một trong các lựa chọn dưới đây:",
        exit_option_text="\033[91m" + "Thoát" + "\033[0m",
    )
    main_function_1 = FunctionItem("\033[92m" + "Tải sách" + "\033[0m", download_book)
    main_function_2 = FunctionItem("Thay đổi tài khoản RMIT", login_credentials, [True])
    main_function_3 = FunctionItem("Dọn file rác " + "\033[36m" + "(Xóa file trong folder segments)" + "\033[0m", clean_up)
    
    # A SelectionMenu constructs a menu from a list of strings
    selection_menu = SelectionMenu(
        title=ascii_text.settings,
        strings=["Ngôn ngữ", "Lưu tài khoản vào máy", "Enable Threading"],
        exit_option_text="\033[91m" + "Thoát" + "\033[0m",
    )

    # Settings sub-menu
    submenu_item = SubmenuItem("Cài đặt", selection_menu, menu)

    menu.append_item(main_function_1)
    menu.append_item(main_function_2)
    menu.append_item(main_function_3)
    menu.append_item(submenu_item)

    menu.show()
