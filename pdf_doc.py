#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pip3 install pdfminer.six chardet

import os
import pickle
from multiprocessing import Pool

import sys
import argparse

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO


def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                  check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text


def find_file(suf, fdir):
    filelist = []
    names = os.listdir(fdir)
    for name in names:
        fullname = os.path.join(fdir, name)  # получаем полное имя
        # (os.path.basename(fullname).split('.')[1]) == suf: #привести сравниваемое к нижнему регистру,
        if os.path.isfile(fullname) and name[-3:] == suf:
            filelist.append(fullname)
        elif os.path.isdir(fullname):
            z = (os.path.abspath(fullname))
            find_file(suf, z)
    return filelist


def pars_text(data):
    # надо проверять карточка это или нет!!
    docIndex = []  # тут сложим индексы  нужных мест документа в кучку
    docInfo = []  # тут сложим полезные данные из файла и возвратим список по окончании
    docIndex.append(len(data))
    # проверяем карточка или нет.
    if (data.find("КОНТРОЛЬНО-КАССОВОЙ ТЕХНИКИ")) == 0:
        # print(x.find("КОНТРОЛЬНО-КАССОВОЙ ТЕХНИКИ"))
        # 1
        docIndex.append(data.find("Контрольно-кассовая техника"))
        # print(x.find("Контрольно-кассовая техника"))
        # 2
        docIndex.append(data.find("Заводской номер экземпляра модели контрольно-кассовой техники:"))
        # print(x.find("Заводской номер экземпляра модели контрольно-кассовой техники:"))
        # 3
        docIndex.append(data.find("регистрационный номер контрольно-кассовой техники:"))
        # print(x.find("регистрационный номер контрольно-кассовой техники:"))
        # 4
        docIndex.append(data.find("Модель фискального накопителя:"))
        # print(x.find("Модель фискального накопителя:"))
        # 5
        docIndex.append(data.find("Заводской номер экземпляра модели фискального накопителя:"))
        # print(x.find("Заводской номер экземпляра модели фискального накопителя:"))
        # 6
        # надо преверять на кого ркгистрация (проверять по огрнип + инн для ип и огрн + инн\кпп для всех остальных
        docIndex.append(data.find("Принадлежит:"))
        # print(x.find("Принадлежит:"))
        # 7
        docIndex.append(data.find("Адрес установки (применения) контрольно-кассовой техники:"))
        # print(x.find("Адрес установки (применения) контрольно-кассовой техники:"))
        # 8
        docIndex.append(data.find("Место установки (применения) контрольно-кассовой техники:"))
        # print(x.find("Место установки (применения) контрольно-кассовой техники:"))
        # 9
        docIndex.append(data.find("Входит в состав автоматического устройства для расчетов (да/нет)"))
        # print(x.find("Входит в состав автоматического устройства для расчетов (да/нет)"))
        # 10
        docIndex.append(data.find("Обработку  фискальных  данных  осуществляет"))
        # print(x.find("Обработку  фискальных  данных  осуществляет"))
        # 11
        docIndex.append(data.find("Количество перерегистраций контрольно-кассовой техники"))
        # print(x.find("Количество перерегистраций контрольно-кассовой техники"))
        # 12
        docIndex.append(data.find("Зарегистрирована в налоговом органе с"))
        # print(x.find("Зарегистрирована в налоговом органе с"))

        ######################
        # пока принтами вывод отладки, надо складывать в список, а список в еше один список.
        # print(docIndex)

        # что-то с индексами, надо писать сразу что и откуда берётся.

        # модель ккт
        # print(data[docIndex[1]+28:docIndex[2]-1]) #добавить проверку на спецсимволы типа \n и чистить от них
        docInfo.append(data[docIndex[1] + 28:docIndex[2] - 1])
        # серийный номер ккт
        # print(data[docIndex[2]+63:docIndex[3]-1]) #убрать -1 от индека.
        docInfo.append(data[docIndex[2] + 63:docIndex[3] - 1])
        # рег номер ккт
        # print(data[docIndex[3]+51:docIndex[4]-1]) #наверное надо убрать пробелы
        docInfo.append(data[docIndex[3] + 51:docIndex[4] - 1])
        # модель ФН, думаю не шибко нужно
        # ЗН ФН
        # print(data[docIndex[5]+58:docIndex[6]-1])
        docInfo.append(data[docIndex[5] + 58:docIndex[6] - 1])
        # На кого зареган
        # print(data[docIndex[6]+13:docIndex[7]-1])
        docInfo.append(data[docIndex[6] + 13:docIndex[7] - 1])
        # тут видимо надо будет вкорячить еще и инн кпп огрн и прочее
        # адрес установки ккт
        # print(data[docIndex[7]+58:docIndex[8]-1]) #убрать \n
        docInfo.append(data[docIndex[7] + 58:docIndex[8] - 1])
        # место установки
        # print(data[docIndex[8]+58:docIndex[9]-1])
        docInfo.append(data[docIndex[8] + 58:docIndex[9] - 1])
        # ОФД
        # print(data[docIndex[10]+45:docIndex[11]-1])
        docInfo.append(data[docIndex[10] + 45:docIndex[11] - 1])
        # дата регистрации в налоговом органе
        # print(data[docIndex[12]+40:docIndex[12]+50])
        docInfo.append(data[docIndex[12] + 40:docIndex[12] + 50])
        return docInfo


def pars_filelist(fl):
    data = []
    print(len(fl))
    for x in fl:
        # разбираем страничку и положим результат в список
        text = pars_text(convert_pdf_to_txt(x))
        if type(text) == list:  # проверяем не пустой ли список (сравнение типов)?
            text.append(x)  # в конец списка добавим путь к файлу
            data.append(text)  # положим результат в список
    # aa.append(convert_pdf_to_txt(x))
    return data


def pars_filelist_map(fl):
    data = []
    print(fl)
    # разбираем страничку и положим результат в список
    text = pars_text(convert_pdf_to_txt(fl))
    if type(text) == list:  # проверяем не пустой ли список
        text.append(fl)  # в конец списка добавим путь к файлу
        data.append(text)  # положим результат в список
    # aa.append(convert_pdf_to_txt(x))
    return data

# pickle
def record_data_in_file(data, file):
    with open(file, 'wb') as f:
        pickle.dump(data, f)



def main_wiz(dir: str, mode: int = 1, out: str = 'data.pl'):
    # mode: 1 - 1 thread, 2 - 2 thread, 4 - 4 thread
    # out: output file
    filelist = find_file('pdf', dir)
    if mode > 1:
        pool = Pool(mode)
        pdfdata = pool.map(pars_filelist_map, filelist)
        pool.close()
        pool.join()
        record_data_in_file(pdfdata, out)
    else:
        pdfdata = pars_filelist(filelist)
        record_data_in_file(pdfdata, out)

def arg_parse():
    #разбираем параметры запуска файла
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', type=str, default='.')
    parser.add_argument('-m', '--mode', type=int, default=1)
    parser.add_argument('-o', '--out', type=str, default='data.pl')
    return parser


def main():
    parser = arg_parse()
    namespace = parser.parse_args(sys.argv[1:])
    main_wiz(namespace.dir, namespace.mode, namespace.out)

if __name__ == '__main__':
    main()