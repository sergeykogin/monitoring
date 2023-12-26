import pandas as pd
import numpy as np
from datetime import datetime
import os


# проверяем корректность даты и если она корректна, возвращаем ее
def validate_date(date_string, date_format="%Y-%m-%d %H:%M:%S"):
    try:
        datetime.strptime(str(date_string), date_format) # пробуем разобрать  строку в объект datetime
        return date_string
    except ValueError: # если не получается, возникает исключение
        return np.nan

# проверяем корректность ФИО и если все корректно, возвращаем это значение
def validate_name(row):
    parts = str(row).split()  # Разбиваем строку на слова
    # Проверяем, содержит ли строка хотя бы три слова (фамилию, имя и отчество)
    if len(parts) >= 3:
        return row
    else:
        return np.nan  # Заменяем на NaN, если не хватает частей

def parsing_shtat(in_file_name, arrival_date, start_id_man):

    current_date_time = datetime.now()
    current_date = current_date_time.date()
    try:
        input_xl_file = pd.ExcelFile(in_file_name) # Чтение файла Excel
    except:
        return "Ошибка формата файла"

    try:# Извлечение данных из листов 'ВШДР' и 'РЕЗЕРВ'
        df1 = input_xl_file.parse('ВШДР', usecols=[1, 12, 18, 19, 20, 21, 22, 23, 24, 27, 28, 29])
        df2 = input_xl_file.parse('РЕЗЕРВ', usecols=[1, 12, 18, 19, 20, 21, 22, 23, 24, 27, 28, 29])
    except:
        return "В документе нет листов 'ВШДР' или 'РЕЗЕРВ'"

    df1.columns = ['Группа', 'Должность по ВШДР', 'Воинское звание', 'Фамилия Имя Отчество', 'Группа.1', 'Дата рождения', 'Личный номер', 'Группа.2', 'Должность в РФ', 'в/ч', 'Округ', 'Дата пересечения границы']
    df2.columns = ['Группа', 'Должность по ВШДР', 'Воинское звание', 'Фамилия Имя Отчество', 'Группа.1', 'Дата рождения', 'Личный номер', 'Группа.2', 'Должность в РФ', 'в/ч', 'Округ', 'Дата пересечения границы']
    result_df = pd.concat([df1, df2]) # Объединение данных из двух датафреймов

    result_df['Фамилия Имя Отчество'] = result_df['Фамилия Имя Отчество'].apply(validate_name) # Обработка значений в столбце 'Фамилия Имя Отчество'
    result_df.dropna(subset=['Фамилия Имя Отчество'], inplace=True) # Удаление строк с пустыми значениями в столбце 'Фамилия Имя Отчество'

    result_df['Дата рождения'] = result_df['Дата рождения'].apply(validate_date) # Обработка значений в столбце 'Дата рождения'
    result_df.dropna(subset=['Дата рождения'], inplace=True) # Удаление строк с пустыми значениями в столбце 'Дата рождения'

    result_df['Дата пересечения границы'] = result_df['Дата пересечения границы'].apply(validate_date)# Обработка значений в столбце 'Дата пересечения границы'
    result_df.dropna(subset=['Дата пересечения границы'], inplace=True) # Удаление строк с пустыми значениями в столбце 'Дата пересечения границы'
    condition = result_df['Дата пересечения границы'] < pd.to_datetime(arrival_date, format="%Y-%m-%d %H:%M:%S") #  проверка условия пересечения границы после определенной даты
    result_df = result_df.loc[~condition] # удаление значений, если граница пересечена раньше даты в условии condition

    result_df['Дата рождения'] = result_df['Дата рождения'].dt.strftime("%d.%m.%Y") # преобразование значений столбцов к строке в нужном формате даты
    result_df['Дата пересечения границы'] = result_df['Дата пересечения границы'].dt.strftime("%d.%m.%Y") # преобразование значений столбцов к строке в нужном формате даты

    result_df.sort_values(by='Фамилия Имя Отчество', inplace=True) # сортируем по столбцу 'Фамилия Имя Отчество' в порядке возрастания
    result_df.drop_duplicates(inplace=True) # удаляем дубликаты
    result_df.reset_index(drop=True, inplace=True)  # Сброс индексов
    result_df = result_df[result_df['Воинское звание']!= "ГП"]# удаляем ГП

    subfolder = 'data_out'# Путь к подпапке
    file_path = os.path.join(subfolder, f"Выгрузка_{current_date}.xlsx")# Полный путь к файлу, включая подпапку
    with pd.ExcelWriter(file_path, engine="openpyxl") as writer1:# Используйте полный путь при создании ExcelWriter
        result_df.to_excel(writer1, index=False)

    #изменение столбца с личным номером
    for index, row in result_df.iterrows():
        result_df.at[index, 'Личный номер'] = f"ZV-{start_id_man:06}"
        start_id_man += 1


    result_df.columns = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] # изменяем название столбцов для файла *.csv
    file_path = os.path.join(subfolder, f"output_parsfile_{current_date}.csv")  # Полный путь к файлу, включая подпапку
    result_df.to_csv(file_path, index=False, sep=';', encoding='utf-8-sig') # Создание объекта для записи данных в новый файл Excel
    return "Файл успешно обработан"