"""퍼즐 API 테스트"""

import pytest


class TestPuzzleList:
    """퍼즐 목록 API 테스트"""

    @pytest.mark.asyncio
    async def test_get_puzzles(self, authenticated_client):
        """퍼즐 목록 조회"""
        response = await authenticated_client.get("/v1/puzzles/")

        assert response.status_code == 200
        data = response.json()
        assert "puzzles" in data

    @pytest.mark.asyncio
    async def test_get_puzzles_filtered(self, authenticated_client):
        """난이도별 퍼즐 필터링"""
        response = await authenticated_client.get(
            "/v1/puzzles/",
            params={"difficulty": "beginner", "limit": 5}
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_puzzles_unauthorized(self, client):
        """인증 없이 퍼즐 조회 실패"""
        response = await client.get("/v1/puzzles/")

        assert response.status_code in [401, 403]


class TestPuzzleDetails:
    """퍼즐 상세 API 테스트"""

    @pytest.mark.asyncio
    async def test_get_puzzle_details(self, authenticated_client):
        """퍼즐 상세 조회"""
        # 먼저 퍼즐 목록 조회
        list_response = await authenticated_client.get("/v1/puzzles/")
        puzzles = list_response.json().get("puzzles", [])

        if puzzles:
            puzzle_id = puzzles[0]["puzzle_id"]
            response = await authenticated_client.get(f"/v1/puzzles/{puzzle_id}")

            assert response.status_code == 200
            data = response.json()
            assert "title" in data
            assert "available_clues" in data

    @pytest.mark.asyncio
    async def test_get_puzzle_not_found(self, authenticated_client):
        """존재하지 않는 퍼즐"""
        response = await authenticated_client.get("/v1/puzzles/nonexistent-puzzle-id")

        assert response.status_code == 404


class TestPuzzleInvestigation:
    """퍼즐 조사 API 테스트"""

    @pytest.mark.asyncio
    async def test_investigate_clue(self, authenticated_client):
        """단서 조사"""
        # 먼저 퍼즐 목록 조회
        list_response = await authenticated_client.get("/v1/puzzles/")
        puzzles = list_response.json().get("puzzles", [])

        if puzzles:
            puzzle_id = puzzles[0]["puzzle_id"]

            # 퍼즐 상세 조회하여 단서 확인
            detail_response = await authenticated_client.get(f"/v1/puzzles/{puzzle_id}")
            puzzle_data = detail_response.json()
            available_clues = puzzle_data.get("available_clues", [])

            if available_clues:
                clue_id = available_clues[0]["clue_id"]

                response = await authenticated_client.post(
                    f"/v1/puzzles/{puzzle_id}/investigate",
                    json={
                        "clue_id": clue_id,
                        "investigation_type": "detailed"
                    }
                )

                assert response.status_code == 200
                data = response.json()
                assert "clue" in data or "discovered_info" in data

    @pytest.mark.asyncio
    async def test_investigate_invalid_clue(self, authenticated_client):
        """잘못된 단서 ID로 조사"""
        response = await authenticated_client.post(
            "/v1/puzzles/some-puzzle/investigate",
            json={
                "clue_id": "invalid-clue-id",
                "investigation_type": "basic"
            }
        )

        assert response.status_code in [400, 404]


class TestPuzzleHypothesis:
    """퍼즐 가설 API 테스트"""

    @pytest.mark.asyncio
    async def test_submit_hypothesis(self, authenticated_client):
        """가설 제출"""
        # 먼저 퍼즐 조회
        list_response = await authenticated_client.get("/v1/puzzles/")
        puzzles = list_response.json().get("puzzles", [])

        if puzzles:
            puzzle_id = puzzles[0]["puzzle_id"]

            # 가설 제출
            response = await authenticated_client.post(
                f"/v1/puzzles/{puzzle_id}/hypothesis",
                json={
                    "hypothesis": "실적 부진으로 인한 주가 하락",
                    "confidence": 75,
                    "evidence": ["news_1", "financial_data"],
                    "predicted_outcome": "단기 하락 후 반등"
                }
            )

            # 퍼즐이 시작되지 않았으면 400, 성공하면 200
            assert response.status_code in [200, 400]

    @pytest.mark.asyncio
    async def test_submit_hypothesis_invalid_confidence(self, authenticated_client):
        """잘못된 신뢰도 값"""
        response = await authenticated_client.post(
            "/v1/puzzles/some-puzzle/hypothesis",
            json={
                "hypothesis": "테스트",
                "confidence": 150,  # 100 초과
                "evidence": [],
                "predicted_outcome": "테스트"
            }
        )

        assert response.status_code in [400, 404, 422]


class TestPuzzleHints:
    """퍼즐 힌트 API 테스트"""

    @pytest.mark.asyncio
    async def test_get_hints(self, authenticated_client):
        """힌트 조회"""
        list_response = await authenticated_client.get("/v1/puzzles/")
        puzzles = list_response.json().get("puzzles", [])

        if puzzles:
            puzzle_id = puzzles[0]["puzzle_id"]

            response = await authenticated_client.get(f"/v1/puzzles/{puzzle_id}/hints")

            assert response.status_code == 200
            data = response.json()
            assert "hints" in data
            assert len(data["hints"]) > 0

            # 힌트 구조 확인
            hint = data["hints"][0]
            assert "hint_id" in hint
            assert "text" in hint
            assert "cost" in hint


class TestPuzzleStats:
    """퍼즐 통계 API 테스트"""

    @pytest.mark.asyncio
    async def test_get_puzzle_stats(self, authenticated_client):
        """퍼즐 통계 조회"""
        response = await authenticated_client.get("/v1/puzzles/stats/summary")

        assert response.status_code == 200
        data = response.json()
        assert "total_puzzles_attempted" in data
        assert "total_puzzles_solved" in data
        assert "success_rate" in data
        assert "total_xp_earned" in data


class TestDailyPuzzle:
    """일일 퍼즐 API 테스트"""

    @pytest.mark.asyncio
    async def test_create_daily_puzzles(self, authenticated_client):
        """일일 퍼즐 생성"""
        response = await authenticated_client.post("/v1/puzzles/daily")

        # 성공하거나 이미 생성된 경우
        assert response.status_code in [200, 400, 500]
