from playwright.sync_api import sync_playwright, Page, TimeoutError
import json
import os
from Pit import Pit


class Bot:
    def __init__(self, login=None, password=None, proxy=None, headless=False):
        self.login = login
        self.password = password
        self.proxy = proxy
        self.TARGET_URL = 'https://vk.com/im/convo/-182985865?entrypoint=list_all'
        self.QR_TEXT = 'Наведите камеру устройства на QR-код'
        self.COOKIES_FILE = 'vk_cookies.json'
        self.browser, self.page, self.context = None, None, None
        self.headless = headless
        self.playwright = sync_playwright().start()
        self.last_stage = None

    def start_browser(self):
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context()

        if cookies := self.load_cookies():
            self.context.add_cookies(cookies)
            print('Загружены сохраненные куки')

        self.page = self.context.new_page()
        self.page.goto(self.TARGET_URL)
    def __enter__(self):
        self.playwright = sync_playwright().start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def load_cookies(self):
        if os.path.exists(self.COOKIES_FILE):
            with open(self.COOKIES_FILE, 'r') as f:
                return json.load(f)
        return None

    def save_cookies(self):
        cookies = self.context.cookies()
        with open(self.COOKIES_FILE, 'w') as f:
            json.dump(cookies, f)

    def auth_vk(self):
        self.start_browser()
        if self.page.url != self.TARGET_URL:
            # Основной процесс авторизации
            self.page.goto('https://vk.com')

            try:
                # Проверяем наличие текста с QR-кодом
                self.page.wait_for_selector(f"text='{self.QR_TEXT}'", timeout=5000)
                print('Обнаружена страница авторизации с QR-кодом')

                # Ждем завершения авторизации
                print('Сканируйте QR-код через мобильное приложение VK')
                print('Или нажмите "Войти другим способом" в браузере')
                self.page.wait_for_navigation(url='https://vk.com/feed', timeout=180000)

            except Exception as e:
                # Если текст не найден - проверяем текущий URL
                if self.TARGET_URL in self.page.url:
                    print('Уже авторизованы и находимся на целевой странице')
                else:
                    print(f'Текст QR-кода не найден: {e}')
                    print('Проверяем статус авторизации...')
                    if 'feed' in self.page.url:
                        print('Обнаружена страница ленты новостей - авторизация успешна')
                    else:
                        print('Требуется ручная авторизация!')
                        input('После завершения авторизации нажмите Enter...')

            # Сохраняем куки в любом случае
            cookies = self.context.cookies()
            with open(self.COOKIES_FILE, 'w') as f:
                json.dump(cookies, f)
            print('Куки обновлены')

            # Финалный переход на целевую страницу
            if self.TARGET_URL not in self.page.url:
                self.page.goto(self.TARGET_URL)
                print(f'Переход на целевую страницу: {self.TARGET_URL}')

            # Проверка результата
            if self.TARGET_URL in self.page.url:
                print('Успешное завершение!')
                return True
            else:
                print(f'Не удалось перейти на целевую страницу. Текущий URL: {self.page.url}')
                return False
        else:
            print('Успешная авторизация через куки')
            return True

    def start(self):
        if not (self.auth_vk()):
            print("Ошбибка авторизации")
            exit()
        else:
            pit = Pit(page=self.page)
            while True:
                stage_method, stage = pit.get_stage()
                if stage:
                    if stage == self.last_stage:
                        self.page.wait_for_timeout(2000)
                        stage_method, stage = pit.get_stage()
                    if stage:
                        print(stage)
                        stage_method()
                        self.last_stage = stage
                        self.page.wait_for_timeout(1000)
                else:
                    self.page.wait_for_timeout(1000)



# pit = Pit(bot.page)
# print(pit.get_bait('Лодка медленно пoкачиваетcя нa воде...🐛Нaживки осталоcь: 2'))


