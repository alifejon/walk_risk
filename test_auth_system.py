#!/usr/bin/env python3
"""
인증 시스템 테스트 스크립트
Tests the authentication system endpoints including register, login, and refresh token functionality.
"""

import asyncio
import aiohttp
import json
import subprocess
import time
import signal
import os
from contextlib import asynccontextmanager


class APITestServer:
    """API 서버 관리 클래스"""

    def __init__(self):
        self.process = None
        self.base_url = "http://localhost:8000"

    async def start(self):
        """API 서버 시작"""
        try:
            # API 서버를 백그라운드에서 시작
            self.process = subprocess.Popen([
                "uv", "run", "python", "api_server.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # 서버가 시작될 때까지 대기
            print("🚀 API 서버 시작 중...")
            await asyncio.sleep(3)

            # 서버 헬스체크
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(f"{self.base_url}/") as response:
                        if response.status == 200:
                            print("✅ API 서버가 성공적으로 시작되었습니다")
                            return True
                except aiohttp.ClientConnectorError:
                    print("❌ API 서버 연결 실패")
                    return False

        except Exception as e:
            print(f"❌ API 서버 시작 실패: {e}")
            return False

    async def stop(self):
        """API 서버 중지"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            print("🛑 API 서버가 중지되었습니다")


class AuthSystemTester:
    """인증 시스템 테스터"""

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_user = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "preferred_mentor": "buffett"
        }
        self.access_token = None
        self.refresh_token = None

    async def test_user_registration(self, session):
        """사용자 등록 테스트"""
        print("\n📝 사용자 등록 테스트...")

        try:
            async with session.post(
                f"{self.base_url}/v1/auth/register",
                json=self.test_user
            ) as response:

                if response.status == 200:
                    data = await response.json()
                    self.access_token = data.get("access_token")
                    self.refresh_token = data.get("refresh_token")

                    print(f"✅ 사용자 등록 성공!")
                    print(f"   - 사용자 ID: {data.get('user_id')}")
                    print(f"   - 사용자명: {data.get('username')}")
                    print(f"   - 이메일: {data.get('email')}")
                    print(f"   - 토큰 만료시간: {data.get('expires_in')}초")
                    return True
                else:
                    error_data = await response.text()
                    print(f"❌ 등록 실패 (Status: {response.status}): {error_data}")
                    return False

        except Exception as e:
            print(f"❌ 등록 테스트 중 오류: {e}")
            return False

    async def test_user_login(self, session):
        """사용자 로그인 테스트"""
        print("\n🔐 사용자 로그인 테스트...")

        login_data = {
            "email": self.test_user["email"],
            "password": self.test_user["password"]
        }

        try:
            async with session.post(
                f"{self.base_url}/v1/auth/login",
                json=login_data
            ) as response:

                if response.status == 200:
                    data = await response.json()
                    self.access_token = data.get("access_token")
                    self.refresh_token = data.get("refresh_token")

                    print(f"✅ 로그인 성공!")
                    print(f"   - 사용자 ID: {data.get('user_id')}")
                    print(f"   - 사용자명: {data.get('username')}")
                    print(f"   - 토큰 만료시간: {data.get('expires_in')}초")
                    return True
                else:
                    error_data = await response.text()
                    print(f"❌ 로그인 실패 (Status: {response.status}): {error_data}")
                    return False

        except Exception as e:
            print(f"❌ 로그인 테스트 중 오류: {e}")
            return False

    async def test_token_refresh(self, session):
        """토큰 갱신 테스트"""
        print("\n🔄 토큰 갱신 테스트...")

        if not self.refresh_token:
            print("❌ 리프레시 토큰이 없습니다")
            return False

        refresh_data = {"refresh_token": self.refresh_token}

        try:
            async with session.post(
                f"{self.base_url}/v1/auth/refresh",
                json=refresh_data
            ) as response:

                if response.status == 200:
                    data = await response.json()
                    old_token = self.access_token
                    self.access_token = data.get("access_token")

                    print(f"✅ 토큰 갱신 성공!")
                    print(f"   - 새 토큰 만료시간: {data.get('expires_in')}초")
                    print(f"   - 토큰 변경됨: {'예' if old_token != self.access_token else '아니오'}")
                    return True
                else:
                    error_data = await response.text()
                    print(f"❌ 토큰 갱신 실패 (Status: {response.status}): {error_data}")
                    return False

        except Exception as e:
            print(f"❌ 토큰 갱신 테스트 중 오류: {e}")
            return False

    async def test_protected_endpoint(self, session):
        """보호된 엔드포인트 접근 테스트"""
        print("\n🔒 보호된 엔드포인트 테스트...")

        if not self.access_token:
            print("❌ 액세스 토큰이 없습니다")
            return False

        headers = {"Authorization": f"Bearer {self.access_token}"}

        try:
            # 플레이어 정보 조회 테스트 (인증 필요)
            async with session.get(
                f"{self.base_url}/v1/players/profile",
                headers=headers
            ) as response:

                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 보호된 엔드포인트 접근 성공!")
                    print(f"   - 플레이어 레벨: {data.get('level', 'N/A')}")
                    print(f"   - 경험치: {data.get('experience', 'N/A')}")
                    return True
                else:
                    error_data = await response.text()
                    print(f"❌ 보호된 엔드포인트 접근 실패 (Status: {response.status}): {error_data}")
                    return False

        except Exception as e:
            print(f"❌ 보호된 엔드포인트 테스트 중 오류: {e}")
            return False

    async def test_logout(self, session):
        """로그아웃 테스트"""
        print("\n👋 로그아웃 테스트...")

        try:
            async with session.post(f"{self.base_url}/v1/auth/logout") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 로그아웃 성공: {data.get('message')}")
                    return True
                else:
                    error_data = await response.text()
                    print(f"❌ 로그아웃 실패 (Status: {response.status}): {error_data}")
                    return False

        except Exception as e:
            print(f"❌ 로그아웃 테스트 중 오류: {e}")
            return False

    async def run_all_tests(self):
        """모든 인증 테스트 실행"""
        print("🧪 InvestWalk 인증 시스템 테스트 시작")
        print("=" * 50)

        results = []

        async with aiohttp.ClientSession() as session:
            # 1. 사용자 등록
            results.append(await self.test_user_registration(session))

            # 2. 사용자 로그인 (동일한 사용자로 다시 로그인)
            results.append(await self.test_user_login(session))

            # 3. 토큰 갱신
            results.append(await self.test_token_refresh(session))

            # 4. 보호된 엔드포인트 접근
            results.append(await self.test_protected_endpoint(session))

            # 5. 로그아웃
            results.append(await self.test_logout(session))

        # 결과 요약
        print("\n" + "=" * 50)
        print("🎯 테스트 결과 요약")
        print(f"✅ 성공: {sum(results)}/5")
        print(f"❌ 실패: {5 - sum(results)}/5")

        if all(results):
            print("🎉 모든 인증 테스트가 성공했습니다!")
        else:
            print("⚠️  일부 테스트가 실패했습니다. 로그를 확인하세요.")

        return all(results)


async def main():
    """메인 테스트 실행"""
    server = APITestServer()
    tester = AuthSystemTester()

    # 서버 시작
    if not await server.start():
        print("서버 시작 실패로 테스트를 중단합니다.")
        return False

    try:
        # 인증 테스트 실행
        success = await tester.run_all_tests()
        return success

    finally:
        # 서버 정리
        await server.stop()


if __name__ == "__main__":
    # 비동기 메인 실행
    try:
        success = asyncio.run(main())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 사용자에 의해 테스트가 중단되었습니다.")
        exit(1)