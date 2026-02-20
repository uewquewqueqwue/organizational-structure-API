from api.models.departments import Department
from api.models.employees import Employee
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


class EmployeeCreateTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

        self.user = User.objects.create_superuser(
            username="testuser", email="testuser@gmail.com", password="testuser111"
        )

        self.client.force_login(self.user)

        self.department = Department.objects.create(name="Test company")

        self.url = f"/api/departments/{self.department.pk}/employees/"

        self.valid_data = {
            "full_name": "Бедный тестер",
            "position": "Tester",
            "hired_at": "2026-02-20",
        }

    def test_create_employee_without_auth(self) -> None:
        self.client.logout()
        response = self.client.post(self.url, self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_employee_with_auth(self) -> None:
        response = self.client.post(self.url, self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["full_name"], self.valid_data["full_name"])  # type: ignore
        self.assertEqual(response.data["position"], self.valid_data["position"])  # type: ignore
        self.assertEqual(response.data["department"], self.department.pk)  # type: ignore

        self.assertEqual(Employee.objects.count(), 1)
        employee = Employee.objects.first()
        self.assertEqual(employee.full_name, self.valid_data["full_name"])  # type: ignore

    def test_create_employee_invalid_department(self) -> None:
        invalid_url = "/api/departments/999/employees/"
        response = self.client.post(invalid_url, self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_employee_invalid_data(self) -> None:
        invalid_data = {
            "full_name": "",
            "position": "Tester",
        }
        response = self.client.post(self.url, invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("full_name", response.data)  # type: ignore
