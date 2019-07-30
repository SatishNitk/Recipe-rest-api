from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

def create_user(**params):
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    """Test the user Api public"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_sucess(self):
        """Test creating user with validpayload is susccessful"""
        payload = {
        'email':'test@gmail.com',
        'password' : 'testpassword',
        'name' : "Test name"
        }
        res = self.client.post(CREATE_USER_URL,payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password',res.data)

    def test_user_exists(self):
        """Test creating user that already exists"""
        payload = {'email':'test@gmail.com','password':'testpassword'}
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL,payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """ Test that the password must be more than 4 character"""
        payload = {'email':'test@gmail.com','password':'pw'}
        res  = self.client.post(CREATE_USER_URL,payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token s create for the user"""

        payload = {'email':'test@gamil.com','password':'testpassword'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token',res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not creared if invalid credential"""

        create_user(email='test@gmail.com',password='testpassword')
        payload = {'email':'test@gmail.com','password':'wrong'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_craete_token_no_user(self):
        """ Test that token is not created if user doesn't exists"""
        payload = {'email':'test@gmail.com','password':'testpassword'}
        res = self.client.post(TOKEN_URL,payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_craete_token_missing_field(self):
        """Test that email and passwod are required"""
        res = self.client.post(TOKEN_URL, {'email':'one','password':''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_retrive_user_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTest(TestCase):
    """ Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email ='test@gamil.com',
            password ='testpassword',
            name= 'name'
            )
        self.client= APIClient()
        self.client.force_authenticate(user=self.user) # whatever request will make using self.client will be authenticated with self.user 

    def test_retrieve_profile_success(self):
        """Test retrirving profile for logged in  user  """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,{
            'name':self.user.name,
            'email':self.user.email
            })
    def test_post_me_not_allowed(self):
        """ Test That POST is not allowed on the me url"""

        res = self.client.post(ME_URL,{})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """ Test updating the user profle for authenticated user"""
        payload = {'name':'new_name', 'password' :'newpassword'}

        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
