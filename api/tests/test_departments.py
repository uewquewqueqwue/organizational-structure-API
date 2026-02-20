from api.models.departments import Department
from api.models.employees import Employee
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


class DepartmentTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

        self.user = User.objects.create_superuser(
            username="testuser", email="testuser@gmail.com", password="testuser111"
        )

        self.client.force_login(self.user)

    def test_create_department(self) -> None:
        data = {"name": "Бедная IT компания", "parent": None}

        response = self.client.post("/api/departments/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Бедная IT компания")  # type: ignore
        self.assertIsNone(response.data["parent"])  # type: ignore

    def test_create_department_with_parent(self) -> None:
        parent = Department.objects.create(name="Папа бедной IT компании")

        data = {"name": "Бедная IT компания", "parent": parent.pk}

        response = self.client.post("/api/departments/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["parent"], parent.pk)  # type: ignore

    def test_create_department_duplicate_name_parent(self) -> None:
        parent = Department.objects.create(name="Папа?")

        Department.objects.create(name="Папа?", parent=parent)

        data = {"name": "Папа?", "parent": parent.pk}
        response = self.client.post("/api/departments/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", str(response.data))  # type: ignore

    def test_department_patch_edit(self) -> None:
        parent1 = Department.objects.create(name="Папа тестера")
        parent2 = Department.objects.create(name="Второй папа?")
        department = Department.objects.create(
            name="Наш маленький тестер", parent=parent1
        )

        response = self.client.get(f"/api/departments/{department.pk}/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Наш маленький тестер")  # type: ignore
        self.assertEqual(response.data["parent"], parent1.pk)  # type: ignore

        # Поменял имя и стал крутым
        response = self.client.patch(
            f"/api/departments/{department.pk}/",
            {"name": "Тестер повзраслел"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Тестер повзраслел")  # type: ignore
        self.assertEqual(response.data["parent"], parent1.pk)  # type: ignore

        # Поменял папу и стал..
        response = self.client.patch(
            f"/api/departments/{department.pk}/", {"parent": parent2.pk}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Тестер повзраслел")  # type: ignore
        self.assertEqual(response.data["parent"], parent2.pk)  # type: ignore

    def test_department_delete_casscade(self) -> None:
        parent = Department.objects.create(name="Папа")
        child = Department.objects.create(name="Младший", parent=parent)
        Employee.objects.create(
            full_name="Бедный работник", position="Скоро уволится", department=child
        )

        response = self.client.delete(f"/api/departments/{parent.pk}/?mode=cascade")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Department.objects.all().count(), 0)
        self.assertEqual(Employee.objects.all().count(), 0)

    def test_delete_department_reassign(self) -> None:
        old_department = Department.objects.create(name="Старый папа")
        new_department = Department.objects.create(name="Новый папа")
        employee = Employee.objects.create(
            full_name="Бедный работник",
            position="Скоро переводится",
            department=old_department,
        )

        response = self.client.delete(
            f"/api/departments/{old_department.pk}/?mode=reassign&reassign_to_department_id={new_department.pk}"
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Department.objects.filter(pk=old_department.pk).exists())
        self.assertIn(employee, new_department.employees.all())  # type: ignore
