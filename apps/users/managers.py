from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a general user with the given email and password.
        """
        if not email:
            raise ValueError("User must have an email")
        email = self.normalize_email(email=email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        """
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields["is_superuser"]:
            raise ValueError("User must have set is_superuser=True")
        if not extra_fields["is_staff"]:
            raise ValueError("User must have set is_staff=True")

        return self.create_user(email=email, password=password, **extra_fields)
