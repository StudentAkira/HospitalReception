from django.contrib.auth import logout
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect

from .filters import PatientFilter
from .models import CustomUser, MedicalCard, Disease
from .permissions import access_permission_role, unauthorized, authorized, card_owner_or_doctor
from .forms import RegisterForm, LoginForm
from .services import CreateUserService, LoginUserService, MedicalCardContentService, ManyMedicalCardsService


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
            service = MedicalCardContentService(user)
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
            service = MedicalCardContentService(user)
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

