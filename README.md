# Назначение
Выкачиваем форум сайта www.roller.ru для последующего статистического анализа
(разрешение администрации получено)
[https://www.roller.ru/forum/viewtopic.php?f=2&t=56763]
(Тема на сайте www.roller.ru)

# Файлы

* 01_download_list.py - сформировать листинг форума (01_Pages)
* 02_parse_list.py - переработать листин в посты
* 03_parse_post.py - разобрать посты на содержимое
* 04_download_prev2013.py - выкачать сообщения из постов до 2013 года (там нет статистики по посещениям)
* 05_parse_post2013.py - разобрать посты (до 2013) на содержимое
* 06_export.py - сформировать файлы с исходными данными
* 07_achive.py - сформировать файлы достижений

# Установка
git clone https://github.com/MasyGreen/Ro_ru.git