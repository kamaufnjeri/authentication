from app import db
import uuid


class Organization(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))

    def to_dict(self):
        org_dict = {}

        org_dict['orgId'] = self.id
        org_dict['name'] = self.name
        org_dict['description'] = self.description

        return org_dict