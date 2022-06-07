import subprocess
import threading
import time
import sys
#import openpyxl
import re


def getping(host, result, i):
    """
    Получает 1 хост, пингует с помощью смд 2 пакетами, возвращает значение в список результатов
    Возврат сделан не через return, ведь потоки не умеют его получать
    """
    completed_ping = subprocess.run(['ping', '-n', '2', host[i]], stdout=subprocess.PIPE)
    tosplit = completed_ping.stdout.decode('cp866')
    result[i] = tosplit.split('\r\n')[1] + '\t' + tosplit.split('\r\n')[2]


def openthread():
    """
    создаются потоки, передаются в функцию пинга хост, результат и порядковый номер
    """
    threads = []
    for i in range(len(host)):
        tread = threading.Thread(target=getping, args=(host, result, i), daemon=True)
        threads.append(tread)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()  # Ждем завершения всех потоков


def printto(flag, timenow):
    """
    Записывает результаты в файл,стандартный вывод, в эксель
    """
    if flag == 0:
        print(timenow[-1])
        for i in range(len(host)):
            print(str(host[i]) + '\t' + str(result[i]) + 'мс')

    if flag == 1:
        f = open('1.txt', 'w')
        f.writelines(timenow[-1] + '\n')
        for i in range(len(host)):
            f.writelines(host[i] + '\t   Ответ - \t' + str(result[i]) + ' мс \n')
            f.flush()
        f.close()

    if flag == 2:
        wb = openpyxl.Workbook()
        for sheetdelete in wb.sheetnames:
            wb.remove(wb[sheetdelete])
        wb.create_sheet('Ping')
        sheet = wb['Ping']

        colnum = 2
        sheet['A1'] = 'Time'
        sheet.column_dimensions['A'].width = 18
        for reccol in listOfResult:
            rawnum = 1
            for recrow in reccol:
                sheet.cell(row=rawnum, column=colnum).value = recrow
                rawnum += 1
            colnum += 1


        for eltime in timenow:
            sheet.cell(row=timenow.index(eltime) + 2, column=1).value = eltime

        for row in sheet.iter_rows():
            for cell in row:
                if cell.column_letter != "A":
                    sheet.column_dimensions[cell.column_letter].width = 12

        wb.save('1.xlsx')


def regresult(datatoreg):

            x = re.search('время\S*', datatoreg)
            if x:
                return str(x.group()[6:-2])
            else:
                return str(-1)

def operationfiles():

    host = []
    while True:
        x = input("Введите название файла со списком хостов \n")
        try:
            with open(x, "r") as reader:
                for line in reader.readlines():
                    x = re.search("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line)
                    if x:
                        host.append(x.group())  # Заполняем список хостов из файла экспорт
            if host:
                host.sort()
                break
            else:
                print("В файле не найдены IP, повторите \n")
        except FileNotFoundError:
            print("Попробуйте еще раз")

    return host


def wheretowrite():
    while True:
        x = input("Куда будем писать? \n 0. - В консоль \t 1. - В текстовик \t 2. - В exel\n")
        if x.isdigit():
            if int(x) == 0 or int(x) == 1 or int(x) == 2:
                break
    return int(x)


if __name__ == '__main__':

    listtime = []
    host = operationfiles()
    pishem = wheretowrite()

    listOfResult = [[] for i in range(len(host))]  # Создаем пустой список списков результатов
    result = [None] * len(host)  # Создаем список результатов, который обновляется при каждом тике while
    for i in range(len(host)):
        listOfResult[i].append(host[i])  # Добавляем хосты в начало списка
    try:
        while True:

            time.sleep(1)
            openthread()
            listtime.append(time.strftime("%Y-%m-%d %H:%M:%S"))
            for i in range(len(host)):
                result[i] = regresult(result[i])
                listOfResult[i].append(result[i])  # Добавляем результаты в конец
            printto(pishem, listtime)
    except KeyboardInterrupt:
        print("Операция отменена пользователем")

        sys.exit(1)
