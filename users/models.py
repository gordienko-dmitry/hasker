from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from hasker.settings import BASE_USER_PHOTO


class UserWithAvatar(AbstractUser):
    """add avatar to user"""
    avatar = models.ImageField("Avatar", upload_to="media/img", null=True)

    @staticmethod
    def get_user(user_id):
        """get or create user"""
        user, _ = UserWithAvatar.objects.get_or_create(id=user_id)
        return user

    def get_avatar(self):
        return self.avatar.url if self.avatar else BASE_USER_PHOTO

    def update_profile(self, email, avatar):
        """change user e-mail or avatar"""
        with transaction.atomic():
            need_to_save = False
            if self.email != email:
                self.email = email
                need_to_save = True

            if avatar:
                self.avatar = avatar
                need_to_save = True

            if need_to_save:
                self.save()
