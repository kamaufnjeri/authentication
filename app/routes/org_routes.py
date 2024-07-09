from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils import UserUtils, OrganizationUtils
from app.models import User, Organization
from app import db

org_bp = Blueprint('org_bp', __name__, url_prefix='/api/organisations')
user_utils = UserUtils()
org_utils = OrganizationUtils()

@org_bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_user_organizations():
    try:
        current_user_id = get_jwt_identity()
        
        current_user = User.query.filter_by(id=current_user_id).first()

        if not current_user:
            return jsonify({
                "status": "Bad Request",
                "message": "User not found",
                "statusCode": 400
            }), 400


        user_orgs = user_utils.get_user_organizations(current_user)

        if not user_orgs:
            return jsonify({
                "status": "Bad Request",
                "message": "User organisations not found",
                "statusCode": 400
            }), 400

        return jsonify({
            "status": "success",
		    "message": "User organisations retrieved successfully",
            "data": {
                "organisations": user_orgs
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "Bad Request",
            "message": "Client error",
            "statusCode": 400
        }), 400


@org_bp.route('/<string:orgId>', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_organization(orgId):
    try:
        current_user_id = get_jwt_identity()
        
        current_user = User.query.filter_by(id=current_user_id).first()

        if not current_user:
            return jsonify({
                "status": "Bad Request",
                "message": "Current user not found",
                "statusCode": 400
            }), 400

        user_orgs = user_utils.get_user_organizations(current_user)

        if not user_orgs:
             return jsonify({
                "status": "Bad Request",
                "message": "User organisations not found",
                "statusCode": 400
            }), 400
        
        org = Organization.query.filter_by(id=orgId).first()

        if not org:
            return jsonify({
                "status": "Bad Request",
                "message": "Organisation not found",
                "statusCode": 400
            }), 400
        
        for org in user_orgs:
            if org.get('orgId') == orgId:
                return jsonify({
                    "status": "success",
                    "message": "Organisation retrieved successfully",
                    "data": org
                }), 200
            
        return jsonify({
            "status": "Bad Request",
            "message": "Can't access this organisation's information",
            "statusCode": 400
        }), 400

    except Exception as e:
        return jsonify({
            "status": "Bad Request",
            "message": "Client error",
            "statusCode": 400
        }), 400



@org_bp.route('/', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_organization():
    try:
        current_user_id = get_jwt_identity()

        current_user = User.query.filter_by(id=current_user_id).first()
        
        data = request.get_json()

        if not data.get('name') or not current_user:
            return jsonify({
                "status": "Bad Request",
                "message": "name is required",
                "statusCode": 400,
            }), 400
        
        new_organization = org_utils.create_organization(data)

        db.session.add(new_organization)
        current_user.organizations.append(new_organization)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Organisation created successfully",
            "data": new_organization.to_dict()
        }), 201


    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "Bad Request",
            "message": "Client error",
            "statusCode": 400
        }), 400


@org_bp.route('/<string:orgId>/users', methods=['POST'], strict_slashes=False)
@jwt_required()
def add_user_to_organization(orgId):
    try:
        current_user_id = get_jwt_identity()

        data = request.get_json()

        user_id = data.get('userId')

        if not user_id:
            return jsonify({
                "status": "Bad Request",
                "message": "User ID is required",
                "statusCode": 400
            }), 400
        
        current_user = User.query.filter_by(id=current_user_id).first()

        user_to_add = User.query.filter_by(id=user_id).first()

        if not current_user:
            return jsonify({
                "status": "Bad Request",
                "message": "Current user not found",
                "statusCode": 400
            }), 400

        if not user_to_add:
            return jsonify({
                "status": "Bad Request",
                "message": "User not found",
                "statusCode": 400
            }), 400

        org = Organization.query.filter_by(id=orgId).first()

        if not org:
            return jsonify({
                "status": "Bad Request",
                "message": "Organisation not found",
                "statusCode": 400
            }), 400
        

        user_to_add_orgs = user_utils.get_user_organizations(user=user_to_add)

        for org in user_to_add_orgs:
            if org.get('orgId') == orgId:
                return jsonify({
                    "status": "Bad Request",
                    "message": "User already in organisation",
                    "statusCode": 400
                }), 400

        current_user_orgs = user_utils.get_user_organizations(user=current_user)

        for organization in current_user_orgs:
            if organization.get('orgId') == orgId:
                org = Organization.query.filter_by(id=orgId).first()

                org.users.append(user_to_add)
                db.session.commit()
                return jsonify({
                    "status": "success",
                    "message": "User added to organisation successfully",
                }), 200
            
        return jsonify({
            "status": "Bad Request",
            "message": "You cannot add user to organisation",
            "statusCode": 400
        }), 400
                        

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "Bad Request",
            "message": "Client error",
            "statusCode": 400
        }), 400
    