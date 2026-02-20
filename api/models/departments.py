from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=200, verbose_name="Department name")
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Parent department",
        related_name="children",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["name", "parent"]
        verbose_name = "Department"
        verbose_name_plural = "Departments"

    def __str__(self) -> str:
        return self.name
