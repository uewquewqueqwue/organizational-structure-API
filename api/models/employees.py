from django.db import models


class Employee(models.Model):
    department = models.ForeignKey(
        "api.Department",
        on_delete=models.PROTECT,
        verbose_name="Employee department",
        related_name="employees",
    )
    full_name = models.CharField(max_length=200, verbose_name="Full name employee")
    position = models.CharField(max_length=200, verbose_name="Position employee")
    hired_at = models.DateField(
        blank=True, null=True, verbose_name="When hired employee"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.full_name} - {self.position}"
