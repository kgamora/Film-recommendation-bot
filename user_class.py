import pandas as pd
import numpy as np
import os
import csv
import subprocess

class User ():
    # XXX атрибуты класса
    users_list = list()
    all_films = pd.read_csv('D:\\py fi\\new_tg_bot\\bot data\\html_final_1.csv', index_col=0)

    def __init__ (self, id):
        self.id = id
        self.films_not_asked = __class__.all_films.copy()
        self.stage = 0
        self.times_asked = 0
        self.writes_review = False
        self.what_to_ask()
        self.create_user_directory()
        self.create_user_ds()
        __class__.users_list.append(self)
    
    def what_to_ask (self, length = 10):
        '''Данный метод выбирает индексы десяти фильмов из датасета films_not_asked и перезаписывает этот датасет, убирая из него засэмплированные фильмы.\n
        Длина (length) по умолчанию - 10, однако для случая с отрубленным инетом можно будет проверять, на каком шаге остановился человек и продолжать.'''
        self.films_to_ask = np.random.choice(self.films_not_asked.index, size = length, replace = False)
        self.films_not_asked = self.films_not_asked[~self.films_not_asked.index.isin(self.films_to_ask)]
        return self.films_to_ask

    def create_user_directory (self):
        '''Если применён для юзера впервые, создаст его персональную папку'''
        if not os.path.exists(f'D:\\py fi\\new_tg_bot\\users data\\{self.id}'):
            os.mkdir(f'D:\\py fi\\new_tg_bot\\users data\\{self.id}')

    def create_user_ds (self):
        '''Данный метод создаёт новый датасет в папке пользователя для каждого нового опроса'''
        if self.times_asked == 0:
            with open(f'D:\\py fi\\new_tg_bot\\users data\\{self.id}\\{self.times_asked} poll {self.id}.csv', 'w', newline='') as f:
                thewriter = csv.writer(f)
                thewriter.writerow(['user_id', 'film_id', 'user_rate'])
            f.close()
        elif self.times_asked % 10 == 0 and self.times_asked > 0:
            with open(f'D:\\py fi\\new_tg_bot\\users data\\{self.id}\\{self.times_asked} poll {self.id}.csv', 'w', newline='') as f:
                thewriter = csv.writer(f)
                thewriter.writerow(['user_id', 'film_id', 'user_rate'])
            f.close()
        else:
            current_ds = pd.read_csv(f'D:\\py fi\\new_tg_bot\\users data\\{self.id}\\{self.times_asked - 1} poll {self.id}.csv')
            new_csv = current_ds.to_csv(f'D:\\py fi\\new_tg_bot\\users data\\{self.id}\\{self.times_asked} poll {self.id}.csv', index = False)    

    def rates (self, rate):
        '''данный метод должен брать фильмс_ту_аск по индексу stage и записывать строку с ответом юзера в датасет (по id и разу, который спрашивают) и плюсовать к стейджу 1.'''
        with open(f'D:\\py fi\\new_tg_bot\\users data\\{self.id}\\{self.times_asked} poll {self.id}.csv', 'a', newline='') as f:
            thewriter = csv.writer(f)
            rate = rate if rate != 'Не смотрел' else 0
            thewriter.writerow(['self.id', f"{__class__.all_films.copy().iloc[self.films_to_ask[self.stage], :]['id']}", rate])
        f.close()
        self.stage += 1

    def review_create (self, text):
        '''Данный метод вызывается лишь однажды и нужен для фидбека. Аргумент - текст отзыва.'''
        with open(f'D:\\py fi\\new_tg_bot\\users data\\{self.id}\\review on stage {self.times_asked}.txt', 'w') as f:
            for i in range(int(np.ceil(len(text) / 120))):
                if i != int(np.ceil(len(text) / 120)) - 1:
                    f.write(text[i * 120:(i + 1) * 120] + '\n')
                else:
                    f.write(text[i * 120:] + '\n')
        self.review = text

    def users_dataset_refresh (self):
        '''Данный метод необходим для случая разрыва инета - он чекает, есть ли уже хотя бы одна версия себя и если нет - создаёт. Также полезен для перезаписи.'''
        if not os.path.exists(f'D:\\py fi\\new_tg_bot\\users data\\users_data.csv'):
            with open(f'D:\\py fi\\new_tg_bot\\users data\\users_data.csv', 'w', newline='') as f:
                thewriter = csv.writer(f)
                thewriter.writerow(['user_id', 'film_id', 'user_rate'])
            f.close()
        else:
            self.__class__.all_rates = pd.read_csv('D:\\py fi\\new_tg_bot\\users data\\users_data.csv')

    def user_recommend (self):
        user_path = [f"D:/py fi/new_tg_bot/users data/{self.id}/{self.times_asked} poll {self.id}.csv"]
        cmd = ['RScript', 'D:\\py fi\\new_tg_bot\\bot data\\Recsys.R'] + user_path
        routput = subprocess.check_output(cmd, universal_newlines=True)[3:]
        self.stage = 0
        self.times_asked += 1
        self.create_user_ds()
        return routput 

#TODO: все фильмы должны делаться методом copy основного дс