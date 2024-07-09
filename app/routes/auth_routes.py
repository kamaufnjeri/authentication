from flask import Blueprint, jsonify, request
from app.utils import OrganizationUtils, UserUtils
from app import db
from flask_jwt_extended import create_access_token


auth_bp = Blueprint("auth_bp", __name__, url_prefix='/auth', strict_slashes=False)


org_utils = OrganizationUtils()
user_utils = UserUtils()


@auth_bp.route('/register', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        errors = user_utils.validate_data(data)


        if errors:
            return jsonify({
                "errors": errors
            }), 422
        
        new_user = user_utils.create_user(data)
        db.session.add(new_user)

        if new_user.firstName[-1] == 's':
            organization_name = f"{new_user.firstName}' Organisation"
        else:
            organization_name = f"{new_user.firstName}'s Organisation"

        organization_data = {"name": organization_name}
        new_organization = org_utils.create_organization(organization_data)
        db.session.add(new_organization)
        new_user.organizations.append(new_organization)
        db.session.commit()
        
        accessToken = create_access_token(identity=new_user.id)

        return jsonify({
            "status": "success",
            "message": "Registration successful",
            "data": {
                "accessToken": accessToken,
                "user": new_user.to_dict()
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "Bad request",
            "message": "Registration unsuccessful",
            "statusCode": 400
        }), 400
    

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        info, code = user_utils.login_user(data)

        if code != 200:
            if code == 422:
                return jsonify({
                    "errors": info
                }), code
            
            if code == 401:
                return jsonify({
                    "status": "Bad request",
                    "message": "Authentication failed",
                    "statusCode": code,
                }), code

        user = info
        accessToken = create_access_token(identity=user.id)
        return jsonify({
            "status": "success",
            "message": "Login successful",
            "data": {
                "accessToken": accessToken,
                "user": user.to_dict()
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "Bad request",
            "message": "Authentication failed",
            "statusCode": 401
        }), 401