import pytest


@pytest.mark.django_db
def test_login_api(client, django_user_model):
    email = "test@example.com"
    password = "strong-pass-123"
    # create user (variable not used directly)
    _ = django_user_model.objects.create_user(email=email, password=password)

    url = "/api/auth/login/"
    resp = client.post(
        url, {"email": email, "password": password}, content_type="application/json"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access" in data and "refresh" in data
