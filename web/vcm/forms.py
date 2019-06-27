from django.forms import ModelForm
from django.contrib.auth.forms import forms
from django.contrib.auth.models import User
from vcm.models import Concurso, Video_participante
from django.forms import widgets
from django.contrib.auth import password_validation


class UserForm(ModelForm):
    username = forms.CharField(label="Usuario", max_length=50)
    first_name = forms.CharField(label="Nombres", max_length=50)
    last_name = forms.CharField(label="Apellidos", max_length=50)
    email = forms.EmailField(label="Correo electrónico", widget=forms.EmailInput())
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput())
    password2 = forms.CharField(label="Confirmación de contraseña", widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'password2']

    # verificacion correo unico
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username):
            raise forms.ValidationError('Correo ya ha sido registrado')
        return username

    # verificacion las contraseñas coinciden y seguridad
    def clean_password2(self):
        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']
        if password != password2:
            raise forms.ValidationError('Contraseñas no coinciden')
        try:
            password_validation.validate_password(password2)
        except password_validation.ValidationError as errores:
            mensajes = []
            for m in errores.messages:
                if m == 'This password is too short. It must contain at least 8 characters.':
                    mensajes.append('Contraseña muy corta, debe contener más de 7 caracteres')
                if m == 'This password is too common.':
                    mensajes.append('Contraseña muy común')
                if m == 'This password is entirely numeric.':
                    mensajes.append('Contraseña no puede contener solo números')
                if m.startswith("The password is too similar"):
                    mensajes.append('Contraseña muy similar a los datos del usuario')
            raise forms.ValidationError(mensajes)
        return password2

class loginForm(ModelForm):
    usernameL = forms.CharField(label="Usuario", max_length=50)
    passwordL = forms.CharField(label="Contraseña", widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['usernameL', 'passwordL']

class ConcursoForm(ModelForm):
    nombre = forms.CharField(max_length=100)
    url = forms.CharField(max_length=100)
    imagen = forms.ImageField(required=True)

    fecha_inicio = forms.DateField(widget=widgets.SelectDateWidget(
        empty_label=("Choose Year", "Choose Month", "Choose Day"),
    ))
    fecha_terminacion =  forms.DateField(widget=widgets.SelectDateWidget(
        empty_label=("Choose Year", "Choose Month", "Choose Day"),
    ))

    descripcion= forms.CharField(label="Descripción", widget=forms.Textarea, max_length=500)

    class Meta:
        model = Concurso
        fields = ['nombre', 'url', 'imagen', 'fecha_inicio', 'fecha_terminacion', 'descripcion']

    # verificacion fecha de termiacion es mayor a la de inicio
    def clean_fecha_terminacion(self):
        fecha_inicio = self.cleaned_data['fecha_inicio']
        fecha_terminacion = self.cleaned_data['fecha_terminacion']
        if fecha_terminacion < fecha_inicio:
            raise forms.ValidationError('La fecha de inicio debe ser anterior a la fecha de terminacion')
        return fecha_inicio

    def clean_url(self):
        url = self.cleaned_data['url']
        if self.instance:
            concurso = Concurso.objects.filter(url=url)
            if len(concurso) > 0 and concurso[0].id != self.instance.id:
                raise forms.ValidationError('La url ya está ha sido tomada por otro concurso')
        else:
            if Concurso.objects.filter(url=url):
                raise forms.ValidationError('La url ya está ha sido tomada por otro concurso')
        return url
        
class Video_participanteForm(ModelForm):

    nombres_participante = forms.CharField(label = "Nombres",max_length=200)
    apellidos_participante = forms.CharField(label = "Apellidos",max_length=200)
    correo_participante = forms.EmailField(label="Correo electrónico", widget=forms.EmailInput())

    video_original = forms.FileField(required=True, label="Video para participar")

    descripcion = forms.CharField(label="Descripción", widget=forms.Textarea, max_length=500)


    class Meta:
        model = Video_participante
        fields = ['nombres_participante', 'apellidos_participante', 'correo_participante', 'video_original',
                  'descripcion']