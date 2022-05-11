import os
import json

import requests
from flask import Flask, redirect, url_for, render_template, request, flash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_restful import Api
from werkzeug.security import generate_password_hash, check_password_hash
from jobs_resource import JobsResourse, JobsListResourse

import jobs_api
import users_api
from data import db_session
from create import create_users, add_job
from data.users import User
from data.jobs import Jobs
from data.department import Department
from forms.add_job import JobForm
from forms.autorize import AutorizeForm
from forms.department import DepForm
from forms.register import RegisterForm
from forms.file import FileForm
from maps_api import YandexApi

app = Flask(__name__)

db_session.global_init("db/new.db")
sess = db_session.create_session()
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Вы должны быть авторизованы для просмотра этой страницы.'
rest = Api(app)

def cur_user(_id=None):
    if not _id and current_user:
        _id = current_user.get_id()
    return sess.query(User).filter_by(id=_id).first()


def get_collabs(_collaborators):
    try:
        collaborators = str(int(_collaborators))
        succ = True
    except ValueError:
        succ = False

    if not succ:
        collaborators = ', '.join(
            sorted(map(str, list(set(map(int, _collaborators.split(', '))))))
        )
    return collaborators


def create_dep(title: str, chief_id: int, email: str, members: str=None):
    _members = None
    if members:
        try:
            _members = get_collabs(members)
        except Exception:
            raise IndexError
    _new = Department(
        title=title,
        chief=chief_id,
        members=_members,
        email=email
    )
    sess.add(_new)
    sess.commit()


def create_job(leader_id: int, desc: str, time: int, is_finish: bool, hazard: int, _collaborators=None):
    leader = leader_id
    desc = desc
    time = time
    is_finish = is_finish
    if _collaborators:
        try:
            collaborators = get_collabs(_collaborators)
            _new = Jobs(
                team_leader=leader,
                job=desc,
                work_size=time,
                collaborators=collaborators,
                hazard=hazard,
                is_finished=is_finish
            )
        except Exception:
            raise IndexError
    else:
        _new = Jobs(
            team_leader=leader,
            job=desc,
            work_size=time,
            hazard=hazard,
            is_finished=is_finish
        )
    sess.add(_new)
    sess.commit()


def url(filename, _type='css'):
    return url_for('static', filename=f'{_type}/{filename}')


@login_manager.user_loader
def load_user(user_id):
    return cur_user(user_id)


@app.route('/')
@app.route('/index')
def index():
    works = sess.query(Jobs).all()
    return render_template('index.html', css=url_for('static', filename='css/index.css'),
                           works=works, user=cur_user())


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = AutorizeForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = sess.query(User).filter_by(email=form.login.data).first()
            if user and check_password_hash(user.hashed_password, form.password.data):
                login_user(user)
                return redirect(url_for('index'))
    return render_template('login.html', form=form, user=cur_user())


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    message = ''
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                message = 'Пароли не совпадают!'
            else:
                user = User(
                    surname=form.surname.data,
                    name=form.name.data,
                    age=form.age.data,
                    position=form.position.data,
                    speciality=form.speciality.data,
                    address=form.address.data,
                    email=form.email.data,
                    hashed_password=generate_password_hash(form.password.data)
                )
                sess.add(user)
                sess.commit()
                message = 'Зарегано!'
    return render_template('register.html', form=form, message=message, user=cur_user())


@app.route('/logout')
def logout():
    if current_user.get_id():
        logout_user()
    return redirect(url_for('index'))


@app.route('/distribution')
def distribution():
    users = sess.query(User).all()
    return render_template('distribution.html', users=users)


@app.route('/table/<string:gender>/<int:age>')
def table(gender, age):
    return render_template('table.html', gender=gender, age=age, css=url('table.css'))


@app.route('/galery', methods=['GET', 'POST'])
def galery():
    form = FileForm()
    path = './static/img/carousel'
    files = os.listdir(path)[:-1]
    print(files)
    files_len = len(files)
    if request.method == 'POST':
        if form.validate_on_submit():
            files_str = ':'.join(files)
            if form.file.data.filename.split('.')[-1] in ['png', 'jpg', 'jpeg']:
                _index = 1
                while True:
                    if str(_index) in files_str:
                        _index += 1
                        print(_index)
                    else:
                        file = form.file.data
                        file.save(f'./static/img/carousel/{_index}.png')
                        break
                return redirect(url_for('galery'))

    return render_template('galery.html', files=files, files_len=files_len, css=url('galery.css'),
                           form=form)


@app.route('/member')
def member():
    j_data = json.load(open('templates/users.json'))
    return render_template('member.html', j_data=j_data, css=url('member.css'))


@app.route('/add_job', methods=['GET', 'POST'])
@login_required
def add_job():
    form = JobForm()
    message = ''
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                leader = sess.query(User).filter_by(id=form.team_leader.data).first()
                if not leader:
                    message = 'Такого лидера не существует'
                else:
                    create_job(leader.id, form.job.data, form.work_size.data,
                               form.finished.data, form.hazard.data, form.collaborators.data)
                    message = 'Работа создана'
            except IndexError:
                message = 'Должен быть список id, разделенных ", "'
            except Exception:
                message = 'Что-то пошло не так'
    return render_template('manage_job.html', user=cur_user(), form=form, message=message)


@app.route('/edit_job', methods=['GET', 'POST'])
@login_required
def edit_job():
    form = JobForm()
    message = ''
    if not request.args.get('id'):
        return redirect(url_for('index'))
    else:
        try:
            work_id = int(request.args.get('id'))
        except ValueError:
            return redirect(url_for('index'))
    work = sess.query(Jobs).filter_by(id=work_id).first()
    user = cur_user()
    if not work or (work.team_leader != user.id and user.id != 1):
        flash('У вас нет прав на редактирования этой работы')
        return redirect(url_for('index'))
    if request.method == 'POST':
        try:
            work.team_leader = int(form.team_leader.data)
            work.job = form.job.data
            work.work_size = int(form.work_size.data)
            work.hazard = int(form.hazard.data)
            work.is_finished = form.finished.data
            if form.collaborators.data:
                try:
                    work.collaborators = get_collabs(form.collaborators.data)
                except Exception:
                    raise IndexError
            elif not form.collaborators.data and work.collaborators:
                work.collaborators = None
            sess.commit()
            flash('Работа отредакированна', 'succ')
            return redirect(url_for('index'))
        except IndexError:
            message = 'Должен быть список id, разделенных ", "'
        except Exception:
            message = 'Что-то пошло не так'
    form.team_leader.data = work.team_leader
    form.job.data = work.job
    form.work_size.data = work.work_size
    form.collaborators.data = work.collaborators if work.collaborators else ''
    form.finished.data = work.is_finished
    return render_template('manage_job.html', form=form, user=user, message=message)


@app.route('/delete_job')
def delete_job():
    if not request.args.get('id'):
        return redirect(url_for('index'))
    else:
        try:
            work_id = int(request.args.get('id'))
        except ValueError:
            return redirect(url_for('index'))
    work = sess.query(Jobs).filter_by(id=work_id).first()
    user = cur_user()
    if not work or (work.team_leader != user.id and user.id != 1):
        flash('У вас нет прав на удаление этой работы')
        return redirect(url_for('index'))
    sess.delete(work)
    sess.commit()
    flash('Работа удалена', 'succ')
    return redirect(url_for('index'))


@app.route('/departments')
def departments():
    deps = sess.query(Department).all()
    chiefs = [sess.query(User).filter_by(id=i.chief).first() for i in deps]
    len_all = len(chiefs)
    return render_template('departments.html', user=cur_user(), deps=deps,
                           chiefs=chiefs, css=url('department.css'),
                           len_all=len_all)


@app.route('/add_department', methods=['GET', 'POST'])
@login_required
def add_department():
    form = DepForm()
    message = ''
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                leader = sess.query(User).filter_by(id=form.chief.data).first()
                if not leader:
                    message = 'Такого лидера не существует'
                else:
                    create_dep(form.title.data, form.chief.data,
                               form.email.data, form.members.data)
                    message = 'Department created'
            except IndexError:
                message = 'Должен быть список id, разделенных ", "'
            except Exception:
                message = 'Что-то пошло не так'
    return render_template('manage_dep.html', form=form, message=message)


@app.route('/edit_department', methods=['GET', 'POST'])
@login_required
def edit_department():
    form = DepForm()
    message = ''
    if not request.args.get('id'):
        return redirect(url_for('departments'))
    else:
        try:
            work_id = int(request.args.get('id'))
        except ValueError:
            return redirect(url_for('departments'))
    work = sess.query(Department).filter_by(id=work_id).first()
    user = cur_user()
    if not work or (work.chief != user.id and user.id != 1):
        flash('У вас нет прав на редактирование этого')
        return redirect(url_for('departments'))
    if request.method == 'POST':
        if form.validate_on_submit():
            _ = sess.query(User).filter_by(id=form.chief.data).first()
            if not _:
                message = 'Такого лидера не существует'
            else:
                try:
                    work.title = form.title.data
                    work.chief = form.chief.data
                    work.email = form.email.data
                    if form.members.data:
                        try:
                            work.members = get_collabs(form.members.data)
                        except Exception:
                            raise IndexError
                    elif not form.members.data and work.members:
                        work.members = None
                    sess.commit()
                    flash('Department edited successfully', 'succ')
                    return redirect(url_for('departments'))
                except IndexError:
                    message = 'Должен быть список id, разделенных ", "'
    form.title.data = work.title
    form.chief.data = work.chief
    form.email.data = work.email
    form.members.data = work.members
    return render_template('manage_dep.html', form=form, message=message)


@app.route('/delete_department')
@login_required
def delete_department():
    if not request.args.get('id'):
        return redirect(url_for('departments'))
    else:
        try:
            work_id = int(request.args.get('id'))
        except ValueError:
            return redirect(url_for('departments'))
    work = sess.query(Department).filter_by(id=work_id).first()
    user = cur_user()
    if not work or (work.chief != user.id and user.id != 1):
        flash('У вас нет прав на удаление этого')
        return redirect(url_for('departments'))
    sess.delete(work)
    sess.commit()
    flash('Department deleted', 'succ')
    return redirect(url_for('departments'))


@app.route('/users_show/<int:user_id>')
def users_show(user_id):
    def create_map(response, __id):
        if not os.path.exists('./static/img/users/hometown'):
            os.mkdir('./static/img/users/hometown')
        with open(f'./static/img/users/hometown/{__id}.png', "wb") as file:
            file.write(response.content)
    api = YandexApi(
        geocode_apikey="40d1649f-0493-4b70-98ba-98533de7710b",
        search_apikey='dda3ddba-c9ea-4ead-9010-f43fbc15c6e3'
    )
    user = requests.get(f'http://127.0.0.1:5000/api/users/{user_id}').json()
    if not user['response']:
        return redirect(url_for('index'))

    lan, lot = api.get_position(user['response']['city_from'])
    test, link = api.static_get('sat', (lan, lot), z=13, add_spn=False, add_zoom_manual=True, return_link=True)
    print(link)
    create_map(test, user_id)

    return render_template('show_user.html', user=user, css=url('show_user.css'),
                           img=url(f'{user_id}.png', _type='img/users/hometown'))


if __name__ == '__main__':
    app.config['SECRET_KEY'] = '1234'
    app.register_blueprint(users_api.user_blueprint)
    app.register_blueprint(jobs_api.jobs_blueprint)
    rest.add_resource(JobsResourse, '/api/v1.0' + "/jobs/<int:user_id>")
    rest.add_resource(JobsListResourse, '/api/v1.0' + "/jobs")
    app.run()
