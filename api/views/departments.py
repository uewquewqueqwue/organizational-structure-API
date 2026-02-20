from typing import NoReturn

from api.models.departments import Department
from api.models.employees import Employee
from api.serializers.departments import DepartmentSerializer
from api.serializers.employees import EmployeeSerializer
from api.views.permissions import ReadOnlyOrAuth
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.utils.serializer_helpers import ReturnDict


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [ReadOnlyOrAuth]

    def retrieve(self, request: Request, *args, **kwargs) -> NoReturn:
        depth = int(request.query_params.get("depth", 1))

        if not 1 <= depth <= 5:
            raise ValidationError({"depth": "Must be from 1 to 5"})

        include_employees = (
            request.query_params.get("include_employees", "true").lower() == "true"
        )

        department = Department.objects.prefetch_related(
            "children", "employees" if include_employees else None
        ).get(pk=kwargs["pk"])

        data = self.get_serializer(department).data
        data["employees"] = self._get_employees(department, include_employees)
        data["children"] = self._build_tree(department, depth, include_employees)

        return Response(data)

    @action(detail=True, methods=["post"], url_path="employees")
    def create_employee(self, request, pk=None) -> Response:
        department = get_object_or_404(Department, pk=pk)

        data = request.data.copy()
        data["department"] = department.pk

        serializer = EmployeeSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def destroy(self, request: Request, *args, **kwargs) -> NoReturn:
        department = self.get_object()
        mode = request.query_params.get("mode")
        reassign_id = request.query_params.get("reassign_to_department_id")

        if mode == "cascade":
            return self._cascade_delete(department)
        elif mode == "reassign":
            if not reassign_id:
                return Response(
                    {"error": "reassign_to_department_id required for reassign mode"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return self._reassign_delete(department, reassign_id)
        else:
            return Response(
                {"error": "specify mode 'cascade' or 'reassing'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def _get_employees(
        self, department: Department, include_employees: bool
    ) -> list | ReturnDict:
        if not include_employees:
            return []

        return EmployeeSerializer(department.employees.all(), many=True).data  # type: ignore

    def _build_tree(
        self, department, depth, include_employees
    ) -> list | list[ReturnDict]:
        if depth <= 1:
            return []

        result = []
        for child in department.children.all():
            child_data: ReturnDict = DepartmentSerializer(child).data  # type: ignore
            child_data["employees"] = self._get_employees(child, include_employees)
            child_data["children"] = self._build_tree(
                child, depth - 1, include_employees
            )
            result.append(child_data)
        return result

    def _collect_descendant_ids(self, department) -> list[int]:
        ids = [department.pk]

        for child in department.children.all():
            ids.extend(self._collect_descendant_ids(child))
        return ids

    @transaction.atomic
    def _cascade_delete(self, department: Department) -> Response:
        Employee.objects.filter(
            department_id__in=self._collect_descendant_ids(department)
        ).delete()

        department.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @transaction.atomic
    def _reassign_delete(self, department: Department, reassign_id: int) -> Response:
        try:
            new_department = Department.objects.get(pk=reassign_id)

        except Department.DoesNotExist:
            return Response(
                {"error": "Department not found"}, status=status.HTTP_404_NOT_FOUND
            )

        department.employees.update(department=new_department)  # type: ignore

        # Про дочерние компании и их сотрудников
        # сказано не было поэтому их просто удаляем
        for child in department.children.all():  # type: ignore
            self._cascade_delete(child)

        department.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
