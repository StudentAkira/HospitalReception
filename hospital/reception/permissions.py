from django.http import HttpResponse
from django.shortcuts import redirect

from reception.models import CustomUser


def authorized(func):
    def inner(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/login')
        return func(request, *args, **kwargs)
    return inner


def unauthorized(func):
    def inner(request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponse('You are not allowed to see this page')
        return func(request, *args, **kwargs)
    return inner


def access_permission_role(role):
    def decorator(func):
        def inner(request, *args, **kwargs):
            if request.user.role.lower() != role:
                return HttpResponse('You are not allowed to see this page')
            return func(request, *args, **kwargs)
        return inner
    return decorator


def card_owner_or_doctor(func):
    def inner(request, user_id, *args, **kwargs):
        if request.user.role == CustomUser.RoleChoices.PATIENT and request.user.id != user_id:
            return HttpResponse('You are not allowed to see this page')
        return func(request, user_id, *args, **kwargs)
    return inner
