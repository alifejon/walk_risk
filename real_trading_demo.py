#!/usr/bin/env python3
"""Real Trading Demo - 실시간 모의투자 시스템 데모"""

import asyncio
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
from rich import box
from rich.prompt import Prompt, Confirm
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


class RealTradingDemo:
    """실시간 모의투자 데모 인터페이스"""
    
    def __init__(self):
        self.console = console
        self.portfolio = None
        self.player = None
        self.is_running = False
        
    async def start_demo(self):
        """데모 시작"""
        try:
            self._show_intro()
            
            # 플레이어 생성
            self.player = Player(
                id="real_trading_demo",
                name="실전 투자자",
                level=10,  # 튜토리얼 완료 상태
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
            
            self.console.print("\n[green]✅ 실시간 모의투자 시스템 초기화 완료![/green]\n")
            
            # 메인 루프
            await self._main_loop()
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]👋 데모를 종료합니다.[/yellow]")
        except Exception as e:
            logger.error(f"데모 실행 오류: {e}", exc_info=True)
            self.console.print(f"[red]❌ 오류 발생: {e}[/red]")
            
    def _show_intro(self):
        """인트로 화면"""
        intro_text = """
[bold yellow]📈 Walk Risk: 실시간 모의투자 시스템[/bold yellow]

[cyan]실제 시장 데이터로 모의투자를 체험해보세요![/cyan]

🔥 주요 기능:
• 실시간 한국 주식 데이터 (Yahoo Finance)
• 실제적인 거래 수수료 및 세금
• 버핏 멘토의 실시간 투자 조언
• 지정가, 시장가, 스톱 주문 지원
• 포트폴리오 성과 분석

💵 시작 자금: 1,000만원
        """
        
        panel = Panel(
            intro_text,
            title="🎆 실시간 모의투자 데모 🎆",
            border_style="bright_green",
            box=box.DOUBLE
        )
        self.console.print(panel)
        
    async def _main_loop(self):
        """메인 루프"""
        self.is_running = True
        
        while self.is_running:
            # 메뉴 표시
            self._show_main_menu()
            
            # 사용자 입력
            choice = Prompt.ask(
                "\n[bold cyan]선택[/bold cyan]",
                choices=["1", "2", "3", "4", "5", "6", "7", "0"],
                default="1"
            )
            
            if choice == "1":
                await self._show_portfolio_status()
            elif choice == "2":
                await self._show_market_data()
            elif choice == "3":
                await self._buy_stock()
            elif choice == "4":
                await self._sell_stock()
            elif choice == "5":
                await self._show_advisor_messages()
            elif choice == "6":
                await self._show_order_status()
            elif choice == "7":
                await self._run_market_analysis()
            elif choice == "0":
                if Confirm.ask("\n[yellow]정말 종료하시겠습니까?[/yellow]"):
                    self.is_running = False
                    
            if self.is_running:
                self.console.print("\n[dim]계속하려면 Enter를 누르세요...[/dim]")
                input()
                
    def _show_main_menu(self):
        """메인 메뉴 표시"""
        self.console.clear()
        
        menu_text = """
[bold cyan]📊 실시간 모의투자 시스템[/bold cyan]

1. 💼 포트폴리오 현황
2. 📈 시장 데이터
3. 💰 주식 매수
4. 💸 주식 매도
5. 🤖 AI 멘토 조언
6. 📋 주문 현황
7. 🔍 시장 분석
0. 🚀 종료
        """
        
        self.console.print(menu_text)
        
    async def _show_portfolio_status(self):
        """포트폴리오 현황 표시"""
        self.console.clear()
        self.console.print("[bold yellow]💼 포트폴리오 현황 업데이트 중...[/bold yellow]\n")
        
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
        else:
            self.console.print("[dim]보유 주식이 없습니다.[/dim]")
            
    async def _show_market_data(self):
        """시장 데이터 표시"""
        self.console.clear()
        self.console.print("[bold yellow]📈 시장 데이터 수집 중...[/bold yellow]\n")
        
        # 시장 지수
        market_summary = await yahoo_finance.get_market_summary()
        if market_summary:
            market_table = Table(title="🏆 시장 지수", box=box.ROUNDED)
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
            
        # 인기 주식
        popular_stocks = yahoo_finance.get_popular_korean_stocks()[:5]
        stocks_data = await yahoo_finance.get_multiple_stocks(popular_stocks)
        
        if stocks_data:
            stocks_table = Table(title="📊 인기 주식", box=box.SIMPLE)
            stocks_table.add_column("종목", style="cyan")
            stocks_table.add_column("현재가", justify="right")
            stocks_table.add_column("전일대비", justify="right")
            stocks_table.add_column("변동률", justify="right")
            stocks_table.add_column("거래량", justify="right")
            
            for symbol, stock in stocks_data.items():
                if stock:
                    change_color = "green" if stock.is_gain else "red"
                    stocks_table.add_row(
                        stock.name,
                        f"{stock.current_price:,.0f}원",
                        f"[{change_color}]{stock.change:+,.0f}[/{change_color}]",
                        f"[{change_color}]{stock.change_percent:+.2f}%[/{change_color}]",
                        f"{stock.volume:,}"
                    )
                    
            self.console.print(stocks_table)
            
    async def _buy_stock(self):
        """주식 매수"""
        self.console.clear()
        self.console.print("[bold green]💰 주식 매수[/bold green]\n")
        
        # 주식 선택
        symbol = Prompt.ask(
            "매수할 주식 심볼 (ex: 005930.KS)",
            default="005930.KS"
        )
        
        # 주식 정보 확인
        stock_data = await yahoo_finance.get_stock_data(symbol)
        if not stock_data:
            self.console.print(f"[red]❌ 주식 정보를 찾을 수 없습니다: {symbol}[/red]")
            return
            
        # 주식 정보 표시
        stock_info = Panel(
            f"""
종목: {stock_data.name}
현재가: {stock_data.current_price:,.0f}원
전일대비: {stock_data.formatted_change}
거래량: {stock_data.volume:,}
            """.strip(),
            title=f"📊 {stock_data.name} 정보",
            border_style="green"
        )
        self.console.print(stock_info)
        
        # 수량 입력
        try:
            quantity = float(Prompt.ask("매수 수량 (주)", default="1"))
            if quantity <= 0:
                self.console.print("[red]❌ 유효하지 않은 수량입니다.[/red]")
                return
        except ValueError:
            self.console.print("[red]❌ 숫자를 입력해주세요.[/red]")
            return
            
        # 예상 금액 계산
        total_amount = quantity * stock_data.current_price
        commission = self.portfolio.calculate_commission(total_amount)
        net_amount = total_amount + commission
        
        order_summary = Panel(
            f"""
매수 예상 금액: {total_amount:,.0f}원
수수료: {commission:,.0f}원
총 필요 금액: {net_amount:,.0f}원
보유 현금: {self.portfolio.cash:,.0f}원
            """.strip(),
            title="💵 주문 요약",
            border_style="yellow"
        )
        self.console.print(order_summary)
        
        # 주문 확인
        if not Confirm.ask(f"\n{stock_data.name} {quantity}주를 매수하시겠습니까?"):
            self.console.print("[yellow]매수를 취소했습니다.[/yellow]")
            return
            
        # 주문 실행
        self.console.print("\n[yellow]매수 주문 실행 중...[/yellow]")
        
        success, message, transaction = await self.portfolio.buy_stock(symbol, quantity)
        
        if success:
            self.console.print(f"[green]✅ {message}[/green]")
            if transaction:
                self.console.print(f"[dim]거래 ID: {transaction.id}[/dim]")
        else:
            self.console.print(f"[red]❌ {message}[/red]")
            
    async def _sell_stock(self):
        """주식 매도"""
        self.console.clear()
        self.console.print("[bold red]💸 주식 매도[/bold red]\n")
        
        if not self.portfolio.positions:
            self.console.print("[yellow]매도할 주식이 없습니다.[/yellow]")
            return
            
        # 보유 주식 목록
        self.console.print("[cyan]보유 주식 목록:[/cyan]")
        for i, (symbol, position) in enumerate(self.portfolio.positions.items(), 1):
            pnl_color = "green" if position.is_profit else "red"
            self.console.print(
                f"{i}. {position.name} ({symbol}) - "
                f"{position.quantity:.0f}주, "
                f"[{pnl_color}]{position.unrealized_pnl_percent:+.2f}%[/{pnl_color}]"
            )
            
        # 주식 선택
        try:
            choice = int(Prompt.ask("매도할 주식 번호", default="1")) - 1
            symbols = list(self.portfolio.positions.keys())
            
            if choice < 0 or choice >= len(symbols):
                self.console.print("[red]❌ 유효하지 않은 선택입니다.[/red]")
                return
                
            symbol = symbols[choice]
            position = self.portfolio.positions[symbol]
            
        except ValueError:
            self.console.print("[red]❌ 숫자를 입력해주세요.[/red]")
            return
            
        # 수량 입력
        try:
            max_quantity = position.quantity
            quantity = float(Prompt.ask(
                f"매도 수량 (최대 {max_quantity:.0f}주)",
                default=str(int(max_quantity))
            ))
            
            if quantity <= 0 or quantity > max_quantity:
                self.console.print("[red]❌ 유효하지 않은 수량입니다.[/red]")
                return
        except ValueError:
            self.console.print("[red]❌ 숫자를 입력해주세요.[/red]")
            return
            
        # 현재 가격 확인
        stock_data = await yahoo_finance.get_stock_data(symbol)
        if not stock_data:
            self.console.print("[red]❌ 주식 정보를 가져올 수 없습니다.[/red]")
            return
            
        # 예상 금액 계산
        total_amount = quantity * stock_data.current_price
        commission = self.portfolio.calculate_commission(total_amount)
        net_amount = total_amount - commission
        
        # 손익 계산
        avg_cost = quantity * position.average_price
        profit_loss = net_amount - avg_cost
        profit_loss_percent = (profit_loss / avg_cost * 100) if avg_cost > 0 else 0
        
        pnl_color = "green" if profit_loss > 0 else "red"
        
        order_summary = Panel(
            f"""
매도 예상 금액: {total_amount:,.0f}원
수수료: {commission:,.0f}원
실수령 금액: {net_amount:,.0f}원

매수 평균단가: {position.average_price:,.0f}원
현재가: {stock_data.current_price:,.0f}원
[{pnl_color}]예상 손익: {profit_loss:+,.0f}원 ({profit_loss_percent:+.2f}%)[/{pnl_color}]
            """.strip(),
            title="💵 매도 요약",
            border_style="yellow"
        )
        self.console.print(order_summary)
        
        # 주문 확인
        if not Confirm.ask(f"\n{position.name} {quantity}주를 매도하시겠습니까?"):
            self.console.print("[yellow]매도를 취소했습니다.[/yellow]")
            return
            
        # 주문 실행
        self.console.print("\n[yellow]매도 주문 실행 중...[/yellow]")
        
        success, message, transaction = await self.portfolio.sell_stock(symbol, quantity)
        
        if success:
            self.console.print(f"[green]✅ {message}[/green]")
            if transaction:
                self.console.print(f"[dim]거래 ID: {transaction.id}[/dim]")
        else:
            self.console.print(f"[red]❌ {message}[/red]")
            
    async def _show_advisor_messages(self):
        """멘토 조언 표시"""
        self.console.clear()
        self.console.print("[bold yellow]🤖 AI 멘토 조언 분석 중...[/bold yellow]\n")
        
        # 실시간 분석 수행
        new_advice = await real_time_advisor.analyze_and_advise(self.portfolio, force_analysis=True)
        
        if new_advice:
            self.console.print(f"[green]✅ {len(new_advice)}개의 새로운 조언이 생성되었습니다![/green]\n")
        
        # 최근 조언 표시
        recent_advice = real_time_advisor.get_recent_advice(limit=5)
        
        if recent_advice:
            for advice in recent_advice[-3:]:  # 최근 3개만 표시
                priority_color = {
                    "urgent": "red",
                    "high": "yellow", 
                    "medium": "cyan",
                    "low": "dim"
                }.get(advice.priority.value, "white")
                
                advice_panel = Panel(
                    advice.message,
                    title=f"[{priority_color}]{advice.title}[/{priority_color}]",
                    border_style=priority_color,
                    subtitle=f"[dim]{advice.created_at.strftime('%H:%M:%S')}[/dim]"
                )
                self.console.print(advice_panel)
                self.console.print()
                
            # 조언 요약
            summary = real_time_advisor.get_advice_summary()
            self.console.print(f"[dim]총 {summary['total_advice_count']}개 조언 | "
                             f"읽지 않음: {summary['unread_count']}개 | "
                             f"중요: {summary['high_priority_count']}개[/dim]")
        else:
            self.console.print("[dim]아직 조언이 없습니다.[/dim]")
            
    async def _show_order_status(self):
        """주문 현황 표시"""
        self.console.clear()
        self.console.print("[bold cyan]📋 주문 현황[/bold cyan]\n")
        
        # 활성 주문
        active_orders = order_engine.get_active_orders(self.portfolio.portfolio_id)
        if active_orders:
            active_table = Table(title="활성 주문", box=box.SIMPLE)
            active_table.add_column("주문 ID", style="cyan")
            active_table.add_column("종목")
            active_table.add_column("방향")
            active_table.add_column("수량")
            active_table.add_column("가격")
            active_table.add_column("상태")
            
            for order in active_orders:
                active_table.add_row(
                    order.id[:8] + "...",
                    yahoo_finance.get_stock_name(order.symbol),
                    order.side.value,
                    f"{order.quantity:.0f}주",
                    f"{order.price:,.0f}원" if order.price else "시장가",
                    order.status.value
                )
                
            self.console.print(active_table)
        else:
            self.console.print("[dim]활성 주문이 없습니다.[/dim]")
            
        # 최근 거래 내역
        if self.portfolio.transactions:
            recent_transactions = self.portfolio.transactions[-5:]  # 최근 5건
            
            history_table = Table(title="최근 거래 내역", box=box.SIMPLE)
            history_table.add_column("시간", style="dim")
            history_table.add_column("종목")
            history_table.add_column("구분")
            history_table.add_column("수량")
            history_table.add_column("가격")
            history_table.add_column("금액")
            
            for tx in reversed(recent_transactions):
                tx_color = "green" if tx.transaction_type == "buy" else "red"
                history_table.add_row(
                    tx.timestamp.strftime("%H:%M"),
                    tx.asset_name,
                    f"[{tx_color}]{매수 if tx.transaction_type == 'buy' else '매도'}[/{tx_color}]",
                    f"{tx.quantity:.0f}주",
                    f"{tx.price:,.0f}원",
                    f"{tx.total_amount:,.0f}원"
                )
                
            self.console.print(history_table)
        else:
            self.console.print("\n[dim]거래 내역이 없습니다.[/dim]")
            
        # 거래 통계
        stats = order_engine.get_order_statistics(self.portfolio.portfolio_id)
        if stats["total_orders"] > 0:
            self.console.print(f"\n[dim]총 거래: {stats['total_orders']}건 | "
                             f"성공률: {stats['success_rate']:.1f}% | "
                             f"총 수수료: {stats['total_commission']:,.0f}원[/dim]")
            
    async def _run_market_analysis(self):
        """시장 분석 수행"""
        self.console.clear()
        self.console.print("[bold yellow]🔍 시장 분석 수행 중...[/bold yellow]\n")
        
        # 시장 데이터 수집
        market_summary = await yahoo_finance.get_market_summary()
        popular_stocks = yahoo_finance.get_popular_korean_stocks()[:10]
        stocks_data = await yahoo_finance.get_multiple_stocks(popular_stocks)
        
        if market_summary and stocks_data:
            # 상승종목/하락종목 분석
            gainers = [(symbol, stock) for symbol, stock in stocks_data.items() if stock and stock.is_gain]
            losers = [(symbol, stock) for symbol, stock in stocks_data.items() if stock and not stock.is_gain]
            
            gainers.sort(key=lambda x: x[1].change_percent, reverse=True)
            losers.sort(key=lambda x: x[1].change_percent)
            
            if gainers:
                gainers_table = Table(title="📈 상승종목 TOP 5", box=box.SIMPLE)
                gainers_table.add_column("종목", style="green")
                gainers_table.add_column("현재가", justify="right")
                gainers_table.add_column("상승률", justify="right", style="green")
                
                for symbol, stock in gainers[:5]:
                    gainers_table.add_row(
                        stock.name,
                        f"{stock.current_price:,.0f}원",
                        f"+{stock.change_percent:.2f}%"
                    )
                    
                self.console.print(gainers_table)
                
            if losers:
                losers_table = Table(title="📉 하락종목 TOP 5", box=box.SIMPLE)
                losers_table.add_column("종목", style="red")
                losers_table.add_column("현재가", justify="right")
                losers_table.add_column("하락률", justify="right", style="red")
                
                for symbol, stock in losers[:5]:
                    losers_table.add_row(
                        stock.name,
                        f"{stock.current_price:,.0f}원",
                        f"{stock.change_percent:.2f}%"
                    )
                    
                self.console.print(losers_table)
                
            # 시장 감정 분석
            sentiment_analysis = Panel(
                f"""
전체 시장 심리: {market_summary.market_sentiment}
상승 종목 수: {len(gainers)}개
하락 종목 수: {len(losers)}개

평균 변동률: {(market_summary.kospi_change_percent + market_summary.kosdaq_change_percent) / 2:+.2f}%
                """.strip(),
                title="📊 시장 감정 분석",
                border_style="cyan"
            )
            self.console.print(sentiment_analysis)
            
            # 버핏 멘토의 시장 분석 조언
            advice = await real_time_advisor.analyze_and_advise(self.portfolio, force_analysis=True)
            if advice:
                latest_advice = advice[-1]
                buffett_analysis = Panel(
                    latest_advice.message,
                    title="🏛️ 버핏 멘토의 시장 분석",
                    border_style="yellow"
                )
                self.console.print(buffett_analysis)
        else:
            self.console.print("[red]❌ 시장 데이터를 가져올 수 없습니다.[/red]")


async def main():
    """메인 함수"""
    demo = RealTradingDemo()
    await demo.start_demo()


if __name__ == "__main__":
    asyncio.run(main())