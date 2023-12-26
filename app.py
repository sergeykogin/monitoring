from flask import Flask, render_template, url_for, request, redirect, Response, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from parsing_shtat import parsing_shtat
import pandas as pd
from dateutil.relativedelta import relativedelta
import unicodecsv as csv
import io
import os
from docxtpl import DocxTemplate, InlineImage
import re

app = Flask(__name__)  # создание объекта Flask

# Получение абсолютного пути к текущей директории
current_directory = os.path.abspath(os.path.dirname(__file__))

# Установка путей для шаблонов и статических файлов
app.template_folder = os.path.join(current_directory, 'templates_html')
app.static_folder = os.path.join(current_directory, 'styles')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(current_directory,
                                                                    'ls.db')  # Настройка базы данных с использованием SQLite:
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Отключение отслеживания изменений в базе данных
db = SQLAlchemy(app)  # Создание объекта SQLAlchemy


class LS(db.Model):  # определение класса модели базы данных
    __tablename__ = 'ls'  # Эта строка указывает имя таблицы в базе данных
    # поля таблицы в базе данных с разными типами данных
    id = db.Column(db.Integer, primary_key=True)
    self_number = db.Column(db.String(30), nullable=False)
    surname = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(30), nullable=False)
    patronymic = db.Column(db.String(30), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    arrival_date = db.Column(db.Date, nullable=True)
    DB_date = db.Column(db.Date, nullable=True)
    rank = db.Column(db.String(30), nullable=True)
    post = db.Column(db.String(100), nullable=True)
    group = db.Column(db.String(30), nullable=True)
    detachment = db.Column(db.String(30), nullable=True)
    post_russia = db.Column(db.String(100), nullable=True)
    military = db.Column(db.String(10), nullable=True)
    district = db.Column(db.String(10), nullable=True)
    mobile_phone = db.Column(db.String(15), nullable=True)
    vk_existence = db.Column(db.Integer, default=0)
    ok_existence = db.Column(db.Integer, default=0)
    violation_category_vk = db.Column(db.String(50), default='')
    link_vk = db.Column(db.String(50), nullable=True)
    link_ok = db.Column(db.String(50), nullable=True)
    violation_category_ok = db.Column(db.String(50), default='')
    violation_date = db.Column(db.Date, nullable=True)
    punishment = db.Column(db.String(100), nullable=True)
    note = db.Column(db.String(100), nullable=True)

    def __repr__(self):  # метод для представления объекта в виде строки
        return '<LS %r>' % self.id


class VK(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ls_self_number = db.Column(db.String(30), db.ForeignKey('ls.self_number'))
    link = db.Column(db.String(50), nullable=False)
    date_of_visit = db.Column(db.Date, nullable=True)
    date_of_check = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return '<VK %r>' % self.id


class OK(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ls_self_number = db.Column(db.String(30), db.ForeignKey('ls.self_number'))
    link = db.Column(db.String(50), nullable=False)
    date_of_visit = db.Column(db.Date, nullable=True)
    date_of_check = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return '<OK %r>' % self.id


class TASK(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(100), nullable=False)
    text = db.Column(db.String(300), nullable=True)
    date = db.Column(db.Date, nullable=False)
    cycle = db.Column(db.Integer, default=0)
    cycle_period = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return '<task %r>' % self.id


with app.app_context():  # Создать таблицы, если они не существуют
    db.create_all()


@app.route('/')
def main():
    vk = 0
    ok = 0
    ls = LS.query.all()
    for el in ls:
        if el.vk_existence > 0:
            vk = vk + el.vk_existence
        if el.ok_existence > 0:
            ok = ok + el.ok_existence
    all = LS.query.count()
    ''' на момент корректировки скрипта, закомментированный код не был актуальным
    photo = LS.query.filter((LS.violation_category_ok == 'фото в форме') | (LS.violation_category_vk == 'фото в форме'),
                            LS.punishment != 'нет', LS.punishment != '').count()
    ts = LS.query.filter((LS.violation_category_ok == 'использование личного технического средства') | (
                LS.violation_category_vk == 'использование личного технического средства'), LS.punishment != 'нет',
                         LS.punishment != '').count()
    inf = LS.query.filter((LS.violation_category_ok == 'информация о принадлежности') | (
                LS.violation_category_vk == 'информация о принадлежности'), LS.punishment != 'нет',
                          LS.punishment != '').count()
    strict = LS.query.filter(LS.punishment == 'строгий выговор').count()
    rebuke = LS.query.filter(LS.punishment == 'выговор').count()
    ppd = LS.query.filter(LS.punishment == 'материалы направлены в ППД').count()
    ukaz = LS.query.filter(
        LS.punishment == 'приказано удалить страницу (указано на недопустимость подобных нарушений)').count()
    vvo = LS.query.filter(LS.district == 'ВВО', LS.punishment != 'нет', LS.punishment != '').count()
    vdv = LS.query.filter(LS.district == 'ВДВ', LS.punishment != 'нет', LS.punishment != '').count()
    vks = LS.query.filter(LS.district == 'ВКС', LS.punishment != 'нет', LS.punishment != '').count()
    vuz = LS.query.filter(LS.district == 'ВУЗ', LS.punishment != 'нет', LS.punishment != '').count()
    zvo = LS.query.filter(LS.district == 'ЗВО', LS.punishment != 'нет', LS.punishment != '').count()
    sf = LS.query.filter(LS.district == 'СФ', LS.punishment != 'нет', LS.punishment != '').count()
    cvo = LS.query.filter(LS.district == 'ЦВО', LS.punishment != 'нет', LS.punishment != '').count()
    covu = LS.query.filter(LS.district == 'ЦОВУ', LS.punishment != 'нет', LS.punishment != '').count()
    uvo = LS.query.filter(LS.district == 'ЮВО', LS.punishment != 'нет', LS.punishment != '').count()
    tasks = TASK.query.filter(TASK.date <= datetime.now().date()).all()
    return render_template("main.html", all=all, tasks=tasks, vk=vk, ok=ok, photo=photo, ts=ts, inf=inf, vvo=vvo, vdv=vdv, vks=vks, vuz=vuz, zvo=zvo, sf=sf, cvo=cvo, covu=covu, uvo=uvo, strict=strict, rebuke=rebuke, ppd=ppd, ukaz=ukaz)
    '''

    return render_template("main.html", all=all, vk=vk, ok=ok)


''' этот функционал на момент корректировки скрипта не был актуальным 
@app.route('/delete/<int:id>')
def delete(id):
    tasks = TASK.query.get_or_404(id)
    if tasks.cycle == 0:
        try:
            db.session.delete(tasks)
            db.session.commit()
            return redirect('/')
        except:
            return "При удалении задачи возникла ошибка"
    else:
        try:
            if tasks.cycle_period == 1:
                tasks.date = tasks.date + relativedelta(days=+1)
            elif tasks.cycle_period == 2:
                tasks.date = tasks.date + relativedelta(days=+7)
            else:
                tasks.date = tasks.date + relativedelta(months=+1)
            db.session.commit()
            return redirect('/')
        except:
            return "При удалении задачи возникла ошибка"


@app.route('/task_create', methods=['POST', 'GET'])
def task_create():
    if request.method == "POST":
        task = request.form['task']
        text = request.form['text']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        try:
            cycle = request.form['cycle']
            cycle_period = request.form['cycle_period']
        except:
            cycle = 0
            cycle_period = 0
        print(task, text, date, cycle, cycle_period)
        tasks = TASK(task=task, text=text, date=date, cycle=cycle, cycle_period=cycle_period)
        try:
            db.session.add(tasks)
            db.session.commit()
            return redirect('/')
        except:
            return "Ошибка"
    else:
        return render_template("task_create.html")

'''


@app.route('/add_to_bd', methods=['POST', 'GET'])
def add_to_bd():
    if request.method == "POST":
        if 'btn_parsing' in request.form:  # если была нажата кнопка "Обработать" в add_to_bd.html
            input_file = request.files['input_file_parsing']  # получаем выбранный файл
            from_date = f"{request.form.get('from_date')} 00:00:00"  # получаем указанную дату и преобразуем в формат "%Y-%m-%d %H:%M:%S"
            last_elem = LS.query.order_by(LS.id.desc()).first()  # получаем последний элемент БД таблицы ls
            id_last_num = 1
            if last_elem:
                id_last_num = int(last_elem.self_number[3:]) + 1
            message = parsing_shtat(input_file, from_date, id_last_num)
            return render_template("add_to_bd.html", message=message)
        # ======================================================================================
        if 'btn_add_bd' in request.form:  # если была нажата кнопка "Добавить в БД" в add_to_bd.html
            input_file = request.files['input_file']
            data_in = pd.read_csv(input_file, encoding='utf8', sep=';')
            for row in range(0, len(data_in)):
                data = data_in.values[row]
                if not bool(LS.query.filter_by(self_number=data[6]).first()):
                    try:
                        stripped_data = data[3].strip()
                        surname, name, patronymic = re.split(r'\s+',stripped_data, maxsplit=2)
                        ls = LS(self_number=data[6], surname=surname,
                                name=name, patronymic=patronymic,
                                date_of_birth=datetime.strptime(data[5], '%d.%m.%Y'),
                                arrival_date=datetime.strptime(data[11], '%d.%m.%Y'),
                                DB_date=datetime.now(), group=data[0],
                                post=data[1], rank=data[2],
                                detachment=data[7], post_russia=data[8],
                                military=data[9], district=data[10])
                        print(surname, name, patronymic)
                    except:
                        print("Ошибка")
                    try:
                        db.session.add(ls)
                    except:
                        return "Возникла ошибка"
            db.session.commit()
            return redirect('/')
    # ======================================================================================
    else:
        return render_template("add_to_bd.html")


@app.route('/all_analyzed', methods=['POST', 'GET'])
def all_analyzed():
    if request.method == "POST":
        if 'export_list' in request.form:
            arrival_date = f"{request.form.get('from_date')}"
            if arrival_date:
                ls_all = LS.query.filter(LS.arrival_date >= arrival_date).all()
            else:
                ls_all = LS.query.all()
            output = io.BytesIO()
            writer = csv.writer(output, encoding='cp1251')
            for ls in ls_all:
                line = [
                    ls.self_number + ';' + ls.surname + ';' + ls.name + ';' + ls.patronymic + ';' + ls.date_of_birth.strftime(
                        '%d.%m.%Y')]
                writer.writerow(line)
            output.seek(0)
            return Response(output, mimetype="text/csv",
                            headers={"Content-Disposition": "attachment;filename=report.csv"})
        if 'add_violator_vk' in request.form:
            input_file = request.files['file_vk']
            data_in = pd.read_csv(input_file, encoding='cp1251', sep=';')
            for row in range(0, len(data_in)):
                data = data_in.values[row]
                ls = LS.query.filter(LS.self_number == data[0]).first()
                if ls.link_vk == data[1]:
                    continue
                ls.violation_category_vk = data[3]
                ls.link_vk = data[1]
                violator_vk = VK(ls_self_number=data[0], link=data[1],
                                 date_of_visit=datetime.strptime(data[2], '%d.%m.%Y'), date_of_check=datetime.now())
                ls.vk_existence = 1
                try:
                    db.session.add(violator_vk)
                except:
                    return "Возникла ошибка"
            db.session.commit()
            return redirect('/all_analyzed')
        if 'add_violator_ok' in request.form:
            input_file = request.files['file_ok']
            data_in = pd.read_csv(input_file, encoding='cp1251', sep=';')
            for row in range(0, len(data_in)):
                data = data_in.values[row]
                ls = LS.query.filter(LS.self_number == data[0]).first()
                if ls.link_ok == data[1]:
                    continue
                ls.violation_category_ok = data[3]
                ls.link_ok = data[1]
                violator_ok = OK(ls_self_number=data[0], link=data[1],
                                 date_of_visit=datetime.strptime(data[2], '%d.%m.%Y'), date_of_check=datetime.now())
                ls.ok_existence = 1
                try:
                    db.session.add(violator_ok)
                except:
                    return "Возникла ошибка"
            db.session.commit()
            return redirect('/all_analyzed')
    else:
        ls = LS.query.all()
        return render_template("all_analyzed.html", ls=ls)


@app.route('/vk_osint', methods=['POST', 'GET'])
def vk_osint():
    if request.method == "POST":
        if request.form["btn"] == "Сохранить изменения":
            ls_all = LS.query.filter(LS.violation_category_vk != '', LS.violation_category_vk != 'нет').all()
            for ls in ls_all:
                id = request.form.get(str(ls.id))
                if id != None:
                    ls.violation_category_vk = id
                    if (id != 'нет') or (id != ''):
                        ls.punishment = ''
            db.session.commit()
            return redirect('/vk_osint')
        else:
            id = request.form["btn"]
            vk = db.session.get(VK, id)
            ls = LS.query.filter(LS.self_number == vk.ls_self_number).first()
            ls.violation_date = datetime.now()
            db.session.commit()

            templates_docx = 'templates_docx'  # Путь к подпапке с шаблоном документа
            file_path = os.path.join(templates_docx, "шаблон_вк.docx")  # Полный путь к файлу, включая подпапку
            doc = DocxTemplate(file_path)
            # Получаем фото со страниц нарушителя
            image_folder = os.path.join(current_directory, 'violators_foto\\VK', ls.self_number)
            # Создайте список изображений для вставки
            images = []
            for root, dirs, files in os.walk(image_folder):
                for file in files:
                    image_path = os.path.join(root, file)
                    images.append(InlineImage(doc, image_path))  # Измените ширину и высоту по вашему желанию

            context = {'rank': ls.rank, 'surname': ls.surname, 'name': ls.name, 'patronymic': ls.patronymic,
                       'date_of_birth': ls.date_of_birth.strftime('%d.%m.%Y'),
                       'post': ls.post, 'group': ls.group, 'detachment': ls.detachment,
                       'arrival_date': ls.arrival_date.strftime('%d.%m.%Y'),
                       'date_of_visit': vk.date_of_visit.strftime('%d.%m.%Y'), 'post_russia': ls.post_russia,
                       'military': ls.military,
                       'district': ls.district, 'link': vk.link, 'images': images}
            doc.render(context)
            output = io.BytesIO()
            doc.save(output)
            output.seek(0)
            return send_file(output, as_attachment=True,
                             download_name=f"{datetime.now().strftime('%d/%m/%Y')} {ls.surname}.docx")
    else:
        t = {}
        j = 0
        ls = LS.query.filter(LS.violation_category_vk != '', LS.violation_category_vk != 'нет').all()
        for el in ls:
            vk = VK.query.filter(VK.ls_self_number == el.self_number, VK.link == el.link_vk).all()
            for units in vk:
                t[j] = {'id1': units.id, 'id2': el.id, 'self_number': el.self_number,
                        'surname': el.surname, 'name': el.name, 'arrival_date': el.arrival_date,
                        'link': units.link, 'date_of_visit': units.date_of_visit,
                        'violation_category': el.violation_category_vk, 'DB_date': el.DB_date}
                j += 1
        return render_template("vk_osint.html", t=t)


@app.route('/ok_osint', methods=['POST', 'GET'])
def ok_osint():
    if request.method == "POST":
        if request.form["btn"] == "Сохранить изменения":
            ls_all = LS.query.filter(LS.violation_category_ok != '', LS.violation_category_ok != 'нет').all()
            for ls in ls_all:
                id = request.form.get(str(ls.id))
                if id != None:
                    ls.violation_category_ok = id
                    if (id != 'нет') or (id != ''):
                        ls.punishment = ''
            db.session.commit()
            return redirect('/ok_osint')
        else:
            id = request.form["btn"]
            ok = OK.query.get(id)
            ls = LS.query.filter(LS.self_number == ok.ls_self_number).first()
            ls.violation_date = datetime.now()
            db.session.commit()
            templates_docx = 'templates_docx'  # Путь к подпапке с шаблоном документа
            file_path = os.path.join(templates_docx, "шаблон_ок.docx")  # Полный путь к файлу, включая подпапку
            doc = DocxTemplate(file_path)
            # Получаем фото со страниц нарушителя
            image_folder = os.path.join(current_directory, 'violators_foto\\OK', ls.self_number)
            # Создайте список изображений для вставки
            images = []
            for root, dirs, files in os.walk(image_folder):
                for file in files:
                    image_path = os.path.join(root, file)
                    images.append(InlineImage(doc, image_path))  # Измените ширину и высоту по вашему желанию
            context = {'rank': ls.rank, 'surname': ls.surname, 'name': ls.name, 'patronymic': ls.patronymic,
                       'date_of_birth': ls.date_of_birth.strftime('%d.%m.%Y'),
                       'post': ls.post, 'group': ls.group, 'detachment': ls.detachment,
                       'arrival_date': ls.arrival_date.strftime('%d.%m.%Y'),
                       'date_of_visit': ok.date_of_visit.strftime('%d.%m.%Y'),
                       'post_russia': ls.post_russia, 'military': ls.military, 'district': ls.district, 'link': ok.link,
                       'images': images}
            doc.render(context)
            output = io.BytesIO()
            doc.save(output)
            output.seek(0)
            return send_file(output, as_attachment=True,
                             download_name=f"{datetime.now().strftime('%d/%m/%Y')} {ls.surname}.docx")
    else:
        t = {}
        j = 0
        ls = LS.query.filter(LS.violation_category_ok != '', LS.violation_category_ok != 'нет').all()
        for el in ls:
            ok = OK.query.filter(OK.ls_self_number == el.self_number, OK.link == el.link_ok).all()
            for units in ok:
                t[j] = {'id1': units.id, 'id2': el.id, 'self_number': el.self_number,
                        'surname': el.surname, 'name': el.name, 'arrival_date': el.arrival_date,
                        'link': units.link, 'date_of_visit': units.date_of_visit,
                        'violation_category': el.violation_category_ok, 'DB_date': el.DB_date}
                j += 1
        return render_template("ok_osint.html", t=t)


@app.route('/upload_report')
def upload_report():
    ls = LS.query.filter((LS.violation_category_vk != '') | (LS.violation_category_ok != ''),
                         (LS.violation_category_vk != 'нет') | (LS.violation_category_ok != 'нет'),
                         LS.punishment == '').all()
    templates_docx = 'templates_docx'  # Путь к подпапке с шаблоном документа
    file_path = os.path.join(templates_docx, "шаблон_доклада.docx")  # Полный путь к файлу, включая подпапку
    doc = DocxTemplate(file_path)
    context = {'ls': ls}
    doc.render(context)
    output = io.BytesIO()
    doc.save(output)
    output.seek(0)
    return send_file(output, as_attachment=True,
                     download_name=datetime.now().strftime('%d/%m/%Y') + " Доклад.docx")


@app.route('/violators', methods=['POST', 'GET'])
def violators():
    if request.method == "POST":
        ls_all = LS.query.all()
        for ls in ls_all:
            id = request.form.get(str(ls.id))
            if id != None:
                ls.punishment = id
        db.session.commit()
        return redirect('/')
    else:
        ls = LS.query.filter(
            (LS.violation_category_vk == 'фото в форме') | (LS.violation_category_vk == 'информация о принадлежности') |
            (LS.violation_category_vk == 'использование личного технического средства') | (
                    LS.violation_category_ok == 'фото в форме') |
            (LS.violation_category_ok == 'информация о принадлежности') | (
                    LS.violation_category_ok == 'использование личного технического средства')).all()

        return render_template("violators.html", ls=ls)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
