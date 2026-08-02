"""Auth Endpoint Tests"""

import pytest
from fastapi import status


class TestSignup:
    """Test user signup endpoint."""

    def test_signup_success(self, client, test_user_data):
        """Test successful user signup."""
        response = client.post("/api/v1/auth/signup", json=test_user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Check response structure
        assert "user" in data
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

        # Check user data
        user = data["user"]
        assert user["email"] == test_user_data["email"].lower()
        assert user["full_name"] == test_user_data["full_name"]
        assert user["is_active"] is True

    def test_signup_duplicate_email(self, client, test_user_data):
        """Test signup with duplicate email."""
        # First signup
        client.post("/api/v1/auth/signup", json=test_user_data)

        # Second signup with same email
        response = client.post("/api/v1/auth/signup", json=test_user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"]

    def test_signup_invalid_email(self, client, test_user_data):
        """Test signup with invalid email."""
        test_user_data["email"] = "invalid-email"
        response = client.post("/api/v1/auth/signup", json=test_user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_signup_short_password(self, client, test_user_data):
        """Test signup with password < 8 chars."""
        test_user_data["password"] = "short"
        response = client.post("/api/v1/auth/signup", json=test_user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_signup_missing_fields(self, client):
        """Test signup with missing required fields."""
        response = client.post("/api/v1/auth/signup", json={})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogin:
    """Test user login endpoint."""

    def test_login_success(self, client, test_user_data):
        """Test successful login."""
        # Signup first
        client.post("/api/v1/auth/signup", json=test_user_data)

        # Login
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check response
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert data["user"]["email"] == test_user_data["email"].lower()

    def test_login_invalid_email(self, client, test_user_data):
        """Test login with non-existent email."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123",
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_invalid_password(self, client, test_user_data):
        """Test login with wrong password."""
        # Signup first
        client.post("/api/v1/auth/signup", json=test_user_data)

        # Login with wrong password
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": "WrongPassword123",
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_case_insensitive_email(self, client, test_user_data):
        """Test that email is case-insensitive."""
        # Signup
        client.post("/api/v1/auth/signup", json=test_user_data)

        # Login with different case
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"].upper(),
                "password": test_user_data["password"],
            }
        )

        assert response.status_code == status.HTTP_200_OK


class TestRefresh:
    """Test token refresh endpoint."""

    def test_refresh_success(self, client, test_user_data):
        """Test successful token refresh."""
        # Signup
        signup_response = client.post("/api/v1/auth/signup", json=test_user_data)
        refresh_token = signup_response.json()["refresh_token"]

        # Refresh
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 900  # 15 minutes

    def test_refresh_invalid_token(self, client):
        """Test refresh with invalid token."""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.token.here"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid" in response.json()["detail"]


class TestTokenUsage:
    """Test using tokens to access protected endpoints."""

    def test_access_with_valid_token(self, client, test_user_data):
        """Test accessing endpoint with valid token."""
        # Signup
        signup_response = client.post("/api/v1/auth/signup", json=test_user_data)
        access_token = signup_response.json()["access_token"]

        # Try to access protected endpoint (if we had one)
        # For now, just verify token is present in response
        assert len(access_token) > 0
        assert "." in access_token  # JWT has 3 parts separated by dots

    def test_access_without_token(self, client):
        """Test accessing protected endpoint without token."""
        # This would be tested when protected endpoints exist
        # For now, just verify basic endpoint works without auth
        response = client.get("/api/v1/")
        assert response.status_code == status.HTTP_200_OK
