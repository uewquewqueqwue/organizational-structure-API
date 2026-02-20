from rest_framework import serializers

from api.models.employees import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    hired_at = serializers.DateField(allow_null=True, required=False)

    class Meta:
        model = Employee
        fields = "__all__"
        read_only_fields = ("id", "created_at")
