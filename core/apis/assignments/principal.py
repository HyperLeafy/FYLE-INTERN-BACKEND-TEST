from flask import Blueprint, jsonify
from core import db
from core.apis import decorators
from core.models.assignments import Assignment,AssignmentStateEnum
from core.models.teachers import Teacher
from core.apis.responses import APIResponse
from .schema import AssignmentSchema, TeacherSchema, AssignmentGradeSchema


# Blueprint for principle api
principal_assignment_resources = Blueprint('principal_assignment_resources',__name__)

@principal_assignment_resources.route('/assignments', methods=['GET'], strict_slashes = False)
@decorators.authenticate_principal
def list_assignment(p):
    try :
        # Returns only those assingmnt that have been graded
        graded_assingments = Assignment.filter(Assignment.state.in_(
        [AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED])).all()
        graded_assingments_dump = AssignmentSchema().dump(graded_assingments, many=True)
        
        return APIResponse.respond(data=graded_assingments_dump), 200 # currently returning and empty data dictionary
    
    except Exception as e:
        error_data = {
            'status': 'error',
            'message': str(e)
        }
        return APIResponse.respond(data=error_data), 500
    
    
    
@principal_assignment_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def update_assignment_grade(p, incoming_payload):
    try:
        # **Validate Required Fields**
        if 'id' not in incoming_payload or 'grade' not in incoming_payload:  # Check for missing fields
            error_Data = {
                "status": "error",
                "message": "Missing required fields: 'id' and 'grade'"  # Provide meaningful error message
            }
            return APIResponse.respond(data=error_Data), 400  # Return 400 for bad request
        
        grade_payload = AssignmentGradeSchema().load(incoming_payload)
        print(grade_payload)
        
        graded_assignment = Assignment.mark_grade(
            _id=grade_payload.id,
            grade=grade_payload.grade,
            auth_principal=p 
        )
        db.session.commit()
        graded_assignment_dump = AssignmentSchema().dump(graded_assignment)

        return APIResponse.respond(data=graded_assignment_dump), 200
        
    except Exception as e:
        error_Data = {
            "status": "error",
            'message': str(e)
        }
        
        return APIResponse.respond(data=error_Data), 500

    


@principal_assignment_resources.route('/teachers', methods=['GET'], strict_slashes = False)
@decorators.authenticate_principal
def list_teachers(p):
    try:
        list_of_teachers = Teacher.query.all()
        list_of_teachers_dump = TeacherSchema().dump(list_of_teachers, many=True)
        return APIResponse.respond(list_of_teachers_dump), 200
    
    except Exception as e:
        error_data = {
            'status': 'error',
            'message': str(e)
        }
        return APIResponse.respond(data=error_data),500

    

