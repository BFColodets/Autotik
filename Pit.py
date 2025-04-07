from playwright.sync_api import Page, TimeoutError
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import random


class Pit:
    def __init__(self, page: Page):
        self.page = page
        self.hp = None
        self.trophy = None
        self.hunger = 100
        self.last_stage = None
        self.eating_time = datetime.now() - timedelta(hours=4)
        self.is_healing_spring = False

    def click_button(self, title, timeout: float = 5000) -> None:
        try:
            button = self.page.wait_for_selector(
                f'button[title="{title}"]',
                timeout=timeout
            )
            button.scroll_into_view_if_needed()
            button.click()
            print(f"Кнопка '{title}' успешно нажата")
        except TimeoutError:
            print(f"Кнопка '{title}' не найдена за {timeout / 1000} сек")

    def get_messages_text(self):
        html = self.page.content()
        soup = BeautifulSoup(html, "html.parser")
        messages = soup.find_all('span', {'class': 'MessageText'})
        messages = [msg.get_text(strip=True) for msg in messages]
        messages.reverse()
        return messages

    def get_buttons_text(self):
        html = self.page.content()
        soup = BeautifulSoup(html, "html.parser")
        messages = soup.find_all('span', {'class': 'vkuiButton__content'})
        messages = [msg.get_text(strip=True) for msg in messages]
        messages.reverse()
        return messages

    def get_hp(self, input_str: str):
        print(input_str)
        hp_index = input_str.find("HP:")
        if hp_index == -1:
            return ""

        start_index = hp_index + 4  # Смещение после 'HP:'
        end_index = input_str.find('■')

        # Возвращаем срез, обрезая его, если строка короче
        return [int(hp) for hp in input_str[start_index:end_index].split('/')]

    def get_trophy(self, input_str: str):
        trophy_index = input_str.find("Трoфеев:")
        if trophy_index == -1:
            return ""

        start_index = trophy_index + 9  # Смещение после 'HP:'
        end_index = input_str.find("HP:")

        # Возвращаем срез, обрезая его, если строка короче
        return int(input_str[start_index:end_index])

    def get_bait(self, input_str: str):
        bait_index = input_str.find("Нaживки осталоcь:")
        if bait_index == -1:
            return ""

        start_index = bait_index + 18  # Смещение после 'HP:'
        end_index = start_index + 5

        return int(input_str[start_index:end_index])

    def get_hunger(self, input_str: str):
        hunger_index = input_str.find("%")
        if hunger_index == -1:
            return ""

        start_index = hunger_index - 3  # Смещение после 'HP:'
        end_index = hunger_index

        return int(input_str[start_index:end_index])

    def get_time(self, input_str: str):
        time_index = input_str.find("Требуется времени:")
        start_index = time_index + 19
        end_index = input_str.find("минут")

        return int(input_str[start_index:end_index])

    def get_injuries(self, input_str: str):
        injuries_index = input_str.find("Количество травм:")
        start_index = injuries_index + 18
        end_index = input_str.find("Излечить")
        return int(input_str[start_index:end_index])

    def get_stay_time(self, input_str: str):
        time_index = input_str.find("Время отдыха:")
        start_index = time_index + 14
        end_index = input_str.find("час")
        return int(input_str[start_index:end_index])

    def get_inventory(self, input_str: str):
        inventory_index = input_str.find("Осталось места в инвентаре:")
        start_index = inventory_index
        return int(input_str[start_index::].split(':')[1])

    def explore(self):
        messages = self.get_messages_text()
        for message in messages:
            if 'HP' in message or 'Трoфеев' in message:
                self.hp = self.get_hp(message)
                if 'Трoфеев' in message:
                    self.trophy = self.get_trophy(message)
                    break
                break

        if self.hp[1] - self.hp[0] != 0:
            self.click_button('Отдых')
            if self.hunger < 80:
                self.click_button('Готовка')

        self.page.wait_for_timeout(5 * 1000)
        self.page.wait_for_selector('button[title="Исследовать уровень"]', timeout=300 * 1000)

        def go_lvl():
            self.click_button('Исследовать уровень')

            self.page.wait_for_timeout(5 * 1000)

            messagess = self.get_messages_text()
            for msg in messagess:
                if 'Скорость исследования' in msg:
                    self.hunger = self.get_hunger(msg)
                    break
            print(self.hunger)

        if self.hunger > 30:
            go_lvl()
        else:
            if datetime.now() - self.eating_time > timedelta(hours=4):
                print("Покорми бля")
                self.eating()
            else:
                go_lvl()

    def fight(self):
        self.click_button('В бой')
        print("Хуярь его я пока не умею")
        input()

    def to_pit(self):
        self.click_button('В колодец')

    def fishing(self):
        def fish_wait():
            self.click_button('Закинуть удочку')
            self.page.wait_for_selector('button[title="Подсечь"]', timeout=300 * 1000)
            self.click_button('Подсечь')

        while True:
            self.page.wait_for_timeout(1000)
            messages = self.get_messages_text()
            for message in messages:
                if 'Нaживки осталоcь' in message:
                    bait = self.get_bait(message)
                    if bait != 0:
                        fish_wait()
                        break
                    else:
                        self.click_button('Прeрвать рыбaлку')
                        return None
            else:
                break

    def nahui(self):
        self.click_button('Уйти')

    def search(self):
        messages = self.get_messages_text()
        for message in messages:
            if 'Вы обнаруживаете мертвое тело одного из погибших искателей приключений.' in message:
                self.nahui()
                return None
            if 'Рядом уже нечего обыскивать!' in message:
                return None
            elif not (self.page.query_selector(f'button[title="Уйти"]')):
                self.click_button('Обыскать')
                return None

    def wait_event(self):
        messages = self.get_messages_text()
        for message in messages:
            if 'Требуется времени' in message:
                time = self.get_time(message)
                if time <= 10:
                    self.page.wait_for_timeout(((time * 60) + 30) * 1000)
                    self.click_button('Покинуть')

    def sanctuary(self):
        self.click_button('Изучить святилище')

    def runes_square(self):
        self.click_button('Уйти')

    def open(self):
        self.click_button('Открыть')

    def big_chest(self):
        self.click_button('Попытаться открыть силой')

    def ruins(self):
        messages = self.get_messages_text()

        for message in messages:
            if 'В этих руинах бoльше нет дoбычи!' in message:
                self.click_button('Прервать поиск')
                break

    def free_yourself(self):
        self.click_button('Освободиться')

    def maze(self):
        self.click_button('Покинуть лабиринт')
        self.page.wait_for_timeout(2 * 1000)
        self.click_button('Покинуть лабиринт')

    def take(self):
        self.click_button('Собрать')

    def down(self):
        self.click_button('Спуститься')

    def doors(self):
        buttons = ['Левая', 'Правая', 'Центральная']
        button = random.choice(buttons)
        button.click(button)

        self.page.wait_for_timeout(5 * 1000)

        buttons = [bt for bt in self.get_buttons_text() if bt.startswith('Открыть')]
        button = random.choice(buttons)
        button.click(button)

    def skin_them(self):
        self.click_button('Освежевать')
        self.page.wait_for_timeout(5 * 1000)

    def eating(self):
        print('Ищу портал')
        self.page.wait_for_selector('button[title="В портал"]', timeout=30 * 1000)
        self.click_button('В портал')

        print("Иду в портовый квартал")
        self.page.wait_for_selector('button[title="Портовый квартал"]', timeout=30 * 1000)
        self.page.wait_for_timeout(1000)
        self.click_button('Портовый квартал')

        print('Захожу в таверну')
        self.page.wait_for_selector('button[title="Таверна"]', timeout=30 * 1000)
        self.page.wait_for_timeout(1000)
        self.click_button('Таверна')

        print('Заказываю еду')
        self.page.wait_for_selector('button[title="Заказать еду"]', timeout=30 * 1000)
        self.page.wait_for_timeout(1000)
        self.click_button('Заказать еду')

        print('Ем')
        self.page.wait_for_selector('button[title="Дешевый обед"]', timeout=30 * 1000)
        self.page.wait_for_timeout(1000)
        self.click_button('Дешевый обед')
        self.hunger = 100

        print('Иду обратно в город')
        self.page.wait_for_timeout(2000)
        self.click_button('Вернуться')

    def ways(self):
        self.click_button('Уйти')

    def inspect(self):
        self.click_button('Осмотреть')

    def seller(self):
        self.click_button('Уйти')

    def healing_spring(self):
        self.page.wait_for_selector('button[title="Покинуть"]')
        self.click_button('Покинуть')

    def hunting(self):
        self.click_button('Прервать охоту')

    def up(self):
        self.click_button('Улучшить броню')

    def next(self):
        self.click_button('Продoлжить')

    def get_stage(self):
        """Определяет текущую стадию игры и возвращает соответствующий метод"""
        stage_to_method = {
            "Собрать": self.take,
            "Освежевать": self.skin_them,
            "Осмотреть": self.inspect,
            "Исследовать уровень": self.explore,
            "В бой": self.fight,
            "В колодец": self.to_pit,
            "Закинуть удочку": self.fishing,
            "Обыскать": self.search,
            "⛔1": self.runes_square,
            "✅1": self.runes_square,
            "Покинуть": self.wait_event,
            "Изучить святилище": self.sanctuary,
            "1": self.nahui,
            "Открыть": self.open,
            "Прервать поиск": self.ruins,
            "Попытаться открыть силой": self.big_chest,
            "Освободиться": self.free_yourself,
            "Покинуть лабиринт": self.maze,
            "Спуститься": self.down,
            "Левая": self.doors,
            "Запад": self.ways,
            "Другой товар": self.seller,
            "Покинуть источник": self.healing_spring,
            "Прервать охоту": self.hunting,
            "Полить растение": self.nahui,
            "Вставить камень судьбы": self.nahui,
            "Открыть силой": self.nahui,
            "Улучшить броню": self.up,
            "Продoлжить": self.next
        }

        button_triggers = list(stage_to_method)

        for button_title in button_triggers:
            button = self.page.query_selector(f'button[title="{button_title}"]')
            if button:
                print(button_title)
                one_using = ['Собрать', 'Освежевать', 'Осмотреть']
                if self.last_stage in one_using and button_title in one_using:
                    continue
                else:
                    print(f"Определена стадия: {button_title}")
                    self.last_stage = button_title
                    return stage_to_method.get(button_title), button_title

            # Пауза между циклами проверки
            self.page.wait_for_timeout(1000)

        print("Не удалось определить стадию")
        return None, None
