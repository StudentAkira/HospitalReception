from django.http import HttpResponse
from django.shortcuts import redirect


def authorized(func):
    def inner(request):
        if not request.user.is_authenticated:
            return redirect('/login')
        return func(request)
    return inner


def unauthorized(func):
    def inner(request):
        if request.user.is_authenticated:
            return HttpResponse('You are not allowed to see this page')
        return func(request)
    return inner


def access_permission_role(role):
    def decorator(func):
        def inner(request):
            print(request.user.role, role)
            if request.user.role != role:
                return HttpResponse('You are not allowed to see this page')
            return func(request)
        return inner
    return decorator
