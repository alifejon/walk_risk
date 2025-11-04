# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Walk Risk is a comprehensive gamified financial risk management learning platform called "언락: 리스크 마스터" (Unlock: Risk Master). The project transforms real-world financial risks into engaging educational experiences through real-time market data integration and AI-powered guidance.

## Development Commands

### 🚨 IMPORTANT: Python Package Management Policy
**This project uses `uv` for ALL Python package management. Do NOT use pip, conda, or other package managers.**

#### Why uv?
- **Fast**: 10-100x faster than pip
- **Reliable**: Consistent dependency resolution
- **Reproducible**: Exact version locking with uv.lock
- **Modern**: Built-in virtual environment management

#### uv Setup (First Time)
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Initialize project (already done)
# uv init

# Sync all dependencies from pyproject.toml
uv sync
```

### Running the Application
```bash
# Install/sync dependencies
uv sync

# Run the main CLI application
uv run python main.py

# Run the FastAPI server
uv run python api_server.py
# OR using the entry point
uv run walk-risk-api

# Run via CLI entry point
walk-risk

# Run demos (recommended for testing)
uv run python integrated_tutorial_demo.py
uv run python risk_puzzle_auto_demo.py
```

### Package Management
```bash
# Add runtime dependencies
uv add package-name

# Add development dependencies
uv add --dev package-name

# Add specific version
uv add "package-name>=1.0.0,<2.0.0"

# Remove dependencies
uv remove package-name

# Update all dependencies
uv sync --upgrade

# Show dependency tree
uv tree
```

### Environment Setup
- **Python 3.12+ required** (managed by uv)
- **Virtual environment**: Automatically managed by uv
- Use `.env` file for API keys and configuration
- SQLite database for development (configurable for production)

### 🔧 Development Workflow
```bash
# 1. Fresh setup
uv sync

# 2. Add new dependency
uv add fastapi

# 3. Run application
uv run python api_server.py

# 4. Test functionality
uv run python integrated_tutorial_demo.py

# 5. Update dependencies (when needed)
uv sync --upgrade
```

### ⚠️ Troubleshooting
```bash
# If imports fail, ensure dependencies are synced
uv sync

# Clear cache if needed
uv cache clean

# Check Python version
uv python --version

# List installed packages
uv pip list
```

## Core Architecture

### System Components

- **Game Manager** (`walk_risk/core/game_state/game_manager.py`): Central orchestration system managing game state, player sessions, and system coordination
- **Risk Engine** (`walk_risk/core/risk_engine/`): Risk analysis, factory pattern for risk creation, and risk classification
- **Unlock System** (`walk_risk/core/unlock_system/`): Challenge types, unlock mechanics, and progression management
- **AI Guide System** (`walk_risk/ai/`): Personalized mentoring with famous investor personas (Buffett, Lynch, Graham, Dalio, Wood)
- **Data Management** (`walk_risk/data/`): Real-time market data integration with fallback systems

### Key Design Patterns

- **Factory Pattern**: Risk creation and classification (`walk_risk/core/risk_engine/`)
- **Strategy Pattern**: Different unlock mechanisms and AI mentor personalities
- **Observer Pattern**: Real-time market data feeds and event handling
- **State Pattern**: Player progression and skill tree advancement

### Data Flow

1. **Real-time Market Data** → Risk Engine → Risk Classification
2. **Player Actions** → Unlock System → Reward Calculation
3. **AI Analysis** → Personalized Guidance → Player Learning
4. **Social Features** → Community Intelligence → Shared Learning

## Core Philosophy

The game redefines risk from "danger" to "locked opportunity":
- **🔒 Locked Risk**: Not yet understood
- **🔓 Unlocking Risk**: Being analyzed  
- **🔑 Unlocked Risk**: Conquered risks
- **💎 Mastered Risk**: Transformed into opportunities

## Technical Stack

- **Python 3.12** with async/await patterns
- **Dependencies**: aiohttp, pydantic, rich, click, numpy
- **Data Sources**: Yahoo Finance with extensible source system
- **Package Management**: uv for modern Python dependency management
- **UI**: Rich-based CLI interface with interactive elements

## Key Features

### Risk Categories & Progression
- **Market Risk Master**: Volatility, trends, technical analysis
- **Credit Risk Guardian**: Credit analysis, default prediction
- **Operational Risk Controller**: Human error prevention, system management
- **Strategic Risk Visionary**: Business model analysis, regulatory navigation

### Player Systems
- **Classes**: Risk Novice → Risk Walker → Risk Master → Risk Transcender
- **Skill Trees**: 4 specialized paths with 99 levels each
- **Key System**: Knowledge, Experience, and Wisdom Keys for unlocking risks
- **Real-time Integration**: Market data affects available challenges

### AI Guidance
- **Mentor Personalities**: Warren Buffett, Peter Lynch, Benjamin Graham, Ray Dalio, Cathie Wood
- **Context-aware Advice**: Based on player progress and market conditions
- **Adaptive Learning**: System learns player preferences and adjusts guidance

## File Structure

```
walk_risk/
├── ai/                    # AI guide system with mentor personas
├── config/               # Application configuration
├── core/                 # Core game systems
│   ├── game_state/      # Game state management
│   ├── risk_engine/     # Risk analysis engine
│   └── unlock_system/   # Risk unlock mechanics
├── data/                # Data management and sources
├── models/              # Data models and structures
├── ui/                  # User interface (CLI)
└── utils/               # Utilities and logging
```

## Development Context

### When Working on This Codebase:
- Focus on async/await patterns for real-time data integration
- Maintain the educational philosophy - risks as learning opportunities
- Preserve the Korean language content and cultural context
- Ensure real market data integration remains central to the experience
- Build social features for collaborative learning
- Implement progressive skill trees with clear advancement paths

### Important Notes:
- All game content is in Korean
- Emphasis on educational value over pure entertainment
- Real market data integration is central to the experience
- Social learning and community features are key components
- Use Rich CLI for consistent terminal-based user experience

## 🔄 Development Session Management

### Work Session Documentation
**IMPORTANT**: Every development session must be properly documented to ensure continuity.

#### At the Start of Each Session:
1. **Check Previous Work**: 
   ```bash
   # Always start by reading the latest development log
   cat docs/development_log_*.md | tail -50
   
   # Check current project status
   ls -la docs/
   cat docs/roadmap_next_steps.md
   ```

2. **Review Last Session**: Read the most recent development log in `docs/` folder to understand:
   - What was accomplished
   - What problems were solved
   - What systems were implemented
   - What needs to be done next

3. **Test Current State**:
   ```bash
   # Verify all systems still work
   uv run python risk_puzzle_auto_demo.py     # New puzzle system
   uv run python tutorial_auto_demo.py        # Tutorial system  
   uv run python real_trading_auto_demo.py    # Trading system
   ```

#### During Each Session:
1. **Track Progress**: Use TodoWrite tool to track current session tasks
2. **Document Decisions**: Record why certain approaches were chosen
3. **Note Challenges**: Document any technical difficulties or roadblocks

#### At the End of Each Session:
1. **Create Development Log**: Always create a new development log file
   ```
   docs/development_log_YYYY_MM_DD.md
   ```

2. **Update Roadmap**: Modify `docs/roadmap_next_steps.md` with:
   - Completed tasks
   - New priorities discovered
   - Updated timelines
   - Next session goals

3. **Update This File**: Add any new important context to CLAUDE.md

### Current Project Status (Last Updated: 2025-08-03 - 통합 완료)

#### ✅ Recently Completed (2025-08-03):

**오전: 퍼즐 시스템 구현**
- **Core Problem Identified**: Original system was just a trading simulator, not a real game
- **Solution Implemented**: Revolutionary "Risk Puzzle System" 
- **New Game Loop**: Discovery → Investigation → Hypothesis → Validation → Learning
- **Files Added**:
  - `walk_risk/core/risk_puzzle/` - Complete puzzle system
  - `risk_puzzle_auto_demo.py` - Working demonstration
  - `docs/development_log_2025_08_03.md` - Detailed session record

**오후: 시스템 통합 완료**
- **Integration Achieved**: Puzzle system fully integrated with existing tutorial
- **Mentor Upgrade**: Buffett now provides contextual hints and validation
- **7-Stage Learning Path**: Systematic tutorial from intro to graduation
- **Files Added**:
  - `walk_risk/tutorials/puzzle_tutorial.py` - Integrated puzzle tutorial system
  - `ai/mentor_personas.py` - Enhanced with puzzle guidance (207+ lines added)
  - `integrated_tutorial_demo.py` - Complete integrated experience
  - `docs/development_log_2025_08_03_integration.md` - Integration session record

#### 🎯 Key Achievement:
Transformed Walk Risk from a "stock trading simulator" into a true "investment learning game" where:
- Players investigate market mysteries like detective puzzles
- Risk becomes something to unlock through understanding
- Learning happens through discovery, not memorization
- Each market event becomes an educational quest

#### 🚀 Immediate Next Priorities:
1. ~~**Integrate with existing systems**~~ ✅ COMPLETED
2. **Add real-time market data** - Auto-generate puzzles from actual market events  
3. **Expand puzzle content** - More scenarios, difficulty levels, and mentor integration
4. **Multi-mentor system** - Add Lynch, Graham, Dalio personalities

#### ⚠️ Critical Success Factors:
- Always ask "Is this fun?" and "Does this teach real investing?"
- Maintain the core insight: Risk = Puzzle to be solved
- Keep the educational value while maximizing engagement
- Ensure each feature serves the "investment learning" mission

### Key Demo Commands for Quick Testing:
```bash
# 🌟 MAIN: Integrated puzzle tutorial (RECOMMENDED!)
uv run python integrated_tutorial_demo.py

# Core puzzle system (2025-08-03 오전)
uv run python risk_puzzle_auto_demo.py

# Original tutorial system (reference)
uv run python tutorial_auto_demo.py

# Original trading system (reference)
uv run python real_trading_auto_demo.py
```

### Documentation Standards:
- Always include session date in development log filenames
- Use clear headings and bullet points for easy scanning  
- Include code examples for important implementations
- Note both successes AND failures for future reference
- Update roadmap with realistic timelines based on actual progress