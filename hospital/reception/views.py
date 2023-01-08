from django.contrib.auth import logout
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import CustomUser, MedicalCard, Disease
from .permissions import access_permission_role, unauthorized, authorized, card_owner_or_doctor
from .forms import RegisterForm, LoginForm, DiseaseForm
from .services import CreateUserService, LoginUserService, DiseaseService, ManyMedicalCardsService, \
    DoctorService, TicketService


@authorized
def logout_view(request):
    logout(request)
    return redirect('/login')


@unauthorized
def register_view(request):
    print('test')
    if request.method == 'GET':
        form = RegisterForm()
        return render(template_name='register.html',
                      request=request,
                      context={"form": form, "message": "Register"})
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        try:
            CreateUserService(form).create_user()
            return redirect('/login')
        except ValidationError:
            username = form.data.dict()['username']
            form = RegisterForm()
            return render(template_name='register.html',
                          request=request,
                          context={'form': form, 'message': f'Username {username} taken'})


@unauthorized
def login_view(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(template_name='login.html',
                      request=request,
                      context={"form": form, "message": "Login"})

    if request.method == 'POST':
        form = LoginForm(request.POST)
        try:
            service = LoginUserService(form)
            user = service.log_in(request)
            return redirect(f'/{user.role}'.lower())
        except ValidationError:
            form = LoginForm()
            return render(template_name='login.html',
                          request=request,
                          context={"form": form, "message": "Invalid password or username"})


@authorized
@access_permission_role(CustomUser.RoleChoices.DOCTOR)
def doctor_view(request):
    if request.method == 'GET':
        return render(template_name='doctor.html', request=request)


@authorized
@access_permission_role(CustomUser.RoleChoices.PATIENT)
def patient_view(request):
    if request.method == 'GET':
        return render(
            template_name='patient.html',
            request=request,
            context={'patient_id': request.user.id}
        )


@authorized
@access_permission_role(CustomUser.RoleChoices.DOCTOR)
def many_cards_view(request):
    if request.method == 'GET':
        service = ManyMedicalCardsService(request)
        filtrator = service.patient_filtrator
        card_info_items = service.get_cards_info()
        return render(
            template_name='cards.html',
            request=request,
            context={
                'user_role': request.user.role,
                'card_info_items': card_info_items,
                'filter': filtrator,
            }
        )


@authorized
@card_owner_or_doctor
def card_content_view(request, user_id):
    if request.method == 'GET':
        try:
            user = CustomUser.objects.get(id=user_id)
            service = DiseaseService(user)
            diseases = service.get_diseases_short_data()
            return render(
                template_name='card.html',
                request=request,
                context={
                    'patient_fio': user.fio,
                    'patient_id': user.id,
                    'user_role': request.user.role,
                    'back_to_cards': request.user.role == CustomUser.RoleChoices.DOCTOR,
                    'diseases': diseases,
                }
            )
        except (MedicalCard.DoesNotExist, CustomUser.DoesNotExist):
            return redirect(f'{request.user.role.lower()}')


@authorized
@card_owner_or_doctor
def disease_view(request, user_id, disease_id):
    if request.method == 'GET':
        try:
            user = CustomUser.objects.get(id=user_id)
            service = DiseaseService(user)
            disease = service.get_full_disease(disease_id)
            return render(
                template_name='disease.html',
                request=request,
                context={
                    'disease': disease,
                    'user_id': user.id,
                    'user_role': request.user.role,
                },
            )
        except (MedicalCard.DoesNotExist, CustomUser.DoesNotExist, Disease.DoesNotExist):
            return redirect(f'{request.user.role.lower()}')


@authorized
@access_permission_role(CustomUser.RoleChoices.DOCTOR)
def create_disease_view(request, user_id):
    if request.method == 'GET':
        form = DiseaseForm()
        return render(request=request,
                      template_name='new_disease.html',
                      context={
                            'user_role': request.user.role,
                            'form': form,
                      })
    if request.method == 'POST':
        form_data = DiseaseForm(request.POST)
        service = DiseaseService(user_id)
        disease_id = service.create_new_disease(form_data)
        return redirect(f'/card/patient/{user_id}/disease/{disease_id}/')


@authorized
@access_permission_role(CustomUser.RoleChoices.PATIENT)
def select_doctor_view(request):
    if request.method == 'GET':
        service = DoctorService(request)
        doctors = service.get_all()
        return render(
            template_name='appointment_doctors.html',
            request=request,
            context={
                'user_role': request.user.role,
                'doctors': doctors,
            }
        )


@authorized
@access_permission_role(CustomUser.RoleChoices.PATIENT)
def select_datetime_view(request, doctor_id):
    if request.method == 'GET':
        service = TicketService(request.user, doctor_id)
        tickets = service.get_accessible_dates(request)
        return render(
            template_name='appointment_date_time.html',
            request=request,
            context={
                'doctor_id': doctor_id,
                'user_role': request.user.role,
                'tickets': tickets,
            }
        )


@authorized
@access_permission_role(CustomUser.RoleChoices.PATIENT)
def get_ticket_view(request, doctor_id, month, day, hour, minute):
    if request.method == 'GET':
        try:
            service = TicketService(request.user, doctor_id)
            service.get_ticket(month, day, hour, minute)
            return redirect('patient')
        except IntegrityError:
            return HttpResponse('Too many tickets for one user')


@authorized
@access_permission_role(CustomUser.RoleChoices.PATIENT)
def get_my_tickets(request):
    if request.method == 'GET':
        service = TicketService(request.user)
        tickets = service.get_my_tickets()
        return render(
            template_name='my_tickets.html',
            request=request,
            context={
                'user_role': request.user.role,
                'tickets': tickets,
            }
        )
