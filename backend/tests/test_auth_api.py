from backend.security import create_access_token


def test_signup_creates_user_with_empty_defaults(client, user_credentials):
    response = client.post("/signup", json=user_credentials)

    assert response.status_code == 201
    payload = response.json()
    assert payload["email"] == user_credentials["email"]
    assert payload["preferences"] == []
    assert payload["allergies"] == []


def test_signup_rejects_duplicate_email(client, user_credentials):
    first_response = client.post("/signup", json=user_credentials)
    second_response = client.post("/signup", json=user_credentials)

    assert first_response.status_code == 201
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Email already registered"


def test_login_returns_bearer_token(client, create_user, user_credentials):
    create_user(user_credentials["email"], user_credentials["password"])

    response = client.post("/login", json=user_credentials)

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert isinstance(payload["access_token"], str)
    assert payload["access_token"]


def test_login_rejects_invalid_password(client, create_user, user_credentials):
    create_user(user_credentials["email"], user_credentials["password"])

    response = client.post(
        "/login",
        json={"email": user_credentials["email"], "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_token_endpoint_accepts_oauth_form(client, create_user, user_credentials):
    create_user(user_credentials["email"], user_credentials["password"])

    response = client.post(
        "/token",
        data={"username": user_credentials["email"], "password": user_credentials["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]


def test_me_returns_current_profile(client, auth_headers):
    response = client.get("/me", headers=auth_headers())

    assert response.status_code == 200
    payload = response.json()
    assert payload["email"] == "tester@example.com"
    assert payload["preferences"] == []
    assert payload["allergies"] == []


def test_me_rejects_invalid_token(client):
    response = client.get("/me", headers={"Authorization": "Bearer not-a-real-token"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_me_rejects_expired_token(client, create_user, user_credentials):
    create_user(user_credentials["email"], user_credentials["password"])
    expired_token = create_access_token({"sub": user_credentials["email"]}, expires_minutes=-1)

    response = client.get("/me", headers={"Authorization": f"Bearer {expired_token}"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_me_rejects_tampered_token(client, create_user, user_credentials):
    create_user(user_credentials["email"], user_credentials["password"])
    valid_token = create_access_token({"sub": user_credentials["email"]})
    tampered_token = f"{valid_token}tampered"

    response = client.get("/me", headers={"Authorization": f"Bearer {tampered_token}"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_profile_update_persists_preferences_and_allergies(client, auth_headers):
    response = client.put(
        "/me",
        headers=auth_headers(),
        json={
            "preferences": ["vegetarian", "low sugar"],
            "allergies": ["peanut", "milk"],
        },
    )

    assert response.status_code == 200
    updated_profile = response.json()
    assert updated_profile["preferences"] == ["vegetarian", "low sugar"]
    assert updated_profile["allergies"] == ["peanut", "milk"]

    follow_up = client.get("/me", headers=auth_headers())
    assert follow_up.status_code == 200
    persisted_profile = follow_up.json()
    assert persisted_profile["preferences"] == ["vegetarian", "low sugar"]
    assert persisted_profile["allergies"] == ["peanut", "milk"]


def test_login_endpoint_enforces_rate_limit(client, create_user, user_credentials):
    create_user(user_credentials["email"], user_credentials["password"])

    responses = [
        client.post("/login", json=user_credentials)
        for _ in range(6)
    ]

    assert [response.status_code for response in responses[:5]] == [200, 200, 200, 200, 200]
    assert responses[5].status_code == 429
    assert responses[5].json()["detail"] == "Rate limit exceeded. Please try again later."
    assert responses[5].headers["Retry-After"]
