def test_get_assignments_teacher_1(client, h_teacher_1):
    response = client.get(
        '/teacher/assignments',
        headers=h_teacher_1
    )

    assert response.status_code == 200

    data = response.json['data']
    assert len(data) > 0  
    for assignment in data:
        assert assignment['teacher_id'] == 1  
        assert 'state' in assignment 


def test_get_assignments_teacher_2(client, h_teacher_2):
    response = client.get(
        '/teacher/assignments',
        headers = h_teacher_2
    )

    assert response.status_code == 200

    data = response.json['data']
    assert len(data) > 0
    for assignment in data:
        assert assignment['teacher_id'] == 2
        assert 'content' in assignment
        assert 'state' in assignment


def test_grade_assignment_success(client, h_teacher_1):
    """
    success case: teacher 1 grades assignment 1 successfully
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 1, 
            "grade": "A"
        }
    )

    assert response.status_code == 200

    data = response.json['data']
    assert data['grade'] == 'A' 
    assert data['teacher_id'] == 1  
    assert data['state'] == 'GRADED' 


def test_grade_assignment_cross(client, h_teacher_2):
    """
    failure case: assignment 1 belongs to teacher 1, not teacher 2
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_2,
        json={
            "id": 1,
            "grade": "A"
        }
    )

    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'FyleError'
    assert 'error' in data  
    assert 'message' not in data 


def test_grade_assignment_invalid_grade(client, h_teacher_1):
    """
    failure case: API should allow only valid grades from enum
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 1,
            "grade": "AB"  
        }
    )

    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'ValidationError' 
    assert 'grade' in data['message'] 


def test_grade_assignment_nonexistent(client, h_teacher_1):
    """
    failure case: non-existent assignment
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 100000, 
            "grade": "A"
        }
    )

    assert response.status_code == 404
    data = response.json
    assert data['error'] == 'FyleError'
    assert 'message' not in data


def test_grade_assignment_draft(client, h_teacher_1):
    """
    failure case: only a submitted assignment can be graded, not draft
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 2,  
            "grade": "A"
        }
    )

    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'FyleError'


def test_grade_assignment_empty_body(client, h_teacher_1):
    """
    failure case: empty body for grading assignment
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={}  
    )

    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'ValidationError'
    assert 'id' in data['message']  
    assert 'grade' in data['message'] 


def test_grade_assignment_no_grade(client, h_teacher_1):
    """
    failure case: missing grade field in request
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 1 
        }
    )

    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'ValidationError'
    assert 'grade' in data['message']  
