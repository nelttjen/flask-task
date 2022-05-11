from data import db_session
from data.jobs import Jobs
from data.users import User


def create_users():
    capt = User(
        surname='Scott',
        name='Ridley',
        age=21,
        position='captain',
        speciality='research engineer',
        address='module_1',
        email='scott_chief@mars.org'
    )

    colonist1 = User(
        surname='Smith',
        name='Riddle',
        age=24,
        position='colonist',
        speciality='engineer',
        address='module_2',
        email=f'Smith_Riddle@mars.org'
    )
    colonist2 = User(
        surname='Fabian',
        name='Ratter',
        age=19,
        position='colonist',
        speciality='pilot',
        address='module_2',
        email=f'Fabian_Ratter@mars.org'
    )
    colonist3 = User(
        surname='Alphie',
        name='Lockwood',
        age=27,
        position='colonist',
        speciality='scientist',
        address='module_2',
        email=f'Alphie_Lockwood@mars.org'
    )
    sess = db_session.create_session()
    [sess.add(i) for i in [capt, colonist1, colonist2, colonist3]]
    sess.commit()


def add_job():
    job = Jobs(
        team_leader=1,
        job='deployment of residential modules 1 and 2',
        work_size=15,
        collaborators='2, 3',
        is_finished=False
    )
    job2 = Jobs(
        team_leader=2,
        job='j2',
        work_size=15,
        collaborators='2, 3, 5, 2',
        is_finished=False
    )
    job3 = Jobs(
        team_leader=3,
        job='j3',
        work_size=15,
        collaborators='2, 3, 5',
        is_finished=False
    )
    job4 = Jobs(
        team_leader=4,
        job='j4',
        work_size=15,
        collaborators='2, 3, 5, 5',
        is_finished=False
    )
    sess = db_session.create_session()
    [sess.add(i) for i in [job, job2, job3, job4]]
    sess.commit()