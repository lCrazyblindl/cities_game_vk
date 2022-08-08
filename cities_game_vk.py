from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from random import randint

# можно запустить генерацию городов еще раз, убрав коммент
# exec(open("list_of_cities.py").read())

# беру логопасс из файла, чтоб не показывать в коде
with open('credentials.txt') as file:
    login = file.readline()
    password = file.readline()


# беру сформированный заранее список городов к себе в массив
with open('cities.txt', encoding='UTF-8') as file:
    cities = file.read().splitlines()


# список допустимых букв для нового города
possible_characters = ['а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з', 'и', 'к', 'л', 'м', 'н', 'о',
                       'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'э', 'ю', 'я']


# для поиска CSS селектора, чтобы код был менее громоздким
def find_selector(text):
    needed_selector = browser.find_element(By.CSS_SELECTOR, text)
    return needed_selector


# вынес отдельно функцию для написания сообщения в чат
def type_message_in_chat(text):
    input_text_field = find_selector('#im_editable0')
    input_text_field.send_keys(text)
    send_button = find_selector('button[class="im-send-btn im-chat-input--send _im_send im-send-btn_send"]')
    send_button.click()


try:
    browser = webdriver.Chrome()
    browser.get("https://vk.com")
    # следующая строка для обхода капчи и предотвращения выпадения ошибок, если какой-то элемент не успел догрузиться
    browser.implicitly_wait(600)
    # логинимся
    login_input = find_selector('#index_email')
    login_input.send_keys(login)
    password_input = find_selector('input[name="password"]')
    password_input.send_keys(password)
    submit_pass_button = find_selector('div[class="vkc__Button__title"]')
    submit_pass_button.click()
    # захожу в сообщения
    messages = find_selector('#l_msg')
    messages.click()
    # ищу нужный чат
    test_chat = browser.find_element(By.XPATH, '//*[contains(text(), "QAA alpha")]')
    test_chat.click()
    # собираю участников чата в список
    time.sleep(2)
    members_button = find_selector('button[class="_im_chat_members im-page--members"]')
    members_button.click()
    members = []
    # i = 3 если есть кнопка add members и нужно убрать саму группу (не ответит), 1 в ином случае
    i = 3
    while True:
        member = find_selector(f'div .ChatSettingsMembersWidget__list > ul > li:nth-child({i}) > div.ListItem__main > div.Entity > div.Entity__main > div > a')
        members.append(member.get_attribute('href')[15::])
        if member == find_selector(f'div .ChatSettingsMembersWidget__list > ul > li:last-child > div.ListItem__main > div.Entity > div.Entity__main > div > a'):
            break
        i += 1
    close_members_button = find_selector('button[class="PopupHeader__closeBtn"]')
    close_members_button.click()
    used_cities = []
    losers = ['id471672657']
    type_message_in_chat('Я готов')
    # начинаем игру после команды старт
    while True:
        last_message = find_selector('div:last-child  > div.im-mess-stack--content > ul > li:last-child')
        if 'старт' not in last_message.text.lower():
            time.sleep(0.3)
        else:
            break
    # игра началась
    turns = 0
    leaving = False
    while True:
        time.sleep(0.5)
        last_message = find_selector('div:last-child  > div.im-mess-stack--content > ul > li:last-child')
        last_reporter_link = find_selector('div.im-mess-stack._im_mess_stack:last-child .im-mess-stack--pname > a')
        last_reporter = last_reporter_link.get_attribute('href')[15::]

        # если кто-то ушел, то добавить его в список выбывших и смотреть на предыдущее сообщение
        # если он последний, то уйти
        if 'ухожу' in last_message.text.lower():
            if last_reporter not in losers:
                losers.append(last_reporter)
                last_message = find_selector('div:last-child  > div.im-mess-stack--content > ul > li:nth-last-child(2)')
            if len(members) == len(losers):
                leaving = True
                last_message = find_selector('div:last-child  > div.im-mess-stack--content > ul > li:last-child')
                type_message_in_chat('Похоже, что последний участник ушел. Я ухожу')

        # сохраняю использованные города, если сообщение было не ко мне
        last_message2 = last_message.text
        if '@id471672657' not in last_message2 and 'тебе на' in last_message2.lower() and last_message2.count('@') == 1:
            city_in_message = ''
            for i in range(len(last_message2)):
                if last_message2[i] != '.' and last_message2[i] != ',':
                    city_in_message += last_message2[i]
                else:
                    break
            # если последнее сообщение написано мной, то не нужно заново добавлять город в список использованных
            if city_in_message not in used_cities:
                used_cities.append(city_in_message)

        # если стартовали с меня, то выдаем случайный город из списка
        if '@id471672657' in last_message.text and 'старт' in last_message.text.lower():
            random_city = randint(0, len(cities)-1)
            # проверяем последнюю букву случайного города
            if cities[random_city][-1] in possible_characters:
                last_character = -1
            else:
                i = 2
                while cities[random_city][-i] not in possible_characters:
                    i += 1
                last_character = -i
            # берем случайного участника из списка участников, кому передадим ход
            random_participant = randint(0, len(members)-1)
            while members[random_participant] in losers:
                random_participant = randint(0, len(members)-1)
            # сообщение с передачей хода
            used_cities.append(cities[random_city])
            type_message_in_chat(f'{cities[random_city]}. @{members[random_participant]}'
                                 f' тебе на {cities[random_city][last_character].upper()}')
            # добавляем себе ход, т.к. сходили первый раз
            turns += 1
            # проверка ответа собеседника
            last_message = find_selector('div:last-child  > div.im-mess-stack--content > ul > li:last-child')
            last_message2 = last_message.text
            iteration = 0
            while True:
                time.sleep(0.5)
                last_message = find_selector('div:last-child  > div.im-mess-stack--content > ul > li:last-child')
                if last_message.text != last_message2:
                    break
                if iteration == 10 and last_message.text == last_message2:
                    losers.append(members[random_participant])
                    # если все участники чата уже выбыли
                    if len(members) == len(losers):
                        type_message_in_chat(f'Игрок @{members[random_participant]} выбывает.'
                                             f' Похоже, что все участники выбыли. Я ухожу')
                        leaving = True
                        break
                    else:
                        # берем случайного участника из списка участников, кому передадим ход
                        random_participant2 = randint(0, len(members) - 1)
                        while members[random_participant2] in losers:
                            random_participant2 = randint(0, len(members) - 1)
                        type_message_in_chat(f'Игрок @{members[random_participant]} выбывает,'
                        f' @{members[random_participant2]} тебе на {cities[random_city][last_character].upper()}')
                        random_participant = random_participant2
                        last_message2 = find_selector('div:last-child  > div.im-mess-stack--content > ul > li:last-child').text
                        iteration = 0
                iteration += 1

        # выглядит как ненужный блок
        '''last_message = find_selector('div:last-child  > div.im-mess-stack--content > ul > li:last-child')
        last_reporter_link = find_selector('div.im-mess-stack._im_mess_stack:last-child .im-mess-stack--pname > a')
        last_reporter = last_reporter_link.get_attribute('href')[15::]'''

        # если кто-то другой сказал участнику, что он выбывает
        if 'выбывает' in last_message.text.lower():
            # ищем выбывшего участника
            last_message2 = last_message.text
            loser_doggy = last_message2.index('@')
            loser_nickname = ''
            i = loser_doggy + 1
            while not last_message2[i].isspace():
                loser_nickname += last_message2[i]
                i += 1
            if loser_nickname not in losers:
                losers.append(loser_nickname)

        if '@id471672657' in last_message.text and 'тебе на' in last_message.text.lower():
            text_without_city = False
            last_message2 = last_message.text
            # если кто-то другой выбывает и ход переходит ко мне
            if 'выбывает' in last_message2:
                new_city_character = last_message.text[-1]
                text_without_city = True
            else:
                # если мне передали ход, то ищем название города в этом сообщении
                if not text_without_city:
                    city_in_message = ''
                    for i in range(len(last_message2)):
                        if last_message2[i] != '.' and last_message2[i] != ',':
                            city_in_message += last_message2[i]
                        else:
                            break
                # была проверка на уже названные города, оказалась бесполезна
                '''if city_in_message in used_cities:
                    # такой город уже называли
                    type_message_in_chat(f'Такой город уже называли, @{last_reporter}, ты проиграл')
                else:'''
                if city_in_message in cities:
                    # такой город существует
                    used_cities.append(city_in_message)
                    for i in range(1, len(city_in_message) + 1):
                        if city_in_message[-i].lower() in possible_characters:
                            # найден символ, допустимый для названий новых городов
                            new_city_character = city_in_message[-i]
                            break
            for city in cities:
                # ищем подходящий город на новую букву
                if city.startswith(new_city_character.upper()) and city not in used_cities:
                    # берем случайного участника из списка участников, кому передадим ход
                    random_participant = randint(0, len(members)-1)
                    while members[random_participant] in losers:
                        random_participant = randint(0, len(members)-1)
                    # проверяем последнюю букву случайного города
                    if city[-1] in possible_characters:
                        last_character = -1
                    else:
                        i = 2
                        while city[-i] not in possible_characters:
                            i += 1
                        last_character = -i
                    used_cities.append(city)
                    type_message_in_chat(f'{city}. @{members[random_participant]} тебе на {city[last_character].upper()}')
                    random_city = city
                    # передали ход, добавили себе ход
                    turns += 1
                    # проверка ответа собеседника
                    last_message = find_selector('div:last-child  > div.im-mess-stack--content > ul > li:last-child')
                    last_message2 = last_message.text
                    iteration = 0
                    while True:
                        time.sleep(0.5)
                        last_message = find_selector('div:last-child  > div.im-mess-stack--content > ul > li:last-child')
                        if last_message.text != last_message2:
                            break
                        if iteration == 10 and last_message.text == last_message2:
                            losers.append(members[random_participant])
                            # если все участники чата уже выбыли
                            if len(members) == len(losers):
                                type_message_in_chat(f'Игрок @{members[random_participant]} выбывает.'
                                                     f' Похоже, что все участники выбыли. Я ухожу')
                                leaving = True
                                break
                            else:
                                # берем случайного участника из списка участников, кому передадим ход
                                random_participant2 = randint(0, len(members) - 1)
                                while members[random_participant2] in losers:
                                    random_participant2 = randint(0, len(members) - 1)
                                type_message_in_chat(f'Игрок @{members[random_participant]} выбывает,'
                                                     f' @{members[random_participant2]} тебе на {random_city[last_character].upper()}')
                                random_participant = random_participant2
                                last_message2 = find_selector('div:last-child  > div.im-mess-stack--content > ul > li:last-child').text
                                iteration = 0
                        iteration += 1
                    break
                    # условие на проигрыш, если города кончились, пока тоже не нужно
                '''elif city == cities[-1]:
                    # если мы дошли до конца списка и последний город не выбрался, значит предыдущее условие
                    # не сработало, это проигрыш
                    type_message_in_chat('Я проиграл :(')
                    last_reporter_link = find_selector('div.im-mess-stack._im_mess_stack:last-child .im-mess-stack--pname > a')
                    last_reporter = last_reporter_link.get_attribute('href')[15::]
                    losers.append(last_reporter)
                    break'''
                # условие существует ли названный город, похоже тоже пока не нужно
            '''else:
                # такой город не существует
                type_message_in_chat(f'{last_message.text}? Такой город не существует в РФ,'
                                     f' @{last_reporter}, ты проиграл')
                losers.append(last_reporter)'''

        # условия выхода из бесконечного цикла
        if turns == 999:
            type_message_in_chat('Я наигрался. Ухожу')
            break
        if leaving:
            break

finally:
    # успеваем скопировать код за 30 секунд
    time.sleep(2)
    # закрываем браузер после всех манипуляций
    browser.quit()
