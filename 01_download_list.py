import threading
import time
import requests
from lxml import html

# ШАГ 1
# ПЕРЕХОДИМ НА ПЕРВУЮ СТРАНИЦУ ОГЛАВЛЕНИЯ ФОРУМА https://www.roller.ru/forum/viewforum.php?f=3
# ВСЕ СЛЕДУЮЩИЕ СЧЕТЧИКОМ К СТРОКЕ https://www.roller.ru/forum/viewforum.php?f=3&start=
# НАПРИМЕР https://www.roller.ru/forum/viewforum.php?f=3&start=50, https://www.roller.ru/forum/viewforum.php?f=3&start=8000
# СОХРАНЯЕМ ВСЕ СТРАНИЦЫ ОГЛАВЛЕНИЯ _folder_list = r..\01_list\\'

def get_html(dw_url, dw_file):
    _headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0',
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain"
    }
    _response = requests.get(dw_url, headers=_headers, timeout=(160000, 200000))

    with open(dw_file, 'w', encoding='UTF-8') as fw:
        fw.write(_response.text)


class ThreadUrl(threading.Thread):
    """Threaded Url Grab"""

    def __init__(self, host):
        threading.Thread.__init__(self)
        self.host = host

    def run(self):
        _path_url = _url + self.host  # ссылка для скачивания
        _path_file = '{}{}{}{}'.format(_export_folder, 'list', self.host, '.html')  # путь для сохранения
        print('Post page. URL: {} -> file: {}'.format(_path_url, _path_file))
        get_html(_path_url, _path_file)


#  ------------------------------------------------------------------------
def main():
    _page_count = 0
    _post_count = 50 * _max_page
    print('Count post (plan) = {}'.format( _post_count))  # ГЕНЕРИРУЕМ ЦИКЛОМ СТАНИЦЫ ДЛЯ СКАЧКИ (НА КАЖДОЙ СТАНИЦЕ 50 ПОСТОВ)
    for _i in range(50, _post_count, 50):
        _page_count = _page_count + 1
        if _page_count == 20:  # пауза в полсекунды каждые 20 потоков
            _page_count = 0
            time.sleep(.5)

        t = ThreadUrl(str(_i))
        t.start()


if __name__ == "__main__":
    _start_folder = r'd:\_roru\\'[:-1]
    _export_folder = '{}{}'.format(_start_folder, r'01_list\\'[:-1])  # куда качать
    _url = 'https://www.roller.ru/forum/viewforum.php?f=3&start='  # цикл по станицам скачки

    # ПАРСИМ ПЕРВУЮ СТРАНИЦУ НА МАКСИМАЛЬНОЕ КОЛИЧЕСТВО СТРАНИЦ С ПОСТАМИ
    _path_file = '{}{}{}{}'.format(_export_folder, 'list', '0', '.html')  # путь для сохранения
    _path_url = 'https://www.roller.ru/forum/viewforum.php?f=3'
    print('First page. URL: {} -> file: {}'.format(_path_url, _path_file))
    get_html(_path_url, _path_file)
    with open(_path_file, 'r', encoding='UTF-8') as fileR:
        file_data_str = fileR.read()
        tree = html.fromstring(file_data_str)  # загружаем в строку
        _max_pages = tree.xpath('.//td[@class="nav"]/strong')[1]
        _max_page = int(_max_pages.text)
        print('Max page = {}'.format( _max_page))  # МАКСИМАЛЬНОЕ КОЛИЧЕСТВО СТРАНИЦ С ПОСТАМИ

    main()
#  ------------------------------------------------------------------------
