"""포트폴리오 API 테스트"""

import pytest


class TestPortfolioBasic:
    """포트폴리오 기본 API 테스트"""

    @pytest.mark.asyncio
    async def test_get_portfolio(self, authenticated_client):
        """포트폴리오 조회 (자동 생성 포함)"""
        response = await authenticated_client.get("/v1/portfolio/")

        assert response.status_code == 200
        data = response.json()
        assert "portfolio_id" in data
        assert "total_value" in data
        assert "cash_balance" in data
        assert "holdings" in data

    @pytest.mark.asyncio
    async def test_get_portfolio_unauthorized(self, client):
        """인증 없이 포트폴리오 조회 실패"""
        response = await client.get("/v1/portfolio/")

        assert response.status_code in [401, 403]


class TestPortfolioOrders:
    """주문 API 테스트"""

    @pytest.mark.asyncio
    async def test_place_buy_order(self, authenticated_client, test_order_data):
        """매수 주문"""
        response = await authenticated_client.post(
            "/v1/portfolio/orders",
            json=test_order_data
        )

        assert response.status_code == 200
        data = response.json()
        assert "order_id" in data
        assert data["status"] == "filled"

    @pytest.mark.asyncio
    async def test_place_sell_order(self, authenticated_client, test_order_data):
        """매도 주문"""
        # 먼저 매수
        await authenticated_client.post(
            "/v1/portfolio/orders",
            json=test_order_data
        )

        # 매도
        sell_order = test_order_data.copy()
        sell_order["side"] = "sell"
        sell_order["quantity"] = 5  # 매수한 것보다 적게

        response = await authenticated_client.post(
            "/v1/portfolio/orders",
            json=sell_order
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_order_insufficient_cash(self, authenticated_client):
        """현금 부족 주문 실패"""
        # 엄청 큰 금액의 주문
        response = await authenticated_client.post(
            "/v1/portfolio/orders",
            json={
                "symbol": "005930.KS",
                "order_type": "market",
                "side": "buy",
                "quantity": 1000000  # 매우 많은 수량
            }
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_order_insufficient_shares(self, authenticated_client):
        """보유 주식 부족 매도 실패"""
        response = await authenticated_client.post(
            "/v1/portfolio/orders",
            json={
                "symbol": "005930.KS",
                "order_type": "market",
                "side": "sell",
                "quantity": 100  # 보유하지 않은 수량
            }
        )

        assert response.status_code == 400


class TestPortfolioPerformance:
    """포트폴리오 성과 API 테스트"""

    @pytest.mark.asyncio
    async def test_get_performance(self, authenticated_client):
        """성과 분석 조회"""
        response = await authenticated_client.get("/v1/portfolio/performance")

        assert response.status_code == 200
        data = response.json()
        assert "performance" in data
        assert "trading_stats" in data
        assert "allocation" in data
        assert "risk_metrics" in data

    @pytest.mark.asyncio
    async def test_performance_metrics(self, authenticated_client):
        """성과 지표 확인"""
        response = await authenticated_client.get("/v1/portfolio/performance")
        data = response.json()

        # 성과 지표 확인
        assert "total_return" in data["performance"]
        assert "realized_pnl" in data["performance"]
        assert "unrealized_pnl" in data["performance"]

        # 거래 통계 확인
        assert "total_trades" in data["trading_stats"]
        assert "buy_trades" in data["trading_stats"]
        assert "sell_trades" in data["trading_stats"]


class TestPortfolioHistory:
    """거래 내역 API 테스트"""

    @pytest.mark.asyncio
    async def test_get_history(self, authenticated_client):
        """거래 내역 조회"""
        response = await authenticated_client.get("/v1/portfolio/history")

        assert response.status_code == 200
        data = response.json()
        assert "trades" in data
        assert "total" in data
        assert "has_more" in data

    @pytest.mark.asyncio
    async def test_history_with_filter(self, authenticated_client, test_order_data):
        """필터링된 거래 내역"""
        # 먼저 주문 실행
        await authenticated_client.post(
            "/v1/portfolio/orders",
            json=test_order_data
        )

        # 특정 종목 필터링
        response = await authenticated_client.get(
            "/v1/portfolio/history",
            params={"symbol": test_order_data["symbol"]}
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_history_pagination(self, authenticated_client):
        """거래 내역 페이지네이션"""
        response = await authenticated_client.get(
            "/v1/portfolio/history",
            params={"limit": 5, "offset": 0}
        )

        assert response.status_code == 200
        data = response.json()
        assert "pagination" in data


class TestPortfolioPositions:
    """포지션 API 테스트"""

    @pytest.mark.asyncio
    async def test_get_positions(self, authenticated_client):
        """포지션 조회"""
        response = await authenticated_client.get("/v1/portfolio/positions")

        assert response.status_code == 200
        data = response.json()
        assert "positions" in data
        assert "summary" in data

    @pytest.mark.asyncio
    async def test_positions_with_holdings(self, authenticated_client, test_order_data):
        """보유 종목이 있을 때 포지션"""
        # 먼저 매수
        await authenticated_client.post(
            "/v1/portfolio/orders",
            json=test_order_data
        )

        response = await authenticated_client.get("/v1/portfolio/positions")

        assert response.status_code == 200
        data = response.json()
        assert len(data["positions"]) > 0

        # 포지션 상세 확인
        position = data["positions"][0]
        assert "symbol" in position
        assert "quantity" in position
        assert "profit_loss" in position
        assert "days_held" in position


class TestPortfolioAllocation:
    """자산 배분 API 테스트"""

    @pytest.mark.asyncio
    async def test_get_allocation(self, authenticated_client):
        """자산 배분 조회"""
        response = await authenticated_client.get("/v1/portfolio/allocation")

        assert response.status_code == 200
        data = response.json()
        assert "asset_allocation" in data
        assert "sector_allocation" in data
        assert "recommendations" in data

    @pytest.mark.asyncio
    async def test_allocation_recommendations(self, authenticated_client):
        """배분 추천 확인"""
        response = await authenticated_client.get("/v1/portfolio/allocation")
        data = response.json()

        # 추천이 있는지 확인
        assert len(data["recommendations"]) > 0


class TestPortfolioRebalance:
    """리밸런싱 API 테스트"""

    @pytest.mark.asyncio
    async def test_suggest_rebalancing(self, authenticated_client):
        """리밸런싱 제안"""
        response = await authenticated_client.post(
            "/v1/portfolio/rebalance",
            json={
                "target_allocation": {
                    "Technology": 50,
                    "Healthcare": 30,
                    "Cash": 20
                }
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "rebalancing_needed" in data
        assert "current_allocation" in data
        assert "target_allocation" in data
        assert "suggested_trades" in data
        assert "estimated_cost" in data

    @pytest.mark.asyncio
    async def test_rebalancing_with_positions(self, authenticated_client, test_order_data):
        """포지션이 있을 때 리밸런싱"""
        # 먼저 매수
        await authenticated_client.post(
            "/v1/portfolio/orders",
            json=test_order_data
        )

        response = await authenticated_client.post(
            "/v1/portfolio/rebalance",
            json={
                "target_allocation": {
                    "Technology": 30,
                    "Healthcare": 40,
                    "Materials": 30
                }
            }
        )

        assert response.status_code == 200
        data = response.json()
        # 포지션이 있으면 리밸런싱 필요할 수 있음
        assert "suggested_trades" in data
