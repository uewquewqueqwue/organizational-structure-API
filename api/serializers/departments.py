from api.models.departments import Department
from api.types.departments import DepartmentData
from rest_framework import serializers


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"
        read_only_fields = ("id", "created_at")

    def validate(self, data: DepartmentData) -> DepartmentData:
        name = data.get("name")
        parent = data.get("parent")

        if self.instance and parent == self.instance:
            raise serializers.ValidationError(
                {"parent": "Department cannot be parent of itself"}
            )

        if Department.objects.filter(name=name, parent=parent).exists():
            raise serializers.ValidationError({"name": "Parent already exists"})

        return data
