from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout

from vcm.forms import UserForm, ConcursoForm , loginForm , Video_participanteForm
from django.contrib.auth.models import User
from vcm.models import Concurso , Video_participante
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from . import sqs_queue

# Create your views here.
# Autenticación
def autenticacion(request):

    if request.user.is_authenticated:
        if request.method == 'POST':
            eliminar = True if 'idE' in request.POST else False
            if eliminar:
                pk = request.POST.get('idE')
                concurso = Concurso.objects.get(id=pk)
                return eliminar_concurso(concurso, request)
        else:
            return concurso_view(request)

    else:
        if request.method == 'POST':
            registro = True if 'password2' in request.POST else False
            if registro:
                return usuario_create(request)
            else:
                return login_view(request)
        else:
            form = loginForm()
            formregistro = UserForm()
            return render(request, 'usuario/login.html', {'form': form, 'formRegistro': formregistro})

def login_view(request):
    mensaje = ''
    username = request.POST.get('usernameL')
    password = request.POST.get('passwordL')
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect(reverse('vcm:index'))
    else:
        mensaje = 'Nombre de usuario o clave no valida'
        messages.warning(request, mensaje, extra_tags='alert alert-warning')
        return redirect(reverse('vcm:index'))

def usuario_create(request):
    formregistro = UserForm(request.POST)
    if formregistro.is_valid():
        cleaned_data = formregistro.cleaned_data
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user_model = User.objects.create_user(username=username, password=password)
        user_model.save()
        messages.success(request, 'Se ha creado con éxito su cuenta, ahora inicie sesión',
                         extra_tags='alert alert-success')
        return HttpResponseRedirect(reverse('vcm:index'))
    else:
        form = loginForm()
        return render(request, 'usuario/login.html', {'form': form, 'formRegistro': formregistro, "registro": True})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('vcm:index'))


def concurso_view(request):
    if request.user.is_authenticated:
        concursos = Concurso.objects.all().filter(usuario_id=request.user.id)
        for concurso in concursos:
            videos = Video_participante.objects.all().filter(concurso=concurso.id)
            total = len(videos)
            concurso.videos = total
            convertidos = 0
            for video in videos:
                if video.estado == 2:
                    convertidos += 1
            concurso.videos_convertidos = convertidos

        context = {'concursos': concursos}
        return render(request, 'usuario/index.html', context)


def concurso_videos(request, pk):

    concurso = Concurso.objects.get(id=pk)

    if request.user.is_authenticated and concurso.usuario.id == request.user.id:
        videos_list = Video_participante.objects.all().filter(concurso=concurso.id).order_by('id')

        paginator = Paginator(videos_list, 12)  # Show 25 contacts per page
        page = request.GET.get('page')
        videos = paginator.get_page(page)
        context = {'videos': videos, 'concurso': concurso}
        return render(request, 'usuario/videos_concurso.html', context)


def concurso_crate(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = ConcursoForm(request.POST, request.FILES)
            if form.is_valid():
                cleaned_data = form.cleaned_data

                url = cleaned_data.get('url')
                imagen = request.FILES['imagen']
                nombre = cleaned_data.get('nombre')

                fecha_inicio =  cleaned_data.get('fecha_terminacion')
                fecha_terminacion =  cleaned_data.get('fecha_terminacion')
                descripcion = cleaned_data.get('descripcion')


                concurso = Concurso.objects.create(usuario=request.user, nombre=nombre, url=url,
                                               imagen=imagen, descripcion=descripcion,
                                               fecha_inicio=fecha_inicio,
                                               fecha_terminacion=fecha_terminacion)
                concurso.save()
                messages.success(request, 'Se ha creado con éxito el concurso',
                                 extra_tags='alert alert-success')
                return redirect(reverse('vcm:index'))
        else:
            form = ConcursoForm()
        return render(request, 'usuario/concurso_crear.html', {'form': form})

def concurso_update(request,pk):
    if request.user.is_authenticated:
        concurso = Concurso.objects.get(id=pk)
        if request.method == 'POST':
            form = ConcursoForm(request.POST,instance=concurso)
            if form.is_valid():
                cleaned_data = form.cleaned_data

                concurso.url = cleaned_data.get('url')

                concurso.nombre = cleaned_data.get('nombre')

                concurso.fecha_inicio = cleaned_data.get('fecha_terminacion')
                concurso.fecha_terminacion = cleaned_data.get('fecha_terminacion')
                concurso.descripcion = cleaned_data.get('descripcion')

                if 'imagen' in request.FILES:
                    concurso.imagen = request.FILES['imagen']

                concurso.save()
                messages.success(request, 'Se ha actualizado con éxito el evento',
                                 extra_tags='alert alert-success')
                return redirect(reverse('vcm:index'))
        else:

            form = ConcursoForm(instance=concurso)
        return render(request, 'usuario/concurso_actualizar.html', {'form': form})

def eliminar_concurso(concurso, request):
    concurso.delete()
    messages.success(request, 'Se ha eliminado con éxito a ' + str(concurso.nombre),
                     extra_tags='alert alert-success')
    return redirect(reverse('vcm:index'))


def participar(request,concurso_url):
    concurso = Concurso.objects.get(url=concurso_url)
    videos_list = Video_participante.objects.all().filter(concurso=concurso.id).filter(estado=2).order_by('id')
    formParticipante = Video_participanteForm()

    paginator = Paginator(videos_list, 12)
    page = request.GET.get('page')
    videos = paginator.get_page(page)

    context = {'videos': videos, 'form':formParticipante, 'concurso':concurso, 'numbervideos':videos_list.count() }

    if request.method == 'POST':
        form = Video_participanteForm(request.POST, request.FILES)
        if form.is_valid():
            cleaned_data = form.cleaned_data

            nombres_participante = cleaned_data.get('nombres_participante')
            apellidos_participante = cleaned_data.get('apellidos_participante')
            correo_participante = cleaned_data.get('correo_participante')
            video_original = request.FILES['video_original']
            descripcion = cleaned_data.get('descripcion')



            video = Video_participante.objects.create(nombres_participante=nombres_participante,
                                                      apellidos_participante=apellidos_participante,
                                                      correo_participante=correo_participante,
                                                      video_original=video_original,
                                                      descripcion=descripcion,
                                                      estado=1,
                                                      concurso=concurso)
            video.save()
        messages.success(request, 'Se ha agregado con exito tu video, cuando esté listo en la página te enviaremos un correo electronico',
                         extra_tags='alert alert-success')
        sqs_queue.sendMessageToQueue(str(video.video_original))

    return render(request, 'participante/index.html', context)