import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import comunity_token, acces_token
from core import VkTools
from data_store import engine, data_store_tools
#отправка сообщений


class BotInterface():
    def __init__(self, comunity_token, acces_token):
        self.vk = vk_api.VkApi(token=comunity_token)
        self.longpoll = VkLongPoll(self.vk)
        self.vk_tools = VkTools(acces_token)
        self.data_store_tools = data_store_tools(engine)
        self.check_user = data_store_tools(engine)
        self.params = {}
        self.worksheets = []
        self.offset = 0


    def message_send(self, user_id, message, attachment=None):
        vk.method('messages.send', {'user_id': user_id,
                                    'message': message,
                                    'attachment': attachment,
                                    'random_id': get_random_id()})



    def event_handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'привет':
                    self.params = self.vk_tools.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'Привет, {self.params["name"]}')
                    # Логика для получения данных о пользователе
                    if self.params is not None:
                        while self.params['city'] == None:
                            self.message_send(event.user_id, 'Вижу, вы такие скрытные, что даже не указали город в профиле. Напишите его в чат, пожалуйста, а мы никому не скажем')
                            for eve in self.longpoll.listen():
                                if eve.type == VkEventType.MESSAGE_NEW and eve.to_me:
                                    self.params = self.vk_tools.get_profile_info(event.user_id)
                                    self.params['city'] = eve.text
                                    self.message_send(event.user_id, 'Спасибо за ответ!')
                                    break
                        while self.params['sex'] == None:
                            self.message_send(event.user_id, 'Введите 1, если вы женщина. Если вы мужчина, введите 2')
                            for event_sex in self.longpoll.listen():
                                if event_sex.type == VkEventType.MESSAGE_NEW and event_sex.to_me:
                                    try:
                                        self.params['sex'] = int(event_sex.text)
                                        self.message_send(event.user_id, 'Спасибо! Теперь мы знаем, кого искать')
                                    except:
                                        self.message_send(event.user_id, 'Неверный формат возраста')


                                    break
                        while self.params['year'] == None:
                            self.message_send(event.user_id, 'Введите ваш возраст числом')
                            for event_year in self.longpoll.listen():
                                if event_year.type == VkEventType.MESSAGE_NEW and event_year.to_me:
                                    try:
                                        self.params['year'] = int(event_year.text)
                                        self.message_send(event.user_id, 'Спасибо! Теперь мы знаем, сколько вам лет')
                                    except:
                                        self.message_send(event.user_id, 'Неверный формат даты')
                                    break
                        else:
                            self.message_send(event.user_id, 'Напиши "Поиск", чтобы я нашел анкеты')


                elif event.text.lower() == 'поиск':
    #Логика для поиска анкет
                    self.message_send(
                        event.user_id, 'Начинаем поиск')
                    if self.worksheets:
                        worksheet = self.worksheets.pop()
                        #проверка в бд
                        while self.data_store_tools.check_user(event.user_id, worksheet["id"]) is True:
                            worksheet = self.worksheets.pop()
                        # добавление в бд
                        if self.data_store_tools.check_user(event.user_id, worksheet["id"]) is False:
                            self.data_store_tools.add_user(event.user_id, worksheet["id"])
                        photos = self.vk_tools.get_photos(worksheet['id'])
                        photo_string = ''
                        for photo in photos:
                            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
                    else:
                        self.worksheets = self.vk_tools.search_worksheet(
                            self.params, self.offset)
                        #если пользователь абракадабру набрал
                        if len(self.worksheets) == 0:
                            self.message_send(event.user_id, 'Прости, но я ничего не нашёл')
                        else:
                            worksheet = self.worksheets.pop()
                            self.offset += 50
                            # проверка в бд
                            while self.data_store_tools.check_user(event.user_id, worksheet["id"]) is True:
                                worksheet = self.worksheets.pop()
                            # добавление в бд
                            if self.data_store_tools.check_user(event.user_id, worksheet["id"]) is False:
                                self.data_store_tools.add_user(event.user_id, worksheet["id"])

                        photos = self.vk_tools.get_photos(worksheet['id'])
                        photo_string = ''
                        for photo in photos:
                            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'

                    self.message_send(
                        event.user_id,
                        f'Имя: {worksheet["name"]}, ссылка: vk.com/id{worksheet["id"]}, город: {worksheet["hometown"]}',
                        attachment=photo_string
                    )



                elif event.text.lower() == 'пока':
                    self.message_send(event.user_id, 'До новых встреч!')
                else:
                    self.message_send(event.user_id, 'Неизвестная команда')


vk = vk_api.VkApi(token=comunity_token)
longpoll = VkLongPoll(vk)

if __name__ == '__main__':
    bot_interface = BotInterface(comunity_token, acces_token)
    bot_interface.event_handler()