"""인증 API 테스트"""

import pytest
from httpx import AsyncClient


class TestAuthRegister:
    """회원가입 API 테스트"""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """정상 회원가입"""
        response = await client.post(
            "/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "securepassword123",
                "preferred_mentor": "buffett"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient):
        """중복 이메일 회원가입 실패"""
        # 첫 번째 등록
        await client.post(
            "/v1/auth/register",
            json={
                "username": "user1",
                "email": "duplicate@example.com",
                "password": "password123"
            }
        )

        # 중복 이메일로 재등록 시도
        response = await client.post(
            "/v1/auth/register",
            json={
                "username": "user2",
                "email": "duplicate@example.com",
                "password": "password456"
            }
        )

        assert response.status_code in [400, 409]

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """잘못된 이메일 형식"""
        response = await client.post(
            "/v1/auth/register",
            json={
                "username": "baduser",
                "email": "invalid-email",
                "password": "password123"
            }
        )

        assert response.status_code == 422


class TestAuthLogin:
    """로그인 API 테스트"""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user_data):
        """정상 로그인"""
        # 먼저 등록
        await client.post("/v1/auth/register", json=test_user_data)

        # 로그인
        response = await client.post(
            "/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user_data):
        """잘못된 비밀번호"""
        # 먼저 등록
        await client.post("/v1/auth/register", json=test_user_data)

        # 잘못된 비밀번호로 로그인
        response = await client.post(
            "/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": "wrongpassword"
            }
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """존재하지 않는 사용자"""
        response = await client.post(
            "/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "anypassword"
            }
        )

        assert response.status_code in [401, 404]


class TestAuthRefresh:
    """토큰 갱신 API 테스트"""

    @pytest.mark.asyncio
    async def test_refresh_success(self, client: AsyncClient, test_user_data):
        """정상 토큰 갱신"""
        # 등록하여 토큰 획득
        register_response = await client.post(
            "/v1/auth/register",
            json=test_user_data
        )
        refresh_token = register_response.json().get("refresh_token")

        # 토큰 갱신
        response = await client.post(
            "/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, client: AsyncClient):
        """잘못된 리프레시 토큰"""
        response = await client.post(
            "/v1/auth/refresh",
            json={"refresh_token": "invalid.token.here"}
        )

        assert response.status_code == 401
