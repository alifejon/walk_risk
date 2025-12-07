"""플레이어 API 테스트"""

import pytest


class TestPlayerProfile:
    """플레이어 프로필 API 테스트"""

    @pytest.mark.asyncio
    async def test_get_current_player(self, authenticated_client):
        """현재 플레이어 정보 조회"""
        response = await authenticated_client.get("/v1/players/me")

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "username" in data
        assert "email" in data
        assert "level" in data
        assert "experience" in data

    @pytest.mark.asyncio
    async def test_get_current_player_unauthorized(self, client):
        """인증 없이 프로필 조회 실패"""
        response = await client.get("/v1/players/me")

        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_update_player_mentor(self, authenticated_client):
        """멘토 설정 변경"""
        response = await authenticated_client.put(
            "/v1/players/me",
            json={"preferred_mentor": "lynch"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["player"]["preferred_mentor"] == "lynch"

    @pytest.mark.asyncio
    async def test_update_player_settings(self, authenticated_client):
        """플레이어 설정 변경"""
        response = await authenticated_client.put(
            "/v1/players/me",
            json={"settings": {"notifications": True, "theme": "dark"}}
        )

        assert response.status_code == 200


class TestPlayerEnergy:
    """플레이어 에너지 API 테스트"""

    @pytest.mark.asyncio
    async def test_consume_energy(self, authenticated_client):
        """에너지 소모"""
        response = await authenticated_client.post(
            "/v1/players/me/energy/consume",
            json={"amount": 10}
        )

        assert response.status_code == 200
        data = response.json()
        assert "energy" in data
        assert "max_energy" in data
        assert data["energy"] == 90  # 초기 100 - 10

    @pytest.mark.asyncio
    async def test_consume_energy_insufficient(self, authenticated_client):
        """에너지 부족"""
        response = await authenticated_client.post(
            "/v1/players/me/energy/consume",
            json={"amount": 1000}  # 보유량보다 많이
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_restore_energy(self, authenticated_client):
        """에너지 회복"""
        # 먼저 에너지 소모
        await authenticated_client.post(
            "/v1/players/me/energy/consume",
            json={"amount": 50}
        )

        # 에너지 회복
        response = await authenticated_client.post(
            "/v1/players/me/energy/restore"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["energy"] == data["max_energy"]  # 완전 회복


class TestPlayerProgress:
    """플레이어 진행도 API 테스트"""

    @pytest.mark.asyncio
    async def test_update_progress_experience(self, authenticated_client):
        """경험치 추가"""
        response = await authenticated_client.post(
            "/v1/players/me/progress",
            json={"experience_gained": 100}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["experience"] >= 100

    @pytest.mark.asyncio
    async def test_level_up(self, authenticated_client):
        """레벨업 테스트"""
        # 많은 경험치 추가하여 레벨업 유도
        response = await authenticated_client.post(
            "/v1/players/me/progress",
            json={"experience_gained": 500}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["level"] >= 2  # 레벨업 확인

    @pytest.mark.asyncio
    async def test_unlock_skill(self, authenticated_client):
        """스킬 언락"""
        response = await authenticated_client.post(
            "/v1/players/me/progress",
            json={"skills_unlocked": ["basic_analysis"]}
        )

        assert response.status_code == 200
        data = response.json()
        assert "basic_analysis" in data["unlocked_skills"]


class TestPlayerStats:
    """플레이어 통계 API 테스트"""

    @pytest.mark.asyncio
    async def test_get_stats(self, authenticated_client):
        """플레이어 통계 조회"""
        response = await authenticated_client.get("/v1/players/stats")

        assert response.status_code == 200
        data = response.json()
        assert "player_info" in data
        assert "puzzle_stats" in data
        assert "portfolio_stats" in data


class TestLeaderboard:
    """리더보드 API 테스트"""

    @pytest.mark.asyncio
    async def test_get_leaderboard(self, authenticated_client):
        """리더보드 조회"""
        response = await authenticated_client.get("/v1/players/leaderboard")

        assert response.status_code == 200
        data = response.json()
        assert "leaderboard" in data
        assert "my_rank" in data

    @pytest.mark.asyncio
    async def test_leaderboard_pagination(self, authenticated_client):
        """리더보드 페이지네이션"""
        response = await authenticated_client.get(
            "/v1/players/leaderboard",
            params={"limit": 5, "offset": 0}
        )

        assert response.status_code == 200
        data = response.json()
        assert "pagination" in data
        assert data["pagination"]["limit"] == 5


class TestPlayerSearch:
    """플레이어 검색 API 테스트"""

    @pytest.mark.asyncio
    async def test_search_by_username(self, authenticated_client):
        """사용자명으로 검색"""
        response = await authenticated_client.get(
            "/v1/players/search",
            params={"username": "test"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "count" in data

    @pytest.mark.asyncio
    async def test_search_by_class(self, authenticated_client):
        """클래스로 검색"""
        response = await authenticated_client.get(
            "/v1/players/search",
            params={"current_class": "Risk Novice"}
        )

        assert response.status_code == 200


class TestPlayerDelete:
    """플레이어 삭제 API 테스트"""

    @pytest.mark.asyncio
    async def test_delete_player(self, authenticated_client):
        """계정 삭제"""
        response = await authenticated_client.delete("/v1/players/me")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
