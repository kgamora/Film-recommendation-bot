from user_class import User
from get_image import get_image_url
import bot_settings
import telebot
import time
import winsound
from telebot import apihelper
from telebot import types

iamdone = 'Я высказал всё, что хотел (на данный момент)'

# apihelper.proxy = {'https':'http://{}:{}'.format(bot_settings.ip, bot_settings.port)}

tb = telebot.TeleBot(bot_settings.TOKEN)

rateitems = [types.KeyboardButton(f'{i + 1}') for i in range(5)]
itemidk = types.KeyboardButton('Не смотрел')

@tb.message_handler(commands = ['start'])
def privet(message):
    if next((x for x in User.users_list if x.id == message.chat.id), None) == None:
        User(message.chat.id)
        tb.send_message(message.chat.id, 'Здравствуйте! \n Наш бот задаст вам пару вопросов касательно наиболее популярных фильмов с IMDB по версии пользователей, чтобы порекомендовать вам фильм, который, согласно результату, вам, скорее всего, стоит посмотреть!')
        tb.send_message(message.chat.id, 'Вам необходимо оценить 10 фильмов')
        markup = types.ReplyKeyboardMarkup()
        itemyes = types.KeyboardButton('Да, поехали!')
        itemno = types.KeyboardButton('Не, долго... Может, позже!')
        markup.row(itemyes, itemno)
        tb.send_message(message.chat.id, "Вы готовы?", reply_markup=markup)

@tb.message_handler(func = lambda msg: msg.text is not None and msg.text in ['Да, поехали!', 'Хочу более точную рекомендацию!', 'Попробуем ещё раз!'])
def opros(message):
    if next((x for x in User.users_list if x.id == message.chat.id), None) != None:
        if next((x for x in User.users_list if x.id == message.chat.id), None).stage == 0 and not next((x for x in User.users_list if x.id == message.chat.id), None).writes_review:
            user = next((x for x in User.users_list if x.id == message.chat.id), None)
            if user.times_asked > 0 and user.times_asked % 10 == 0:
                user.create_user_ds()
                user.films_not_asked = User.all_films.copy()
                user.what_to_ask()
            user.what_to_ask()
            film = User.all_films.copy().iloc[user.films_to_ask[user.stage], :]
            tb.send_photo(user.id, film['path_image'], caption=film['title'])
            markup = types.ReplyKeyboardMarkup()
            markup.row(rateitems[0], rateitems[1], rateitems[2])
            markup.row(rateitems[3], rateitems[4])
            markup.row(itemidk)
            tb.send_message(message.chat.id, "Как оцените?", reply_markup=markup)
    else:
        tb.send_message(message.chat.id, "Введите '/start'")

@tb.message_handler(func = lambda msg: msg.text is not None and msg.text in ['1', '2', '3', '4', '5', 'Не смотрел'])
def opros_repeat(message):
    if next((x for x in User.users_list if x.id == message.chat.id), None) != None:
        user = next((x for x in User.users_list if x.id == message.chat.id), None)
        if user.stage < 9 and not user.writes_review:
            user.rates(message.text)
            film = User.all_films.copy().iloc[user.films_to_ask[user.stage], :]
            tb.send_photo(user.id, film['path_image'], caption=film['title'])
            markup = types.ReplyKeyboardMarkup()
            markup.row(rateitems[0], rateitems[1], rateitems[2])
            markup.row(rateitems[3], rateitems[4])
            markup.row(itemidk)
            tb.send_message(message.chat.id, "Как оцените?", reply_markup=markup)
        else:
            tb.send_photo(user.id, 'https://www.meme-arsenal.com/memes/44751371a68e227ab763580bd26f9e0c.jpg', caption='Подождите, происходят сложные манипуляции с ващими оценками...')
            tb.send_message(user.id, text = user.user_recommend())
            markup = types.ReplyKeyboardMarkup()
            itemyes = types.KeyboardButton('Хочу более точную рекомендацию!')
            itemno = types.KeyboardButton('Оставить фидбек!')
            markup.row(itemyes, itemno)
            tb.send_message(user.id, """Вы можете дополнить данные о просмотренных фильмах.
            Это позволит системе сделать рекомендацию точнее.
            Или вы можете оценить работу данной системы.
            (отзыв можно дополнять после каждого десятка фильмов)
            Нам очень нужен фидбек!""", reply_markup=markup)
    else:
        tb.send_message(message.chat.id, "Введите '/start'")

@tb.message_handler(func = lambda msg: msg.text is not None and msg.text == 'Оставить фидбек!')
def response(message):
    if next((x for x in User.users_list if x.id == message.chat.id), None) != None:
        user = next((x for x in User.users_list if x.id == message.chat.id), None)
        if user.stage == 0:
            user.to_write = list()
            user.writes_review = True
            print(user.writes_review)
            markup = types.ReplyKeyboardMarkup()
            itemyes = types.KeyboardButton('Написал/a')
            markup.row(itemyes)
            tb.send_message(user.id, 'Мы слушаем - пишите всё, что думаете о системе.', reply_markup=markup)
    else:
        tb.send_message(message.chat.id, "Введите '/start'")

@tb.message_handler(func = lambda msg: msg.text in [iamdone, 'Написал/a'])
def end_of_response(message):
    if next((x for x in User.users_list if x.id == message.chat.id), None) != None:
        user = next((x for x in User.users_list if x.id == message.chat.id), None)
        print(f'Мы наконец-то здесь {user.writes_review}')
        if user.writes_review == True:
            user.to_write.append(user.rawtext)
            from_new_str = '\n Следующее сообщение \n'
            user.review_create(from_new_str.join(user.to_write))
            user.writes_review = False
            markup = types.ReplyKeyboardMarkup()
            itemyes = types.KeyboardButton('Хочу более точную рекомендацию!')
            itemno = types.KeyboardButton('Я более более не хочу пользоваться этим ботом')
            markup.row(itemyes, itemno)
            tb.send_message(user.id, """Вы можете дополнить данные о просмотренных вами фильмах.
            Это позволит системе сделать рекомендацию точнее.""", reply_markup=markup)
    else:
        tb.send_message(message.chat.id, "Введите '/start'")

@tb.message_handler(func = lambda msg: msg.text is not None)
def review_messages(message):
    if next((x for x in User.users_list if x.id == message.chat.id), None) != None:
        user = next((x for x in User.users_list if x.id == message.chat.id), None)
        if user.writes_review == True:
            user.rawtext = message.text
            user.to_write.append(user.rawtext)
    else:
        tb.send_message(message.chat.id, "Введите '/start'")
# TODO: insert вместо append


tb.polling(none_stop=True)


