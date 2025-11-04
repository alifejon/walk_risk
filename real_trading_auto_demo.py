#!/usr/bin/env python3
"""Real Trading Auto Demo - 실시간 모의투자 시스템 자동 데모"""

import asyncio
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from walk_risk.models.portfolio.real_portfolio import RealPortfolio
from walk_risk.core.trading.order_system import order_engine, OrderRequest, OrderSide, OrderType
from walk_risk.data.market_data.yahoo_finance import yahoo_finance
from walk_risk.ai.real_time_advisor import real_time_advisor
from walk_risk.models.player.base import Player
from walk_risk.utils.logger import setup_logger

logger = setup_logger(__name__)
console = Console()


class RealTradingAutoDemo:
    """실시간 모의투자 자동 데모"""
    
    def __init__(self):
        self.console = console
        self.portfolio = None
        self.player = None
        
    async def run_demo(self):
        """자동 데모 실행"""
        try:
            self._show_intro()
            await asyncio.sleep(2)
            
            # 플레이어 생성
            self.player = Player(
                id="real_trading_demo",
                name="실전 투자자",
                level=10,
                experience=1000,
                portfolio_value=10_000_000
            )
            
            # 포트폴리오 생성
            self.portfolio = RealPortfolio(
                portfolio_id="demo_portfolio_001",
                owner_id=self.player.id,
                initial_cash=10_000_000,  # 1천만원
                commission_rate=0.0015  # 0.15% 수수료
            )
            
            self.console.print("[green]✅ 실시간 모의투자 시스템 초기화 완료![/green]\n")
            await asyncio.sleep(1)
            
            # 데모 시나리오 실행
            await self._demo_scenario()
            
        except Exception as e:
            logger.error(f"데모 실행 오류: {e}", exc_info=True)
            self.console.print(f"[red]❌ 오류 발생: {e}[/red]")
            
    def _show_intro(self):
        """인트로 화면"""
        intro_text = """
[bold yellow]📈 Walk Risk: 실시간 모의투자 시스템[/bold yellow]
[bold cyan]자동 데모 모드[/bold cyan]

[white]실제 시장 데이터로 모의투자를 자동으로 체험해보세요![/white]

🔥 데모 시나리오:
• 시장 데이터 수집 및 분석
• AI 멘토 조언 생성
• 삼성전자 모의 매수
• 포트폴리오 성과 분석
• 리스크 관리 조언

💵 시작 자금: 1,000만원
        """
        
        panel = Panel(
            intro_text,
            title="🎆 실시간 모의투자 자동 데모 🎆",
            border_style="bright_green",
            box=box.DOUBLE
        )
        self.console.print(panel)
        
    async def _demo_scenario(self):
        """데모 시나리오 실행"""
        # 1. 시장 데이터 수집
        await self._step_market_data()
        await asyncio.sleep(2)
        
        # 2. AI 멘토 조언
        await self._step_ai_advice()
        await asyncio.sleep(2)
        
        # 3. 주식 매수
        await self._step_buy_stock()
        await asyncio.sleep(3)
        
        # 4. 포트폴리오 현황
        await self._step_portfolio_status()
        await asyncio.sleep(2)
        
        # 5. 시장 분석
        await self._step_market_analysis()
        await asyncio.sleep(2)
        
        # 6. 최종 성과
        await self._step_final_results()
        
    async def _step_market_data(self):
        """단계 1: 시장 데이터 수집"""
        self.console.print("[bold yellow]📈 1단계: 시장 데이터 수집 중...[/bold yellow]\n")
        
        # 시장 지수
        market_summary = await yahoo_finance.get_market_summary()
        if market_summary:
            market_table = Table(title="🏆 한국 주식 시장 현황", box=box.ROUNDED)
            market_table.add_column("지수", style="cyan")
            market_table.add_column("현재값", justify="right")
            market_table.add_column("전일대비", justify="right")
            market_table.add_column("변동률", justify="right")
            
            kospi_color = "green" if market_summary.kospi_change > 0 else "red"
            kosdaq_color = "green" if market_summary.kosdaq_change > 0 else "red"
            
            market_table.add_row(
                "KOSPI",
                f"{market_summary.kospi_index:.2f}",
                f"[{kospi_color}]{market_summary.kospi_change:+.2f}[/{kospi_color}]",
                f"[{kospi_color}]{market_summary.kospi_change_percent:+.2f}%[/{kospi_color}]"
            )
            market_table.add_row(
                "KOSDAQ",
                f"{market_summary.kosdaq_index:.2f}",
                f"[{kosdaq_color}]{market_summary.kosdaq_change:+.2f}[/{kosdaq_color}]",
                f"[{kosdaq_color}]{market_summary.kosdaq_change_percent:+.2f}%[/{kosdaq_color}]"
            )
            
            self.console.print(market_table)
            self.console.print(f"\n[dim]시장 심리: {market_summary.market_sentiment}[/dim]")
        else:
            self.console.print("[red]❌ 시장 데이터 수집 실패[/red]")
            
        # 인기 주식 3개
        popular_stocks = ["005930.KS", "035420.KS", "000660.KS"]  # 삼성전자, 네이버, SK하이닉스
        stocks_data = await yahoo_finance.get_multiple_stocks(popular_stocks)
        
        if stocks_data:
            stocks_table = Table(title="📊 주요 주식 현황", box=box.SIMPLE)
            stocks_table.add_column("종목", style="cyan")
            stocks_table.add_column("현재가", justify="right")
            stocks_table.add_column("전일대비", justify="right")
            stocks_table.add_column("변동률", justify="right")
            
            for symbol, stock in stocks_data.items():
                if stock:
                    change_color = "green" if stock.is_gain else "red"
                    stocks_table.add_row(
                        stock.name,
                        f"{stock.current_price:,.0f}원",
                        f"[{change_color}]{stock.change:+,.0f}[/{change_color}]",
                        f"[{change_color}]{stock.change_percent:+.2f}%[/{change_color}]"
                    )
                    
            self.console.print(stocks_table)
            self.console.print("\n✅ 시장 데이터 수집 완료")
        else:
            self.console.print("[red]❌ 주식 데이터 수집 실패[/red]")
            
    async def _step_ai_advice(self):
        """단계 2: AI 멘토 조언"""
        self.console.print("\n[bold yellow]🤖 2단계: AI 멘토 조언 생성 중...[/bold yellow]\n")
        
        # 실시간 분석 수행
        new_advice = await real_time_advisor.analyze_and_advise(self.portfolio, force_analysis=True)
        
        if new_advice:
            self.console.print(f"[green]✅ {len(new_advice)}개의 새로운 조언이 생성되었습니다![/green]\n")
            
            # 최신 조언 표시
            latest_advice = new_advice[-1]
            priority_color = {
                "urgent": "red",
                "high": "yellow", 
                "medium": "cyan",
                "low": "dim"
            }.get(latest_advice.priority.value, "white")
            
            advice_panel = Panel(
                latest_advice.message,
                title=f"[{priority_color}]{latest_advice.title}[/{priority_color}]",
                border_style=priority_color
            )
            self.console.print(advice_panel)
        else:
            # 기본 조언 생성
            default_advice = Panel(
                """
🏛️ 워런 버핏: "투자를 시작하려는 초보자에게 기본 조언을 드립니다."

📊 초보자를 위한 기본 원칙:
• 이해할 수 있는 기업에 투자하세요
• 장기적인 관점으로 접근하세요
• 분산투자를 통해 리스크를 줄이세요
• 감정이 아닌 논리에 따라 판단하세요

좋은 시작입니다. 천천히 하지만 꿀끈히 나아가세요.
                """.strip(),
                title="🏛️ 버핏 멘토의 초보자 가이드",
                border_style="yellow"
            )
            self.console.print(default_advice)
            
    async def _step_buy_stock(self):
        """단계 3: 주식 매수 (삼성전자)"""
        self.console.print("\n[bold green]💰 3단계: 삼성전자 모의 매수 중...[/bold green]\n")
        
        symbol = "005930.KS"  # 삼성전자
        quantity = 10  # 10주
        
        # 주식 정보 확인
        stock_data = await yahoo_finance.get_stock_data(symbol)
        if stock_data:
            stock_info = Panel(
                f"""
종목: {stock_data.name}
현재가: {stock_data.current_price:,.0f}원
전일대비: {stock_data.formatted_change}
매수 수량: {quantity}주
예상 금액: {quantity * stock_data.current_price:,.0f}원
                """.strip(),
                title=f"📊 {stock_data.name} 매수 정보",
                border_style="green"
            )
            self.console.print(stock_info)
            
            # 매수 실행
            self.console.print("\n[yellow]매수 주문 실행 중...[/yellow]")
            
            success, message, transaction = await self.portfolio.buy_stock(symbol, quantity)
            
            if success:
                self.console.print(f"[green]✅ {message}[/green]")
                if transaction:
                    self.console.print(f"[dim]거래 ID: {transaction.id}[/dim]")
                    self.console.print(f"[dim]수수료: {transaction.commission:,.0f}원[/dim]")
            else:
                self.console.print(f"[red]❌ {message}[/red]")
        else:
            self.console.print("[red]❌ 주식 정보를 가져올 수 없습니다.[/red]")
            
    async def _step_portfolio_status(self):
        """단계 4: 포트폴리오 현황"""
        self.console.print("\n[bold cyan]💼 4단계: 포트폴리오 현황 업데이트 중...[/bold cyan]\n")
        
        # 가격 업데이트
        updated_count = await self.portfolio.update_all_prices()
        self.console.print(f"✅ {updated_count}개 종목 가격 업데이트 완료\n")
        
        # 전체 요약
        summary_table = Table(title="📊 포트폴리오 요약", box=box.ROUNDED)
        summary_table.add_column("항목", style="cyan")
        summary_table.add_column("값", style="white")
        
        summary_table.add_row("총 자산", f"{self.portfolio.total_portfolio_value:,.0f}원")
        summary_table.add_row("현금", f"{self.portfolio.cash:,.0f}원")
        summary_table.add_row("주식 시가", f"{self.portfolio.total_market_value:,.0f}원")
        summary_table.add_row("평가손익", f"{self.portfolio.unrealized_pnl:+,.0f}원")
        summary_table.add_row("총 수익률", f"{self.portfolio.total_return_percent:+.2f}%")
        
        self.console.print(summary_table)
        
        # 보유 종목
        if self.portfolio.positions:
            positions_table = Table(title="📊 보유 종목", box=box.SIMPLE)
            positions_table.add_column("종목", style="cyan")
            positions_table.add_column("수량", justify="right")
            positions_table.add_column("평균단가", justify="right")
            positions_table.add_column("현재가", justify="right")
            positions_table.add_column("평가손익", justify="right")
            positions_table.add_column("수익률", justify="right")
            
            for symbol, position in self.portfolio.positions.items():
                pnl_color = "green" if position.is_profit else "red"
                positions_table.add_row(
                    position.name,
                    f"{position.quantity:.0f}주",
                    f"{position.average_price:,.0f}원",
                    f"{position.current_price:,.0f}원",
                    f"[{pnl_color}]{position.unrealized_pnl:+,.0f}원[/{pnl_color}]",
                    f"[{pnl_color}]{position.unrealized_pnl_percent:+.2f}%[/{pnl_color}]"
                )
                
            self.console.print(positions_table)
            
    async def _step_market_analysis(self):
        """단계 5: 시장 분석"""
        self.console.print("\n[bold yellow]🔍 5단계: 시장 분석 및 리스크 평가 중...[/bold yellow]\n")
        
        # 리스크 분석 수행
        advice = await real_time_advisor.analyze_and_advise(self.portfolio, force_analysis=True)
        
        if advice:
            risk_advice = advice[-1]
            risk_panel = Panel(
                risk_advice.message,
                title=f"🏛️ 버핏 멘토의 리스크 분석",
                border_style="yellow"
            )
            self.console.print(risk_panel)
        else:
            self.console.print("[dim]현재 특별한 리스크는 발견되지 않았습니다.[/dim]")
            
        # 간단한 리스크 지표
        risk_metrics = Panel(
            f"""
📊 리스크 지표:

• 포트폴리오 집중도: {(1 - len(self.portfolio.positions)) * 100 if self.portfolio.positions else 0:.1f}%
• 현금 비중: {self.portfolio.asset_allocation.get('cash', 0):.1f}%
• 최대 단일 보유 비중: {max(self.portfolio.asset_allocation.values()) if self.portfolio.asset_allocation else 0:.1f}%
• 총 포지션 수: {len(self.portfolio.positions)}개
            """.strip(),
            title="📊 리스크 지표",
            border_style="cyan"
        )
        self.console.print(risk_metrics)
        
    async def _step_final_results(self):
        """단계 6: 최종 성과"""
        self.console.print("\n[bold green]🏆 6단계: 모의투자 데모 최종 성과[/bold green]\n")
        
        # 최종 성과 정리
        final_summary = Panel(
            f"""
💵 시작 자금: {self.portfolio.initial_cash:,.0f}원
💰 최종 자산: {self.portfolio.total_portfolio_value:,.0f}원
📈 수익/손실: {self.portfolio.total_return:+,.0f}원
📉 수익률: {self.portfolio.total_return_percent:+.2f}%

📋 거래 통계:
• 총 거래 횟수: {len(self.portfolio.transactions)}건
• 총 수수료: {sum(t.commission for t in self.portfolio.transactions):,.0f}원
• 보유 종목 수: {len(self.portfolio.positions)}개
            """.strip(),
            title="🏆 모의투자 데모 최종 성과",
            border_style="bright_green",
            box=box.DOUBLE
        )
        self.console.print(final_summary)
        
        # 버핏 멘토의 최종 평가
        performance_message = ""
        if self.portfolio.total_return_percent > 0:
            performance_message = "🏛️ 버핏: \"\ud6cc륭합니다! 좋은 시작입니다. 하지만 기억하세요 - 진짜 투자는 장기전입니다.\""
        else:
            performance_message = "🏛️ 버핏: \"\uc190실도 배움의 한 부분입니다. 중요한 것은 증시한 경험에서 배우는 것입니다.\""
            
        final_advice = Panel(
            f"""
{performance_message}

🎓 다음 단계 추천:
• 더 많은 기업 연구하기
• 분산투자 연습하기  
• 장기적 투자 계획 세우기
• 리스크 관리 기술 향상

"시장에서 살아남는 것이 돈을 버는 것보다 중요합니다."
            """.strip(),
            title="🏛️ 버핏 멘토의 최종 평가",
            border_style="yellow"
        )
        self.console.print(final_advice)
        
        # 축하 효과
        for i in range(3):
            self.console.print(f"[bright_yellow]{'🎉' * 10}[/bright_yellow]")
            await asyncio.sleep(0.5)
            
        self.console.print("\n[bold green]🎉 실시간 모의투자 데모 완료![/bold green]")
        
        # 데모 정보
        demo_info = Panel(
            f"""
🚀 이 데모에서 경험한 기능들:

• 실시간 Yahoo Finance API 연동
• 실제적인 거래 수수료 및 세금 계산
• AI 기반 투자 조언 시스템
• 리스크 관리 및 포트폴리오 분석
• 버핏 멘토의 가치투자 철학 적용

📚 다음 단계: 고급 리스크 시스템과 다른 멘토 추가 예정
            """.strip(),
            title="🚀 Walk Risk 실시간 모의투자 시스템",
            border_style="bright_cyan"
        )
        self.console.print(demo_info)


async def main():
    """메인 함수"""
    demo = RealTradingAutoDemo()
    await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main())