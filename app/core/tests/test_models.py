from django.test import TestCase
from django.contrib.auth import get_user_model

class ModelTests(TestCase):

	def test_create_user_with_email_successfull(self):
		""" Tst craete new user with given email and password """
		email = "satai@gamil.com"
		password = "satish1234"
		user = get_user_model().objects.create_user(email= email, password= password)

		self.assertEqual(user.email, email)
		self.assertTrue(user.check_password(password))

	def test_new_user_email_normalized(self):
		""" Test the email for a new user is normalized.. case sensitive, after @ .. for this i have to change in user model with normalize method
		foo@bar.com and foo@BAR.com are equivalent;"""
		email = "satish12s34@GMAIL.COM"
		user = get_user_model().objects.create_user(email, "satish12s34")

		self.assertEqual(user.email, email.lower())

	def test_craete_user_without_email(self):
		"""  Try to ceate a user without email   below  if it will not raise the value error then it will fails """
		with self.assertRaises(ValueError):
			get_user_model().objects.create_user(None, "satis1121")

	def test_craete_new_superuser(self):
		"""  Test create new super user"""
		user = get_user_model().objects.create_superuser("satus@amil.com", "2332323sass@")

		self.assertTrue(user.is_superuser)
		self.assertTrue(user.is_staff)
