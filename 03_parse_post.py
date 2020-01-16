import time
import os
from threading import Thread
from multiprocessing import Queue
from lxml import html
from xml.etree import ElementTree as ET
import re

# ШАГ 3
# ПРОХОДИМ ПО ВСЕМ СКАЧАННЫМ ПОСТАМ В _folder_post = r'..\02_post\\'[:-1]  # каталог с постами - для чтения
# РАЗБИРАЕМ КАЖДЫЙ ПОСТ И ФОРМИРУЕМ РАЗОБРАННУЮ ИНФОРМАЦИЮ ИЗ ПОСТОВ В
# _folder_post_prs = r'..\03_post_prs\\'[:-1]  # каталог для записи
#
# ДОПУЩЕНИЯ:
# ВЕДУЩИЙ ТОТ КТО СОЗДАЛ ПЕРВЫЙ ПОСТ
# ЕСЛИ НЕТ ДАТЫ ПОКАТУШКИ - ПОКАТУШКА НА ДАТУ ПЕРВОГО ПОСТА
#
# ФОРМИРУЕМ 3 ФАЙЛА: user.xml (ПОЛЬЗОВАТЕЛИ), post_user.xml (УЧАСТНИКИ ПОКАТУШЕК), post.xml (ПОКАТУШКИ)


# словарь для даты '28', 'мар', '2007'
unit_month = {'янв': '01', 'фев': '02', 'мар': '03', 'апр': '04', 'май': '05', 'июн': '06', 'июл': '07', 'авг': '08',
              'сен': '09', 'окт': '10', 'ноя': '11', 'дек': '12'}


def get_date_from_str(d_str):  # разбираем дату типа '28', 'мар', '2007'
    s_str_s = d_str.split(' ')
    var_date = '{}.{}.{}'.format(s_str_s[0], unit_month[s_str_s[1]], s_str_s[2])
    return var_date


def add_el_user(user_code, user_name):  # пользователи
    if user_code != "":
        if not user_code in _user_u:
            _user_u.append(user_code)
            _row = {"user_code": user_code,
                    "user_name": user_name}
            _user_array.append(_row)

def add_el_post_user(user_code, user_name,
                     post_code, post_date, master_code, master_name):  # посты
    _find_str = '{}{}'.format(user_code, post_code)
    if not _find_str in _post_user_u:
        _post_user_u.append(_find_str)
        _row = {"user_code": user_code,
                "user_name": user_name,
                "post_code": post_code,
                "post_date": post_date,
                "master_code": master_code,
                "master_name": master_name}
        _post_user_array.append(_row)

def add_el_post(post_code, post_name, post_date, user_code,
                user_name):  # пишем уникальных пльзователй в xml
    _row = {"post_code": post_code,
            "post_name": post_name,
            "post_date": post_date,
            "user_code": user_code,
            "user_name": user_name}
    _post_array.append(_row)

def get_postuser(d_first_post, d_post_code, d_host_code, d_host_name):  # получем набор +1 на покатушку
    # print('------------get_postuser-----------')
    # print(html.tostring(d_first_post, encoding='unicode'))
    # d_links = d_first_post.xpath('.//a[@href]')
    # print('---------------------------------------------------------')
    # print(html.tostring(d_links[1], encoding='unicode'))
    d_linksm = d_first_post.xpath('.//table[@cellpadding="3"]/tr/td')
    d_links = d_linksm[2].xpath('.//a[@href]')

    # print(html.tostring(d_links[0], encoding='unicode'))
    add_host = False
    for d_link in d_links:  # коды пользователей
        d_links_txt = html.tostring(d_link, encoding='unicode')
        d_user_code = ''
        d_user_name = ''
        if d_links_txt.find('<a href="memberlist.php?mode=viewprofile&amp;u=') != -1 and d_links_txt.find(
                'forum') == -1:
            # print(d_links_txt)
            d_user_code = d_link.get('href')
            d_user_code = d_user_code.replace('memberlist.php?mode=viewprofile&u=', '')
            d_user_name = d_link.text
            if d_host_code == d_user_name:
                add_host = True
            add_el_post_user(d_user_code, d_user_name, d_post_code,'','','')
            add_el_user(d_user_code, d_user_name)

            # print('{}-{}'.format(d_user_code, d_user_name))  # код поста
            # print('---------------------------------------------------')
            # print(d_links_txt)
            # print(html.tostring(d_link, encoding='unicode'))
    if not add_host:
        add_el_post_user(d_host_code, d_host_name, d_post_code,'','','')

def parse_file(_list_file):
    try:
        _post_code = _list_file.split('.')[0]  # получаем код поста из имени файла
        if True:
        #if _list_file == '56678.html':
            #print(_list_file)
            _file_name = '{}{}'.format(_export_folder, _list_file)  # html с постом
            # ----------------------------------------------------------------------------
            # Получаем перый пост, в нем вся нужная информация
            # ----------------------------------------------------------------------------
            with open(_file_name, 'r', encoding='UTF-8') as fileR:
                file_data_str = fileR.read()
                tree = html.fromstring(file_data_str)  # загружаем в строку
                links_h3 = tree.xpath('.//h3')  # выбираем блоки h3
                links_tablebg = tree.xpath('.//table[@class = "tablebg"]')  # выбираем блоки

            try:
                is_first = True
                for link_tablebg in links_tablebg:
                    txt_link = html.tostring(link_tablebg, encoding='unicode')
                    if txt_link.find("memberlist.php?mode=viewprofile") != -1 and is_first:
                        main_post = link_tablebg  # сохраняем первый пост - это первый бок
                        is_first = False
                        # print(txt_link)
                        # print('---------------------------------------------------------------------')
                        # print(re.findall('cap-div', txt_link))
                        # print(html.tostring(links[1], encoding='unicode'))
            except:
                print('Error {}_{}({})'.format(_list_file, 'Error', 'main_post'))

            # print(html.tostring(first_post, encoding='unicode'))

            # ----------------------------------------------------------------------------
            # Разбираем параметры поста
            # ----------------------------------------------------------------------------

            # Название покатушки
            # ----------------------------------------------------------------------------
            try:
                _post_name = links_h3[0].text  # Название покатушки
                #print('{} = {}'.format('_post_name', _post_name))
            except:
                print('Error {}_{}({})'.format(_list_file, 'Error', '_post_name'))
                _post_name = '########'

            try:
                _links_nofollow = main_post.xpath('.//a[@rel="nofollow"]')
            except:
                print('Error {}_{}({})'.format(_list_file, 'Error', '_links_nofollow'))

            try:
                head_post = main_post.xpath('.//div[@class="postbody"]')
            except:
                print('Error {}_{}({})'.format(_list_file, 'Error', 'head_post'))

            # print(html.tostring(head_post[0], encoding='unicode'))

            # Дата проведения
            # ----------------------------------------------------------------------------
            try:
                _post_date = re.findall('\d\d.\d\d.\d\d\d\d', head_post[0].text)[0]
                #print('{} = {}'.format('_post_date', _post_date))
            except:
                # print(html.tostring(main_post, encoding='unicode'))
                # print('----------------------------------------------------------------------')
                try:
                    _links_postdate = main_post.xpath('.//span[@class="postdate"]/text()')[0]
                    _post_date = get_date_from_str(_links_postdate)
                    #print('{} = {}'.format('_post_date', _post_date))
                except:
                    print('Error {}_{}({})'.format(_list_file, 'Error', '_post_date'))
                    _post_date = '##/##/####'

            # Имя ведущего
            # ----------------------------------------------------------------------------
            try:
                _user_name = _links_nofollow[0].text
                #print('{} = {}'.format('_user_name', _user_name))
            except:
                print('Error {}_{}({})'.format(_list_file, 'Error', '_user_name'))
                _user_name = '########'

            # Код ведущего
            # ----------------------------------------------------------------------------
            try:
                _user_code = _links_nofollow[0].get('href')
                _user_code = _user_code.replace('./memberlist.php?mode=viewprofile&u=', '')
                _user_code = _user_code.split('&')[0]
                if not _user_code in _user_u:  # сохраняем уникальный набор пользователй
                    _user_u.append(_user_code)
                    add_el_user(_user_code, _user_name)

                #print('{} = {}'.format('_user_code', _user_code))
            except:
                print('Error {}_{}({})'.format(_list_file, 'Error', '_user_code'))
                _user_code = '########'

            # Участники покатушки
            # ----------------------------------------------------------------------------
            try:
                get_postuser(main_post, _post_code, _user_code,
                             _user_name)  # получаем коды отметившихся/заполняем таблицы user, postuser
            except:
                add_el_post_user(_user_code, _user_name, _post_code,'','','')
                print('Error {}_{}({})'.format(_list_file, 'Error', 'get_post_user'))

            #  записываем в XML
            add_el_post(_post_code, _post_name, _post_date, _user_code, _user_name)
    except:
        print('Error {}_{}'.format(_list_file, 'Error'))

def process(dw_TheadName):
    while not work_queue.empty():
        _list_file = work_queue.get()
        time.sleep(.1)
        parse_file(_list_file)
        #print('THEAD {} - {}'.format(_list_file, dw_TheadName))

def main():

    list_th = []
    for i in range(50):
        p1 = Thread(target=process,  args=['Thead{}'.format(i)])
        list_th.append(p1)

    for th in list_th:
        th.start()

    for th in list_th:
        th.join()

    # ----------------------------file exchange----------------------------------------
    _export_xml_file = '{}{}'.format(_folder_post_prs, 'full_data.xml')  # имя файла
    _xml_root = ET.Element("root")  # корневой элемент
    _xml_references = ET.SubElement(_xml_root, "references")  # общее дерево

    # ----------------------------ЗАПИСЫВАЕМ УНИКАЛЬНЫХ ПОЛЬЗОВАТЕЛЕЙ-----------------------------------
    _user_root_SBR = ET.SubElement(_xml_references, "reference")
    _user_root_SBR.set("reference_name", "user")

    for _i in sorted(_user_array, key=lambda i: int(i['user_code'])):
        _user_unique_item = ET.SubElement(_user_root_SBR, "item")
        _user_unique_item.set("user_code", _i.get('user_code'))
        _user_unique_item.set("user_name", _i.get('user_name'))

    # ----------------------------ЗАПИСЫВАЕМ ПОСЕТИТЕЛЕЙ ПОКАТУШЕК------------------------------
    _post_user_root_SBR = ET.SubElement(_xml_references, "reference")
    _post_user_root_SBR.set("reference_name", "post_user")

    for _i in _post_user_array:
        _post_user_item = ET.SubElement(_post_user_root_SBR, "item")
        _post_user_item.set("user_code", _i.get('user_code'))
        _post_user_item.set("user_name", _i.get('user_name'))
        _post_user_item.set("post_code", _i.get('post_code'))
        _post_user_item.set("post_date", _i.get('post_date'))
        _post_user_item.set("master_code", _i.get('master_code'))
        _post_user_item.set("master_name", _i.get('master_name'))

    # ----------------------------ЗАПИСЫВАЕМ ПОСТЫ------------------------------------------
    _post_root_SBR = ET.SubElement(_xml_references, "reference")
    _post_root_SBR.set("reference_name", "post")

    for _i in _post_array:
        _post_item = ET.SubElement(_post_root_SBR, "item")
        _post_item.set("post_code", _i.get('post_code'))
        _post_item.set("post_name", _i.get('post_name'))
        _post_item.set("post_date", _i.get('post_date'))
        _post_item.set("user_code", _i.get('user_code'))
        _post_item.set("user_name", _i.get('user_name'))

    # ----------------------------file exchange----------------------------------------
    _xml_tree = ET.ElementTree(_xml_root)  # записываем дерево в файл
    _xml_tree.write(_export_xml_file)  # сохраняем файл


if __name__ == "__main__":
    _start_folder = r'd:\\_roru\\'[:-1]
    _export_folder = '{}{}'.format(_start_folder, r'02_post\\'[:-1])  #   # каталог с постами - для чтения
    _folder_post_prs = '{}{}'.format(_start_folder, r'03_post_prs\\'[:-1])  # # каталог с постами - для чтения

    _list_files = os.listdir(_export_folder)  # получаем все файлы с постами

    _user_array = []
    _post_user_array = []
    _post_array = []

    _user_u = []
    _user_u.clear()

    _post_u = []
    _post_u.clear()

    _post_user_u = []
    _post_user_u.clear()

    work_queue = Queue()

    for _list_file in _list_files:
        work_queue.put(_list_file)

    main()
