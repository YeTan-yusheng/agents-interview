from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


def test_password_roundtrip():
    hashed = hash_password("password123")
    assert verify_password("password123", hashed) is True


def test_wrong_password_rejected():
    hashed = hash_password("password123")
    assert verify_password("wrong_password", hashed) is False


def test_same_password_produces_different_hashes():
    assert hash_password("same-pwd") != hash_password("same-pwd")


def test_token_roundtrip():
    token = create_access_token(user_id=42)
    assert decode_access_token(token) == 42


def test_tampered_token_rejected():
    token = create_access_token(user_id=42)
    assert decode_access_token(token + "123") is None
