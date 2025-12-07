"""Pytest fixtures for Walk Risk API tests"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from walk_risk.api.main import app
from walk_risk.database.connection import database, get_db
from walk_risk.database.models import Base


# 테스트용 데이터베이스 URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_db():
    """테스트용 인메모리 데이터베이스 설정"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with async_session() as session:
            yield session

    # 의존성 오버라이드
    app.dependency_overrides[get_db] = override_get_db

    yield async_session

    # 정리
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(test_db):
    """비동기 테스트 클라이언트"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def authenticated_client(client, test_db):
    """인증된 테스트 클라이언트 (JWT 토큰 포함)"""
    # 테스트 유저 등록
    register_response = await client.post(
        "/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "preferred_mentor": "buffett"
        }
    )

    if register_response.status_code == 201:
        token_data = register_response.json()
        access_token = token_data.get("access_token")
    else:
        # 이미 등록된 경우 로그인
        login_response = await client.post(
            "/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        token_data = login_response.json()
        access_token = token_data.get("access_token")

    # 인증 헤더가 포함된 새 클라이언트 생성
    class AuthenticatedClient:
        def __init__(self, client, token):
            self._client = client
            self._token = token
            self._headers = {"Authorization": f"Bearer {token}"}

        async def get(self, url, **kwargs):
            headers = kwargs.pop("headers", {})
            headers.update(self._headers)
            return await self._client.get(url, headers=headers, **kwargs)

        async def post(self, url, **kwargs):
            headers = kwargs.pop("headers", {})
            headers.update(self._headers)
            return await self._client.post(url, headers=headers, **kwargs)

        async def put(self, url, **kwargs):
            headers = kwargs.pop("headers", {})
            headers.update(self._headers)
            return await self._client.put(url, headers=headers, **kwargs)

        async def delete(self, url, **kwargs):
            headers = kwargs.pop("headers", {})
            headers.update(self._headers)
            return await self._client.delete(url, headers=headers, **kwargs)

        @property
        def token(self):
            return self._token

    return AuthenticatedClient(client, access_token)


@pytest.fixture
def test_user_data():
    """테스트 유저 데이터"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "preferred_mentor": "buffett"
    }


@pytest.fixture
def test_order_data():
    """테스트 주문 데이터"""
    return {
        "symbol": "005930.KS",
        "order_type": "market",
        "side": "buy",
        "quantity": 10,
        "reason": "테스트 매수"
    }
