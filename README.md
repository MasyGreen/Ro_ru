# Назначение
Выкачиваем форум сайта www.roller.ru для последующего статистического анализа
(разрешение администрации получено)
[https://www.roller.ru/forum/viewtopic.php?f=2&t=56763]
(Тема на сайте www.roller.ru)

# Файлы

* 01_download_list.py - скачать страницы форума (01_Pages)
* 02_parse_list.py - скачать первые листы постов с стараниц форума (02_Post)
* 03_parse_post.py - разобрать первые листы постов на содержимое: покатушка\ведущий\участники (03_PostProcess\full_data.xml)
* 04_download_prev2013.py - выкачать все листы постов из постов до 2013 года, там нет статистики по посещениям (04_Post_2013)
* 05_parse_post2013.py - разобрать посты (до 2013) на содержимое (03_PostProcess\full_data_2013.xml)
* 06_export.py - сформировать файлы с исходными данными (03_PostProcess\full_data_exp.xml)
* 07_achive.py - сформировать файлы достижений ()

# Установка
git clone https://github.com/MasyGreen/Ro_ru.git

config.py - создать папки и заполнить локальные пути