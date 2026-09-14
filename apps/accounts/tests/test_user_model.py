import pytest
from django.conf import settings
from django.contrib.auth import get_user_model

from apps.accounts.models import User


@pytest.mark.django_db
def test_custom_user_is_the_swappable_model_and_persists() -> None:
    assert settings.AUTH_USER_MODEL == "accounts.User"
    assert get_user_model() is User

    user = User.objects.create_user(username="pilot", password="not-a-real-password")  # noqa: S106

    assert User.objects.get(pk=user.pk).username == "pilot"
