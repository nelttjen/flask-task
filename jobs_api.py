from flask import Blueprint, jsonify, request

from data import db_session
from data.jobs import Jobs
from data.users import User

API_ROUTE = '/api/'

jobs_blueprint = Blueprint(
    'jobs_api',
    __name__,
    template_folder='templates'
)


class IdException(BaseException):
    pass


@jobs_blueprint.route(f'{API_ROUTE}/jobs')
def get_jobs():
    sess = db_session.create_session()
    return jsonify({'response': [job.to_dict() for job in sess.query(Jobs).all()], 'message': 'OK'})


@jobs_blueprint.route(f'{API_ROUTE}/jobs/<string:job>')
def get_job(job):
    sess = db_session.create_session()
    try:
        job = int(job)
    except ValueError:
        return jsonify({'response': None, 'message': 'id must be Integer'})
    _job = sess.query(Jobs).get(job)
    if not _job:
        return jsonify({'response': None, 'message': 'Not found'})
    return jsonify({'response': _job.to_dict(), 'message': 'OK'})


@jobs_blueprint.route(f'{API_ROUTE}/jobs', methods=['POST'])
def add_job():
    json = request.json
    _id = json.get('id')
    team_leader = json.get('team_leader')
    job = json.get('job')
    work_size = json.get('work_size')
    collaborators = json.get('collaborators')
    hazard = json.get('hazard')
    is_finished = json.get('is_finished')
    try:
        sess = db_session.create_session()
        assert all([i is not None for i in [team_leader, job, work_size, is_finished]])
        if _id is not None:
            if sess.query(Jobs).get(int(_id)):
                raise IdException
        assert sess.query(User).get(int(team_leader))
        if _id is not None and int(_id) > 0:
            _new = Jobs(
                id=_id,
                team_leader=int(team_leader),
                job=job,
                work_size=int(work_size),
                collaborators=collaborators,
                hazard=hazard,
                is_finished=bool(is_finished)
            )
        else:
            _new = Jobs(
                team_leader=int(team_leader),
                job=job,
                work_size=int(work_size),
                collaborators=collaborators,
                hazard=hazard,
                is_finished=bool(is_finished)
            )
        sess.add(_new)
        sess.commit()
        return jsonify({'message': 'OK'})
    except AssertionError:
        return jsonify({'message': 'json must contains next fields: team_leader, job, work_size, is_finished '
                                   'or team leader not found'})
    except ValueError:
        return jsonify({'message': 'id, team_leader and work_size fields must be integer'})
    except IdException:
        return jsonify({'message': 'id already exists'})
    except Exception as e:
        return jsonify({'message': e.__str__()})


@jobs_blueprint.route(f'{API_ROUTE}/jobs', methods=['PUT'])
def edit_job():
    sess = db_session.create_session()
    json = request.json
    _id = json.get('id')
    team_leader = json.get('team_leader')
    job = json.get('job')
    work_size = json.get('work_size')
    collaborators = json.get('collaborators')
    hazard = json.get('hazard')
    is_finished = json.get('is_finished')
    if _id is None:
        return jsonify({'message': 'id required'})
    work = sess.query(Jobs).get(_id)
    if not work:
        return jsonify({'message': 'work not found'})
    try:
        if team_leader is not None:
            if not sess.query(User).get(int(team_leader)):
                return jsonify({'message': 'team leader not found'})
            else:
                work.team_leader = team_leader
        if job is not None:
            work.job = job
        if work_size is not None:
            work.work_size = int(work_size)
        if collaborators is not None:
            work.collaborators = collaborators
        if hazard is not None:
            work.hazard = hazard
        if is_finished is not None:
            work.is_finished = bool(is_finished)
        sess.commit()
        return jsonify({'message': 'OK'})
    except ValueError:
        return jsonify({'message': 'team_leader and work_size fields must be Integer'})


@jobs_blueprint.route(f'{API_ROUTE}/jobs', methods=['DELETE'])
def delete_job():
    _id = request.json.get('id')
    if _id is None:
        return jsonify({'message': 'id required'})
    try:
        sess = db_session.create_session()
        job = sess.query(Jobs).get(int(_id))
        assert job
        sess.delete(job)
        sess.commit()
        return jsonify({'message': 'OK'})
    except AssertionError:
        return jsonify({'message': 'job not found'})
    except ValueError:
        return jsonify({'message': 'id must be int'})