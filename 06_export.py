from datetime import datetime
from xml.etree import ElementTree as ET

from lxml import html


def add_el_user(user_code, user_name):  # пользователи
    if user_code != "" and user_name != "":
        if not user_code in _user_u:  # только уникальные пользователи
            _user_u.append(user_code)
            _row = {"user_code": user_code,
                    "user_name": user_name}
            _user_array.append(_row)


def add_el_post(post_code, post_name, post_date, user_code,
                user_name):  # пишем уникальных пльзователй в xml
    if post_code != "" and user_code != "":
        if not post_code in _post_u:
            _add_row = True

            try:
                datetime_object = datetime.strptime(post_date, '%d.%m.%Y')
            except ValueError as ve:
                _add_row = False
                print('Error strptime: {}, {} '.format(post_code,post_date))

            if _add_row:
                _post_u.append(post_code)
                _row = {"post_code": post_code,
                        "post_name": post_name,
                        "post_date": post_date,
                        "user_code": user_code,
                        "user_name": user_name}
                _post_array.append(_row)


def add_el_post_user(user_code, user_name,
                     post_code, post_date, master_code, master_name):  # посты
    _find_str = '{}{}'.format(user_code, post_code)
    if not _find_str in _post_user_u:  # только уникальные пользователи
        if post_code in _post_u:  # только для добавленных покатушек
            _post_user_u.append(_find_str)
            _row = {"user_code": user_code,
                    "user_name": user_name,
                    "post_code": post_code,
                    "post_date": post_date,
                    "master_code": master_code,
                    "master_name": master_name}
            _post_user_array.append(_row)


def main():
    _file_name = r'{}\{}'.format(_export_folder, 'full_data.xml')  # XML
    _file_name_2013 = r'{}\{}'.format(_export_folder, 'full_data_2013.xml')  # XML 2013

    # -----------------------------2013>--------------------------------------
    with open(_file_name, 'r', encoding='UTF-8') as fileR:  # user общие
        file_data_str = fileR.read()
        _XML = html.fromstring(file_data_str)  # загружаем в строку

        # ----------------------------------------------------------------------------------
        _users = _XML.xpath('.//reference[@reference_name="user"]/item')
        for _user in _users:
            add_el_user(_user.get('user_code'), _user.get('user_name'))
            # print('user_code {}'.format(_user.get('user_code')))

        # ----------------------------------------------------------------------------------
        _posts = _XML.xpath('.//reference[@reference_name="post"]/item')
        for _post in _posts:
            add_el_post(_post.get('post_code'), _post.get('post_name'), _post.get('post_date'),
                        _post.get('user_code'), _post.get('user_name'))
            # print('post_code {}'.format(_post.get('post_code')))

        # ----------------------------------------------------------------------------------
        _post_users = _XML.xpath('.//reference[@reference_name="post_user"]/item')
        for _post_user in _post_users:
            d_post_date = ''
            d_master_code = ''
            d_master_name = ''
            # print('post_user {}-{}'.format(_post_user.get('user_code'), _post_user.get('post_code')))

            a = [d for d in _post_array if d['post_code'] == _post_user.get('post_code')]
            if len(a) > 0:
                d_post_date = a[0].get('post_date')
                d_master_code = a[0].get('user_code')
                d_master_name = a[0].get('user_name')

            add_el_post_user(_post_user.get('user_code'), _post_user.get('user_name'),
                             _post_user.get('post_code'), d_post_date, d_master_code, d_master_name)

    # -----------------------------<=2013--------------------------------------
    with open(_file_name_2013, 'r', encoding='UTF-8') as fileR:  # user 2013
        file_data = fileR.read()
        _XML = html.fromstring(file_data)  # загружаем в строку

        # ----------------------------------------------------------------------------------
        _users = _XML.xpath('.//reference[@reference_name="user"]/item')
        for _user in _users:
            add_el_user(_user.get('user_code'), _user.get('user_name'))
            # print('user_code 2013 {}'.format(_user.get('user_code')))

        # ----------------------------------------------------------------------------------
        _posts = _XML.xpath('.//reference[@reference_name="post"]/item')
        for _post in _posts:
            add_el_post(_post.get('post_code'), _post.get('post_name'), _post.get('post_date'),
                        _post.get('user_code'), _post.get('user_name'))
            # print('post_code 2013 {}'.format(_post.get('post_code')))

        # ----------------------------------------------------------------------------------
        _post_users = _XML.xpath('.//reference[@reference_name="post_user"]/item')
        for _post_user in _post_users:
            d_post_date = ''
            d_master_code = ''
            d_master_name = ''
            a = [d for d in _post_array if d['post_code'] == _post_user.get('post_code')]
            if len(a) > 0:
                d_post_date = a[0].get('post_date')
                d_master_code = a[0].get('user_code')
                d_master_name = a[0].get('user_name')

            add_el_post_user(_post_user.get('user_code'), _post_user.get('user_name'),
                             _post_user.get('post_code'), d_post_date, d_master_code, d_master_name)
            # print('post_user 2013 {}-{}'.format(_post_user.get('user_code'), _post_user.get('post_code')))

    print('Print to Export File')
    # ----------------------------file exchange----------------------------------------
    _export_xml_file = '{}{}'.format(_export_folder, 'full_data_exp.xml')  # имя файла
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
    _start_folder = r'd:\_roru\\'[:-1]
    _export_folder = '{}{}'.format(_start_folder, r'03_post_prs\\'[:-1])  # каталог для записи

    _user_array = []
    _post_user_array = []
    _post_array = []

    _user_u = []
    _user_u.clear()

    _post_u = []
    _post_u.clear()

    _post_user_u = []
    _post_user_u.clear()

    main()
