import requests
from flask import jsonify, request
from flask_restful import abort, Resource
from data import db_session
from data.jobs import Jobs


def abort_if_not_found(job_id):
    session = db_session.create_session()
    user = session.query(Jobs).get(job_id)
    if not user:
        abort(404, message=f'Job not found')


class JobsResourse(Resource):
    def get(self, job_id):
        abort_if_not_found(job_id)
        session = db_session.create_session()
        job = session.query(Jobs).get(job_id)
        return jsonify({'response': job.to_dict(), 'message': 'OK'})

    def post(self, job_id):
        json = request.get_json()
        json['id'] = job_id
        try:
            resp = requests.post('http://127.0.0.1:5000/api/jobs', json=json)
            return jsonify(resp.json())
        except Exception as e:
            return jsonify({'message': e.__str__()})

    def put(self, job_id):
        json = request.get_json()
        json['id'] = job_id
        try:
            resp = requests.put('http://127.0.0.1:5000/api/jobs', json=json)
            return jsonify(resp.json())
        except Exception as e:
            return jsonify({'message': e.__str__()})

    def delete(self, job_id):
        abort_if_not_found(job_id)
        session = db_session.create_session()
        job = session.query(Jobs).get(job_id)
        session.delete(job)
        session.commit()
        return jsonify({'success': 'OK'})


class JobsListResourse(Resource):
    def get(self):
        session = db_session.create_session()
        jobs = session.query(Jobs).all()
        return jsonify({'response': [job.to_dict() for job in jobs], 'message': 'OK'})