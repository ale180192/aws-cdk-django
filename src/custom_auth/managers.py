from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)

        user.save()
        return user

    def get_by_natural_key(self, username):
        case_insensitive_username_field = f'{self.model.USERNAME_FIELD}__iexact'
        return self.get(**{case_insensitive_username_field: username})
