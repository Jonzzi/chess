from PIL import Image
import pandas as pd
import re
import telegram
from telegram.error import NetworkError, Unauthorized
#from telegram.ext import Updater
from time import sleep
import logging

# задаем оснвновные константы
global ALL_LITERS
ALL_LITERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
COMMANDS = ['help', 'exit', 'show', 'new', 'stat']

TG = True # вывод в телеграм
#TG = False # вывод в local
chat_id = тут должен быть чат-ид
global UPDATE_ID
UPDATE_ID = None
TOKEN = 'тут должен быть токен'

if TG == True:
    bot = telegram.Bot(token=TOKEN)
    print(bot.get_me())
else:
    bot = None

PATH = r'F:\_DS'
board_image = Image.open(PATH + r'\green_board.png')
figures_images_all = Image.open(PATH + r'\chess-svg-1.png')
board_width, board_height = figures_images_all.size

fig_width = board_width // 6
fig_height = board_height // 2
off_wdth = 160
off_hgth = 130
board_step = 320

# Нарезка белых фигур
wh_king_img = figures_images_all.crop((0, 0, fig_width, fig_height))
wh_queen_img = figures_images_all.crop((fig_width, 0, 2 * fig_width, fig_height))
wh_elefant_img = figures_images_all.crop((2 * fig_width + 1, 0, 3 * fig_width + 1, fig_height))
wh_horse_img = figures_images_all.crop((3 * fig_width + 1, 0, 4 * fig_width + 1, fig_height))
wh_rook_img = figures_images_all.crop((4 * fig_width + 2, 0, 5 * fig_width + 2, fig_height))
wh_pawn_img = figures_images_all.crop((5 * fig_width + 2, 0, 6 * fig_width + 2, fig_height))
# Нарезка черных фигур
bl_king_img = figures_images_all.crop((0, fig_height + 1, fig_width, 2 * fig_height + 1))
bl_queen_img = figures_images_all.crop((fig_width, fig_height + 1, 2 * fig_width, 2 * fig_height + 1))
bl_elefant_img = figures_images_all.crop((2 * fig_width + 1, fig_height + 1, 3 * fig_width + 1, 2 * fig_height + 1))
bl_horse_img = figures_images_all.crop((3 * fig_width + 1, fig_height + 1, 4 * fig_width + 1, 2 * fig_height + 1))
bl_rook_img = figures_images_all.crop((4 * fig_width + 2, fig_height + 1, 5 * fig_width + 2, 2 * fig_height + 1))
bl_pawn_img = figures_images_all.crop((5 * fig_width + 2, fig_height + 1, 6 * fig_width + 2, 2 * fig_height + 1))

# 0 - white, 1 - black
figures_images = [
        {'king': wh_king_img,
          'queen': wh_queen_img,
          'elefant': wh_elefant_img,
          'horse': wh_horse_img,
          'rook': wh_rook_img,
          'pawn': wh_pawn_img},
        {'king': bl_king_img,
          'queen': bl_queen_img,
          'elefant': bl_elefant_img,
          'horse': bl_horse_img,
          'rook': bl_rook_img,
          'pawn': bl_pawn_img}]

# перечень и свойства фигур
figures_features = [
    [{'qty': 8, 'name': 'Белая Пешка', 'color': 'white', 'type': 'pawn', 'lit_axis': ALL_LITERS, 'num_axis': 2},
     {'qty': 2, 'name': 'Белая Ладья', 'color': 'white', 'type': 'rook', 'lit_axis': ['A', 'H'], 'num_axis': 1},
     {'qty': 2, 'name': 'Белый Конь', 'color': 'white', 'type': 'horse', 'lit_axis': ['B', 'G'], 'num_axis': 1},
     {'qty': 2, 'name': 'Белый Слон', 'color': 'white', 'type': 'elefant', 'lit_axis': ['C', 'F'], 'num_axis': 1},
     {'qty': 1, 'name': 'Белый Ферзь', 'color': 'white', 'type': 'queen', 'lit_axis': ['D'], 'num_axis': 1},
     {'qty': 1, 'name': 'Белый Король', 'color': 'white', 'type': 'king', 'lit_axis': ['E'], 'num_axis': 1}],
    [{'qty': 8, 'name': 'Черная Пешка', 'color': 'black', 'type': 'pawn', 'lit_axis': ALL_LITERS, 'num_axis': 7},
     {'qty': 2, 'name': 'Черная Ладья', 'color': 'black', 'type': 'rook', 'lit_axis': ['A', 'H'], 'num_axis': 8},
     {'qty': 2, 'name': 'Черный Конь', 'color': 'black', 'type': 'horse', 'lit_axis': ['B', 'G'], 'num_axis': 8},
     {'qty': 2, 'name': 'Черный Слон', 'color': 'black', 'type': 'elefant', 'lit_axis': ['C', 'F'], 'num_axis': 8},
     {'qty': 1, 'name': 'Черный Ферзь', 'color': 'black', 'type': 'queen', 'lit_axis': ['D'], 'num_axis': 8},
     {'qty': 1, 'name': 'Черный Король', 'color': 'black', 'type': 'king', 'lit_axis': ['E'], 'num_axis': 8}]]

def show(text):
    if TG==True:
        bot.send_message(chat_id=chat_id, text=text)
    else:
        print(text)


# начальная страница
def begin_page():
#    show('==========================================')
    show('============== НАЧАЛО ИГРЫ ==============')
#    show('==========================================')
    if TG:
        show('Игрок, который будет играть белыми должен ввести команду: white')
        show('Игрок, который будет играть черными должен ввести команду: black')
        show('Пока игроки не наберутся, игра не начнется. Ожидание игроков...')

# конечная страница
def end_page(txt):
#    show('==========================================')
    show('============== КОНЕЦ ИГРЫ ==============')
#    show('Победил '+txt)
#    show('==========================================')


# описание объекта фигур
class Figure:
    def __init__(self, id_fig, name, color, type, lit_axis, num_axis, img, status):
        self.id = id_fig
        self.name = name
        self.color = color
        self.type = type
        self.lit_axis = lit_axis
        self.num_axis = num_axis
        self.img = img
        self.status = status
        print(f'Создана фигура {self.name} (ID:{self.id}) на {self.lit_axis}{self.num_axis}')

    def put(self):
        board.board_buffer.paste(self.img, (off_wdth + board_step * ALL_LITERS.index(self.lit_axis), off_hgth + board_step * (8 - self.num_axis)), self.img)
        board.grid.loc[self.num_axis, self.lit_axis] = self.id

    def kill(self):
        self.status = False
        board.killed.append(self.id)
        board.grid.loc[self.num_axis, self.lit_axis] = '#'
        show('Побито: ' + self.name)
        board.log.append('Побито: ' + self.name)

    def move(self, move_from, move_to):
        err = False
        prohod = False
        svoy = False

        lit_axis = move_from[0]
        num_axis = int(move_from[1])

        lit_axis_to = move_to[0]
        num_axis_to = int(move_to[1])

        fig_id = board.get_fig(move_to)
        if fig_id != '#':
            fig_id = int(fig_id)
            svoy = board.figures[fig_id].color == self.color
        else:
            svoy = False

        if (fig_id != 'error') and (fig_id != '#') and (not svoy):
            fig_id = int(fig_id)
            board.figures[fig_id].kill()
            # проверяю - не на проходе ли взято?
            if self.type == 'pawn' and board.figures[fig_id].type == 'pawn': # если они обе пешки, то это подозрительно
                if (num_axis == num_axis_to) and abs(ALL_LITERS.index(lit_axis_to) - ALL_LITERS.index(lit_axis)) < 2: # то есть если пешка взяла другую шагом вбок
                    # тут надо вставить проверку того, что до этого та пешка ходила на 2 из лога
                    prohod = True

        elif fig_id == 'error':
            show('Вы ввели что-то не то...')
        elif svoy:
            show('Там же Ваша фигура!!!')
            err = True
        else:
            pass
        if not err:
            board.grid.loc[num_axis, lit_axis] = '#'
            lit_axis_to = move_to[0]
            num_axis_to = int(move_to[1])
            if prohod:
                show('Взятие на проходе!')
                board.log.append('Взятие на проходе!')
                if self.color == 'white':
                    self.num_axis = num_axis_to + 1
                else:
                    self.num_axis = num_axis_to - 1
            else:
                self.num_axis = num_axis_to

            self.lit_axis = lit_axis_to
            board.turn += 1
            board.chet = not board.chet

        return err

class Board:
    def __init__(self):
        # инициализация доски
        self.board = board_image.copy()
        self.board_buffer = board_image.copy()
        self.grid = pd.DataFrame(data=None, index=range(1, 9, 1), columns=ALL_LITERS)
        self.grid = self.grid.fillna('#')
        self.killed = []
        self.log = []
        self.chet = False
        self.turn = 1
        self.start = False

        # инициализация фигур
        # 0 - white, 1 - black
        self.figures = []

        for fig_color in range(2):
            i = 0
            for fig_type in figures_features[fig_color]:
                for n in range(fig_type['qty']):
                     fg = Figure(id_fig=i+16*fig_color,
                                 name=fig_type['name'],
                                 color=fig_type['color'],
                                 type=fig_type['type'],
                                 lit_axis=fig_type['lit_axis'][n],
                                 num_axis=fig_type['num_axis'],
                                 img=figures_images[fig_color][fig_type['type']],
                                 status=True)
                     self.figures.append(fg)
                     i += 1

        show('Создана новая шахматная доска с фигурами')

    def show(self):
        self.board_buffer = board_image.copy()
        for i in range(len(self.figures)):
            if self.figures[i].status == True:
                    self.figures[i].put()
        self.board = self.board_buffer.copy()
        self.board_buffer = board_image.copy()

        if TG == True:
            self.board.save(PATH + r'\board.png') # от этого нужно будет избавиться!!!!!!
            bot.sendPhoto(chat_id, photo=open(r'F:\_DS\board.png', "rb"))
        else:
            self.board.save(PATH + r'\board.png')
            print(self.grid)
        ttt = turn_str()
        show(ttt)
        self.log.append(ttt)

    def get_fig(self, cell):
        try:
            lit_axis = cell[0]
            num_axis = int(cell[1])
            fig_id = self.grid.loc[num_axis, lit_axis]
        except:
            fig_id = 'error'
        return fig_id


def turn_str():
    if not board.chet:
        ts = 'Ход ' + str(board.turn) + ' Белых'
    else:
        ts = 'Ход ' + str(board.turn) + ' Черных'
    return ts


def save_game():
    board.grid.to_csv(PATH + r'\save_game.csv') # записали доску

    with open(PATH + r'\log_game.txt', 'w') as filehandle: # записали лог
        for listitem in board.log:
            filehandle.write('%s\n' % listitem)


def load_game():
    log_file = open(PATH + r'\log_game.txt', "r")
    board.log = []
    while True:
        # считываем строку
        ln = log_file.readline()
        # прерываем цикл, если строка пустая
        if not ln:
            break
        # выводим строку
        board.log.append(ln.strip())
    # закрываем файл
    log_file.close

    ii = 1
    ts = board.log[len(board.log) - ii]
    if 'Белых' in ts:
        board.chet = False
    else:
        board.chet = True

    while True:  # крутим цикл пока не считаем номер хода
        try:
            rrr = re.split(r' ', ts)
            board.turn = int(
                rrr[1])  # второй элемент в списке - это номер хода, но может быть ошибка и тогда надо подняться выше
            ex = True
        except:
            ii += 1
            ts = board.log[len(board.log) - ii]
            ex = False

        if ex:
            break

    board.grid = pd.read_csv(PATH + r'\save_game.csv')
    board.grid.index = board.grid.index + 1
    for i in range(31):
        board.figures[i].status = False  # сначала сбросим все фигуры с доски

    for lit in ALL_LITERS:  # и начнем расставлять заново
        ln = board.grid[lit].tolist()
        for nm in range(8):
            if ln[nm] != '#':
                fn = int(ln[nm])
                board.figures[fn].lit_axis = lit
                board.figures[fn].num_axis = nm + 1  # т.к. там от нуля а у нас от 1
                board.figures[fn].status = True


def game_stat():
    show('Информация по игре:')
    ttt = turn_str()
    show(ttt)
    #board.log.append(ttt) # записывать в лог-то это не надо! :)
    show('Выбитые фигуры:')
    if len(board.killed) == 0:
        show('--нет--')
    else:
        sps = []
        for i in range(len(board.killed)):
            sps.append(board.figures[board.killed[i]].name)
        show(', '.join(sps))


def if_make_rook(txt):
    short_rook = re.compile('0-0')
    long_rook = re.compile('0-0-0')
    if_rook = short_rook.findall(txt)
    if len(if_rook) > 0:  # если есть короткая, тогда поищем длинную
        if_rook = long_rook.findall(txt)  # а если есть длинная, то короткая уже не актуальна
        err = False
        if len(if_rook) > 0:  # обрабатываем длинную
            ttt = '0-0-0'
            if not board.chet:  # 'это значит Белые
                # надо двинуть короля с E1 на C1 а ладью с A1 на D1
                err = err or board.figures[15].move('E1', 'C1')  # белый король
                err = err or board.figures[8].move('A1', 'D1')  # белая ладья слева
            else:
                err = err or board.figures[31].move('E8', 'C8')  # черный король
                err = err or board.figures[24].move('A8', 'D8')  # черная ладья слева

        else:  # обрабатываем короткую
            ttt = '0-0'
            if not board.chet:  # 'это значит Белые
                # надо двинуть короля с E1 на G1 а ладью с H1 на F1
                err = err or board.figures[15].move('E1', 'G1')  # белый король
                err = err or board.figures[9].move('H1', 'F1')  # белая ладья справа
            else:
                err = err or board.figures[31].move('E8', 'G8')  # черный король
                err = err or board.figures[25].move('H8', 'F8')  # черная ладья справа

        if not err:
            board.turn -= 1  # компенсируем лишние движения
            board.chet = not board.chet
            show(ttt)
            board.log.append(ttt)
            board.show()

def pl_action(txt):
    global board
    ex = False
    # Ответ на сообщение
    txt = txt.upper()
    if 'exit'.upper() in txt:
        ex = True

    elif 'show'.upper() in txt:
        board.show()

    elif 'log'.upper() in txt: # надо это и ниже расидать по отдельным ФУНКЦИЯМ!!!
        show('Запись ходов:')
        show(', '.join(board.log))

    elif 'load'.upper() in txt:
        show('Игра загружается...')
        load_game()
        board.show()

    elif 'save'.upper() in txt:
        save_game()
        show('Игра записана.')

    elif 'stat'.upper() in txt:
        game_stat()

    elif 'new'.upper() in txt:
        begin_page()
        board = Board()
        board.show()

    elif 'help'.upper() in txt:
        show('Поддерживаются команды: ' + ', '.join(COMMANDS))

    if_make_rook(txt) # обработка возможной рокировки

    result = re.findall(r'\w{1}\d{1}', txt) # обработка ходов
    try:
        move_from = result[0]
        move_to = result[1]
        fig_id = board.get_fig(move_from)
        if fig_id != 'error' and fig_id != '#':
            fig_id = int(fig_id)
            if (board.figures[fig_id].color == 'white' and not board.chet) or (board.figures[fig_id].color == 'black' and board.chet):
                board.figures[fig_id].move(move_from, move_to)
                ttt = 'Ход: ' + board.figures[fig_id].name + ' ' + '-'.join(result)
                show(ttt)
                board.log.append(ttt)
                board.show()
            else:
                show('Это не Ваш ход!')
        else:
           show('Вы ввели что-то не то... или там нет фигуры.')
    except:
        pass
        #show('Ошибка!') # не надо выводить чтобы не реагировать на простое общение игроков
    return ex


def answ(bot):
    ex = False
#    """Эхо сообщение отправленное пользователем."""
    global UPDATE_ID
    # Запрашиваем обновление после последнего update_id
    for update in bot.get_updates(offset=UPDATE_ID, timeout=10):
        UPDATE_ID = update.update_id + 1

        # бот может получать обновления без сообщений
        if update.message:
            # не все сообщения содержат текст
            if update.message.text:
                txt = update.message.text
                ex = pl_action(txt)
    return ex


def collect_gamers():
    gamer = False
    gamer_color = '-'
    #    """Эхо сообщение отправленное пользователем."""
    global UPDATE_ID
    # Запрашиваем обновление после последнего update_id
    for update in bot.get_updates(offset=UPDATE_ID, timeout=10):
        UPDATE_ID = update.update_id + 1

        # бот может получать обновления без сообщений
        if update.message:
            # не все сообщения содержат текст
            if update.message.text:
                txt = update.message.text
                txt = txt.upper()
                if 'white'.upper() in txt:
                    try:
                        gamer_name = str(update.message.from_user.username)
                        gamer_color = 'white'
                        gamer = True
                    except:
                        gamer = False
                elif 'black'.upper() in txt:
                    try:
                        gamer_name = str(update.message.from_user.username)
                        gamer_color = 'black'
                        gamer = True
                    except:
                        gamer = False
                else:
                    gamer = False

    if len(gamers) > 0:
        if gamer_color == gamers[0]['color']:
            gamer = False

    if gamer != False:
        gamer = {'name': gamer_name, 'color': gamer_color}
        show('Заявка ' + gamer_name + ' на игру за ' + gamer_color + ' принята!')
    return gamer

begin_page()
global gamers
gamers = []

global board
board = Board()
#board.show()

game_continue = True

if not TG:
    board.start = True
    board.show()
    while game_continue:
        txt = input("Ваш ход: ")
        game_continue = not pl_action(txt)

else:
    if __name__ == '__main__':
    #    """Запускаем бота."""
        #global UPDATE_ID

        # получаем первый ожидающий `update_id`
        try:
            UPDATE_ID = bot.get_updates()[0].update_id
        except IndexError:
            UPDATE_ID = None

        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        while True:
            try:
                if len(gamers) < 2:
                    g = collect_gamers()
                    if g != False:
                        gamers.append(g)

                elif len(gamers) == 2 and not board.start:
                    show('Игроки набраны, игра начинается!')
                    ttt = 'Игрок 1: ' + gamers[0]['name'] + ' (' + gamers[0]['color'] + ')'
                    show(ttt)
                    board.log.append(ttt)
                    ttt = 'Игрок 2: ' + gamers[1]['name'] + ' (' + gamers[1]['color'] + ')'
                    show(ttt)
                    board.log.append(ttt)
                    board.start = True
                    board.show()

                elif answ(bot):
                    break

            except NetworkError:
                sleep(1)
            except Unauthorized:
                # Пользователь удалил или заблокировал бота.
                UPDATE_ID += 1


end_page('')



#import matplotlib.pyplot as plt
#import numpy as np

#print(figures.size)
#arr2 = np.array(im2)
#print(arr2.shape)
#print(arr2)

#width = arr2.shape[0] - 2
#height = arr2.shape[1] - 2
#target_size = (int(width * 1.5), int(height * 1.5))

#im2 = im2.crop((off_w, off_h, width, height))
#im2 = im2.resize(target_size)

#im3 = im3.crop((off_w, off_h, width, height))
#im3 = im3.resize(target_size)

#im1 = im1.convert('RGBA')
#im2 = im2.convert('RGBA')
#im3 = im3.convert('RGBA')

#def transp(img):
#    datas = img.getdata()
#    newData = []
#    for item in datas:
#        if item[0] > 200 and item[1] > 200 and item[2] > 200:  # finding white colour by its RGB value
#            # storing a transparent value when we find a black colour
#            newData.append((255, 255, 255, 0))
#        else:
#            newData.append(item)  # other colours remain unchanged
#    img.putdata(newData)
#    return img

#im2 = transp(im2)
#im3 = transp(im3)

#rgba.save("transparent_image.png", "PNG")

#im1.paste(im2, (175,150), im2)
#im1.paste(im2, (495,150), im2)
#im1.paste(im3, (495+(495-175),150), im3)
#im1.paste(im3, (495+(495-175)*2,150), im3)
#board.paste(figures, (160,130), figures)

#board.paste(wh_pesh, (160,130), wh_pesh)
#board.paste(bl_king, (160+320,130), bl_king)

#wh_pesh.save(r'F:\_DS\wh_pesh.png')
#bl_king.save(r'F:\_DS\bl_king.png')

#arr1 = np.array(im1)
#arr1 = arr1 / 255
#plt.imshow(arr1)
