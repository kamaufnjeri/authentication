from app.models import User
from app import bcrypt

class UserUtils:
    def create_user(self, data):
        password_hash = bcrypt.generate_password_hash(data.get('password')).decode('utf-8')
        new_user = User(
            firstName=data.get('firstName'),
            lastName=data.get('lastName'),
            email=data.get('email'),
            password=password_hash,
            phone=data.get('phone', None)  # phone can be None if not provided in data
        )
        return new_user

    def get_user_by_email(self, email):
        if email is not None:
            email_user = User.query.filter_by(email=email).first()
            if email_user:
                return email_user
        return None

    def validate_data(self, data):
        errors = []
        fields = ['firstName', 'lastName', 'email', 'password']

        for field in fields:
            if not data.get(field):
                errors.append({'field': field, "message": f"{field} is required"})
        
        email_user = self.get_user_by_email(data.get('email'))
        if email_user:
            errors.append({'field': 'email', "message": f"User with email {email_user.email} already exists"})
        
        return errors
    
    def login_user(self, data):
        errors = []
        fields = ['email', 'password']

        for field in fields:
            if not data.get(field):
                errors.append({'field': field, "message": f"{field} is required"})

        if errors:
            return errors, 422
        
        user = self.get_user_by_email(data.get('email'))

        if user:
            if bcrypt.check_password_hash(user.password, data.get('password')):
                return user, 200  # Return user object or token here
            else:
                errors.append({'field': 'password', "message": 'Incorrect password'})
                return errors, 401
        else:
            errors.append({'field': 'email', "message": f"User with email {data.get('email')} doesn't exist"})
            return errors, 401


    def check_users_share_same_organizations(self, current_user_id, user_to_check_id):
        user = User.query.filter_by(id=current_user_id).first()
        if user:
            for org in user.organizations:
                for user in org.users:
                    if user.id == user_to_check_id:
                        return user.to_dict()
        return None
    
    def get_user_organizations(self, user):
        if user:
            return [org.to_dict() for org in user.organizations]
        return []

