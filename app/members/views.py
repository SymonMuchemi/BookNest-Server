from app import db
from app.members import members_bp
from flask import request, jsonify
from ..schema import MemberSchema
from ..models import Member

from math import ceil
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

members_error_dict = {
    'Error': 'Could not find member!'
}


@members_bp.route('/hello')
def hello():
    """Returns a string.

    Returns:
        str: Welcome string.
    """
    return "Hello from the members side"


@members_bp.route('/create', methods=['POST'])
def create_member():
    """Creates a member object and saves to database.

    Returns:
        dict: Response message.
    """
    try:
        member = request.json
        
        member_schema = MemberSchema(**member)
        
        member = Member(
            name = member_schema.name,
            debt = member_schema.debt
        )

        db.session.add(member)
        db.session.commit()
        
        return jsonify({
            'Message': 'Member created succesfully',
            'Member': member_schema.model_dump()
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'Error': 'Validation failed',
            'Details': e.errors()
        }), 400
    
    except IntegrityError as e:
        return jsonify({
            'Error': 'Name already exists',
        })


@members_bp.route('/update/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    """Updates a member object.

    Args:
        member_id (int): Id of the member object.

    Returns:
        dict: Response message.
    """
    member_data = request.json

    member = Member.query.get(member_id)
    
    if member is None:
        return members_error_dict, 400
    
    try:
        member_schema = MemberSchema(**member_data)
        
        member.name = member_schema.name
        member.debt = member_schema.debt
        
        db.session.commit()
        
        return jsonify({
            'Message': "Member updated successfully!",
            'New member': member_schema.model_dump()
        })
        

    except ValidationError as e:
        return jsonify({
            'Error': 'Cannot update member',
            'Details': e.errors()
        })
