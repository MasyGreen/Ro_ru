import time
from lxml import html
from threading import Thread
from multiprocessing import Queue
import requests
import config

# ШАГ 4
# ПРОХОДИМ ПО ВСЕМ ПОСТАМ В ..\03_post_prs\full_data.xml './/reference[@reference_name="post"]/item'
# ОТБИРАЕМ ПОСТЫ ДО 2013 ГОДА post_date<=2013
# ДЛЯ КАЖДОГО ПОСТА СЧИТАЕМ КОЛИЧЕСТВО УЧАСТНИКОВ './/reference[@reference_name="post_user"]/item'
# ЕСЛИ КОЛИЧЕСТВО УЧАСТНИКОВ = 1 ТО СКАЧИВАЕМ ЦЕЛИКОМ ПОСТ СО ВСЕМИ ЕГО СТАНИЦАМИ В КАТАЛОГ 04_post_2013

def parse_file(dw_text):
    _main_tree = html.fromstring(dw_text)  # загружаем в строку
    _tree_body = _main_tree.xpath('./body')  # выбираем блоки
    _tree_tablebg = _tree_body[0].xpath('.//table[@class="tablebg"]')  # получаем сообщения на странице
    _out_text = ''
    for _msg in _tree_tablebg:  # цикл по сообщениям
        _text = html.tostring(_msg, encoding='unicode')
        if _text.find("memberlist.php?mode=viewprofile") != -1:  # отсекаем голосовалку
            _out_text = _out_text + html.tostring(_msg, encoding='unicode')
    return _out_text


def get_html(dw_url):
    _headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
    }
    _response = requests.get(dw_url, headers=_headers, timeout=(160000, 300000))
    return _response.text


def parse_post(dw_code_post, dw_code_user):
    # Получаем первый файл поста
    page_url = f'https://www.roller.ru/forum/viewtopic.php?f=3&t={dw_code_post}'  # ссылка для скачивания
    _txt_first_page = get_html(page_url)
    _path_file = f'{_file_post_parse2013}{dw_code_post}_{dw_code_user}_0.html'# путь для сохранения
    _value_file = parse_file(_txt_first_page)
    print(_path_file)
    with open(_path_file, 'w', encoding='UTF-8') as fw:
        fw.write(_value_file)

    # количество страниц
    _tree_first_page = html.fromstring(_txt_first_page)  # загружаем в строку
    _max_pages = _tree_first_page.xpath('.//td[@class="nav"]/strong')[1]
    _max_page = int(_max_pages.text)
    _post_count = 15 * _max_page
    for _i in range(15, _post_count, 15):
        page_url = f'https://www.roller.ru/forum/viewtopic.php?f=3&t={dw_code_post}&start={str(_i)}'
        print(page_url)
        _txt_page = get_html(page_url)
        _path_file = f'{_file_post_parse2013}{dw_code_post}_{dw_code_user}_{str(_i)}.html' # путь для сохранения
        _value_file = parse_file(_txt_page)
        with open(_path_file, 'w', encoding='UTF-8') as fw:
            fw.write(_value_file)


def process(dw_TheadName):
    while not work_queue.empty():
        _post_uq = work_queue.get()
        _code_post = _post_uq.split('_')[0]
        _code_user = _post_uq.split('_')[1]
        time.sleep(.1)
        print(f'THEAD {_code_post} {_code_user} - {dw_TheadName}')
        parse_post(_code_post, _code_user)


def main():
    # формируем список постов до 2013 года в list _list_post_prev2013
    _list_post_prev2013 = []
    _list_post_prev2013.clear()

    print('------------ПОЛУЧАЕМ СПИСОК ПОКАТУШЕК--------------')
    with open(_file_post_prs, 'r', encoding='UTF-8') as fileR:
        file_data_str = fileR.read()
        _postXML = html.fromstring(file_data_str)  # загружаем в строку
        _posts = _postXML.xpath('.//reference[@reference_name="post"]/item')
        for _post in _posts:
            # print(html.tostring(post[0], encoding='unicode'))
            _post_date = _post.get('post_date')
            if len(_post_date.split('.')) == 3:
                _year = int(_post_date.split('.')[2])
                if _year <= 2013:
                    _list_post_prev2013.append(f"{_post.get('post_code')}_{_post.get('user_code')}")
                    print(f"{_post.get('post_code')}_{_post.get('user_code')}")

    # -------------------------------------------------------------------------------------------------
    print('------------СЧИТАЕМ УЧАСТНИКОВ ПОКАТУШЕК--------------')
    _list_post_nouser = []
    _list_post_nouser.clear()
    # проходим по списку постов и считаем кол-во участинков
    with open(_file_post_user, 'r', encoding='UTF-8') as fileR:
        file_data_str = fileR.read()
        _posts_userXML = html.fromstring(file_data_str)  # загружаем в строку
        # _posts_users = _postXML.xpath('.//reference[@reference_name="post_user"]/item')
        #  print(html.tostring(_posts_users[0], encoding='unicode'))

        for _post in _list_post_prev2013:  # для каждого поста проверяем участников
            _post_num = _post.split('_')[0]
            _posts_users = _postXML.xpath('.//reference[@reference_name="post_user"]/item[@post_code='+_post_num+']')
            # print(html.tostring(_posts_users[0], encoding='unicode'))
            # print('{} - {}'.format(_post_num, len(_posts_users)))
            _count_user = int(len(_posts_users))
            if _count_user == 1:
                _list_post_nouser.append(_post)
                #  print('{} - {}'.format(_post, _count_user))

    # -------------------------------------------------------------------------------------------------
    # _list_post_nouser.append('15700_3952')
    for _post in _list_post_nouser:
        work_queue.put(_post)
    list_th = []
    for i in range(20):
        p1 = Thread(target=process, args=[f'Thead{i}'])
        list_th.append(p1)

    for th in list_th:
        th.start()

    for th in list_th:
        th.join()


if __name__ == "__main__":
    _file_post_parse2013 = config._POST2013  # папка с постами
    _file_post_prs = f'{config._POSTPROCESS}full_data.xml'  # файл с постами
    _file_post_user = _file_post_prs  # файл с участниками
    # -------------------------------------------------------------------------------------------------
    work_queue = Queue()

    main()
