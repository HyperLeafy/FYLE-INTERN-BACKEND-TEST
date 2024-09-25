from flask import Blueprint, request
from core import db
import json
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment

from .schema import AssignmentSchema, AssignmentGradeSchema
teacher_assignments_resources = Blueprint('teacher_assignments_resources', __name__)


@teacher_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    """Returns list of assignments then filter that list based on which teacher has requsted it"""
    teacher_id = p.teacher_id
    # teachers_assignments = Assignment.get_assignments_by_teacher()
    teachers_assignments = Assignment.query.filter_by(teacher_id=teacher_id).all()

    teachers_assignments_dump = AssignmentSchema().dump(teachers_assignments, many=True)
    return APIResponse.respond(data=teachers_assignments_dump)


@teacher_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment(p, incoming_payload):
    """Grade an assignment"""
    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)
    std_id = grade_assignment_payload.id
    
    #To check if the assingment exist
    assingment_handler = Assignment.get_by_id(std_id)
    if assingment_handler == None:
        error_data = {
            'error': 'FyleError'
        }
        return  error_data, 404
    
    #To check if the assignment belongs to the same teacher
    if p.teacher_id != assingment_handler.teacher_id:
        error_data = {
            'error': 'FyleError'
        }
        return  error_data, 400 
    
    graded_assignment = Assignment.mark_grade(
        _id=grade_assignment_payload.id,
        grade=grade_assignment_payload.grade,
        auth_principal=p
    )
    db.session.commit()
    graded_assignment_dump = AssignmentSchema().dump(graded_assignment)
    return APIResponse.respond(data=graded_assignment_dump)
