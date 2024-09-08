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


@members_bp.route('/get_by_id/<int:member_id>')
def get_member_by_id(member_id):
    """Get member object using id.

    Args:
        member_id (int): The id of the member.

    Returns:
        dict: Response dictionary
    """
    member = Member.query.get(member_id)

    if member is None:
        return members_error_dict, 400

    return jsonify({
        'id': member.id,
        'name': member.name,
        'debt': member.debt
    }), 200


@members_bp.route('/get_members')
def get_members():
    """Gets members in pages.

    Returns:
        dict: Pagination object with data as list.
    """
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    members = Member.query.paginate(page=page, per_page=per_page)

    total_pages = ceil(members.total / per_page)

    members_list = [{
        'id': member.id,
        'name': member.name,
        'debt': member.debt
    } for member in members]

    return jsonify({
        'total_members': members.total,
        'total_pages': total_pages,
        'pages': members.pages,
        'current_page': page,
        'members': members_list,
        'per_page': per_page,
        'has_next': members.has_next,
        'has_prev': members.has_prev,
        'next_page': members.next_num if members.has_next else None,
        'prev_page': members.prev_num if members.has_prev else None
    }), 200


@members_bp.route('/delete/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    """Deletes a member from the database.

    Args:
        member_id (int): The Id of the member.

    Returns:
        dict: Response dictionary
    """
    member = Member.query.get(member_id)

    if member is None:
        return members_error_dict, 400

    db.session.delete(member)
    db.session.commit()

    return jsonify({
        'Message': 'Member deleted succesfully!'
    }), 200
