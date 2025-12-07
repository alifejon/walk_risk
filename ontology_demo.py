#!/usr/bin/env python3
"""
Walk Risk Ontology Integration Demo

이 스크립트는 grokipedia-ontology를 Walk Risk에 통합한 결과를 시연합니다.

실행 방법:
    uv run python ontology_demo.py

데모 내용:
1. 온톨로지 로딩 및 통계
2. 리스크 분류 체계 탐색
3. 멘토 정보 조회
4. 버핏 멘토와 온톨로지 연동
5. 시장 이벤트 리스크 분류
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

console = Console()


def demo_ontology_loading():
    """1. 온톨로지 로딩 및 기본 통계"""
    console.print("\n" + "=" * 60)
    console.print("[bold cyan]1. 온톨로지 로딩 및 통계[/bold cyan]")
    console.print("=" * 60)

    from walk_risk.ontology import WalkRiskOntologyAdapter

    adapter = WalkRiskOntologyAdapter()

    if adapter.is_loaded:
        console.print("[green]✓ 온톨로지 로딩 성공![/green]\n")

        stats = adapter.get_stats()

        table = Table(title="Walk Risk 금융 온톨로지 통계")
        table.add_column("항목", style="cyan")
        table.add_column("값", style="green")

        table.add_row("리스크 개념 수", str(stats.get("risk_concepts", 0)))
        table.add_row("투자 철학 수", str(stats.get("investment_philosophies", 0)))
        table.add_row("멘토 페르소나 수", str(stats.get("mentor_personas", 0)))
        table.add_row("총 트리플 수", str(stats.get("total_triples", 0)))

        console.print(table)
        return adapter
    else:
        console.print("[red]✗ 온톨로지 로딩 실패[/red]")
        console.print("walk_risk_financial.ttl 파일이 존재하는지 확인하세요.")
        return None


def demo_risk_hierarchy(adapter):
    """2. 리스크 분류 체계 탐색"""
    console.print("\n" + "=" * 60)
    console.print("[bold cyan]2. 리스크 분류 체계[/bold cyan]")
    console.print("=" * 60)

    from walk_risk.ontology import RiskOntologyManager
    from walk_risk.models.risk.base import RiskType

    risk_manager = RiskOntologyManager(adapter)

    tree = Tree("[bold]리스크 분류 체계[/bold]")

    for risk_type in RiskType:
        ontology_class = risk_manager.get_ontology_class(risk_type)
        branch = tree.add(f"[cyan]{ontology_class}[/cyan] ({risk_type.value})")

        subcategories = risk_manager.get_subcategories(risk_type)
        for subcat in subcategories:
            label = subcat.get("label", "")
            uri = subcat.get("uri", "")
            class_name = uri.split("#")[-1] if "#" in uri else uri
            branch.add(f"[green]{class_name}[/green]: {label}")

    console.print(tree)


def demo_mentor_info(adapter):
    """3. 멘토 정보 조회"""
    console.print("\n" + "=" * 60)
    console.print("[bold cyan]3. 멘토 정보 (온톨로지 기반)[/bold cyan]")
    console.print("=" * 60)

    mentors = ["WarrenBuffett", "PeterLynch", "BenjaminGraham", "RayDalio", "CathieWood"]

    for mentor_name in mentors:
        info = adapter.get_mentor_philosophy(mentor_name)

        if info.get("philosophy"):
            philosophy = info["philosophy"]
            console.print(f"\n[bold yellow]{mentor_name}[/bold yellow]")

            # Philosophy
            phil_label = philosophy.get("label", "")
            console.print(f"  투자 철학: [cyan]{phil_label}[/cyan]")

            # Risk expertise
            expertise = info.get("risk_expertise", [])
            if expertise:
                risk_names = [r.get("label", r.get("uri", "").split("#")[-1]) for r in expertise]
                console.print(f"  리스크 전문: [green]{', '.join(risk_names)}[/green]")

            # Key concepts
            concepts = info.get("concepts", [])
            if concepts:
                concept_names = [c.get("label", c.get("uri", "").split("#")[-1]) for c in concepts]
                console.print(f"  핵심 개념: [blue]{', '.join(concept_names[:3])}[/blue]")


def demo_buffett_with_ontology(adapter):
    """4. 버핏 멘토와 온톨로지 연동"""
    console.print("\n" + "=" * 60)
    console.print("[bold cyan]4. 버핏 멘토 온톨로지 연동[/bold cyan]")
    console.print("=" * 60)

    from walk_risk.ai.mentor_personas import BuffettPersona

    # Without ontology
    console.print("\n[yellow]온톨로지 없이 생성:[/yellow]")
    buffett_basic = BuffettPersona()
    console.print(f"  {buffett_basic.get_greeting()}")

    # With ontology
    console.print("\n[yellow]온톨로지와 함께 생성:[/yellow]")
    buffett_enhanced = BuffettPersona(ontology_adapter=adapter)
    console.print(f"  {buffett_enhanced.get_greeting()}")

    # Get ontology-enhanced hint
    puzzle_data = {
        "symbol": "AAPL",
        "change_percent": -5.2,
        "has_financial_data": True,
    }

    enhanced_hint = buffett_enhanced.get_ontology_enhanced_hint(
        puzzle_data=puzzle_data,
        risk_type="MarketRisk",
    )

    if enhanced_hint:
        console.print("\n[yellow]온톨로지 기반 힌트:[/yellow]")
        panel = Panel(enhanced_hint, title="버핏의 조언", border_style="green")
        console.print(panel)
    else:
        console.print("\n[dim]온톨로지 컨텍스트가 로드되지 않았습니다.[/dim]")


def demo_risk_classification(adapter):
    """5. 시장 이벤트 리스크 분류"""
    console.print("\n" + "=" * 60)
    console.print("[bold cyan]5. 시장 이벤트 리스크 분류[/bold cyan]")
    console.print("=" * 60)

    from walk_risk.ontology import RiskOntologyManager

    risk_manager = RiskOntologyManager(adapter)

    # Sample market events
    events = [
        {
            "name": "급격한 주가 하락",
            "data": {"change_percent": -8.5, "volume_ratio": 2.5},
        },
        {
            "name": "거래량 급증",
            "data": {"change_percent": 1.2, "volume_ratio": 5.0},
        },
        {
            "name": "실적 발표 이후",
            "data": {"change_percent": -3.0, "volume_ratio": 1.5, "event_type": "earnings"},
        },
        {
            "name": "규제 뉴스",
            "data": {"change_percent": -2.0, "volume_ratio": 1.2, "event_type": "regulatory"},
        },
    ]

    for event in events:
        console.print(f"\n[bold]{event['name']}[/bold]")
        console.print(f"  데이터: {event['data']}")

        classifications = risk_manager.classify_market_event(event["data"])

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("리스크 유형")
        table.add_column("하위 카테고리")
        table.add_column("신뢰도")
        table.add_column("근거")

        for c in classifications:
            table.add_row(
                c["risk_type"].value,
                c.get("subcategory") or "-",
                f"{c['confidence']:.0%}",
                c.get("reason", ""),
            )

        console.print(table)


def demo_sparql_query(adapter):
    """6. SPARQL 쿼리 예시"""
    console.print("\n" + "=" * 60)
    console.print("[bold cyan]6. SPARQL 쿼리 예시[/bold cyan]")
    console.print("=" * 60)

    # Query all risk types with Korean labels
    query = """
    PREFIX wrisk_class: <http://walkrisk.org/class#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?risk ?label WHERE {
        ?risk rdfs:subClassOf wrisk_class:Risk .
        ?risk rdfs:label ?label .
        FILTER(LANG(?label) = "ko")
    }
    ORDER BY ?risk
    """

    console.print("\n[yellow]쿼리: 모든 리스크 유형 (한국어)[/yellow]")
    console.print(f"[dim]{query.strip()}[/dim]\n")

    results = adapter.query(query)

    if results:
        table = Table(title="쿼리 결과")
        table.add_column("URI")
        table.add_column("한국어 라벨")

        for r in results:
            risk_uri = r.get("risk", "")
            class_name = risk_uri.split("#")[-1] if "#" in risk_uri else risk_uri
            table.add_row(class_name, r.get("label", ""))

        console.print(table)
    else:
        console.print("[dim]결과가 없습니다.[/dim]")


def main():
    """메인 데모 실행"""
    console.print(
        Panel.fit(
            "[bold green]Walk Risk - Grokipedia 온톨로지 통합 데모[/bold green]\n"
            "금융 리스크 관리 학습 플랫폼의 온톨로지 연동을 시연합니다.",
            border_style="green",
        )
    )

    # 1. Load ontology
    adapter = demo_ontology_loading()
    if not adapter:
        console.print("[red]온톨로지 로딩 실패. 데모를 종료합니다.[/red]")
        return

    # 2. Risk hierarchy
    demo_risk_hierarchy(adapter)

    # 3. Mentor info
    demo_mentor_info(adapter)

    # 4. Buffett with ontology
    demo_buffett_with_ontology(adapter)

    # 5. Risk classification
    demo_risk_classification(adapter)

    # 6. SPARQL query
    demo_sparql_query(adapter)

    # Summary
    console.print("\n" + "=" * 60)
    console.print("[bold green]데모 완료![/bold green]")
    console.print("=" * 60)
    console.print(
        "\n[cyan]다음 단계:[/cyan]\n"
        "- 더 많은 금융 개념을 온톨로지에 추가\n"
        "- 다른 멘토들도 온톨로지 연동\n"
        "- 퍼즐 자동 생성 시스템 구현\n"
        "- Grokipedia 동기화 기능 추가"
    )


if __name__ == "__main__":
    main()
