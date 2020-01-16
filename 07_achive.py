from datetime import datetime
import pandas as pd
from lxml import html
import xlsxwriter


def print_excel():
    workbook = xlsxwriter.Workbook('{}/ExportBook.xlsx'.format(_export_folder))
    worksheet = workbook.add_worksheet()
    cell_format = workbook.add_format({'bold': True, 'italic': True, 'align': 'center'})

    worksheet.write(0, 0, 'post_code', cell_format)
    worksheet.set_column(0, 0, 12)
    worksheet.write(0, 1, 'user_code', cell_format)
    worksheet.set_column(1, 1, 12)
    worksheet.write(0, 2, 'user_name', cell_format)
    worksheet.set_column(2, 2, 12)
    worksheet.write(0, 3, 'post_date', cell_format)
    worksheet.set_column(3, 3, 12)
    worksheet.write(0, 4, 'post_year', cell_format)
    worksheet.set_column(4, 4, 12)
    worksheet.write(0, 5, 'master_code', cell_format)
    worksheet.set_column(5, 5, 12)
    worksheet.write(0, 6, 'master_name', cell_format)
    worksheet.set_column(6, 6, 12)

    df_post_user = pd.DataFrame(pd_PostUsers["PostUser"])
    df_post_user.head()
    for _i, row in df_post_user.iterrows():
        worksheet.write(_i + 1, 0, row.get('post_code'))
        worksheet.write(_i + 1, 1, row.get('user_code'))
        worksheet.write(_i + 1, 2, row.get('user_name'))
        worksheet.write(_i + 1, 3, row.get('post_date'))
        worksheet.write(_i + 1, 4, row.get('post_year'))
        worksheet.write(_i + 1, 5, row.get('master_code'))
        worksheet.write(_i + 1, 6, row.get('master_name'))
    workbook.close()


def main():
    with open(_in_file, 'r', encoding='UTF-8') as fileR:  # user общие
        file_data_str = fileR.read()
        _XML = html.fromstring(file_data_str)  # загружаем в строку

        # ---------------------------------------------------------------------
        _users = _XML.xpath('.//reference[@reference_name="user"]/item')
        for _user in _users:
            row = {"user_code": _user.get('user_code'), "user_name": _user.get('user_name')}
            pd_Users["User"].append(row)

        # ---------------------------------------------------------------------
        _posts = _XML.xpath('.//reference[@reference_name="post"]/item')
        for _post in _posts:
            try:
                datetime_object = datetime.strptime(_post.get('post_date'), '%d.%m.%Y')
            except ValueError as ve:
                print('ValueError Raised:', ve, _post.get('post_code'))

            row = {"post_code": _post.get('post_code'), "user_code": _post.get('user_code'),
                   "user_name": _user.get('user_name'),
                   "post_date": datetime_object,
                   "post_year": datetime_object.year}
            pd_Posts["Post"].append(row)

        # ---------------------------------------------------------------------
        _posts_users = _XML.xpath('.//reference[@reference_name="post_user"]/item')
        for _post_user in _posts_users:
            try:
                datetime_object = datetime.strptime(_post_user.get('post_date'), '%d.%m.%Y')
            except ValueError as ve:
                print('ValueError Raised:', ve, _post_user.get('post_code'))

            row = {"post_code": _post_user.get('post_code'),
                   "user_code": _post_user.get('user_code'),
                   "user_name": _post_user.get('user_name'),
                   "post_date": datetime_object,
                   "post_year": datetime_object.year,
                   "master_code": _post_user.get('master_code'),
                   "master_name": _post_user.get('master_name')}
            pd_PostUsers["PostUser"].append(row)

        #print_excel()

        df_users = pd.DataFrame(pd_Users["User"])
        df_posts = pd.DataFrame(pd_Posts["Post"])
        df_post_user = pd.DataFrame(pd_PostUsers["PostUser"])

        # год-ведущий-количество участников
        #dfr01 = df_post_user.groupby(["post_year", "master_code", "master_name"], group_keys=False)["user_code"].count()
        #№print(dfr01.head(1000))

        # год-ведущий-количество покатушек
        dfr02 = df_posts.groupby(["post_year", "user_code", "user_name"], group_keys=False).count()
        print(dfr02.head(1000))

        #dfr.to_excel('{}/output.xlsx'.format(_export_folder))


if __name__ == "__main__":
    _start_folder = r'd:\_roru\\'[:-1]
    _export_folder = '{}{}'.format(_start_folder, r'03_post_prs\\'[:-1])  # каталог для записи
    _in_file = r'{}\\full_data_exp.xml'.format(_export_folder)
    _out_file = r'{}\\achive_exp.xml'.format(_export_folder)
    pd_Users = {"User": []}
    pd_Posts = {"Post": []}
    pd_PostUsers = {"PostUser": []}
    main()
