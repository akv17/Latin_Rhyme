import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os


__author__ = 'Kopetsky Artem'


## ПОЖАЛУЙСТА, СОХРАНИТЕ ПРОГРАММУ
## В ТУ ЖЕ ДИРЕКТОРИЮ, ГДЕ
## ЛЕЖИТ lat_rhyme.py


## датафрейм (или структура данных)
## всей статистики
global df

## счетчик для индексации
global i
i = 0

## ф-ия для создания списка
## со статистич. файлами
def get_stats():
    tree = os.walk(r'.\stats\\')
    st_lst = [fl.split('.')[0] for rt in tree for fl in rt[2]]

    return st_lst


## ф-ия возвращает статистич. значения
## для каждого автора в соответств.
## pandas формате
def fl_parse(auth):
    global i
    i += 1
    f = [el.strip('\n') for el in open(r'.\stats\\' + auth + '.txt', 'r', encoding='UTF-8').read().split(';')]

    #name = f[0]

    ## получить статистич. значения
    vals = [el.split(':')[1].strip(' ') for el in f if ':' in el]

    return i, vals


## заполнение датафрейма со
## всей статистикой
def build_df(lst):
    global df

    ## ф-ия собирающая значения
    ## столбцов датафрема
    ## из source-файла
    def get_columns(source):
        f = [el.strip('\n') for el in open(r'.\stats\\' + source + '.txt', 'r', encoding='UTF-8').read().split(';')]
        cols = [el.split(':')[0] for el in f if ':' in el]
        return cols

    ## заполнение статистич. значений
    ##  для всех авторов
    inf = []
    for auth in lst:
        inf.append(fl_parse(auth))

    ## заполнение столбцов
    colmns = get_columns('ALL GLOBAL')

    ## создание датафрейма
    df = pd.DataFrame.from_items(inf, orient='index', columns=colmns)

    return 0


## ф-ия для создания директории
## для хранения изображ. графиков
def plot_dir():
    plot_dir = r'.\plot_data\\'
    if os.path.exists(plot_dir) != True:
        os.makedirs(plot_dir)

    return print('plot_dir rooted')


def main():
    global df

    ## получить список всех
    ## статистич. файлов
    st_lst = get_stats()

    ## создать датафрейм
    build_df(st_lst)

    ## создать html-таблицу датафрейма
    df.to_html('stats_table.html')

    ## экспортировать датафрейм в csv
    df.to_csv('lat_df.csv')

    ## создать директорию для графики
    plot_dir()

    return print('ALL DONE')


main()