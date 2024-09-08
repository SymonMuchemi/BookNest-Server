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
    return "Hello from the members side"


@members_bp.route('/create', methods=['POST'])
def create_member():
    try:
        member_data = request.json
        
        member_schema = MemberSchema(**member_data)
        
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
