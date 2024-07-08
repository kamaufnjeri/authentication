from app import db
import uuid


user_organization = db.Table('user_organization',
    db.Column('user_id', db.String(36), db.ForeignKey('user.id'), primary_key=True),
    db.Column('organization_id', db.String(36), db.ForeignKey('organization.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True)
    firstName = db.Column(db.String(255), nullable=False)
    lastName = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(255))
    organizations = db.relationship('Organization', secondary=user_organization, backref='users', lazy='dynamic')

    def to_dict(self):
        user_dict = {}
        user_dict['userId'] = self.id
        user_dict['firstName'] = self.firstName
        user_dict['lastName'] = self.lastName
        user_dict['email'] = self.email
        user_dict['phone'] = self.phone

        return user_dict
    
    def get_user_organizations(self):
        user_organizations = []

        for organization in self.organizations:
            organization_users = []

            for user in organization.users():
                organization_users.append(user.to_dict())
            user_organizations.append({
                "organizationName": organization.name,
                "users": organization_users
            })
        return user_organizations
        
        
            