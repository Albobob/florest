# contacts/models.py
from django.db import models

class ContactRequest(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    message = models.TextField(verbose_name="Сообщение", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")

    class Meta:
        verbose_name = "Запрос на обратную связь"
        verbose_name_plural = "Запросы на обратную связь"

    def __str__(self):
        return f"Запрос от {self.name} ({self.phone})"