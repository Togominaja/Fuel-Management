from app.core.security import create_access_token, decode_access_token


def test_create_and_decode_token():
    token = create_access_token(subject="sbravatti.nelson@gmail.com")
    payload = decode_access_token(token)
    assert payload["sub"] == "sbravatti.nelson@gmail.com"
    assert "exp" in payload
