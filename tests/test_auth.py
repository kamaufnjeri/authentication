import unittest
import os
from app.app import create_app, db, TestingConfig
from dotenv import load_dotenv
from app.models import User, Organization
from flask_jwt_extended import decode_token
from datetime import datetime, timedelta

load_dotenv()

class TestAuthenticationAndOrganizations(unittest.TestCase):

    def setUp(self):
        self.init_app = create_app(TestingConfig)
        self.init_app.config['TESTING'] = True
        self.app = self.init_app.test_client()

        with self.init_app.app_context():
            db.drop_all()
            db.create_all()

        self.test_user = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "password": "password123",
            "phone": "+1234567890"
        }

        self.test_user_one = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john_one.doe@example.com",
            "password": "password123",
            "phone": "+1234567890"
        }

        self.test_user_two = {
            "firstName": "Jane",
            "lastName": "Doe",
            "email": "jane.doe@example.com",
            "password": "password1234",
            "phone": "+254780324930"
        }

        response_one = self.app.post('/auth/register', json=self.test_user_one)
        if response_one.status_code == 201:
            self.user_one_data = response_one.json.get('data')
            self.user_one_access_token = self.user_one_data['accessToken']
        else:
            self.fail(f"Failed to register user one: {response_one.status_code} - {response_one.json}")

        response_two = self.app.post('/auth/register', json=self.test_user_two)
        if response_two.status_code == 201:
            self.user_two_data = response_two.json.get('data')
            self.user_two_access_token = self.user_two_data['accessToken']
        else:
            self.fail(f"Failed to register user two: {response_two.status_code} - {response_two.json}")


    def tearDown(self):
        with self.init_app.app_context():
            db.session.remove()
            db.drop_all()

    def test_index_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'{"message":"Welcome to backend stage two task for the HNG Internship"}', response.data)

    def test_token_expiration_and_decoded_details(self):
        response = self.app.post('/auth/register', json=self.test_user)
        self.assertEqual(response.status_code, 201)
        data = response.json

        user_data = data.get('data')
        user_id = user_data.get('user').get('userId')
        token = user_data.get('accessToken')

        with self.init_app.app_context():
            try:
                decoded_token = decode_token(token)
                issued_at = datetime.fromtimestamp(decoded_token['iat'])
                expected_expiry = issued_at + timedelta(hours=1)
                exp_timestamp = decoded_token['exp']
                exp_datetime = datetime.fromtimestamp(exp_timestamp)
                token_identity = decoded_token['sub']

                self.assertEqual(expected_expiry, exp_datetime)
                self.assertEqual(token_identity, user_id)

            except Exception as e:
                self.fail(f"Token validation failed: {str(e)}")

    def test_get_user_organisation(self):
        """User one organisations with correct token"""
        response = self.app.get('/api/organisations', headers={'Authorization': f"Bearer {self.user_one_access_token}"}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        data = response.json.get('data')
        self.assertEqual(len(data['organisations']), 1)
        self.assertEqual(data['organisations'][0]['name'], "John's Organisation")

        """User two organisations with correct token"""
        response = self.app.get('/api/organisations', headers={'Authorization': f"Bearer {self.user_two_access_token}"}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        data_two = response.json.get('data')
        self.assertEqual(len(data_two['organisations']), 1)
        self.assertEqual(data_two['organisations'][0]['name'], "Jane's Organisation")

        """User one with user two token and user one organisation Id"""
        user_one_organization_id = data['organisations'][0]['orgId']
        response = self.app.get(
            f'/api/organisations/{user_one_organization_id}',
            headers={'Authorization': f"Bearer {self.user_two_access_token}"},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            {'message': "Can't access this organisation's information", 'status': 'Bad Request', 'statusCode': 400},
            response.json
        )

    def test_registration_successful(self):
        test_user = {
            "firstName": "test",
            "lastName": "user",
            "email": "testuser@gmail.com",
            "password": "testpassword"
        }
        
        response = self.app.post('/auth/register', json=test_user)
        data = response.json.get('data')
        self.assertEqual(response.status_code, 201)
        self.assertIn('accessToken', data)
        self.assertEqual(data.get('user').get('email'), test_user.get('email'))
        self.assertEqual(data.get('user').get('lastName'), test_user.get('lastName'))
        self.assertEqual(data.get('user').get('firstName'), test_user.get('firstName'))
        self.assertEqual(data.get('user').get('phone'), None)

        response = self.app.get(
            '/api/organisations',
            headers={'Authorization': f"Bearer {data.get('accessToken')}"},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        org_data= response.json.get('data')
        self.assertEqual(org_data['organisations'][0]['name'], "test's Organisation")

    def test_registration_missing_required_fields(self):
        test_user = {
            "firstName": "test",
            "lastName": "user",
            "email": "testuser@gmail.com",
        }
        
        response = self.app.post('/auth/register', json=test_user)
        data = response.json.get('errors')
        self.assertEqual(response.status_code, 422)
        self.assertEqual([{"field": "password", "message": "password is required"}], data)

        test_user1 = {
            "password": "test",
            "lastName": "user",
            "email": "testuser1@gmail.com",
        }
        
        response = self.app.post('/auth/register', json=test_user1)
        data = response.json.get('errors')
        self.assertEqual(response.status_code, 422)
        self.assertEqual([{"field": "firstName", "message": "firstName is required"}], data)

        test_user2 = {
            "firstName": "test",
            "password": "user",
            "email": "john_one.doe@gmail.com",
        }
        
        response = self.app.post('/auth/register', json=test_user2)
        data = response.json.get('errors')
        self.assertEqual(response.status_code, 422)
        self.assertEqual([{"field": "lastName", "message": "lastName is required"}], data)

        test_user3 = {
            "firstName": "test",
            "lastName": "user",
            "password": "test.com",
        }
        
        response = self.app.post('/auth/register', json=test_user3)
        data = response.json.get('errors')
        self.assertEqual(response.status_code, 422)
        self.assertEqual([{"field": "email", "message": "email is required"}], data)

    def test_register_duplicate_emails(self):
        test_user = {
            "firstName": "test",
            "lastName": "user",
            "email": "testuser@gmail.com",
            "password": "testpassword"
        }
        
        response = self.app.post('/auth/register', json=test_user)
        data = response.json.get('data')
        self.assertEqual(response.status_code, 201)

        test_user1 = {
            "firstName": "test",
            "lastName": "user",
            "email": "testuser@gmail.com",
            "password": "testpassword"
        }

        response = self.app.post('/auth/register', json=test_user1)
        data = response.json.get('errors')
        self.assertEqual(response.status_code, 422)
        self.assertEqual([{"field": "email", "message": f"User with email {test_user1.get('email')} already exists"}], data)


    def test_login_successful(self):
        test_user = {
            "firstName": "test",
            "lastName": "user",
            "email": "testuser@gmail.com",
            "password": "testpassword"
        }
        
        response = self.app.post('/auth/register', json=test_user)
        data = response.json.get('data')
        self.assertEqual(response.status_code, 201)

        login_data = {
            "email": "testuser@gmail.com",
            "password": "testpassword"
        }
        
        response = self.app.post('/auth/login', json=login_data)
        data = response.json.get('data')
        self.assertEqual(response.status_code, 200)
        self.assertIn('accessToken', data)
        self.assertEqual(data.get('user').get('email'), test_user.get('email'))
        self.assertEqual(data.get('user').get('lastName'), test_user.get('lastName'))
        self.assertEqual(data.get('user').get('firstName'), test_user.get('firstName'))
        self.assertEqual(data.get('user').get('phone'), None)


if __name__ == '__main__':
    unittest.main()
