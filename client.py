from browser import Browser
from database import Data


class Client:
    def __init__(self):
        self.data = Data()
        self.nicknames = iter(self.data('nickname'))
        self.passwords = iter(self.data('password'))
        self.f_names = iter(self.data('f_name'))
        self.s_names = iter(self.data('s_name'))
        self.proxys = iter(self.data('proxy'))

    def reg(self):
        result = False
        self.browser = Browser(next(self.proxys))
        if self.browser.reg(next(self.f_names), next(self.s_names), next(self.nicknames), next(self.passwords)):
            result = True
        self.browser.driver.quit()
        return result


def main():
    client = Client()
    result = 0
    while result <= 15:
        if client.reg():
            result += 1


if __name__ == '__main__':
    main()
