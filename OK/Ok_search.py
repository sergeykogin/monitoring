# -*- coding: utf-8 -*-
import pandas as pd
import datetime
import urllib


file_out = open('../out_data_file/out_OK_' + datetime.datetime.now().strftime('%Y-%m-%d') + '.html', 'w', encoding="utf8")
data_in = pd.read_csv('../in_data_file/in.csv', encoding = 'cp1251', sep = ';', header=None)

def generate_links(data_in):
    for _, row in data_in.iterrows():
        index = row[0]
        last_name = row[1]
        first_name = row[2]
        birthday = row[4]

        if validate(birthday):
            birth_day = int(birthday[:2])
            birth_month = int(birthday[3:5])
            birth_year = int(birthday[6:10])

            if birth_year > 2018:
                print("Oh my sir, invalid year value\n")
            elif birth_month < 1 or birth_month > 12:
                print("Oh my sir, invalid month value\n")
            else:
                out_html = '<a href="https://ok.ru/search?st.query=' + urllib.parse.quote_plus(first_name) + ' '
                out_html += urllib.parse.quote_plus(last_name) + '&st.bthDay=' + str(birth_day)
                out_html += '&st.bthMonth=' + str(birth_month - 1) + '&st.bthYear='
                out_html += str(
                    birth_year) + '&st.mode=Users&st.grmode=Groups&st.posted=set"</a>' + index + ' ' + last_name + ' ' + first_name + ' ' + '0' * (
                                 2 - len(str(birth_day))) + str(birth_day) + '.' + '0' * (
                                 2 - len(str(birth_month))) + str(birth_month) + '.' + str(
                    birth_year) + '<br>'
                file_out.write(out_html + '\n')
                print(out_html)

def validate(date_text):
    result = False
    try:
        datetime.datetime.strptime(date_text, '%d.%m.%Y')

        result = True
    except ValueError:
        print("Oh my sir, incorrect data format\n")
    return result

generate_links(data_in)


