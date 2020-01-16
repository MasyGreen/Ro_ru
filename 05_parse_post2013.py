import os
import time
from lxml import html
from threading import Thread
from multiprocessing import Queue
import requests
import glob
from xml.etree import ElementTree as ET
import re

_stp = r'd:\_roru\\'[:-1]
_folder_post_parse2013 = '{}{}'.format(_stp, r'04_post_2013\\'[:-1])  # папка с постами 2013 года

def write_user_to_xml(d_user_code, d_user_name):  # пишем уникальных пльзователй в xml
    _UUE_Array_El = [d_user_code,
                     '{}{}'.format('https://www.roller.ru/forum/memberlist.php?mode=viewprofile&u=', d_user_code),
                     d_user_name]
    _UUE_Array.append(_UUE_Array_El)


def write_post_user_to_xml(d_user_code, d_user_name,
                           d_post_code):  # пишем набор +1 на покатушку _user_code,_user_name, d_post_code
    _PU_Array_El = [d_user_code,
                    d_user_name,
                    '{}{}'.format('https://www.roller.ru/forum/memberlist.php?mode=viewprofile&u=', d_user_code),
                    d_post_code,
                    '{}{}'.format('https://www.roller.ru/forum/viewtopic.php?f=3&t=', d_post_code)]
    _PU_Array.append(_PU_Array_El)

def parse_post(dw_post_uq):
    _files = glob.glob('{}{}*.html'.format(_folder_post_parse2013, dw_post_uq))
    _user_inpost_unique = []
    _user_inpost_unique.clear()
    for _file in _files:
        print('{}, {}'.format(_file, work_queue.qsize()))
        with open(_file, 'r', encoding='UTF-8') as fileR:
            _str = fileR.read()
            _main_tree = html.fromstring(_str)  # загружаем в строку
            _messages = _main_tree.xpath('.//table[@class="tablebg"]')
            for _message in _messages:
                _user_tree = _message.xpath('.//tr/th/noindex/a')[0]
                # print(html.tostring(_user_tree, encoding='unicode'))
                d_user_code = _user_tree.get('href')
                d_user_code = d_user_code.replace('./memberlist.php?mode=viewprofile&u=', '')
                d_user_code = d_user_code.split('&')[0]
                d_user_name = _user_tree.text

                _mess_tree = _message.xpath('.//div[@class="postbody"]')[0]
                _mess_str = html.tostring(_mess_tree, encoding='unicode')

                if not d_user_code in _user_unique:  # сохраняем уникальный набор пользователй
                    _user_unique.append(d_user_code)
                    write_user_to_xml(d_user_code, d_user_name)

                if not d_user_code in _user_inpost_unique:  # сохраняем уникальный набор участников
                    _user_inpost_unique.append(d_user_code)
                    write_post_user_to_xml(d_user_code, d_user_name, dw_post_uq.split('_')[0])


def process(dw_TheadName):
    while not work_queue.empty():
        _post_uq = work_queue.get()
        # time.sleep(.1)
        print('THEAD {} - {}'.format(_post_uq, dw_TheadName))
        parse_post(_post_uq)


def main():
    list_th = []
    for i in range(200):
        p1 = Thread(target=process, args=['Thead{}'.format(i)])
        list_th.append(p1)

    for th in list_th:
        th.start()

    for th in list_th:
        th.join()
    _folder_post_prs = '{}{}'.format(_stp, r'03_post_prs\\'[:-1])  # каталог для записи

    # ----------------------------file exchange----------------------------------------
    _export_xml_file = '{}{}'.format(_folder_post_prs, 'full_data_2013.xml')  # имя файла
    _xml_root = ET.Element("root")  # корневой элемент
    _xml_references = ET.SubElement(_xml_root, "references")  # общее дерево

    #----------------------------ЗАПИСЫВАЕМ УНИКАЛЬНЫХ ПОЛЬЗОВАТЕЛЕЙ-----------------------------------
    _user_unique_root_SBR = ET.SubElement(_xml_references, "reference")
    _user_unique_root_SBR.set("reference_name", "user")

    for _i in range(len(_UUE_Array)):
        _user_unique_item = ET.SubElement(_user_unique_root_SBR, "item")
        _user_unique_item.set("user_code", _UUE_Array[_i][0])
        _user_unique_item.set("user_link", _UUE_Array[_i][1])
        _user_unique_item.set("user_name", _UUE_Array[_i][2])

    #----------------------------ЗАПИСЫВАЕМ ПОСЕТИТЕЛЕЙ ПОКАТУШЕК------------------------------
    _post_user_root_SBR = ET.SubElement(_xml_references, "reference")
    _post_user_root_SBR.set("reference_name", "post_user")

    for _i in range(len(_PU_Array)):
        _post_user_item = ET.SubElement(_post_user_root_SBR, "item")
        _post_user_item.set("user_code", _PU_Array[_i][0])
        _post_user_item.set("user_name", _PU_Array[_i][1])
        _post_user_item.set("user_link", _PU_Array[_i][2])
        _post_user_item.set("post_code", _PU_Array[_i][3])
        _post_user_item.set("post_link", _PU_Array[_i][4])

    # ----------------------------file exchange----------------------------------------
    _xml_tree = ET.ElementTree(_xml_root)  # записываем дерево в файл
    _xml_tree.write(_export_xml_file)  # сохраняем файл


if __name__ == "__main__":
    _user_unique = []
    _UUE_Array = []
    _PU_Array = []
    # -------------------------------------------------------------------------------------------------
    _list_post = []
    _list_post.clear()
    _list_files = os.listdir(_folder_post_parse2013)  # получаем все файлы с постами (48341_83391_0.html, 48341_83391_1.html....)
    for _file in _list_files:
        _post_user = _file.split('.')[0]
        _post_user = '{}_{}'.format(_post_user.split('_')[0], _post_user.split('_')[1])
        if _post_user not in _list_post:
            _list_post.append(_post_user)  #  выбираем уникальные наборы (пост+ведущий) 48341_83391_0.html = 48341_83391
    # -------------------------------------------------------------------------------------------------
    # _list_post.clear()
    # _list_post.append('15700_3952')
    work_queue = Queue()
    for _post in _list_post:
        work_queue.put(_post)
    main()
