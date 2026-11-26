from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone


class Appointment(models.Model):

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'En attente'
        CONFIRMED = 'CONFIRMED', 'Confirmé'
        CANCELLED = 'CANCELLED', 'Annulé'

    doctor = models.ForeignKey(
        'AccountApp.Doctor', on_delete=models.CASCADE, related_name='appointments'
    )
    patient = models.ForeignKey(
        'AccountApp.Patient', on_delete=models.CASCADE, related_name='appointments'
    )
    appointment_date = models.DateTimeField()
    reason = models.TextField()
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    duration_minutes = models.PositiveIntegerField(default=30)
    prescription = models.FileField(
        upload_to='prescriptions/', blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['appointment_date']
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'appointment_date'],
                name='unique_doctor_appointment_date',
            )
        ]

    def clean(self):
        if not self.appointment_date:
            return
        # Vérifier la règle seulement à la création ou si la date a changé
        if self._state.adding:
            must_check = True
        else:
            old = (Appointment.objects.filter(pk=self.pk)
                   .values_list('appointment_date', flat=True).first())
            must_check = old != self.appointment_date
        if must_check and self.appointment_date <= timezone.now():
            raise ValidationError(
                {'appointment_date': "La date doit être postérieure à la date et l'heure actuelles."}
            )

    def __str__(self):
        return f"{self.patient} / {self.doctor} - {self.appointment_date:%d/%m/%Y %H:%M}"