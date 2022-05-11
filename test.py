import requests

if requests.get('http://127.0.0.1:5000/api/jobs').json()['message'] == 'OK':
    print('Test 1 passed')
else:
    print('Test 1 Failed')

if requests.get('http://127.0.0.1:5000/api/jobs/1').json()['message'] == 'OK':
    print('Test 2 passed')
else:
    print('Test 2 Failed')

if requests.get('http://127.0.0.1:5000/api/jobs/-1').json()['message'] == 'Not found':
    print('Test 3 passed')
else:
    print('Test 3 Failed')

if requests.get('http://127.0.0.1:5000/api/jobs/fsdfs').json()['message'] == 'id must be Integer':
    print('Test 4 passed')
else:
    print('Test 4 Failed')

# Не хватает нужных полей в запросе
if requests.post('http://127.0.0.1:5000/api/jobs', json={
    'title': '123'
}).json()['message'] == 'json must contains next fields: team_leader, ' \
                        'job, work_size, is_finished or team leader not found':
    print('Test 5 passed')
else:
    print('Test 5 failed')

# team leader и work size не int
if requests.post('http://127.0.0.1:5000/api/jobs', json={
    'team_leader': 'sdf',
    'job': 'test post',
    'work_size': 'sda',
    'is_finished': 'sasdf'
}).json()['message'] == 'id, team_leader and work_size fields must be integer':
    print('Test 6 passed')
else:
    print('Test 6 failed')

# id уже есть
if requests.post('http://127.0.0.1:5000/api/jobs', json={
    'id': 1,
    'team_leader': '1',
    'job': 'test post',
    'work_size': '1',
    'is_finished': 'sasdf'
}).json()['message'] == 'id already exists':
    print('Test 7 passed')
else:
    print('Test 7 failed')

requests.post('http://127.0.0.1:5000/api/jobs', json={
    'id': 999,
    'team_leader': '1',
    'job': 'test delete',
    'work_size': '1',
    'is_finished': 1
})
test_before = requests.get('http://127.0.0.1:5000/api/jobs').json()['response']
requests.delete('http://127.0.0.1:5000/api/jobs', json={'id': 999})
test_after = requests.get('http://127.0.0.1:5000/api/jobs').json()['response']
if test_before != test_after:
    print('Test 8 passed')
else:
    print('Test 8 failed')


if requests.delete('http://127.0.0.1:5000/api/jobs', json={'id': 'dasfs'}).json()['message'] == 'id must be int':
    print('Test 9 passed')
else:
    print('Test 9 failed')


if requests.delete('http://127.0.0.1:5000/api/jobs', json={'id': -1000}).json()['message'] == 'job not found':
    print('Test 10 passed')
else:
    print('Test 10 failed')


requests.post('http://127.0.0.1:5000/api/jobs', json={
    'id': 999,
    'team_leader': '1',
    'job': 'test delete',
    'work_size': '1',
    'is_finished': 1
})
test_before = requests.get('http://127.0.0.1:5000/api/jobs').json()['response']
requests.put('http://127.0.0.1:5000/api/jobs', json={
    'id': 999,
    'job': '123asd11',
    'collaborators': '2, 5, 7'
})
test_after = requests.get('http://127.0.0.1:5000/api/jobs').json()['response']
if test_before != test_after:
    print('Test 11 passed')
else:
    print('Test 11 failed')
requests.delete('http://127.0.0.1:5000/api/jobs', json={'id': 999})


if requests.put('http://127.0.0.1:5000/api/jobs', json={
    'id': 'asdf',
    'job': '123asd11',
    'collaborators': '2, 5, 7'
}).json()['message'] == 'work not found':
    print('Test 12 passed')
else:
    print('Test 12 failed')

if requests.put('http://127.0.0.1:5000/api/jobs', json={
    'id': 2,
    'work_size': 'asdf',
    'job': '123asd11',
    'collaborators': '2, 5, 7'
}).json()['message'] == 'team_leader and work_size fields must be Integer':
    print('Test 13 passed')
else:
    print('Test 13 failed')


requests.post('http://127.0.0.1:5000/api/v1.0/jobs/999', json={
    'team_leader': '1',
    'job': 'test delete',
    'work_size': '1',
    'is_finished': 1
})
test_before = requests.get('http://127.0.0.1:5000/api/v1.0/jobs').json()['response']
requests.put('http://127.0.0.1:5000/api/v1.0/jobs/999', json={
    'job': '123asd11',
    'collaborators': '2, 5, 7'
})
test_after = requests.get('http://127.0.0.1:5000/api/v1.0/jobs').json()['response']
if test_before != test_after:
    print('Test 14 passed')
else:
    print('Test 14 failed')
requests.delete('http://127.0.0.1:5000/api/v1.0/jobs/999')

if requests.put('http://127.0.0.1:5000/api/v1.0/jobs/1234', json={
    'job': '123asd11',
    'collaborators': '2, 5, 7'
}).json()['message'] == 'work not found':
    print('Test 15 passed')
else:
    print('Test 12 failed')

if requests.put('http://127.0.0.1:5000/api/jobs/2', json={
    'work_size': 'asdf',
    'job': '123asd11',
    'collaborators': '2, 5, 7'
}).json()['message'] == 'team_leader and work_size fields must be Integer':
    print('Test 16 passed')
else:
    print('Test 16 failed')