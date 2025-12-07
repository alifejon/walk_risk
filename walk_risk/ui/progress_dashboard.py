"""Progress Dashboard - 플레이어 성장 시각화 시스템"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
from rich.columns import Columns


@dataclass
class PlayerProgress:
    """플레이어 진행 상황 데이터"""
    player_id: str
    username: str
    level: int = 1
    experience: int = 0
    experience_to_next: int = 100

    # 퍼즐 통계
    puzzles_completed: int = 0
    puzzles_correct: int = 0
    current_streak: int = 0
    best_streak: int = 0

    # 유형별 숙련도
    mastery: Dict[str, int] = field(default_factory=lambda: {
        "price_drop": 0,
        "price_surge": 0,
        "volatility": 0,
        "divergence": 0,
        "mystery": 0
    })

    # 스킬 및 업적
    skills: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)

    # 시간 추적
    total_play_time_minutes: int = 0
    last_played: Optional[datetime] = None


class ProgressDashboard:
    """플레이어 성장 대시보드"""

    LEVEL_TITLES = {
        1: "초보 투자자",
        2: "견습 분석가",
        3: "주니어 분석가",
        4: "분석가",
        5: "시니어 분석가",
        6: "리스크 스카우트",
        7: "리스크 헌터",
        8: "리스크 전문가",
        9: "리스크 마스터",
        10: "시장 통찰자",
        11: "시장 해석가",
        12: "트렌드 리더",
        13: "베테랑 투자자",
        14: "엘리트 투자자",
        15: "마스터 투자자",
        16: "투자 전략가",
        17: "시장 현자",
        18: "월스트리트 베테랑",
        19: "투자 레전드",
        20: "리스크 초월자"
    }

    MASTERY_NAMES = {
        0: "미경험",
        1: "입문",
        2: "초급",
        3: "중급",
        4: "고급",
        5: "마스터"
    }

    PUZZLE_TYPE_KOREAN = {
        "price_drop": "급락 분석",
        "price_surge": "급등 분석",
        "volatility": "변동성 분석",
        "divergence": "괴리 분석",
        "mystery": "미스터리"
    }

    def __init__(self):
        self.console = Console()

    def display_full_dashboard(self, progress: PlayerProgress) -> None:
        """전체 대시보드 표시"""
        self.console.clear()

        # 헤더
        self._display_header(progress)

        # 레벨 진행률
        self._display_level_progress(progress)

        # 퍼즐 통계
        self._display_puzzle_stats(progress)

        # 숙련도
        self._display_mastery(progress)

        # 스킬 및 업적
        self._display_skills_achievements(progress)

    def _display_header(self, progress: PlayerProgress) -> None:
        """헤더 표시"""
        title = self.LEVEL_TITLES.get(progress.level, f"레벨 {progress.level}")

        header_text = f"""
[bold cyan]╔══════════════════════════════════════════════════════════════╗[/bold cyan]
[bold cyan]║[/bold cyan]                    [bold yellow]📊 투자자 성장 대시보드[/bold yellow]                    [bold cyan]║[/bold cyan]
[bold cyan]╠══════════════════════════════════════════════════════════════╣[/bold cyan]
[bold cyan]║[/bold cyan]  [bold white]{progress.username}[/bold white]                                              [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]  [dim]칭호:[/dim] [bold green]{title}[/bold green]                                        [bold cyan]║[/bold cyan]
[bold cyan]╚══════════════════════════════════════════════════════════════╝[/bold cyan]
        """
        self.console.print(header_text)

    def _display_level_progress(self, progress: PlayerProgress) -> None:
        """레벨 진행률 표시"""
        exp_ratio = progress.experience / progress.experience_to_next if progress.experience_to_next > 0 else 0
        exp_bar_filled = int(exp_ratio * 30)
        exp_bar_empty = 30 - exp_bar_filled

        exp_bar = f"[green]{'█' * exp_bar_filled}[/green][dim]{'░' * exp_bar_empty}[/dim]"

        level_panel = Panel(
            f"""
[bold]레벨 {progress.level}[/bold] → [bold cyan]레벨 {progress.level + 1}[/bold cyan]

{exp_bar}

[dim]경험치:[/dim] [bold yellow]{progress.experience:,}[/bold yellow] / {progress.experience_to_next:,} XP
[dim]다음 레벨까지:[/dim] [bold]{progress.experience_to_next - progress.experience:,}[/bold] XP 필요
            """.strip(),
            title="📈 레벨 진행률",
            border_style="cyan"
        )
        self.console.print(level_panel)

    def _display_puzzle_stats(self, progress: PlayerProgress) -> None:
        """퍼즐 통계 표시"""
        accuracy = (progress.puzzles_correct / progress.puzzles_completed * 100) if progress.puzzles_completed > 0 else 0

        # 정확도에 따른 색상
        if accuracy >= 80:
            accuracy_color = "green"
        elif accuracy >= 60:
            accuracy_color = "yellow"
        else:
            accuracy_color = "red"

        # 연속 성공에 따른 불꽃 표시
        streak_display = "🔥" * min(progress.current_streak, 5) if progress.current_streak > 0 else "💤"

        stats_table = Table(show_header=False, box=None, padding=(0, 2))
        stats_table.add_column("Label", style="dim")
        stats_table.add_column("Value", style="bold")

        stats_table.add_row("완료한 퍼즐", f"[cyan]{progress.puzzles_completed}[/cyan]개")
        stats_table.add_row("정확한 예측", f"[green]{progress.puzzles_correct}[/green]개")
        stats_table.add_row("정확도", f"[{accuracy_color}]{accuracy:.1f}%[/{accuracy_color}]")
        stats_table.add_row("현재 연속 성공", f"{streak_display} {progress.current_streak}회")
        stats_table.add_row("최고 연속 기록", f"[gold1]🏆 {progress.best_streak}회[/gold1]")
        stats_table.add_row("총 플레이 시간", f"[magenta]{progress.total_play_time_minutes}분[/magenta]")

        stats_panel = Panel(
            Align.center(stats_table),
            title="📊 퍼즐 통계",
            border_style="blue"
        )
        self.console.print(stats_panel)

    def _display_mastery(self, progress: PlayerProgress) -> None:
        """숙련도 표시"""
        mastery_table = Table(show_header=True, header_style="bold magenta")
        mastery_table.add_column("퍼즐 유형", style="cyan")
        mastery_table.add_column("숙련도", justify="center")
        mastery_table.add_column("진행 바", justify="left")
        mastery_table.add_column("레벨", justify="center")

        for puzzle_type, level in progress.mastery.items():
            korean_name = self.PUZZLE_TYPE_KOREAN.get(puzzle_type, puzzle_type)
            mastery_name = self.MASTERY_NAMES.get(level, f"레벨 {level}")

            # 진행 바
            bar_filled = int((level / 5) * 10)
            bar_empty = 10 - bar_filled

            if level >= 5:
                bar_color = "gold1"
                bar = f"[{bar_color}]{'★' * 10}[/{bar_color}]"
            else:
                bar_color = "green" if level >= 3 else "yellow" if level >= 1 else "dim"
                bar = f"[{bar_color}]{'●' * bar_filled}[/{bar_color}][dim]{'○' * bar_empty}[/dim]"

            # 레벨 표시
            level_display = f"[bold]{level}[/bold]/5"

            mastery_table.add_row(korean_name, mastery_name, bar, level_display)

        mastery_panel = Panel(
            mastery_table,
            title="🎯 퍼즐 유형별 숙련도",
            border_style="magenta"
        )
        self.console.print(mastery_panel)

    def _display_skills_achievements(self, progress: PlayerProgress) -> None:
        """스킬 및 업적 표시"""
        # 스킬 섹션
        if progress.skills:
            skills_text = " | ".join([f"[cyan]{skill}[/cyan]" for skill in progress.skills[:6]])
            if len(progress.skills) > 6:
                skills_text += f" [dim]... +{len(progress.skills) - 6}개 더[/dim]"
        else:
            skills_text = "[dim]아직 획득한 스킬이 없습니다[/dim]"

        skills_panel = Panel(
            skills_text,
            title=f"🛠️ 획득한 스킬 ({len(progress.skills)}개)",
            border_style="green"
        )

        # 업적 섹션
        if progress.achievements:
            achievements_text = " | ".join([f"[gold1]{ach}[/gold1]" for ach in progress.achievements[:6]])
            if len(progress.achievements) > 6:
                achievements_text += f" [dim]... +{len(progress.achievements) - 6}개 더[/dim]"
        else:
            achievements_text = "[dim]아직 달성한 업적이 없습니다[/dim]"

        achievements_panel = Panel(
            achievements_text,
            title=f"🏅 달성한 업적 ({len(progress.achievements)}개)",
            border_style="yellow"
        )

        # 두 패널을 나란히 표시
        self.console.print(Columns([skills_panel, achievements_panel], equal=True))

    def display_quick_stats(self, progress: PlayerProgress) -> str:
        """빠른 통계 문자열 반환 (게임 중 표시용)"""
        title = self.LEVEL_TITLES.get(progress.level, f"레벨 {progress.level}")
        exp_ratio = progress.experience / progress.experience_to_next if progress.experience_to_next > 0 else 0
        exp_percent = int(exp_ratio * 100)

        streak_fire = "🔥" * min(progress.current_streak, 3) if progress.current_streak > 0 else ""

        return f"""
┌─────────────────────────────────────┐
│ 📊 {progress.username} | Lv.{progress.level} {title}
│ ⭐ XP: {progress.experience:,}/{progress.experience_to_next:,} ({exp_percent}%)
│ 🎯 정확도: {(progress.puzzles_correct / max(progress.puzzles_completed, 1) * 100):.0f}% | 연속: {progress.current_streak} {streak_fire}
└─────────────────────────────────────┘
        """.strip()

    def display_level_up_animation(self, old_level: int, new_level: int) -> None:
        """레벨업 애니메이션"""
        old_title = self.LEVEL_TITLES.get(old_level, f"레벨 {old_level}")
        new_title = self.LEVEL_TITLES.get(new_level, f"레벨 {new_level}")

        animation = f"""
[bold yellow]
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     ██╗     ███████╗██╗   ██╗███████╗██╗         ██╗   ██╗██████╗ ██╗ ║
║     ██║     ██╔════╝██║   ██║██╔════╝██║         ██║   ██║██╔══██╗██║ ║
║     ██║     █████╗  ██║   ██║█████╗  ██║         ██║   ██║██████╔╝██║ ║
║     ██║     ██╔══╝  ╚██╗ ██╔╝██╔══╝  ██║         ██║   ██║██╔═══╝ ╚═╝ ║
║     ███████╗███████╗ ╚████╔╝ ███████╗███████╗    ╚██████╔╝██║     ██╗ ║
║     ╚══════╝╚══════╝  ╚═══╝  ╚══════╝╚══════╝     ╚═════╝ ╚═╝     ╚═╝ ║
║                                                               ║
║                     [bold white]레벨 {old_level}[/bold white] → [bold cyan]레벨 {new_level}[/bold cyan]                     ║
║                                                               ║
║              [dim]{old_title}[/dim] → [bold green]{new_title}[/bold green]             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
[/bold yellow]
        """
        self.console.print(animation)

    def display_achievement_unlock(self, achievement_name: str, description: str) -> None:
        """업적 달성 표시"""
        achievement_box = f"""
[bold gold1]
╔═══════════════════════════════════════════════════════════════╗
║                     🏅 업적 달성! 🏅                          ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║     [bold white]{achievement_name:^45}[/bold white]       ║
║                                                               ║
║     [dim]{description:^45}[/dim]       ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
[/bold gold1]
        """
        self.console.print(achievement_box)

    def display_streak_celebration(self, streak_count: int) -> None:
        """연속 성공 축하"""
        fires = "🔥" * min(streak_count, 10)

        if streak_count >= 10:
            message = "전설적인 기록!"
            color = "gold1"
        elif streak_count >= 7:
            message = "불타고 있어요!"
            color = "red"
        elif streak_count >= 5:
            message = "대단해요!"
            color = "orange1"
        else:
            message = "좋은 흐름!"
            color = "yellow"

        streak_box = f"""
[bold {color}]
┌───────────────────────────────────────┐
│        {fires}        │
│                                       │
│     {streak_count}연속 성공! {message}      │
│                                       │
└───────────────────────────────────────┘
[/bold {color}]
        """
        self.console.print(streak_box)

    def get_progress_summary(self, progress: PlayerProgress) -> Dict[str, Any]:
        """진행 상황 요약 데이터 반환"""
        title = self.LEVEL_TITLES.get(progress.level, f"레벨 {progress.level}")
        accuracy = (progress.puzzles_correct / progress.puzzles_completed * 100) if progress.puzzles_completed > 0 else 0

        return {
            "username": progress.username,
            "level": progress.level,
            "title": title,
            "experience": progress.experience,
            "experience_to_next": progress.experience_to_next,
            "experience_percent": int((progress.experience / progress.experience_to_next) * 100) if progress.experience_to_next > 0 else 0,
            "puzzles_completed": progress.puzzles_completed,
            "accuracy": round(accuracy, 1),
            "current_streak": progress.current_streak,
            "best_streak": progress.best_streak,
            "skills_count": len(progress.skills),
            "achievements_count": len(progress.achievements),
            "total_mastery": sum(progress.mastery.values())
        }


# 편의 함수
def create_sample_progress() -> PlayerProgress:
    """샘플 진행 데이터 생성 (테스트용)"""
    return PlayerProgress(
        player_id="sample_001",
        username="테스트유저",
        level=7,
        experience=450,
        experience_to_next=700,
        puzzles_completed=25,
        puzzles_correct=18,
        current_streak=3,
        best_streak=7,
        mastery={
            "price_drop": 3,
            "price_surge": 2,
            "volatility": 1,
            "divergence": 0,
            "mystery": 1
        },
        skills=["급락 분석 초급", "가설 수립 기초", "단서 수집 입문"],
        achievements=["첫 퍼즐 해결", "3연속 성공", "레벨 5 달성"],
        total_play_time_minutes=120
    )


if __name__ == "__main__":
    # 테스트
    dashboard = ProgressDashboard()
    sample = create_sample_progress()
    dashboard.display_full_dashboard(sample)
