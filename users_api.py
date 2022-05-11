from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash

from data import db_session
from data.users import User


API_ROUTE = '/api/'

user_blueprint = Blueprint(
    'user_api',
    __name__,
    template_folder='templates'
)


@user_blueprint.route(f'{API_ROUTE}/users')
def get_users():
    sess = db_session.create_session()
    return jsonify({'response': [user.to_dict() for user in sess.query(User).all()], 'message': 'OK'})


@user_blueprint.route(f'{API_ROUTE}/users/<string:user>')
def get_job(user):
    sess = db_session.create_session()
    try:
        user = int(user)
    except ValueError:
        return jsonify({'response': None, 'message': 'id must be Integer'})
    _user = sess.query(User).get(user)
    if not _user:
        return jsonify({'response': None, 'message': 'Not found'})
    return jsonify({'response': _user.to_dict(), 'message': 'OK'})


@user_blueprint.route(f'{API_ROUTE}/users', methods=['POST'])
def add_job():
    class IdException(BaseException):
        pass
    json = request.json
    _id = json.get('id')
    surname = json.get('surname')
    name = json.get('name')
    age = json.get('age')
    position = json.get('position')
    speciality = json.get('speciality')
    address = json.get('address')
    city_from = json.get('sity_from')
    email = json.get('email')
    password = json.get('password')
    try:
        sess = db_session.create_session()
        assert all([surname, name, age, position, speciality, address, city_from, email, password])
        assert int(age > 0)
        if _id is not None:
            if sess.query(User).get(int(_id)):
                raise IdException
        if _id is not None and int(_id) > 0:
            _new = User(
                id=_id,
                surname=surname,
                name=name,
                age=int(age),
                position=position,
                speciality=speciality,
                address=address,
                city_from=city_from,
                email=email,
                hashed_password=generate_password_hash(password)
            )
        else:
            _new = User(
                surname=surname,
                name=name,
                age=int(age),
                position=position,
                speciality=speciality,
                address=address,
                city_from=city_from,
                email=email,
                hashed_password=generate_password_hash(password)
            )
        sess.add(_new)
        sess.commit()
        return jsonify({'message': 'OK'})
    except AssertionError:
        return jsonify({'message': 'json must contains next fields: '
                                   'surname, name, age, position, speciality, address, email, password'})
    except ValueError:
        return jsonify({'message': 'id and age fields must be integer'})
    except IdException:
        return jsonify({'message': 'id already exists'})
    except Exception as e:
        return jsonify({'message': e.__str__()})


@user_blueprint.route(f'{API_ROUTE}/users', methods=['PUT'])
def edit_job():
    sess = db_session.create_session()
    json = request.json
    _id = json.get('id')
    surname = json.get('surname')
    name = json.get('name')
    age = json.get('age')
    position = json.get('position')
    speciality = json.get('speciality')
    address = json.get('address')
    city_from = json.get('city_from')
    email = json.get('email')
    password = json.get('password')
    if _id is None:
        return jsonify({'message': 'id required'})
    try:
        user = sess.query(User).get(int(_id))
        if not user:
            return jsonify({'message': 'user not found'})
        if surname:
            user.surname = surname
        if name:
            user.name = name
        if age and int(age) > 0:
            user.age = age
        if position:
            user.position = position
        if speciality:
            user.speciality = speciality
        if address:
            user.address = address
        if city_from:
            user.city_from = city_from
        if email:
            user.email = email
        if password:
            user.hashed_password = generate_password_hash(password)
        sess.commit()
        return jsonify({'message': 'OK'})
    except ValueError:
        return jsonify({'message': 'id and age fields must be Integer'})


@user_blueprint.route(f'{API_ROUTE}/users', methods=['DELETE'])
def delete_job():
    _id = request.json.get('id')
    if _id is None:
        return jsonify({'message': 'id required'})
    try:
        sess = db_session.create_session()
        user = sess.query(User).get(int(_id))
        assert user
        sess.delete(user)
        sess.commit()
        return jsonify({'message': 'OK'})
    except AssertionError:
        return jsonify({'message': 'user not found'})
    except ValueError:
        return jsonify({'message': 'id must be int'})