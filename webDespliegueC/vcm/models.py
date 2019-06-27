from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Concurso(models.Model):
    usuario = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100, null=False, blank=False)
    url = models.CharField(max_length=100, null=False, blank=False)
    imagen = models.ImageField(upload_to='logosConcursos', null=True)

    fecha_inicio = models.DateTimeField(null=False, blank=False)
    fecha_terminacion = models.DateTimeField(null=False, blank=False)

    descripcion= models.CharField(max_length=500, null=False, blank=False)



class Video_participante(models.Model):

    concurso = models.ForeignKey(Concurso, null=False, on_delete=models.CASCADE)
    nombres_participante = models.CharField(max_length=200, null=False, blank=False)
    apellidos_participante = models.CharField(max_length=200, null=False, blank=False)
    correo_participante = models.CharField(max_length=200, null=False, blank=False)
    video_original = models.FileField(upload_to='videosOriginales', null=False)
    video_porcesado = models.CharField(max_length=200, null=True, blank=True)

    #imagen = models.CharField(max_length=500, null=False, blank=False)

    fecha_inscripcion = models.DateTimeField(auto_now_add=True)

    descripcion = models.CharField(max_length=500, null=False, blank=False)

    ESTADO_CHOICES = (
        (1, 'En proceso'),
        (2, 'Convertido')
    )
    estado = models.PositiveSmallIntegerField(choices=ESTADO_CHOICES, null=False, blank=False)
