import json
import sys
import requests
import time
import math
from datetime import date, time as dtime, datetime
import xlsxwriter

def count(dict):
    return dict.__len__()

def get_headers():
    headers = {
        "Host": "api-audience.yandex.ru",
        "Authorization": "OAuth " + token_YM,
        "Content-Type": "application/json",
        "Content-Length": "123"
    }
    return headers

token_YM = sys.argv[1]

URL = {
    "get":"https://api-audience.yandex.ru/v1/management/segments",
    "create":'https://api-audience.yandex.ru/v1/management/segments/create_geo_polygon',
    "delete":'https://api-audience.yandex.ru/v1/management/segment/'
}

req:any
json_data:any

req = requests.get(URL["get"], headers=get_headers())
json_data = json.loads(req.text)

print("info gathered")

segment_count = count(json_data["segments"])

operation_list=[]

for data in json_data["segments"]:
    operation_list.append({
        "method":"DELETE",
        "id":data["id"]
    })
    operation_list.append({
        "method":"CREATE",
        "name":data["name"],
        "type":data["geo_segment_type"],
        "polygons":data["polygons"]
    })

index=0
size = count(operation_list)
for hun in range(math.ceil(size/100)) if size>100 else range(1):

    for ten in range(10) if (size-index)>100 else range(math.ceil((size-index)/10)):
        
        if (ten!=0): print(str(ten)+" "+"sleep 60"); time.sleep(60)
        for i in range(10) if (size-index)>10 else range(size-index):
            
            if (operation_list[index]["method"]=="DELETE"):
                req = requests.delete(URL["delete"]+str(operation_list[index]["id"]), headers=get_headers())
                print(req.text)
 
            if (operation_list[index]["method"]=="CREATE"):
                segment = "".join([
                    "{",
                    "\"segment\":{",
                    "\"name\":\"",
                    str(operation_list[index]["name"]),
                    "\",\"geo_segment_type\":\"",
                    str(operation_list[index]["type"]),
                    "\",\"polygons\":",
                    str(operation_list[index]["polygons"]).replace('\'','\"'),
                    "}}"
                ])
                segment=segment.encode()
                req = requests.post(URL["create"], headers=get_headers(), data=segment)
                print(json.loads(req.text)['segment']['name'])
            index = index + 1
    print("sleep 3600"); time.sleep(3600)

print("***"*9+"Обновление закончено"+"***"*9)
print("Ожидание перерасчета")

not_calculated = True

while not_calculated:

    not_calculated = False

    req = requests.get(URL["get"], headers=get_headers())
    json_data = json.loads(req.text)

    try:
        for data in json_data['segments']:
            if data['status'] == "is_updated" or data['status'] == "is_processed":
                not_calculated = True
        if (not_calculated):
            print("60 мин до проверки перерасчета")
            time.sleep(900)
            print("45 мин до проверки перерасчета")
            time.sleep(900)
            print("30 мин до проверки перерасчета")
            time.sleep(900)
            print("15 мин до проверки перерасчета")
            time.sleep(900)
    except:
        print(json_data)

print("Создание файла")
        
name = str(datetime.now().strftime("%d_%m_%Y__%H_%M_%S")) + "_result.xlsx"    
workbook = xlsxwriter.Workbook(name)
worksheet = workbook.add_worksheet()

worksheet.set_column('A:A', 25)
worksheet.set_column('B:B', 13)
worksheet.set_column('C:C', 13)

my_format = workbook.add_format()
my_format.set_align('center')

worksheet.merge_range("B1:C1", date.today().strftime("%d.%m.%Y"), my_format)
worksheet.write(1,0,"Локация",my_format)  
worksheet.write(1,1,"Работающие",my_format)
worksheet.write(1,2,"Посетители",my_format)
        
row = 2
col = 0

for tea in json_data['segments']:
    name_stripped = str(tea['name'])[:-4]
    count = 0
    id = [0,0]

    for data in json_data['segments']:
        
        if (str(data['name'])[:-4] == name_stripped):
            count += 1
            if (data['geo_segment_type'] == "work"):
                id[0] = data['id']
            if (data['geo_segment_type'] == "regular"):
                id[1] = data['id']
   
    worksheet.write(row, col,     str(name_stripped))

    if (count != 2):
        worksheet.write(row, col + 1, "invalit_amount_of_entries_of_workers_or_visiters")
        worksheet.write(row, col + 2, "invalit_amount_of_entries_of_workers_or_visiters")
    else:
        info_worker = 0
        info_visiter = 0

        for id_json in json_data['segments']:
            try:
                if (id_json['id'] == id[0]):
                    info_worker = id_json['cookies_matched_quantity']
                if (id_json['id'] == id[1]):
                    info_visiter = id_json['cookies_matched_quantity']
            except:
                print("Not updated first time")

        worksheet.write(row, col + 1, info_worker)
        worksheet.write(row, col + 2, info_visiter)
    row += 1

    
    for id_del in id:
        pos = 0
        for id_json in json_data['segments']:
            if (tea['id'] == id_del):
                pos+=1
                continue
            if (id_json['id'] == id_del):
                json_data['segments'].pop(pos)

workbook.close()

print("***"*9+"Завершено. Можно закрыть окно"+"***"*9)