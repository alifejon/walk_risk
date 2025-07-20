"""
Financial statements models for fundamental analysis
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, date
import math

from ...utils.logger import logger


class StatementType(Enum):
    """재무제표 유형"""
    INCOME_STATEMENT = "income_statement"
    BALANCE_SHEET = "balance_sheet"
    CASH_FLOW = "cash_flow"
    STATEMENT_OF_EQUITY = "statement_of_equity"


class Period(Enum):
    """재무제표 기간"""
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    TTM = "ttm"  # Trailing Twelve Months


class Currency(Enum):
    """통화"""
    KRW = "KRW"
    USD = "USD"
    EUR = "EUR"
    JPY = "JPY"


@dataclass
class FinancialStatement:
    """재무제표 기본 클래스"""
    company_code: str
    company_name: str
    statement_type: StatementType
    period: Period
    fiscal_year: int
    fiscal_quarter: Optional[int] = None
    report_date: Optional[date] = None
    currency: Currency = Currency.KRW
    unit: str = "원"  # 백만원, 억원 등
    
    # 메타데이터
    data_source: str = "manual"
    last_updated: datetime = field(default_factory=datetime.now)
    audit_status: str = "unaudited"
    
    def get_period_key(self) -> str:
        """기간 식별 키 생성"""
        if self.period == Period.QUARTERLY:
            return f"{self.fiscal_year}Q{self.fiscal_quarter}"
        elif self.period == Period.ANNUAL:
            return f"{self.fiscal_year}"
        else:
            return f"{self.fiscal_year}_TTM"
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'company_code': self.company_code,
            'company_name': self.company_name,
            'statement_type': self.statement_type.value,
            'period': self.period.value,
            'fiscal_year': self.fiscal_year,
            'fiscal_quarter': self.fiscal_quarter,
            'report_date': self.report_date.isoformat() if self.report_date else None,
            'currency': self.currency.value,
            'unit': self.unit,
            'period_key': self.get_period_key()
        }


@dataclass
class IncomeStatement(FinancialStatement):
    """손익계산서"""
    
    # 매출 관련
    revenue: float = 0.0  # 매출액
    cost_of_goods_sold: float = 0.0  # 매출원가
    gross_profit: float = 0.0  # 매출총이익
    
    # 영업 관련
    operating_expenses: float = 0.0  # 영업비용
    selling_expenses: float = 0.0  # 판매비
    administrative_expenses: float = 0.0  # 관리비
    rd_expenses: float = 0.0  # 연구개발비
    operating_income: float = 0.0  # 영업이익
    
    # 영업외 관련
    other_income: float = 0.0  # 영업외수익
    other_expenses: float = 0.0  # 영업외비용
    financial_income: float = 0.0  # 금융수익
    financial_expenses: float = 0.0  # 금융비용
    
    # 세전/세후 이익
    income_before_tax: float = 0.0  # 법인세비용차감전순이익
    tax_expense: float = 0.0  # 법인세비용
    net_income: float = 0.0  # 당기순이익
    
    # 주당 관련
    shares_outstanding: float = 0.0  # 발행주식수
    eps: float = 0.0  # 주당순이익
    
    def __post_init__(self):
        """초기화 후 계산"""
        self.statement_type = StatementType.INCOME_STATEMENT
        self._calculate_derived_values()
    
    def _calculate_derived_values(self):
        """파생 값들 계산"""
        # 매출총이익 계산
        if self.gross_profit == 0 and self.revenue > 0:
            self.gross_profit = self.revenue - self.cost_of_goods_sold
        
        # 영업이익 계산
        if self.operating_income == 0:
            self.operating_income = self.gross_profit - self.operating_expenses
        
        # 법인세비용차감전순이익 계산
        if self.income_before_tax == 0:
            self.income_before_tax = (self.operating_income + 
                                    self.other_income - self.other_expenses +
                                    self.financial_income - self.financial_expenses)
        
        # 당기순이익 계산
        if self.net_income == 0:
            self.net_income = self.income_before_tax - self.tax_expense
        
        # EPS 계산
        if self.eps == 0 and self.shares_outstanding > 0:
            self.eps = self.net_income / self.shares_outstanding
    
    def get_margins(self) -> Dict[str, float]:
        """각종 마진율 계산"""
        if self.revenue == 0:
            return {
                'gross_margin': 0.0,
                'operating_margin': 0.0,
                'net_margin': 0.0
            }
        
        return {
            'gross_margin': self.gross_profit / self.revenue,
            'operating_margin': self.operating_income / self.revenue,
            'net_margin': self.net_income / self.revenue
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        base_dict = super().to_dict()
        financial_dict = {
            'revenue': self.revenue,
            'cost_of_goods_sold': self.cost_of_goods_sold,
            'gross_profit': self.gross_profit,
            'operating_expenses': self.operating_expenses,
            'operating_income': self.operating_income,
            'net_income': self.net_income,
            'eps': self.eps,
            'shares_outstanding': self.shares_outstanding,
            'margins': self.get_margins()
        }
        return {**base_dict, **financial_dict}


@dataclass
class BalanceSheet(FinancialStatement):
    """재무상태표 (대차대조표)"""
    
    # 자산 (Assets)
    # 유동자산
    cash_and_equivalents: float = 0.0  # 현금및현금성자산
    short_term_investments: float = 0.0  # 단기투자자산
    accounts_receivable: float = 0.0  # 매출채권
    inventory: float = 0.0  # 재고자산
    other_current_assets: float = 0.0  # 기타유동자산
    total_current_assets: float = 0.0  # 유동자산총계
    
    # 비유동자산
    property_plant_equipment: float = 0.0  # 유형자산
    intangible_assets: float = 0.0  # 무형자산
    long_term_investments: float = 0.0  # 장기투자자산
    other_non_current_assets: float = 0.0  # 기타비유동자산
    total_non_current_assets: float = 0.0  # 비유동자산총계
    
    total_assets: float = 0.0  # 자산총계
    
    # 부채 (Liabilities)
    # 유동부채
    accounts_payable: float = 0.0  # 매입채무
    short_term_debt: float = 0.0  # 단기차입금
    current_portion_long_term_debt: float = 0.0  # 유동성장기부채
    other_current_liabilities: float = 0.0  # 기타유동부채
    total_current_liabilities: float = 0.0  # 유동부채총계
    
    # 비유동부채
    long_term_debt: float = 0.0  # 장기차입금
    other_non_current_liabilities: float = 0.0  # 기타비유동부채
    total_non_current_liabilities: float = 0.0  # 비유동부채총계
    
    total_liabilities: float = 0.0  # 부채총계
    
    # 자본 (Equity)
    share_capital: float = 0.0  # 자본금
    retained_earnings: float = 0.0  # 이익잉여금
    other_equity: float = 0.0  # 기타자본
    total_equity: float = 0.0  # 자본총계
    
    def __post_init__(self):
        """초기화 후 계산"""
        self.statement_type = StatementType.BALANCE_SHEET
        self._calculate_derived_values()
    
    def _calculate_derived_values(self):
        """파생 값들 계산"""
        # 유동자산총계
        if self.total_current_assets == 0:
            self.total_current_assets = (self.cash_and_equivalents + 
                                       self.short_term_investments +
                                       self.accounts_receivable + 
                                       self.inventory +
                                       self.other_current_assets)
        
        # 비유동자산총계
        if self.total_non_current_assets == 0:
            self.total_non_current_assets = (self.property_plant_equipment +
                                           self.intangible_assets +
                                           self.long_term_investments +
                                           self.other_non_current_assets)
        
        # 자산총계
        if self.total_assets == 0:
            self.total_assets = self.total_current_assets + self.total_non_current_assets
        
        # 유동부채총계
        if self.total_current_liabilities == 0:
            self.total_current_liabilities = (self.accounts_payable +
                                            self.short_term_debt +
                                            self.current_portion_long_term_debt +
                                            self.other_current_liabilities)
        
        # 비유동부채총계
        if self.total_non_current_liabilities == 0:
            self.total_non_current_liabilities = (self.long_term_debt +
                                                self.other_non_current_liabilities)
        
        # 부채총계
        if self.total_liabilities == 0:
            self.total_liabilities = self.total_current_liabilities + self.total_non_current_liabilities
        
        # 자본총계
        if self.total_equity == 0:
            self.total_equity = self.share_capital + self.retained_earnings + self.other_equity
    
    def get_financial_ratios(self) -> Dict[str, float]:
        """재무비율 계산"""
        ratios = {}
        
        # 유동성 비율
        if self.total_current_liabilities > 0:
            ratios['current_ratio'] = self.total_current_assets / self.total_current_liabilities
            ratios['quick_ratio'] = (self.total_current_assets - self.inventory) / self.total_current_liabilities
        
        # 부채 비율
        if self.total_assets > 0:
            ratios['debt_to_assets'] = self.total_liabilities / self.total_assets
        
        if self.total_equity > 0:
            ratios['debt_to_equity'] = self.total_liabilities / self.total_equity
        
        # 자산 효율성
        if self.total_assets > 0:
            ratios['asset_turnover'] = 0  # 매출액 필요 (손익계산서에서)
        
        return ratios
    
    def check_balance(self) -> bool:
        """대차대조표 균형 확인"""
        return abs(self.total_assets - (self.total_liabilities + self.total_equity)) < 1000  # 1천원 오차 허용


@dataclass
class CashFlowStatement(FinancialStatement):
    """현금흐름표"""
    
    # 영업활동 현금흐름
    net_income_for_cf: float = 0.0  # 당기순이익 (현금흐름 시작점)
    depreciation: float = 0.0  # 감가상각비
    amortization: float = 0.0  # 무형자산상각비
    changes_in_working_capital: float = 0.0  # 운전자본 변동
    other_operating_activities: float = 0.0  # 기타 영업활동
    operating_cash_flow: float = 0.0  # 영업활동 현금흐름
    
    # 투자활동 현금흐름
    capex: float = 0.0  # 자본적지출 (Capital Expenditure)
    acquisitions: float = 0.0  # 인수합병
    asset_sales: float = 0.0  # 자산매각
    investment_purchases: float = 0.0  # 투자자산 취득
    investment_sales: float = 0.0  # 투자자산 매각
    investing_cash_flow: float = 0.0  # 투자활동 현금흐름
    
    # 재무활동 현금흐름
    debt_issued: float = 0.0  # 차입금 증가
    debt_repaid: float = 0.0  # 차입금 상환
    equity_issued: float = 0.0  # 주식 발행
    equity_repurchased: float = 0.0  # 자사주 매입
    dividends_paid: float = 0.0  # 배당금 지급
    financing_cash_flow: float = 0.0  # 재무활동 현금흐름
    
    # 현금 변동
    net_cash_flow: float = 0.0  # 순현금흐름
    cash_beginning: float = 0.0  # 기초현금
    cash_ending: float = 0.0  # 기말현금
    
    def __post_init__(self):
        """초기화 후 계산"""
        self.statement_type = StatementType.CASH_FLOW
        self._calculate_derived_values()
    
    def _calculate_derived_values(self):
        """파생 값들 계산"""
        # 영업활동 현금흐름
        if self.operating_cash_flow == 0:
            self.operating_cash_flow = (self.net_income_for_cf +
                                      self.depreciation +
                                      self.amortization +
                                      self.changes_in_working_capital +
                                      self.other_operating_activities)
        
        # 투자활동 현금흐름 (보통 음수)
        if self.investing_cash_flow == 0:
            self.investing_cash_flow = (-self.capex +
                                      -self.acquisitions +
                                      self.asset_sales +
                                      -self.investment_purchases +
                                      self.investment_sales)
        
        # 재무활동 현금흐름
        if self.financing_cash_flow == 0:
            self.financing_cash_flow = (self.debt_issued +
                                      -self.debt_repaid +
                                      self.equity_issued +
                                      -self.equity_repurchased +
                                      -self.dividends_paid)
        
        # 순현금흐름
        if self.net_cash_flow == 0:
            self.net_cash_flow = (self.operating_cash_flow +
                                self.investing_cash_flow +
                                self.financing_cash_flow)
        
        # 기말현금
        if self.cash_ending == 0:
            self.cash_ending = self.cash_beginning + self.net_cash_flow
    
    def get_cash_flow_ratios(self) -> Dict[str, float]:
        """현금흐름 비율"""
        ratios = {}
        
        # 영업현금흐름 품질
        if self.net_income_for_cf != 0:
            ratios['operating_cf_to_net_income'] = self.operating_cash_flow / self.net_income_for_cf
        
        # 자본지출 대비 영업현금흐름
        if self.capex > 0:
            ratios['operating_cf_to_capex'] = self.operating_cash_flow / self.capex
        
        # 자유현금흐름
        ratios['free_cash_flow'] = self.operating_cash_flow - self.capex
        
        return ratios


@dataclass
class FinancialRatios:
    """종합 재무비율 분석"""
    
    # 수익성 비율
    gross_margin: float = 0.0  # 매출총이익률
    operating_margin: float = 0.0  # 영업이익률
    net_margin: float = 0.0  # 순이익률
    roa: float = 0.0  # 자산수익률
    roe: float = 0.0  # 자기자본수익률
    roic: float = 0.0  # 투하자본수익률
    
    # 효율성 비율
    asset_turnover: float = 0.0  # 자산회전율
    inventory_turnover: float = 0.0  # 재고회전율
    receivables_turnover: float = 0.0  # 매출채권회전율
    
    # 유동성 비율
    current_ratio: float = 0.0  # 유동비율
    quick_ratio: float = 0.0  # 당좌비율
    cash_ratio: float = 0.0  # 현금비율
    
    # 안정성 비율
    debt_to_assets: float = 0.0  # 부채비율
    debt_to_equity: float = 0.0  # 부채대자본비율
    equity_ratio: float = 0.0  # 자기자본비율
    interest_coverage: float = 0.0  # 이자보상배율
    
    # 성장성 비율
    revenue_growth: float = 0.0  # 매출성장률
    operating_income_growth: float = 0.0  # 영업이익성장률
    net_income_growth: float = 0.0  # 순이익성장률
    
    # 밸류에이션 비율
    per: float = 0.0  # 주가수익비율
    pbr: float = 0.0  # 주가순자산비율
    pcr: float = 0.0  # 주가매출비율
    ev_ebitda: float = 0.0  # EV/EBITDA
    
    def get_overall_score(self) -> Dict[str, float]:
        """종합 재무 건전성 점수"""
        
        scores = {}
        
        # 수익성 점수 (0-100)
        profitability_score = 0
        if self.roa > 0.15:
            profitability_score += 25
        elif self.roa > 0.10:
            profitability_score += 20
        elif self.roa > 0.05:
            profitability_score += 15
        
        if self.roe > 0.20:
            profitability_score += 25
        elif self.roe > 0.15:
            profitability_score += 20
        elif self.roe > 0.10:
            profitability_score += 15
        
        if self.net_margin > 0.10:
            profitability_score += 25
        elif self.net_margin > 0.05:
            profitability_score += 20
        elif self.net_margin > 0.02:
            profitability_score += 15
        
        scores['profitability'] = min(100, profitability_score)
        
        # 안정성 점수
        stability_score = 0
        if self.debt_to_equity < 0.5:
            stability_score += 30
        elif self.debt_to_equity < 1.0:
            stability_score += 20
        elif self.debt_to_equity < 2.0:
            stability_score += 10
        
        if self.current_ratio > 2.0:
            stability_score += 25
        elif self.current_ratio > 1.5:
            stability_score += 20
        elif self.current_ratio > 1.0:
            stability_score += 15
        
        if self.interest_coverage > 10:
            stability_score += 25
        elif self.interest_coverage > 5:
            stability_score += 20
        elif self.interest_coverage > 2:
            stability_score += 15
        
        scores['stability'] = min(100, stability_score)
        
        # 성장성 점수
        growth_score = 0
        if self.revenue_growth > 0.20:
            growth_score += 35
        elif self.revenue_growth > 0.10:
            growth_score += 25
        elif self.revenue_growth > 0.05:
            growth_score += 15
        
        if self.net_income_growth > 0.20:
            growth_score += 35
        elif self.net_income_growth > 0.10:
            growth_score += 25
        elif self.net_income_growth > 0.05:
            growth_score += 15
        
        scores['growth'] = min(100, growth_score)
        
        # 효율성 점수
        efficiency_score = 0
        if self.asset_turnover > 1.5:
            efficiency_score += 30
        elif self.asset_turnover > 1.0:
            efficiency_score += 20
        elif self.asset_turnover > 0.5:
            efficiency_score += 10
        
        if self.inventory_turnover > 10:
            efficiency_score += 25
        elif self.inventory_turnover > 6:
            efficiency_score += 20
        elif self.inventory_turnover > 3:
            efficiency_score += 15
        
        scores['efficiency'] = min(100, efficiency_score)
        
        # 종합 점수
        scores['overall'] = (scores['profitability'] * 0.3 +
                           scores['stability'] * 0.3 +
                           scores['growth'] * 0.2 +
                           scores['efficiency'] * 0.2)
        
        return scores
    
    def get_rating(self) -> str:
        """신용등급 스타일 평가"""
        overall_score = self.get_overall_score()['overall']
        
        if overall_score >= 90:
            return "AAA"
        elif overall_score >= 80:
            return "AA"
        elif overall_score >= 70:
            return "A"
        elif overall_score >= 60:
            return "BBB"
        elif overall_score >= 50:
            return "BB"
        elif overall_score >= 40:
            return "B"
        else:
            return "C"


class FinancialMetrics:
    """재무지표 계산 유틸리티"""
    
    @staticmethod
    def calculate_ratios(income: IncomeStatement, balance: BalanceSheet, 
                        cash_flow: Optional[CashFlowStatement] = None,
                        stock_price: Optional[float] = None,
                        market_cap: Optional[float] = None) -> FinancialRatios:
        """종합 재무비율 계산"""
        
        ratios = FinancialRatios()
        
        # 수익성 비율
        if income.revenue > 0:
            ratios.gross_margin = income.gross_profit / income.revenue
            ratios.operating_margin = income.operating_income / income.revenue
            ratios.net_margin = income.net_income / income.revenue
        
        if balance.total_assets > 0:
            ratios.roa = income.net_income / balance.total_assets
            ratios.asset_turnover = income.revenue / balance.total_assets
        
        if balance.total_equity > 0:
            ratios.roe = income.net_income / balance.total_equity
        
        # 유동성 비율
        if balance.total_current_liabilities > 0:
            ratios.current_ratio = balance.total_current_assets / balance.total_current_liabilities
            ratios.quick_ratio = (balance.total_current_assets - balance.inventory) / balance.total_current_liabilities
            ratios.cash_ratio = balance.cash_and_equivalents / balance.total_current_liabilities
        
        # 안정성 비율
        if balance.total_assets > 0:
            ratios.debt_to_assets = balance.total_liabilities / balance.total_assets
            ratios.equity_ratio = balance.total_equity / balance.total_assets
        
        if balance.total_equity > 0:
            ratios.debt_to_equity = balance.total_liabilities / balance.total_equity
        
        # 효율성 비율
        if balance.inventory > 0:
            ratios.inventory_turnover = income.cost_of_goods_sold / balance.inventory
        
        if balance.accounts_receivable > 0:
            ratios.receivables_turnover = income.revenue / balance.accounts_receivable
        
        # 밸류에이션 비율 (주가 정보가 있을 때)
        if stock_price and income.shares_outstanding > 0:
            if income.eps > 0:
                ratios.per = stock_price / income.eps
            
            book_value_per_share = balance.total_equity / income.shares_outstanding
            if book_value_per_share > 0:
                ratios.pbr = stock_price / book_value_per_share
            
            revenue_per_share = income.revenue / income.shares_outstanding
            if revenue_per_share > 0:
                ratios.pcr = stock_price / revenue_per_share
        
        return ratios
    
    @staticmethod
    def calculate_growth_rates(current: FinancialStatement, previous: FinancialStatement) -> Dict[str, float]:
        """성장률 계산"""
        
        growth_rates = {}
        
        if isinstance(current, IncomeStatement) and isinstance(previous, IncomeStatement):
            # 매출 성장률
            if previous.revenue > 0:
                growth_rates['revenue_growth'] = (current.revenue - previous.revenue) / previous.revenue
            
            # 영업이익 성장률
            if previous.operating_income > 0:
                growth_rates['operating_income_growth'] = (current.operating_income - previous.operating_income) / previous.operating_income
            
            # 순이익 성장률
            if previous.net_income > 0:
                growth_rates['net_income_growth'] = (current.net_income - previous.net_income) / previous.net_income
        
        elif isinstance(current, BalanceSheet) and isinstance(previous, BalanceSheet):
            # 총자산 성장률
            if previous.total_assets > 0:
                growth_rates['total_assets_growth'] = (current.total_assets - previous.total_assets) / previous.total_assets
            
            # 자기자본 성장률
            if previous.total_equity > 0:
                growth_rates['equity_growth'] = (current.total_equity - previous.total_equity) / previous.total_equity
        
        return growth_rates
    
    @staticmethod
    def detect_financial_anomalies(statements: List[FinancialStatement]) -> List[Dict[str, Any]]:
        """재무제표 이상 징후 탐지"""
        
        anomalies = []
        
        # 손익계산서 이상 징후
        for statement in statements:
            if isinstance(statement, IncomeStatement):
                # 매출 대비 비정상적인 항목들
                if statement.revenue > 0:
                    # 매출원가율이 100% 초과
                    if statement.cost_of_goods_sold / statement.revenue > 1.0:
                        anomalies.append({
                            'type': 'high_cogs_ratio',
                            'description': '매출원가율이 100%를 초과합니다',
                            'severity': 'high',
                            'period': statement.get_period_key()
                        })
                    
                    # 영업비용이 매출의 50% 초과
                    if statement.operating_expenses / statement.revenue > 0.5:
                        anomalies.append({
                            'type': 'high_operating_expenses',
                            'description': '영업비용이 매출의 50%를 초과합니다',
                            'severity': 'medium',
                            'period': statement.get_period_key()
                        })
                
                # 영업이익은 흑자인데 순이익이 적자
                if statement.operating_income > 0 and statement.net_income < 0:
                    anomalies.append({
                        'type': 'operating_profit_but_net_loss',
                        'description': '영업이익은 흑자이지만 순이익이 적자입니다',
                        'severity': 'medium',
                        'period': statement.get_period_key()
                    })
            
            elif isinstance(statement, BalanceSheet):
                # 유동비율이 극도로 낮음
                if statement.total_current_liabilities > 0:
                    current_ratio = statement.total_current_assets / statement.total_current_liabilities
                    if current_ratio < 0.5:
                        anomalies.append({
                            'type': 'very_low_current_ratio',
                            'description': f'유동비율이 {current_ratio:.2f}로 매우 낮습니다',
                            'severity': 'high',
                            'period': statement.get_period_key()
                        })
                
                # 부채비율이 극도로 높음
                if statement.total_assets > 0:
                    debt_ratio = statement.total_liabilities / statement.total_assets
                    if debt_ratio > 0.8:
                        anomalies.append({
                            'type': 'very_high_debt_ratio',
                            'description': f'부채비율이 {debt_ratio:.1%}로 매우 높습니다',
                            'severity': 'high',
                            'period': statement.get_period_key()
                        })
                
                # 대차대조표 불균형
                if not statement.check_balance():
                    anomalies.append({
                        'type': 'balance_sheet_imbalance',
                        'description': '대차대조표가 균형을 이루지 않습니다',
                        'severity': 'critical',
                        'period': statement.get_period_key()
                    })
        
        return anomalies
    
    @staticmethod
    def generate_synthetic_financial_data(
        company_name: str,
        years: int = 3,
        industry_type: str = "manufacturing",
        performance_trend: str = "growing"  # growing, declining, stable, volatile
    ) -> Dict[str, List[FinancialStatement]]:
        """교육용 합성 재무데이터 생성"""
        
        statements = {
            'income_statements': [],
            'balance_sheets': [],
            'cash_flow_statements': []
        }
        
        # 기본 값들 설정 (산업별로 다르게)
        base_revenue = 100000  # 1억원
        if industry_type == "tech":
            base_revenue = 50000
            growth_rate = 0.25
            margin_profile = {'gross': 0.7, 'operating': 0.15, 'net': 0.12}
        elif industry_type == "manufacturing":
            base_revenue = 200000
            growth_rate = 0.08
            margin_profile = {'gross': 0.3, 'operating': 0.08, 'net': 0.05}
        elif industry_type == "retail":
            base_revenue = 150000
            growth_rate = 0.05
            margin_profile = {'gross': 0.25, 'operating': 0.04, 'net': 0.02}
        else:
            base_revenue = 100000
            growth_rate = 0.10
            margin_profile = {'gross': 0.4, 'operating': 0.10, 'net': 0.07}
        
        # 성과 트렌드 조정
        if performance_trend == "declining":
            growth_rate = -0.05
        elif performance_trend == "stable":
            growth_rate = 0.02
        elif performance_trend == "volatile":
            growth_rates = [0.15, -0.10, 0.20]
        
        current_year = 2024
        
        for year in range(years):
            fiscal_year = current_year - (years - 1 - year)
            
            # 성장률 적용
            if performance_trend == "volatile":
                year_growth = growth_rates[year % len(growth_rates)]
            else:
                year_growth = growth_rate
            
            # 해당 연도 매출
            if year == 0:
                revenue = base_revenue
            else:
                revenue = statements['income_statements'][-1].revenue * (1 + year_growth)
            
            # 노이즈 추가 (±5%)
            revenue *= (1 + np.random.uniform(-0.05, 0.05))
            
            # 손익계산서 생성
            income = IncomeStatement(
                company_code=f"COMP{hash(company_name) % 10000:04d}",
                company_name=company_name,
                period=Period.ANNUAL,
                fiscal_year=fiscal_year,
                revenue=revenue,
                cost_of_goods_sold=revenue * (1 - margin_profile['gross']),
                operating_expenses=revenue * (margin_profile['gross'] - margin_profile['operating']),
                shares_outstanding=1000000,  # 100만주
            )
            
            # 기타 영업외 손익 (랜덤)
            income.other_income = revenue * np.random.uniform(0, 0.02)
            income.other_expenses = revenue * np.random.uniform(0, 0.01)
            income.financial_expenses = revenue * np.random.uniform(0, 0.005)
            income.tax_expense = max(0, income.income_before_tax * 0.25)  # 25% 세율
            
            statements['income_statements'].append(income)
            
            # 재무상태표 생성
            balance = BalanceSheet(
                company_code=income.company_code,
                company_name=company_name,
                period=Period.ANNUAL,
                fiscal_year=fiscal_year,
                
                # 자산 (매출의 배수로 계산)
                cash_and_equivalents=revenue * np.random.uniform(0.05, 0.15),
                accounts_receivable=revenue * np.random.uniform(0.08, 0.12),
                inventory=revenue * np.random.uniform(0.10, 0.20),
                property_plant_equipment=revenue * np.random.uniform(0.3, 0.8),
                
                # 부채 (자산의 비율로)
                accounts_payable=revenue * np.random.uniform(0.05, 0.10),
                short_term_debt=revenue * np.random.uniform(0.02, 0.08),
                long_term_debt=revenue * np.random.uniform(0.10, 0.25),
            )
            
            # 기타 항목들 계산
            balance.other_current_assets = balance.total_current_assets * 0.1
            balance.other_non_current_assets = balance.total_non_current_assets * 0.05
            balance.other_current_liabilities = balance.total_current_liabilities * 0.1
            balance.other_non_current_liabilities = balance.total_non_current_liabilities * 0.05
            
            # 자본 계산 (자산 - 부채)
            balance.retained_earnings = balance.total_assets - balance.total_liabilities - 50000  # 자본금 5천만원
            balance.share_capital = 50000
            
            statements['balance_sheets'].append(balance)
            
            # 현금흐름표 생성
            cash_flow = CashFlowStatement(
                company_code=income.company_code,
                company_name=company_name,
                period=Period.ANNUAL,
                fiscal_year=fiscal_year,
                net_income_for_cf=income.net_income,
                depreciation=balance.property_plant_equipment * 0.1,  # 10% 감가상각
                capex=revenue * np.random.uniform(0.05, 0.15),
                dividends_paid=max(0, income.net_income * 0.3),  # 배당성향 30%
            )
            
            # 운전자본 변동 (전년 대비)
            if year > 0:
                prev_working_capital = (statements['balance_sheets'][-2].total_current_assets - 
                                      statements['balance_sheets'][-2].total_current_liabilities)
                current_working_capital = (balance.total_current_assets - balance.total_current_liabilities)
                cash_flow.changes_in_working_capital = -(current_working_capital - prev_working_capital)
            
            statements['cash_flow_statements'].append(cash_flow)
        
        logger.info(f"합성 재무데이터 생성 완료: {company_name}, {years}년, {industry_type}, {performance_trend}")
        
        return statements


# 업종별 벤치마크 데이터
INDUSTRY_BENCHMARKS = {
    "technology": {
        "gross_margin": 0.65,
        "operating_margin": 0.15,
        "net_margin": 0.12,
        "roe": 0.18,
        "debt_to_equity": 0.3,
        "current_ratio": 2.5,
        "revenue_growth": 0.20
    },
    "manufacturing": {
        "gross_margin": 0.35,
        "operating_margin": 0.08,
        "net_margin": 0.05,
        "roe": 0.12,
        "debt_to_equity": 0.6,
        "current_ratio": 1.8,
        "revenue_growth": 0.08
    },
    "retail": {
        "gross_margin": 0.25,
        "operating_margin": 0.04,
        "net_margin": 0.02,
        "roe": 0.15,
        "debt_to_equity": 0.5,
        "current_ratio": 1.2,
        "revenue_growth": 0.05
    },
    "finance": {
        "net_margin": 0.20,
        "roe": 0.10,
        "debt_to_equity": 8.0,  # 금융업은 부채비율이 높음
        "current_ratio": 1.0,
        "revenue_growth": 0.06
    }
}