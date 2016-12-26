import os
import re

__author__ = 'Kopetsky Artem'


## ПОЖАЛУЙСТА, ОБЯЗАТЕЛЬНО СОХРАНИТЕ ПРОГРАММУ
## В ТУ ЖЕ ДИРЕКТОРИЮ, ГДЕ
## ЛЕЖАТ ИСХОДНИКИ СТИХОТВОРЕНИЙ


## глобальный счетчик строк в стихотворениях
global line_cnt
gl_line_cnt = 0

## глоб. список рифм
global rhyme_lst
rhyme_lst = []

## глоб. список тавтологических рифм
global rhyme_full_lst
rhyme_full_lst = []

## пожалуйста, не меняйте корень!
## программа, исходники и html-шаблон
## должны находиться в одном месте
## иначе придется переписывать код
global user_root
user_root = '.'

## глоб. словарь с персональными данными о рифмах для каждого автора
global auth_dict
auth_dict = {}


## ф-ия для формирования списка авторов и создания глоб. словаря
def get_poems(user_root):
    global auth_dict
    tree = os.walk(user_root)

    for rt in tree:
        ## поиск нужной директории
        if rt[0] == user_root:
            ## списковое выражение для формирования списка стихотворений
            poems_lst = [poem for poem in rt[2] if 'txt' in poem.split('.')[-1].lower() and poem[0].isupper() == True]
            ## формирование словаря
            for auth in rt[2]:
                if 'txt' in auth.split('.')[-1].lower() and auth[0].isupper() == True:
                    # 0 - простые рифмы; 1 - тавтолог. рифмы; 2 - общее число строк для автора
                    auth_dict[auth.split('_')[0]] = [[], [], 0]

    return poems_lst


## ф-ия для опредления рифмы для двух строк
## аргументы: слово предыдущей строки, слово текущей строки
def rhyme(raw_prev, raw_cur):
    #print('inp', raw_prev, raw_cur)
    global rhyme_lst

    ## ф-ия для html-разметки найденной рифмы
    ## аргумент: одно слово
    def html_parse(wd, rhm_len):
        ## цветовая разметка для разноразмерных рифм
        def select_mark(rhm_len):
            ## тавтолог. рифма
            if full_stat == True:
                return '<span class="mrkfull">'
            elif rhm_len == 2:
                return '<span class="mrk2">'
            elif rhm_len == 3:
                return '<span class="mrk3">'
            elif rhm_len >= 4:
                return '<span class="mrk4">'

        ## индекс для вставки html-тэга
        index = len(wd) - rhm_len
        mark = select_mark(rhm_len)
        return wd[:index] + mark + wd[index:] + '</span>'

    ## очистка поступивших на вход слов от знаков препинания
    prev = re.sub('[\W]', '', raw_prev)
    cur = re.sub('[\W]', '', raw_cur)

    ## определение предельного размера рифмы
    if len(prev) > len(cur):
        index = len(cur)
    else:
        index = len(prev)

    rhyme = ''
    i = -1
    flag = True

    ## непосредственно процесс нахождения рифмы
    while i >= index*(-1):
        if prev[i].lower() == cur[i].lower() and flag == True:
            rhyme = cur[i].lower() + rhyme

        ## сброс на первом несовпадении символов
        else:
            flag = False
        i -= 1

    ## работа с найденной ненулевой рифмой
    if rhyme != '' and len(rhyme) > 1:

        ## проверка на тавтологическую рифму
        if prev == cur:
            full_stat = True
            rhyme_full_lst.append(rhyme)
        else:
            full_stat = False
            rhyme_lst.append(rhyme)

        ## html-парсинг рифм в обрабатываемых словах
        ## с сохранением пунктуации
        prev_prs = html_parse(prev, len(rhyme)) + re.sub('[\w]', '', raw_prev)
        cur_prs = html_parse(cur, len(rhyme)) + re.sub('[\w]', '', raw_cur)
        return rhyme, (prev_prs, cur_prs), len(rhyme), full_stat

    ## возврат при отсутствии рифмы
    else:
        return 'none', 0


## ф-ия для разметки стихотворения
## аргумент: стихотворение из списка
## важно: стихотворение считывается в список
## и парсится динамическим изменением
## считанного списка
def parse_poem(poem, auth):
    global gl_line_cnt
    global auth_dict

    ## список рифм и тавтолог. рифм (full) для текущего автора
    cur_rhm = []
    cur_rhm_full = []

    ## вспомогательная ф-ия для очистки слов от html-тэгов
    ## издержка динамического изменения
    def word_fix(wd):
        return re.sub('<.*?>', '', wd).lower()

    ## считывание стиховтворения в список
    lns = open(poem, 'r', encoding='UTF-8').readlines()
    gl_line_cnt += len(lns)

    ## парсинг динамическим изменением списка
    for i in range(1, len(lns)):
        ## извлечение конечных слов для обрабатываемых строк
        ## строки обрабатываются по принципу предыдущая + текущая
        ## исключение для отслеживания и вывода "плохих=пустых строк"
        try:
            if '<span' not in lns[i-1]:
                prev_word =  word_fix(lns[i-1].split()[-1])
            else:
                prev_word = word_fix(''.join(lns[i-1].split()[-2:]))

            if '<span' not in lns[i]:
                cur_word =  word_fix(lns[i].split()[-1])
            else:
                cur_word = word_fix(''.join(lns[i].split()[-2:]))
        except:
            print('bad lines: ' + str(i-1) + ',' + str(i))
            continue

        ## проверка на рифму для конечных слов текущих строк
        rhm_res = rhyme(prev_word, cur_word)

        ## при наличии рифмы
        if rhm_res[0] != 'none':
            # проверка текущей рифмы на тавтологический статус
            if rhm_res[3] == True:
                cur_rhm_full.append(rhm_res[0])
            else:
                cur_rhm.append(rhm_res[0])

            ## динамическое изменение стихотворения
            ## = окончательный html-парсинг строк
            ## исходная "чистая" строка стихотворения
            ## заменяется на html-распарсенную
            if '<span' not in lns[i-1]:
                lns[i-1] = ' '.join(lns[i-1].split()[:-1]) + ' ' + rhm_res[1][0] + '\n'
            if '<span' not in lns[i]:
                lns[i] = ' '.join(lns[i].split()[:-1]) + ' ' + rhm_res[1][1] + '\n'

    ## пополнение статистических данных
    ## для автора текущего стихотворения
    ## 0 - список рифм
    ## 1 - список тавтолог. рифм
    ## 2 - количество строк в текущем стихотворении
    for name in auth_dict:
        if name in auth:
            auth_dict[name][0].extend(cur_rhm)
            auth_dict[name][1].extend(cur_rhm_full)
            auth_dict[name][2] += len(lns)

    return lns


## создание html
## аргументы:
## auth - автор + название (= имя исходника)
## poem - размеченный текст стиховторения
def build_html(auth, poem):
    ## шаблон для порождения html
    tmpl = open('template.txt', 'r', encoding='UTF-8').read()
    ## заполнение шаблона
    poem_data = tmpl.replace('/AUTHOR/', auth)
    poem_data = poem_data.replace('/TEXT/', '<br>'.join(poem))

    ## создание директории parsed_html для хранения html
    prs_dir = user_root + r'\parsed_html\\'
    if os.path.exists(prs_dir) != True:
        os.makedirs(prs_dir)

    ## создание и запись текущего html
    poem_html = open(prs_dir + auth + '.html', 'w', encoding='UTF-8')
    poem_html.write(poem_data)
    poem_html.close()

    return print(auth + ' successfully PARSED')


## ф-ия для получения статистики
## глобальной и для каждого автора
## результаты записываются персональными
## файлами для автров в создаваемую директорию
def get_stats(auth):
    ## ф-ия для статист. обработки списков с рифмами
    def process_rhymes(rhms, rhm_type):
        ## поиск самой частовстречаемой рифмы
        def max_freq(rhms):
            if len(rhms) > 0:
                d = {}

                ## словарь с рифмами и их частотами
                for wd in rhms:
                    if wd in d:
                        d[wd] += 1
                    else:
                        d[wd] = 1
                mx = 0
                res_wd = ''

                ## поиск самой частой
                for wd in d:
                    if d[wd] > mx:
                        mx = d[wd]
                        res_wd = wd
                return res_wd + ' (' + str(mx) + ')'
            else:
                return 'None'

        ## поиск самой длинной рифмы
        def max_len(rhms):
            if len(rhms) > 0:
                mx = rhms[0]
                for i in range(1, len(rhms)):
                    if len(rhms[i]) > len(mx):
                        mx = rhms[i]
                return mx
            else:
                return 'None'

        ## метод обработки списка нетавтолог. рифм
        if rhm_type != 'full':
            ## рифмы длины 2
            rhms2 = [rhm for rhm in rhms if len(rhm) == 2]
            ## рифмы длины 3
            rhms3 = [rhm for rhm in rhms if len(rhm) == 3]
            ## рифмы длины 4 и более
            rhms4 = [rhm for rhm in rhms if len(rhm) >= 4]

            rhms2_inf = str(len(rhms2))#, max_freq(rhms2)]
            rhms3_inf = str(len(rhms3))#, max_freq(rhms3)]
            rhms4_inf = [str(len(rhms4)), max_len(rhms4), max_freq(rhms4)]
            return rhms2_inf, rhms3_inf, rhms4_inf

        ## обработка списка тавтолог. рифм
        else:
            return str(len(rhms)), max_len(rhms), max_freq(rhms)

    ## создание директории для пофайлового
    ## хранения статистики
    stats_dir = user_root + r'\stats\\'
    if os.path.exists(stats_dir) != True:
        os.makedirs(stats_dir)

    ## ALL GLOBAL - ключ для глобальной статистики
    ## при иных значениях auth выполняется
    ## сбор статистики для конкретного автора
    if auth != 'ALL GLOBAL':
        ## создание файла статистики текущего автора
        f = open(stats_dir + auth + '.txt', 'w', encoding='UTF-8')

        ## получение списков рифм
        ## и количества строк
        rhm_lst = auth_dict[auth][0]
        rhm_full_lst = auth_dict[auth][1]
        lns_num = auth_dict[auth][2]

        ## всего рифм для автора
        rhms_num = len(rhm_lst) + len(rhm_full_lst)

        # 0 - 2x рифмы; 1 - 3х рифмы; 2 - 4+ рифмы
        rhm_inf = process_rhymes(rhm_lst, 'not_full')

        # 0 - общее количество; 1 - самая длинная; 2 - самая частая
        rhm_full_inf = process_rhymes(rhm_full_lst, 'full')

    ## аналогичный процесс для глоб. статистики
    else:
        f = open(stats_dir + auth + '.txt', 'w', encoding='UTF-8')

        rhms_num = len(rhyme_lst) + len(rhyme_full_lst)
        lns_num = gl_line_cnt
        rhm_inf = process_rhymes(rhyme_lst, 'not_full')
        rhm_full_inf = process_rhymes(rhyme_full_lst, 'full')

    ## запись статистического файла
    f.write('Id: ' + auth + ';\n\n'
            + 'Rhymes_total: ' + str(rhms_num) + ';\n'
            + 'Lines_total: ' + str(lns_num) + ';\n'
            + 'Rhyme_ratio: ' + str(round(rhms_num / lns_num * 100, 2)) + '%;\n\n'
            + '2x_rhymes: ' + rhm_inf[0] + ';\n'
            + '3x_rhymes: ' + rhm_inf[1] + ';\n'
            + '4+_rhymes: ' + rhm_inf[2][0] + ';\n'
            + 'Most_frequent_4+_rhyme: ' + rhm_inf[2][2] + ';\n'
            + 'Longest_4+_rhyme: ' + rhm_inf[2][1] + ';\n\n'
            + 'Full_rhymes: ' + rhm_full_inf[0] + ';\n'
            + 'Most_frequent_full_rhyme: ' + rhm_full_inf[2] + ';\n'
            + 'Longest_full_rhyme: '  + rhm_full_inf[1] + '\n\n')

    f.close()

    return print(auth + ' STATISTICS PARSED')


## ф-ия для записи в файл
## всех тавтолог. рифм
## с их частотами
def wrt_full_rhms(rhms):
    full_rhm_d = {}
    f = open(r'.\full_rhymes.txt', 'w', encoding='UTF-8')

    ## сбор рифм и частот
    for el in rhms:
        if el not in full_rhm_d:
            full_rhm_d[el] = 1
        else:
            full_rhm_d[el] += 1

    ## запись
    for el in full_rhm_d:
        f.write(el + ':' + str(full_rhm_d[el]) + '\n')
    f.close()

    return 0


def main():
    ## получить список стихотворений
    poems_lst = get_poems(user_root)

    ## разметить стихотворения
    for poem in poems_lst:
        auth = ''.join(poem.split('.')[:-1])
        poem_prs = parse_poem(poem, auth)
        build_html(auth, poem_prs)

    ## получить глоб. статистику
    get_stats('ALL GLOBAL')

    ## получить статистику для авторов
    for name in auth_dict:
        get_stats(name)

    ## записать отдельно все
    ## тавтолог. рифмы и их частоты
    wrt_full_rhms(rhyme_full_lst)

    return print('\nALL DONE')

main()
print('rhymes: ' + str(len(rhyme_lst) + len(rhyme_full_lst)))
print('lines: ' + str(gl_line_cnt))