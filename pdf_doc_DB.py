#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pip3 install pdfminer.six chardet sqlalchemy

import os
import re
import csv
import sys
import argparse
import hashlib

from sqlalchemy import create_engine

from multiprocessing import Pool

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO


def convert_pdf_to_txt(path):
    print(path)
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 1
    caching = True
    pagenos = set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages,
                                 password=password, caching=caching,
                                 check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text


def find_file(suf, fdir, filelist=None):
    if filelist is None:
        filelist = []
    names = os.listdir(fdir)
    for name in names:
        fullname = os.path.join(fdir, name)  # получаем полное имя
        if os.path.isfile(fullname) and name[-3:].lower() == suf:
            filelist.append(fullname)
        elif os.path.isdir(fullname):
            z = (os.path.abspath(fullname))
            find_file(suf, z, filelist)
    return filelist


def pars_text(data):
    # надо проверять карточка это или нет!!
    docIndex = []  # тут сложим индексы  нужных мест документа в кучку
    docInfo = []  # тут сложим полезные данные из файла и возвратим список по окончании
    docIndex.append(len(data))
    # проверяем карточка или нет.
    if (data.find("КОНТРОЛЬНО-КАССОВОЙ ТЕХНИКИ")) == 0:
        # 1
        docIndex.append(data.find("Контрольно-кассовая техника"))
        # 2
        docIndex.append(
            data.find("Заводской номер экземпляра модели контрольно-кассовой техники:"))
        # 3
        docIndex.append(
            data.find("регистрационный номер контрольно-кассовой техники:"))
        # 4
        docIndex.append(data.find("Модель фискального накопителя:"))
        # 5
        docIndex.append(
            data.find("Заводской номер экземпляра модели фискального накопителя:"))
        # 6
        # надо преверять на кого ркгистрация (проверять по огрнип + инн для ип и огрн + инн\кпп для всех остальных
        docIndex.append(data.find("Принадлежит:"))
        # 7
        docIndex.append(
            data.find("Адрес установки (применения) контрольно-кассовой техники:"))
        # 8
        docIndex.append(
            data.find("Место установки (применения) контрольно-кассовой техники:"))
        # 9
        docIndex.append(
            data.find("Входит в состав автоматического устройства для расчетов (да/нет)"))
        # 10
        docIndex.append(
            data.find("Обработку  фискальных  данных  осуществляет"))
        # 11
        docIndex.append(
            data.find("Количество перерегистраций контрольно-кассовой техники"))
        # 12
        docIndex.append(data.find("Зарегистрирована в налоговом органе с"))

        # циферки длина строки поиска + 1
        # модель ккт
        docInfo.append(data[docIndex[1] + 28:docIndex[2] - 1])
        # серийный номер ккт
        docInfo.append(data[docIndex[2] + 63:docIndex[3] - 1])
        # рег номер ккт      #наверное надо убрать пробелы
        docInfo.append(data[docIndex[3] + 51:docIndex[4] - 1])
        # модель ФН
        docInfo.append(data[docIndex[4] + 31:docIndex[5] - 1])
        # ЗН ФН
        docInfo.append(data[docIndex[5] + 58:docIndex[6] - 1])
        # На кого зареган
        docInfo.append(data[docIndex[6] + 13:docIndex[7] - 1])
        # тут видимо надо будет вкорячить еще и инн кпп огрн и прочее
        # адрес установки ккт
        docInfo.append(data[docIndex[7] + 58:docIndex[8] - 1])
        # место установки
        docInfo.append(data[docIndex[8] + 58:docIndex[9] - 1])
        # ОФД
        docInfo.append(data[docIndex[10] + 45:docIndex[11] - 1])
        # дата регистрации в налоговом органе
        docInfo.append(data[docIndex[12] + 40:docIndex[12] + 50])
        # возможно есть способ быстрее
        for x in range(len(docInfo)):
            docInfo[x] = re.sub("^\s+|\n|\r|\s+$", '', docInfo[x])
        return docInfo


def pars_filelist_map(fl):
    data = []
    # разбираем страничку и положим результат в список
    text = pars_text(convert_pdf_to_txt(fl[0]))
    if type(text) == list:  # проверяем не пустой ли список
        text.append(fl[0])
        text.append(fl[1])  # в конец списка добавим путь к файлу и хеш
        data.append(text)  # положим результат в список
    return data


def get_data_from_db():
    query = """select * from file_id"""
    result = engine.execute(query)
    return result.fetchall()


def record_data_in_file(data, file):
    with open(file, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=';',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['порядковый номер', 'расположение файла', 'hash', 'модель ккт',
                             'серийный номер ккт', 'рег номер ккт', 'модель ФН', 'ЗН ФН',
                             'На кого зареган', 'адрес установки ккт', 'место установки',
                             'ОФД', 'дата регистрации в налоговом органе'])
        for x in data:
            if len(x) != 0:
                spamwriter.writerow(x)


def main_wiz(dir: str, mode: int = 1, out: str = None):
    firs_connect_db()
    print('!scan folder!')
    filelist = find_file('pdf', dir)
    print('get_hash!')
    filelist = get_hash_from_file_list(filelist)
    filelist = check_hash_in_db(filelist)
    pool = Pool(mode)
    print('**pars file**')
    pdfdata = pool.map(pars_filelist_map, filelist)
    pool.close()
    pool.join()
    # через pool.map возвращается список в списке в списке, убираем лишнее
    for x in range(len(pdfdata)):
        if len(pdfdata[x]) != 0:
            pdfdata[x] = pdfdata[x][0]
    post_data_to_db(pdfdata)

    if out:
        record_data_in_file(get_data_from_db(), out)


def firs_connect_db():
    """create table on db"""
    query = """
    CREATE TABLE if not exists `file_id` (
        `id`    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        `filepath`  TEXT,
        `hash`  TEXT NOT NULL UNIQUE,
        `model_kkt` TEXT,
        `sn_kkt`    TEXT,
        `reg_num_kkt`   TEXT,
        `model_fn`  TEXT,
        `zn_fn` TEXT,
        `organization`  TEXT,
        `address`   TEXT,
        `place` TEXT,
        `ofd`   TEXT,
        `reg_date`  TEXT
        );
    """
    engine.execute(query)


def check_hash_in_db(checking_list):
    list_ = list(checking_list)
    element_to_del = []
    for file in range(len(list_)):
        query = """ select hash from file_id where 
                hash = '{0}' """.format(list_[file][1])
        result = engine.execute(query)
        if result.fetchone():
            element_to_del.append(file)
    for x in reversed(element_to_del):
        list_.pop(x)
    return(list_)


def get_hash(filename):
    with open(filename, 'rb') as f:
        m = hashlib.sha256()
        while True:
            data = f.read()
            if not data:
                break
            m.update(data)
        return m.hexdigest()


def get_hash_from_file_list(filelist):
    for file_index in range(len(filelist)):
        filelist[file_index] = [filelist[file_index],
                                get_hash(filelist[file_index])]
    return filelist


def post_data_to_db(data):
    for x in data:
        if len(x) != 0:
            query = """ select hash from file_id where hash = '{0}' """.format(
                x[-1])
            result = engine.execute(query)
            if not result.fetchone():
                query = """INSERT INTO file_id (`filepath`, `hash`, `model_kkt`, `sn_kkt`, `reg_num_kkt`, `model_fn`, `zn_fn`,
                `organization`, `address`, `place`, `ofd`, `reg_date`  ) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', 
                '{7}', '{8}', '{9}', '{10}', '{11}') 
                """.format(x[-2], x[-1], x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8], x[9])
                engine.execute(query)


def arg_parse():
    # разбираем параметры запуска файла
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', type=str, default='.')
    parser.add_argument('-m', '--mode', type=int, default=1)
    parser.add_argument('-o', '--out', type=str, default=None)
    return parser


def main():
    parser = arg_parse()
    namespace = parser.parse_args(sys.argv[1:])
    main_wiz(namespace.dir, namespace.mode, namespace.out)


if __name__ == '__main__':
    engine = create_engine('sqlite:///rck.sqlite', echo=False)
    main()
