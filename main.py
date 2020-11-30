from bs4 import BeautifulSoup # парсинг HTML
import datetime  # получение дня недели
import requests # получение страницы с расписанием и HTML
import re # регулярные выражения


class GroupError(Exception):
    # исключение для обработки номера группы
    def __init__(self, text):
        self.txt = text


class Parser():
    @staticmethod
    def get_bs(group_number): # получает объект BS4, содержащий страницу с расписанием "group_number" группы

        # изменяет номер группы для корректного получения расписания у совмещённых групп
        if group_number in ("331", "332"):
            group_number = "331%2B332"
        elif group_number in ("341", "342"):
            group_number = "341%2B342"
        elif group_number in ("531%2B532"):
            group_number = "531%2B532"
        bs_ = None
        # обработка исключений при получении страницы и ее html кода
        # возвращает ошибку, когда происходит редирект на страницу со списком факультетов
        # т.к. неправильно указан номер группы
        url = "https://www.sgu.ru/schedule/knt/do/" + group_number
        try:
            page = requests.get(url)
            if page.url == 'https://www.sgu.ru/schedule':
                raise GroupError('Ошибка в номере группы')
        except GroupError:
            print('Error: Ошибка в номере группы')
        else:
            try:
                bs_ = BeautifulSoup(page.text, "html.parser")
            except Exception as e:
                print(e)
        return bs_

    def get_schedule(self, bs_obj):
        # получает список пар по строчкам, убирает html тэги и прочий мусор.
        # Так же убирает числитель, если неделя - знаменатель и наоборот.
        # возвращает ошибку, если bs_obj - пустой
        schedule_ = []
        week = self.get_date()[1] % 2
        try:
            for el in bs_obj.find_all('td', id=re.compile("^[1-8]_[1-6]")):
                el = el.get_text(' ') if el.contents != [] else '-'
                if el.find(" знам. ") != -1:
                    if week == 0:
                        el = el.split(" знам. ")[0]
                    else:
                        el = el.split(" знам. ")[1]
                if "Иностранный язык" in el:
                    el = "пр. Иностранный язык"
                schedule_.append(el)
        except AttributeError:
            print('Error: Пустой файл bs4')
        except Exception as e:
            print(e)
        return schedule_

    def get_day_schedule(self, _schedule, index):
        # составляет список пар на сегодняшний день
        day = self.get_date()[2]
        day_schedule_ = []
        for i in range(0, 7):
            if index is True:
                el = str(i + 1) + ') ' + _schedule[i*6 + day] # с индексом
            else:
                el = _schedule[i * 6 + day] # без индекса в начале
            day_schedule_.append(el)
        return day_schedule_

    @staticmethod
    def print_schedule(_schedule):
        # выводит расписание
        for el in _schedule:
            print(el)

    @staticmethod
    def get_date():
        # получает Год, номер недели, день недели(0-6)
        return datetime.datetime.now().isocalendar()


if __name__ == "__main__":
    parser = Parser()
    bs = parser.get_bs('181')
    schedule = parser.get_schedule(bs)
    day_schedule = parser.get_day_schedule(schedule, True)
    parser.print_schedule(day_schedule)
