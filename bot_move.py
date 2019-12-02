import random

# Возвращает индекс элемента, куда надо поставить Х или О, или ответ
def bot_move(field, xo):
    # Список с количеством элемента xo в каждой строке
    count_xo = count_XO(field, xo)
    if 3 in count_xo:
        return 'You win!'
    # Список с количеством элемента xo_bot в каждой строке
    xo_bot = 'X' if xo == 'O' else 'O'
    count_xo_bot = count_XO(field, xo_bot)
    # Ищем строку с 2-я xo_bot и третьим ' '
    row_index, elem_index = search_3rd_elem_index(field, count_xo_bot, ' ')
    if type(elem_index) == type(999):
        index = return_index(row_index, elem_index)
        return [index, 'You lose']
    # Ищем строку с 2-я xo и третьим ' '
    row_index, elem_index = search_3rd_elem_index(field, count_xo, ' ')
    if type(elem_index) == type(999):
        index = return_index(row_index, elem_index)
        return index
    # Список с количеством незаполненных клеток в каждой строке
    count_ = count_XO(field, ' ')
    # Ищем строку с 2-я ' ' и третьим элементом xo_bot
    row_index, elem_index = search_3rd_elem_index(field, count_, xo_bot)
    if type(elem_index) == type(999):
        if elem_index == 0:
            rand = random.choice([1,2])
        elif elem_index == 1:
            rand = random.choice([1,-1])
        else:
            rand = random.choice([-1,-2])
        elem_index += rand
        index = return_index(row_index, elem_index)
        return index
    # Строка со всеми пустыми элементами
    if 3 in count_:
        elem_index = random.choice([0,1,2])
        index = return_index(count_.index(3), elem_index)
        return index
    return 'Draw'

def countRow(m, i, xo):
    return m[i].count(xo)

def countCol(m, i, xo):
    return [r[i] for r in m].count(xo)

def countDiag1(m, xo):
    return [m[i][i] for i in range(3)].count(xo)

def countDiag2(m, xo):
    return [m[i][2-i] for i in range(3)].count(xo)

def count_XO(m, xo):
    # Возвращает список с количеством элемента 'xo' в каждой строке 
    count_list = []
    for i in range(3):
        count_list.append(countRow(m, i, xo))
    for i in range(3):
        count_list.append(countCol(m, i, xo))
    count_list.append(countDiag1(m, xo))
    count_list.append(countDiag2(m, xo))
    return count_list

def check_elem(m, i, xo):
    # Проверяет есть ли элемент 'xo' в строке с индексом i
    # Возвращает индекс элемента или False
    if i <= 2:
        l = m[i]
    elif i <= 5:
        l = [r[i-3] for r in m]
    elif i == 6:
        l = [m[j][j] for j in range(3)]
    else:
        l = [m[j][2-j] for j in range(3)]
    if xo in l:
        return l.index(xo)
    else:
        return False

def search_3rd_elem_index(m, list_count, elem):
    # Ищет строку с двумя одинаковыми элементами и третьим элементом 'elem'
    # list_count - список с количеством элемента 'xo' в каждой строке
    # Возвращает индекс строки в list_count и индекс elem в строке, если найдено,
    # и False, False - если нет
    c_2elem = list_count.count(2)
    i_2elem = -1
    while c_2elem != 0:
        i_2elem = list_count.index(2, i_2elem+1)
        index_3rd_elem = check_elem(m, i_2elem, elem)
        if type(index_3rd_elem) == type(999):
            return i_2elem, index_3rd_elem
        c_2elem -= 1
    return False, False

def return_index(row_index, elem_index):
    if row_index <= 2:
        field_index = row_index, elem_index
    elif row_index <= 5:
        field_index = elem_index, row_index-3
    elif row_index == 6:
        field_index = elem_index, elem_index
    else:
        field_index = elem_index, 2-elem_index
    return 3*field_index[0] + field_index[1]


if __name__ == '__main__':
    m = [['O', ' ', 'X'],
         ['X', 'O', 'O'],
         ['O', 'X', 'X']]

    func(m)
