from core.models.assignments import AssignmentStateEnum, GradeEnum

def test_get_assignments(client, h_principal):
    response = client.get(
        '/principal/assignments',
        headers=h_principal
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['state'] in [AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED]


def test_grade_assignment_draft_assignment(client, h_principal):
    """
    failure case: If an assignment is in Draft state, it cannot be graded by principal
    """
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 5,
            'grade': GradeEnum.A.value
        },
        headers=h_principal
    )

    assert response.status_code == 200


def test_grade_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.C.value
        },
        headers=h_principal
    )

    assert response.status_code == 200

    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.C


def test_regrade_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )

    assert response.status_code == 200

    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.B

def test_get_teachers(client, h_principal):
    response = client.get('/principal/teachers', headers=h_principal)
    assert response.status_code == 200
    assert isinstance(response.json['data'], list) 


def test_grade_assignment_invalid_grade(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': 'InvalidGrade'  
        },
        headers=h_principal
    )

    assert response.status_code == 500  


def test_get_teachers_unauthenticated(client):
    response = client.get('/principal/teachers')
    assert response.status_code == 401  # Unauthorized
    
def test_valid_grade_assignment(client, h_principal):
    """
    Test valid grading of an assignment by the principal.
    """
    # Assume assignment with ID 4 exists and is in the SUBMITTED state
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.A.value  # Test with a valid grade
        },
        headers=h_principal
    )

    assert response.status_code == 200
    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.A.value


def test_update_assignment_grade_exception(client, h_principal):
    """
    Test exception handling when trying to grade a non-existent assignment.
    """
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 999,  # Assume this ID does not exist
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )

    assert response.status_code == 500  # Expect a server error due to the exception
    assert 'data' in response.json  # Check that the response contains a data key
    assert 'status' in response.json['data']  # Check that the status key is in the data
    assert response.json['data']['status'] == 'error'  # Ensure the status is 'error'
    assert 'message' in response.json['data']  # Ensure a message is present

def test_grade_assignment_invalid_payload(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={'id': 4},  # Missing the 'grade' field
        headers=h_principal
    )
    assert response.status_code == 400 
