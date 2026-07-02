import json
from datetime import date

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .models import Homework
from .validators import ComplexPasswordValidator


class PasswordValidatorTests(SimpleTestCase):
    def setUp(self):
        self.validator = ComplexPasswordValidator()

    def test_rejects_password_without_required_complexity(self):
        with self.assertRaises(ValidationError):
            self.validator.validate('abcdefghij')

    def test_rejects_password_outside_length_range(self):
        with self.assertRaises(ValidationError):
            self.validator.validate('Abc1!xyz')

    def test_accepts_a_strong_password(self):
        self.validator.validate('Abc12!wxyz')


class StudentSaveFlowTests(TestCase):
    def test_home_page_exposes_csrf_token(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_homework_api_lists_assignments_for_matching_class(self):
        Homework.objects.create(
            title='Math Revision',
            description='Solve the attached worksheet.',
            class_name='Grade 4',
            due_date=date(2026, 7, 10),
            file=SimpleUploadedFile('worksheet.pdf', b'%PDF-1.4', content_type='application/pdf')
        )

        response = self.client.get(reverse('school:homework-list'), {'class_name': 'Grade 4'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['title'], 'Math Revision')
        self.assertIn('worksheet.pdf', response.json()['results'][0]['file'])

    def test_home_page_renders_hidden_csrf_token_input(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="csrfmiddlewaretoken"')

    def test_student_creation_allows_missing_password(self):
        payload = {
            'name': 'Saved Student',
            'email': 'savedstudent@example.com',
            'phone': '1234567890',
            'class_name': 'Pre-Nursery',
            'dob': '2000-01-01',
            'parent_name': 'Parent',
        }

        response = self.client.post(
            reverse('school:student-list'),
            data=json.dumps(payload),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertIn('student_id', response.json())
        self.assertIn('password', response.json())
