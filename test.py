import time

X = {}


def set():
    X[time.time()] = 1


def get():
    global X
    return X


if __name__ == '__main__':
    while True:
        time.sleep(1)
        set()
        print(X)
