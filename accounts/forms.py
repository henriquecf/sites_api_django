from django.contrib.auth.forms import UserCreationForm
from django.forms import EmailField


class UserCreationFormWithEmail(UserCreationForm):
    email = EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        fields = ['username', 'email', 'password1', 'password2']