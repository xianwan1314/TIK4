import os


def cls():
    if os.name == 'nt':
        os.system('cls')
    elif os.name == 'posix':
        os.system('clear')
    else:
        print("Ctrl + L to clear the window")


def dir_has(path, endswith):
    for v in os.listdir(path):
        if v.endswith(endswith):
            return True
    return False
