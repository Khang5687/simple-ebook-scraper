import platform
import subprocess


def clear_scr():
    """
    Clear the screen.
    """
    if platform.system() == "Windows":
        subprocess.check_call("cls", shell=True)
    else:
        print(subprocess.check_output("clear").decode())
