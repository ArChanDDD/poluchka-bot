import telebot
import time
import datetime
import calendar
from multiprocessing import *
import schedule
import numpy as np
import requests

API_TOKEN = '5420901910:AAHkQ9h5OX11yrWR1xaZz-WEM9sCPweNDt4'
bot = telebot.TeleBot(API_TOKEN)
chat_ids = []
poluchka_dates = [3, 17]
komp_dates = [17]
messages_for_poluchka = ['ЕБЕН БОБЕН! СЕГОДНЯ ПОЛУЧКА!!!', 'ПОЛУЧКА.ПРИДЕТ.СЕГОДНЯ.',
                         'Го в бар вечером. Ведь сегодня получка!', 'Ваша зарплата должна прийти сегодня',
                         'Сегодня мы прекращаем есть дошики. Ведь получка уже в пути!!!',
                         'Расчехляем самогонные аппараты, заводчане! Сегодня ПОЛУЧКА!']

messages_for_poluchka_should_not_today = ['ЖДЕМ ПОЛУЧКУ!!! Хоть она должна прийти и не сегодня...',
                                          'Ура! Сегодня получка!!!',
                                          'Сегодня пятница. А еще сегодня погода хорошая. А еще сегодня ПОЛУЧКА!',
                                          'Поздравляю всех с пятницей и зарплатой!',
                                          'Именно сегодня (не на выходных) мы все увидим, на сколько рублей нам НЕ повысили зп']

messages_poluchka_next_week = ['Получка уже через неделю! Бедствовать осталось недолго!',
                               'Ура! Всего 7 дней и зарплата!',
                               'На что потратим следующую получку? Она кстати через неделю...']

messages_for_kompensaciya = ['О, а еще сегодня компенсация придет!',
                             'Сегодня мы узнаем, кто из нас больше всего нажрал', 'А еще сегодня на пожрать скинут',
                             'А еще сегодня компенсация! Праздник какой-то...']

photo_urls = ['http://kotomatrix.ru/images/lolz/2009/06/01/Vq.jpg', 'http://memesmix.net/media/created/qi5phv.jpg',
              'https://proprikol.ru/wp-content/uploads/2019/06/prikolnye-kartinki-pro-zarplatu-4.jpg',
              'https://proprikol.ru/wp-content/uploads/2019/06/prikolnye-kartinki-pro-zarplatu-5.jpg',
              'https://proprikol.ru/wp-content/uploads/2019/06/prikolnye-kartinki-pro-zarplatu-9.jpg',
              'https://proprikol.ru/wp-content/uploads/2019/06/prikolnye-kartinki-pro-zarplatu-14.jpg',
              'https://proprikol.ru/wp-content/uploads/2019/06/prikolnye-kartinki-pro-zarplatu-15.jpg',
              'https://proprikol.ru/wp-content/uploads/2019/06/prikolnye-kartinki-pro-zarplatu-16.jpg',
              'https://proprikol.ru/wp-content/uploads/2019/06/prikolnye-kartinki-pro-zarplatu-18.jpg',
              'https://proprikol.ru/wp-content/uploads/2019/06/prikolnye-kartinki-pro-zarplatu-19.jpg',
              'https://proprikol.ru/wp-content/uploads/2019/06/prikolnye-kartinki-pro-zarplatu-20.jpg',
              'https://proprikol.ru/wp-content/uploads/2019/06/prikolnye-kartinki-pro-zarplatu-22.jpg',
              'https://proprikol.ru/wp-content/uploads/2019/06/prikolnye-kartinki-pro-zarplatu-23.jpg',
              'https://proprikol.ru/wp-content/uploads/2019/06/prikolnye-kartinki-pro-zarplatu-25.jpg',
              'https://proprikol.ru/wp-content/uploads/2019/06/prikolnye-kartinki-pro-zarplatu-26.jpg',
              'https://proprikol.ru/wp-content/uploads/2019/06/prikolnye-kartinki-pro-zarplatu-27.jpg',
              'https://proprikol.ru/wp-content/uploads/2019/06/prikolnye-kartinki-pro-zarplatu-29.jpg',
              'https://proprikol.ru/wp-content/uploads/2019/06/prikolnye-kartinki-pro-zarplatu-30.jpg',
              'https://proprikol.ru/wp-content/uploads/2019/06/prikolnye-kartinki-pro-zarplatu-32.jpg',
              'https://proprikol.ru/wp-content/uploads/2019/06/prikolnye-kartinki-pro-zarplatu-34.jpg',
              'https://proprikol.ru/wp-content/uploads/2019/06/prikolnye-kartinki-pro-zarplatu-35.jpg',
              'https://proprikol.ru/wp-content/uploads/2019/06/prikolnye-kartinki-pro-zarplatu-41-1.jpg',
              'https://proprikol.ru/wp-content/uploads/2019/06/prikolnye-kartinki-pro-zarplatu-44.jpg',
              'https://www.meme-arsenal.com/memes/37c057fb8d89871b9023faadc6b2cdcb.jpg']
proc = None


class Scheduler:  # Class для работы с schedule
    def __init__(self, ids):
        self.ids = ids

    def start_schedule(self):  # Запуск schedule
        schedule.every(1).day.at('11:00').do(Scheduler.handle_poluchka_notify, self)

        while True:  # Запуск цикла
            schedule.run_pending()
            time.sleep(1)

    def handle_poluchka_notify(self):
        d_now = datetime.datetime.now().date().day
        y_now = datetime.datetime.now().date().year
        m_now = datetime.datetime.now().date().month
        if d_now in poluchka_dates:
            self.send_poluchka_today()
            if d_now in komp_dates:
                self.send_kompensaciya()
        elif calendar.weekday(y_now, m_now, d_now) == 4 and (
                ((datetime.datetime.now() + datetime.timedelta(days=1)).day in poluchka_dates) or (
                (datetime.datetime.now() + datetime.timedelta(days=2)).day in poluchka_dates)):
            self.send_poluchka_today_but_must_not_today()
            if (d_now + 1 in komp_dates) or (d_now + 2 in komp_dates):
                self.send_kompensaciya()
        elif (datetime.datetime.now() + datetime.timedelta(days=7)).day in poluchka_dates:
            self.poluchka_next_week()

    def send_poluchka_today(self):
        print('Отправляю уведомление о получке. Всего чатов: ', len(self.ids))
        for m in self.ids:
            bot.send_message(m, np.random.choice(messages_for_poluchka))
            self.send_meme(m)

    def send_poluchka_today_but_must_not_today(self):
        print('Отправляю уведомление о получке. Хотя вообще она не сегодня должна прийти. Всего чатов: ', len(self.ids))
        for m in self.ids:
            bot.send_message(m, np.random.choice(messages_for_poluchka_should_not_today))
            self.send_meme(m)

    def poluchka_next_week(self):
        print('Уведомляю о получке на следующей неделе. Всего чатов: ', len(self.ids))
        for m in self.ids:
            bot.send_message(m, np.random.choice(messages_poluchka_next_week))

    def send_kompensaciya(self):
        print('Уведомляю о компенсации. Всего чатов: ', len(self.ids))
        for m in self.ids:
            bot.send_message(m, np.random.choice(messages_for_kompensaciya))

    def send_meme(self, message):
        sended = False
        while sended is False:
            url = np.random.choice(photo_urls)
            r = requests.get(url)
            if r.status_code == 200:
                bot.send_photo(message.chat.id, r.content)
                sended = True
                print('Фото отправлено')
            else:
                print('Ошибка с url: ' + url)


def start_process(ids):  # Запуск Process
    p = Process(target=Scheduler(ids).start_schedule, args=())
    return p


@bot.message_handler(commands=['start'])
def start(message):
    print(message.chat.id)
    if message.chat.id not in chat_ids:
        chat_ids.append(message.chat.id)
        bot.send_message(message.chat.id, 'ТЕПЕРЬ Я БУДУ ОПОВЕЩАТЬ ВАС О ПОЛУЧКАХ!!!1!')
    else:
        bot.send_message(message.chat.id, 'Да заебал, я тебя помню')
    proc.kill()
    print('restart...')
    raise StopIteration


@bot.message_handler(commands=['stop'])
def stop(message):
    chat_ids.remove(message.chat.id)
    bot.send_message(message.chat.id, 'окей покедова лохи')
    proc.kill()
    raise StopIteration


@bot.message_handler(commands=['kebp_photo'])
def send_meme(message):
    sended = False
    while sended is False:
        url = np.random.choice(photo_urls)
        r = requests.get(url)
        if r.status_code == 200:
            bot.send_photo(message.chat.id, r.content)
            sended = True
            print('Фото отправлено')
        else:
            print('Ошибка с url: ' + url)


@bot.message_handler(commands=['next_poluchka'])
def get_next_poluchka(message):
    dt = datetime.datetime.now().date()
    d_now = dt.day
    m_now = dt.month
    y_now = dt.year
    if d_now in poluchka_dates:
        bot.send_message(message.chat.id, 'Сегодня получка! Просто ждем и радуемся!')
    for k in range(1, 30):
        dt_new = (dt + datetime.timedelta(days=k))
        d_new = dt_new.day
        m_new = dt_new.month
        y_new = dt_new.year
        if (calendar.weekday(y_new, m_new, d_new) == 4 and (
                ((dt_new + datetime.timedelta(days=1)).day in poluchka_dates) or (
                (dt_new + datetime.timedelta(days=2)).day in poluchka_dates))) or (
                (dt_new.day in poluchka_dates) and calendar.weekday(y_new, m_new, d_new) < 5):
            mes = 'Получка придет через: ' + str(datetime.datetime.combine((dt + datetime.timedelta(days=k)),
                                                                           datetime.time(14,
                                                                                         00)) - datetime.datetime.now())
            bot.send_message(message.chat.id, mes)
            break


if __name__ == '__main__':
    while True:
        print('starting bot with {} ids'.format(len(chat_ids)))
        try:
            proc = start_process(chat_ids)
            proc.start()
            bot.polling(none_stop=True)
        except StopIteration:
            pass
        except SystemExit:
            exit()
