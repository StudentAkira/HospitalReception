from django.contrib.auth import authenticate, login
from typing import Dict
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Count

from reception.filters import PatientFilter
from reception.forms import RegisterForm, LoginForm
from reception.models import CustomUser, MedicalCard, Disease


class ProcessUserInterface:
    def __init__(self, user: CustomUser):
        self._user = user

    def process(self):
        raise NotImplementedError


class PatientService(ProcessUserInterface):
    def process(self):
        from .models import MedicalCard
        card = MedicalCard.objects.create(owner=self._user)
        card.save()


class DoctorService(ProcessUserInterface):
    def process(self):
        pass


class CreateUserService:
    _map: Dict[str, type(ProcessUserInterface)] = {
        CustomUser.RoleChoices.PATIENT: PatientService,
        CustomUser.RoleChoices.DOCTOR: DoctorService
    }

    def __init__(self, form: RegisterForm):
        self._form = form

    def create_user(self) -> CustomUser:
        form_data = self._form.data.dict()
        form_data.pop('csrfmiddlewaretoken', None)
        try:
            user = CustomUser(**form_data)
            user.set_password(form_data['password'])
            user.save()
        except IntegrityError:
            raise ValidationError('username taken')
        self._map[user.role](user).process()
        return user


class LoginUserService:

    def __init__(self, form: LoginForm):
        self._form = form

    def log_in(self, request) -> CustomUser:
        form_data = self._form.data.dict()
        user = authenticate(**form_data)
        if user is not None:
            login(request, user)
            return user
        else:
            raise ValidationError('Invalid username or password')


class MedicalCardContentService:

    def __init__(self, user: CustomUser):
        self._card = MedicalCard.objects.get(owner=user)
        self._diseases = Disease.objects.filter(card=self._card).all()

    def get_diseases_short_data(self) -> list:
        return list(self._diseases.values('name', 'discovered_at', 'id'))

    def get_full_disease(self, disease_id) -> Disease:
        return self._diseases.get(id=disease_id)


class ManyMedicalCardsService:
    def __init__(self, request):

        self.patient_filtrator = PatientFilter(
            request.GET,
            queryset=CustomUser.objects.prefetch_related('card_owner').
                filter(role=CustomUser.RoleChoices.PATIENT).
                annotate(disease_count=Count('card_owner__medical_card')),
            request=request,
        )
        self._cards_info = self.patient_filtrator.qs.values('fio', 'id', 'disease_count')

    def get_cards_info(self) -> list:
        return [{
            'fio': owner_card['fio'],
            'owner_id': owner_card['id'],
            'amount_of_diseases': owner_card['disease_count']
        }
            for owner_card in self._cards_info]


class TmpService:

    def create(self, username, password):
        user = CustomUser(
            username=username,
            fio=username,
            role='patient',
        )
        user.set_password(password)
        user.save()
        from .models import MedicalCard
        card = MedicalCard.objects.create(owner=user)
        card.save()
