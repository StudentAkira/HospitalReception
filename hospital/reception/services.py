from datetime import datetime, timezone, timedelta
from django.contrib.auth import authenticate, login
from typing import Dict
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Count
from reception.filters import PatientFilter, TicketFilter
from reception.forms import RegisterForm, LoginForm, DiseaseForm
from reception.models import CustomUser, MedicalCard, Disease, Ticket


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

    def get_all(self):
        return CustomUser.objects \
            .filter(role=CustomUser.RoleChoices.DOCTOR).values('fio', 'id')


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


class DiseaseService:

    def __init__(self, user: CustomUser):
        self._card = MedicalCard.objects.get(owner=user)
        self._diseases = Disease.objects.filter(card=self._card).all()

    def get_diseases_short_data(self) -> list:
        return list(self._diseases.values('name', 'discovered_at', 'id'))

    def get_full_disease(self, disease_id) -> Disease:
        return self._diseases.get(id=disease_id)

    def create_new_disease(self, form_data: DiseaseForm):
        form_data = form_data.data.dict()
        form_data.pop('csrfmiddlewaretoken', None)
        new_disease = Disease.objects.create(**form_data, discovered_at=datetime.now(), card=self._card)
        return new_disease.id


class ManyMedicalCardsService:
    def __init__(self, request):
        self.patient_filtrator = PatientFilter(
            request.GET,
            queryset=CustomUser.objects.prefetch_related('card_owner') \
                .filter(role=CustomUser.RoleChoices.PATIENT) \
                .annotate(disease_count=Count('card_owner__medical_card')),
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


class TicketService:

    def __init__(self, user, doctor_id=None):
        if doctor_id is not None:
            self._selected_doctor = CustomUser.objects.get(id=doctor_id)
        self.user = user

    def get_accessible_dates(self, request):
        ticket_filter_ = TicketFilter(
            request.GET,
            queryset=Ticket.objects.filter(target=self._selected_doctor),
            request=request
        )
        accessible_dates = ticket_filter_.only_accessible()

        return accessible_dates

    def remove_old(self):
        Ticket.objects.\
            filter(owner=self.user, receipt_time__lt=datetime.now() - timedelta(minutes=30))

    def get_ticket(self, month, day, hour, minute):

        self.remove_old()

        ticket_time = datetime.now().replace(
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            second=0,
            microsecond=0,
            tzinfo=timezone.utc
        )

        print(self.user)
        amount_of_user_tickets = CustomUser.objects. \
            filter(id=self.user.id).annotate(amount_of_tickets=Count('ticket_owner')). \
            values_list('amount_of_tickets', flat=True)[0]

        if amount_of_user_tickets < 3:
            Ticket.objects.create(owner=self.user, target=self._selected_doctor, receipt_time=ticket_time)
            return
        raise IntegrityError

    def get_my_tickets(self):
        return Ticket.objects.prefetch_related('owner', 'target').filter(owner=self.user).values('receipt_time', 'target__fio')


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
