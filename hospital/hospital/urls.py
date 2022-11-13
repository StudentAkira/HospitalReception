from django.urls import include, path
from django.contrib import admin
from django.urls import path
from reception.views import patient_view, \
    doctor_view, logout_view, \
    register_view, login_view, \
    card_content_view, disease_view, \
    many_cards_view, select_doctor_view, \
    select_datetime_view, get_ticket_view, \
    get_my_tickets, create_disease_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('patient/', patient_view, name='patient'),
    path('doctor/', doctor_view, name='doctor'),
    path('card/patient/<int:user_id>/', card_content_view, name='card'),
    path('cards/', many_cards_view, name='cards'),
    path('card/patient/<int:user_id>/disease/<int:disease_id>/', disease_view, name='disease'),
    path('doctors/', select_doctor_view, name='select_doctor'),
    path('doctor-date-time-appointment/<int:doctor_id>/', select_datetime_view, name='select_datetime'),
    path('get-ticket/<int:doctor_id>/<int:month>/<int:day>/<int:hour>/<int:minute>/', get_ticket_view, name='get_ticket'),
    path('my-tickets/', get_my_tickets, name='my_tickets'),
    path('new-disease/<int:user_id>/', create_disease_view, name='new_disease'),

    path('__debug__/', include('debug_toolbar.urls')),#debug_tool_bar
]
