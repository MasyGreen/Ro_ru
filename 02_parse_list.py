#  ------------------------------------------------------------------------
from threading import Thread
from multiprocessing import Queue
import os
import time
import requests
from lxml import html


# ШАГ 2
# ИЗ КАТАЛОГА _folder_list = r'..\01_list\\'[:-1] ПРОХОДИМ ПО СОХРАНЕНЫМ СТРАНИЦАМ ОГЛАВЛЕНИЯ
# ИЗ КАЖДОЙ СТАНЦЫ ОГЛАВЛЕНИЯ ПОЛУЧАЕМ ССЫЛКИ НА ПОСТЫ
# СОХРАНЯЕМ ПОСТЫ В (файлы не перазакачиваем) _folder_post = r'...\02_post\\'[:-1]
# ИМЯ ФАЙЛ = ИДЕНТИФИКАТОР ПОСТА
#  ------------------------------------------------------------------------
def get_html(dw_url, dw_name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
    }
    response = requests.get(dw_url, headers=headers)

    # print('========================================================================')
    _main_tree = html.fromstring(response.text)  # загружаем в строку
    links_body = _main_tree.xpath('./body')  # выбираем блоки h3
    # print(html.tostring(links_body[0], encoding='unicode'))
    # print('========================================================================')
    _out_text = html.tostring(links_body[0], encoding='unicode')
    _body_del = links_body[0].xpath('.//table[@class="nopadding"]')
    _body_del2 = links_body[0].xpath('.//table[@class="nopading"]')
    _body_del3 = links_body[0].xpath('.//table[@style="padding-top:30px"]')
    _body_del4 = links_body[0].xpath('.//table[@class = "tablebg"]')

    for outt in _body_del:
        # print('========================================================================')
        # print(html.tostring(outt, encoding='unicode'))
        _out_text = _out_text.replace(html.tostring(outt, encoding='unicode'), '')
    # print('========================================================================')
    # print(html.tostring(_body_del2[0], encoding='unicode'))
    # print('start {} - {}'.format(dw_url, dw_name))
    if len(_body_del2) > 0:
        _out_text = _out_text.replace(html.tostring(_body_del2[0], encoding='unicode'), '')
    # print('end {} - {}'.format(dw_url, dw_name))
    if len(_body_del3) > 0:
        _out_text = _out_text.replace(html.tostring(_body_del3[0], encoding='unicode'), '')

    is_first = True
    for outt in _body_del4:
        txt_link = html.tostring(outt, encoding='unicode')
        if is_first == False:
            _out_text = _out_text.replace(html.tostring(outt, encoding='unicode'), '')
        if txt_link.find("memberlist.php?mode=viewprofile") != -1 and is_first:
            is_first = False
        if is_first == True:
            _out_text = _out_text.replace(html.tostring(outt, encoding='unicode'), '')
    return _out_text


def process(dw_TheadName):
    while not work_queue.empty():
        _num_post = work_queue.get()
        time.sleep(.5)
        page_url = '{}{}'.format('https://www.roller.ru/forum/viewtopic.php?f=3&t=', _num_post)  # ссылка для скачивания
        page_html = '{}{}{}'.format(_post_folder, _num_post, '.html')  # путь для сохранения
        # print(page_url)
        # print(page_html)
        print('THEAD {} - {}'.format(page_url, dw_TheadName))
        r = get_html(page_url, _num_post)
        with open(page_html, 'w', encoding='UTF-8') as fw:
            fw.write(r)


def main():
    list_th = []
    for i in range(5):
        p1 = Thread(target=process, args=['Thead{}'.format(i)])
        list_th.append(p1)

    for th in list_th:
        th.start()

    for th in list_th:
        th.join()


if __name__ == "__main__":
    _start_folder = r'd:\\_roru\\'[:-1]
    _post_folder = '{}{}'.format(_start_folder, r'02_post\\'[:-1])  # r'd:\_roru\post\\'[:-1]
    _list_folder = '{}{}'.format(_start_folder, r'01_list\\'[:-1])  # r'd:\_roru\list\\'[:-1]
    _list_files = os.listdir(_list_folder)

    # -----------------------------------------------------------------------------------
    #  СОБИРАЕМ УЖЕ ЗАГРУЖЕННЫЕ НОМЕРА ПОСТОВ
    _download_file_post = os.listdir(_post_folder)  # листинг файлов постов
    _list_num_dowload_post = []
    _list_num_dowload_post.clear()

    for _download_file in _download_file_post:
        _list_num_dowload_post.append(_download_file.split('.')[0])
    # -----------------------------------------------------------------------------------

    _list_num_post = []  # набор уникальных ссылок
    _list_num_post.clear()

    for _list_file in _list_files:
        if _list_file != '':
            _file_name = '{}{}'.format(_list_folder, _list_file)
            with open(_file_name, 'r', encoding='UTF-8') as fileR:
                FileDataStr = fileR.read()

                tree = html.fromstring(FileDataStr)  # загружаем в строку
                links = tree.xpath('.//a[@class = "topictitle"]/@href')  # выбираем ссылки
                for link in links:
                    _num_post: str = str.replace(link, './viewtopic.php?f=3&t=', '').split('&')[0]
                    if not _num_post in _list_num_post:  # собираем номера постов
                        if not _num_post in _list_num_dowload_post:  # НЕ ВКЛЮЧАЕМ УЖЕ СКАЧАНЫЕ
                            _list_num_post.append(_num_post)  # ДОКАЧИВАЕМ НЕДОСТАЮЩИЕ

    work_queue = Queue()
    for _num_post in _list_num_post:
        work_queue.put(_num_post)
    main()
