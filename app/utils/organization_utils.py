from app.models import Organization, User


class OrganizationUtils:
    def create_organization(self, data):
        new_organization = Organization(
            name=data.get('name'),
            description=data.get('description', None)
        )

        return new_organization
    
    