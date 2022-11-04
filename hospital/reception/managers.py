from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, username=None, password=None, fio=None, role=None):
        if not password or not username:
            return
        user = self.model(
            username=username,
            fio=fio,
            role=role,
        )
        user.set_password(password)
        user.save()
        return user
