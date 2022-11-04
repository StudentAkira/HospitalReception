from django.contrib.auth import logout, login
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect

from .models import CustomUser
from .permissions import access_permission_role, unauthorized, authorized
from .forms import RegisterForm, LoginForm


@authorized
def logout_view(request):
    logout(request)
    return redirect('/login')


@unauthorized
def register_view(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(template_name='register.html',
                      request=request,
                      context={"form": form, "message": "Register"}
                      )
    if request.method == 'POST':
        data = request.POST
        username = data.get('username', None)
        password = data.get('password', None)
        fio = data.get('fio', None)
        role = data.get('role', None)
        all_data_gotten = username and password and fio and role
        if not all_data_gotten:
            form = RegisterForm()
            return render(template_name='register.html',
                          request=request,
                          context={"form": form, "message": f"Invalid data"})

        username_taken = CustomUser.objects.filter(username=username).count()
        if username_taken:
            form = RegisterForm()
            return render(template_name='register.html',
                          request=request,
                          context={"form": form, "message": f"Name {username} is already taken"})

        CustomUser.objects.create_user(
            username=username,
            password=password,
            fio=fio,
            role=role,
        )
        return redirect('/login')


@unauthorized
def login_view(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(template_name='login.html',
                      request=request,
                      context={"form": form, "message": "Login"})

    if request.method == 'POST':
        form = LoginForm()
        data = request.POST
        username = data.get('username', None)
        password = data.get('password', None)
        if not password or not username:
            return render(template_name='login.html',
                          request=request,
                          context={"form": form, "message": "Invalid data"})
        user = CustomUser.objects.filter(username=username)
        if not user.exists():
            return render(template_name='login.html',
                          request=request,
                          context={"form": form, "message": "No such user"})
        user = user.get()
        password_correct = check_password(password, user.password)
        if password_correct:
            login(request, user)
            return redirect(user.role.lower())

        return render(template_name='login.html',
                      request=request,
                      context={"form": form, "message": "Invalid password"})


@authorized
@access_permission_role('Doctor')
def doctor_view(request):
    if request.method == 'GET':
        return render(template_name='doctor.html', request=request)


@authorized
@access_permission_role('Patient')
def patient_view(request):
    if request.method == 'GET':
        return render(template_name='patient.html', request=request)


