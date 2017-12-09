#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import pickle
from multiprocessing import Pool

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
 pagenos=set()

 for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
  interpreter.process_page(page)

 text = retstr.getvalue()

 fp.close()
 device.close()
 retstr.close()
 return text



def findFile(suf, fdir):
 names = os.listdir(fdir)
 for name in names:
  fullname = os.path.join(fdir, name) # получаем полное имя
  if os.path.isfile(fullname) and  name[-3:] == suf:  #(os.path.basename(fullname).split('.')[1]) == suf: #привести сравниваемое к нижнему регистру,
   filelist.append(fullname)
  elif os.path.isdir(fullname):
   z = (os.path.abspath(fullname))
   findFile(suf,z)

def parsText(data):
 # надо проверять карточка это или нет!!
 docIndex=[] #тут сложим индексы  нужных мест документа в кучку
 docInfo=[]  #тут сложим полезные данные из файла и возвратим список по окончании
 docIndex.append(len(data))
 #проверяем карточка или нет. 
 if (data.find("КОНТРОЛЬНО-КАССОВОЙ ТЕХНИКИ")) == 0:
  #print(x.find("КОНТРОЛЬНО-КАССОВОЙ ТЕХНИКИ"))
  #1
  docIndex.append(data.find("Контрольно-кассовая техника"))
  #print(x.find("Контрольно-кассовая техника"))
  #2
  docIndex.append(data.find("Заводской номер экземпляра модели контрольно-кассовой техники:"))
  #print(x.find("Заводской номер экземпляра модели контрольно-кассовой техники:"))
  #3
  docIndex.append(data.find("регистрационный номер контрольно-кассовой техники:"))
  #print(x.find("регистрационный номер контрольно-кассовой техники:"))
  #4
  docIndex.append(data.find("Модель фискального накопителя:"))
  #print(x.find("Модель фискального накопителя:"))
  #5
  docIndex.append(data.find("Заводской номер экземпляра модели фискального накопителя:"))
  #print(x.find("Заводской номер экземпляра модели фискального накопителя:"))
  #6
  docIndex.append(data.find("Принадлежит:")) #надо преверять на кого ркгистрация (проверять по огрнип + инн для ип и огрн + инн\кпп для всех остальных
  #print(x.find("Принадлежит:"))
  #7
  docIndex.append(data.find("Адрес установки (применения) контрольно-кассовой техники:"))
  #print(x.find("Адрес установки (применения) контрольно-кассовой техники:"))
  #8
  docIndex.append(data.find("Место установки (применения) контрольно-кассовой техники:"))
  #print(x.find("Место установки (применения) контрольно-кассовой техники:"))
  #9
  docIndex.append(data.find("Входит в состав автоматического устройства для расчетов (да/нет)"))
  #print(x.find("Входит в состав автоматического устройства для расчетов (да/нет)"))
  #10
  docIndex.append(data.find("Обработку  фискальных  данных  осуществляет"))
  #print(x.find("Обработку  фискальных  данных  осуществляет"))
  #11
  docIndex.append(data.find("Количество перерегистраций контрольно-кассовой техники"))
  #print(x.find("Количество перерегистраций контрольно-кассовой техники"))
  #12
  docIndex.append(data.find("Зарегистрирована в налоговом органе с"))
  #print(x.find("Зарегистрирована в налоговом органе с"))
  ######################
  #пока принтами вывод отладки, надо складывать в список, а список в еше один список.
  #print(docIndex)
  
  #модель ккт
  #print(data[docIndex[1]+28:docIndex[2]-1]) #добавить проверку на спецсимволы типа \n и чистить от них
  docInfo.append(data[docIndex[1]+28:docIndex[2]-1])
  #серийный номер ккт
  #print(data[docIndex[2]+63:docIndex[3]-1]) #убрать -1 от индека.
  docInfo.append(data[docIndex[2]+63:docIndex[3]-1])
  #рег номер ккт
  #print(data[docIndex[3]+51:docIndex[4]-1]) #наверное надо убрать пробелы
  docInfo.append(data[docIndex[3]+51:docIndex[4]-1])
  ##модель ФН, думаю не шибко нужно
  ##ЗН ФН
  #print(data[docIndex[5]+58:docIndex[6]-1])
  docInfo.append(data[docIndex[5]+58:docIndex[6]-1])
  ##На кого зареган
  #print(data[docIndex[6]+13:docIndex[7]-1])
  docInfo.append(data[docIndex[6]+13:docIndex[7]-1])
  ##тут видимо надо будет вкорячить еще и инн кпп огрн и прочее
  ##адрес установки ккт
  #print(data[docIndex[7]+58:docIndex[8]-1]) #убрать \n  
  docInfo.append(data[docIndex[7]+58:docIndex[8]-1])
  ##место установки
  #print(data[docIndex[8]+58:docIndex[9]-1])  
  docInfo.append(data[docIndex[8]+58:docIndex[9]-1])
  ##ОФД
  #print(data[docIndex[10]+45:docIndex[11]-1])
  docInfo.append(data[docIndex[10]+45:docIndex[11]-1])
  return docInfo

def parsFilelist(fl):
 #findFile('pdf', dirName)
 data=[]
 print(len(fl))
 for x in fl:
  text = parsText(convert_pdf_to_txt(x)) # разбираем страничку и положим результат в список
  if type(text) == list: #проверяем не пустой ли список
   text.append(x) # в конец списка добавим путь к файлу
   data.append(text) #положим результат в список
  #aa.append(convert_pdf_to_txt(x))
 return data

def parsFilelistMAP(fl):
 #findFile('pdf', dirName)
 data=[]
 print(fl)
 text = parsText(convert_pdf_to_txt(fl)) # разбираем страничку и положим результат в список
 if type(text) == list: #проверяем не пустой ли список
  text.append(fl) # в конец списка добавим путь к файлу
  data.append(text) #положим результат в список
 #aa.append(convert_pdf_to_txt(x))
 return data

def abr(x):
 return x
	

#pickle 
def recordDataInFile(data, file):
 with open(file, 'wb') as f:
  pickle.dump(data, f)


#Обявим всякие переменные тут а еще лучше в начале файла.
filelist = [] # Надо записать в функцию, чтобы функция возвращала список.
#dirName = './folder' # в один поток 700+с / 4 потока с 327.4С
dirName = './test' # в один поток 2.7-3.7с / 4 потока 1.9с


if __name__ == '__main__':
 print(filelist)
 findFile('pdf', dirName) #так делать плохо, надо возвращать что-то а не писать в глобальную переменную
 print(filelist)
 pool = Pool(4) # указать количество потоков 4
 pdfdata = pool.map(parsFilelistMAP, filelist) # несколько потоков
 #print(pool.map(abr, filelist))
 #pdfdata = parsFilelist(filelist) #1 поток
 recordDataInFile(pdfdata, 'data.pl')
 
 pool.close()
 pool.join()