import pandas as pd
import vk_api
import datetime
import time
from concurrent.futures import ThreadPoolExecutor

#Функция для запросов к API ВКонтакте
def zapros_vk(data):
    result = vk.users.search(q = data[1] + ' ' + data[2],
                         birth_day = data[4][0:2],
                         birth_month = data[4][3:5],
                         birth_year = data[4][6:10],
                         fields='last_seen')
    return result

#Чтение из файла информации по в/с
data_in = pd.read_csv('../in_data_file/in.csv', encoding = 'cp1251', sep = ';')

#Авторизация в ВК и открытие сессии для взаимодействия с API
vk_session = vk_api.VkApi('+77002380403', '!QAZ4rfv*IK')
vk_session.auth()
vk = vk_session.get_api()

#Словарик для хранения информации при вызове функции zapros_vk(data)
t={}

#Многопоточность
#with ThreadPoolExecutor(8) as executor:
for j in range(0, len(data_in)):
    try:
        time.sleep(15)
        t[j]=zapros_vk(data_in.values[j])
    except:
        print('какая-то ошибка')
            
    if not t[j]['items']:
        slovarik1={'S_self_number' : [data_in.values[j][0]],
                      'S_id' : ['нет'],
                      'S_last_name'  : [data_in.values[j][1]],
                      'S_first_name' : [data_in.values[j][2]],
                      'S_bdate'      : [data_in.values[j][4]],
                      'S_last_seen'  : ['-']}
        print(slovarik1)
        data_out = pd.DataFrame(slovarik1)
        data_out.to_csv('../out_data_file/out_vk_' + datetime.datetime.now().strftime('%Y-%m-%d') + '.csv', mode = 'a', encoding = 'cp1251', index=False, header=False, sep=';')
        
    for h in (t[j]['items']):

#Проверка на пустое значение 'last_seen'
        if not h.get('last_seen',{}).get('time',''):
            h.update({'last_seen' : {'time' : 0}})

#Объявление словаря для хранения необходимых значений из запроса к API ВКонтакте
        slovarik2={'S_self_number' : [data_in.values[j][0]],
                      'S_id'         : ['https://vk.com/id'+ str(h['id'])],
                      'S_last_name'  : [data_in.values[j][1]],
                      'S_first_name' : [data_in.values[j][2]],
                      'S_bdate'      : [data_in.values[j][4]],
                      'S_last_seen'  : [datetime.datetime.fromtimestamp(int(h.get('last_seen',{}).get('time',''))).strftime('%H:%M:%S %d.%m.%Y')]}

#Преобразование словаря в тип данных DataFrame и их запись в файл
        data_out = pd.DataFrame(slovarik2)
        data_out.to_csv('../out_data_file/out_vk_' + datetime.datetime.now().strftime('%Y-%m-%d') + '.csv', mode = 'a', encoding = 'cp1251', index=False, header=False, sep=';')

print("Поиск успешно завершен")
