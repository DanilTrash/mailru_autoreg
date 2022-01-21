from io import BytesIO
from time import sleep

from selenium.common import exceptions
from selenium.webdriver import ActionChains, Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from logger import logger
from captcha_solver import CaptchaServiceError, CaptchaSolver, SolutionTimeoutError
from PIL import Image

LOGGER = logger('browser')


class Browser:
    def __init__(self, proxy=None):
        self.options = ChromeOptions()
        # self.options.add_argument('--headless')
        if proxy:
            self.options.add_argument(f'--proxy-server={proxy}')
        self.driver = Chrome(options=self.options)

    def _find_fields(self):
        self.driver.get('https://account.mail.ru/signup')
        try:
            f_name_xpath = '//*/input[@id="fname"]'
            WebDriverWait(self.driver, 10).until(
                lambda d: self.driver.find_element_by_xpath(f_name_xpath), 'unable to find f_name_xpath'
            )
            return True
        except exceptions.TimeoutException as error:
            LOGGER.error(error)
            return False

    def _pass_phone_input(self):
        try:
            skip_button_xpath = '//*/button[text()="Пропустить"]'
            WebDriverWait(self.driver, 10).until(
                lambda d: self.driver.find_element_by_xpath(skip_button_xpath)).click()
            return True
        except Exception as error:
            LOGGER.error(error)
            return False

    def _input_fields(self, f_name, l_name, nickname, password):
        try:
            f_name_xpath = '//*/input[@id="fname"]'
            WebDriverWait(self.driver, 10).until(
                lambda d: self.driver.find_element_by_xpath(f_name_xpath), 'unable to find f_name_xpath'
            ).send_keys(f_name)
            l_name_xpath = '//*/input[@id="lname"]'
            WebDriverWait(self.driver, 10).until(
                lambda d: self.driver.find_element_by_xpath(l_name_xpath), 'unable to find l_name_xpath'
            ).send_keys(l_name)
            username_xpath = '//*/input[@name="username"]'
            WebDriverWait(self.driver, 10).until(
                lambda d: self.driver.find_element_by_xpath(username_xpath), 'unable to find username_xpath'
            ).send_keys(nickname)
            password_xpath = '//*/input[@name="password"]'
            WebDriverWait(self.driver, 10).until(
                lambda d: self.driver.find_element_by_xpath(password_xpath), 'unable to find password_xpath'
            ).send_keys(password)
            rep_password_xpath = '//*/input[@name="repeatPassword"]'
            WebDriverWait(self.driver, 10).until(
                lambda d: self.driver.find_element_by_xpath(rep_password_xpath), 'unable to find rep_password_xpath'
            ).send_keys(password)
            return True
        except exceptions.TimeoutException as error:
            LOGGER.error(error)
            return False

    def _birthday(self):
        try:
            birth_day_xapth = '//*/div[@data-test-id="birth-date"]/div[1]'
            month_xapth = '//*/div[@data-test-id="birth-date"]/div[3]'
            year_xapth = '//*/div[@data-test-id="birth-date"]/div[5]'
            birth_day_element = WebDriverWait(self.driver, 10).until(
                lambda d: self.driver.find_element_by_xpath(birth_day_xapth), 'unable to find birth_day_xapth'
            )
            month_element = WebDriverWait(self.driver, 10).until(
                lambda d: self.driver.find_element_by_xpath(month_xapth), 'unable to find birth_day_xapth'
            )
            year_element = WebDriverWait(self.driver, 10).until(
                lambda d: self.driver.find_element_by_xpath(year_xapth), 'unable to find birth_day_xapth'
            )
            action = ActionChains(self.driver)
            action.move_to_element(birth_day_element)
            action.click()
            action.send_keys(Keys.ENTER)
            action.move_to_element(month_element)
            action.click()
            action.send_keys(Keys.ENTER)
            action.move_to_element(year_element)
            action.click()
            action.send_keys(Keys.ENTER)
            action.move_to_element(self.driver.find_element_by_xpath('//*/label[@data-test-id="gender-male"]/div'))
            action.click()
            action.perform()
            return True
        except Exception as error:
            LOGGER.exception(error)
            return False

    def _first_step_submit(self):
        self.driver.find_element_by_xpath('//*/form/button[@data-test-id="first-step-submit"]').click()

    def _send_qrcode(self):
        captcha_answer = None
        solver = CaptchaSolver('rucaptcha', api_key='42a3a6c8322f1bec4b5ba84b85fdbe2f')
        raw_data = open('captcha.png', 'rb').read()
        while captcha_answer is None:
            print('solving captcha')
            try:
                captcha_answer = solver.solve_captcha(raw_data, recognition_time=80)
                return captcha_answer
            except CaptchaServiceError as error:
                LOGGER.error(error)

    def _solve_qrcode(self):
        try:
            captcha_question_xpath = '//*/img[@data-test-id="captcha-image"]'
            captcha_element = WebDriverWait(self.driver, 20).until(
                lambda d: self.driver.find_element_by_xpath(captcha_question_xpath), 'unable to find captcha_element'
            )
            sleep(5)
            location = captcha_element.location_once_scrolled_into_view
            png = self.driver.get_screenshot_as_png()
            left = location['x']
            top = location['y']
            right = location['x'] + captcha_element.size['width']
            bottom = location['y'] + captcha_element.size['height']
            im = Image.open(BytesIO(png))
            im = im.crop((left, top, right, bottom))
            im.save('captcha.png')
            captcha_answer_xpath = '//*/input[@data-test-id="captcha"]'
            self.driver.find_element_by_xpath(captcha_answer_xpath).send_keys(self._send_qrcode())
            return True
        except Exception as error:
            LOGGER.error(error)

    def _verification_button(self):
        self.driver.find_element_by_xpath('//*/button[@data-test-id="verification-next-button"]').click()
        try:
            WebDriverWait(self.driver, 10).until_not(
                lambda d: self.driver.find_element_by_xpath('//*/button[@data-test-id="verification-next-button"]')
                , 'captcha does`nt solved'
            )
            return True
        except Exception as error:
            LOGGER.info(error)
            return False

    def reg(self, f_name, l_name, nickname, password):
        if not self._find_fields():
            if not self._pass_phone_input():
                return False
        self._input_fields(f_name, l_name, nickname, password)
        self._birthday()
        self._first_step_submit()
        if not self._solve_qrcode():
            return False
        if self._verification_button():
            LOGGER.info(f'{nickname}@mail.ru:{password}')
            return True
