from app.application.auth.passwords import hash_password, verify_password


def test_password_hash_can_be_verified() -> None:
    password = "correct horse battery staple"

    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash) is True


def test_wrong_password_is_rejected() -> None:
    password_hash = hash_password("correct horse battery staple")

    assert verify_password("wrong password", password_hash) is False
