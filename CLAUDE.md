# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Walk Risk is a comprehensive gamified financial risk management learning platform called "언락: 리스크 마스터" (Unlock: Risk Master). The project transforms real-world financial risks into engaging educational experiences through real-time market data integration and AI-powered guidance.

## Development Commands

### Running the Application
```bash
# Install dependencies
uv sync

# Run the main application
uv run python main.py

# Run via CLI entry point (after installation)
walk-risk

# Add new dependencies
uv add package-name

# Add development dependencies  
uv add --dev package-name
```

### Environment Setup
- Python 3.12+ required
- Use `.env` file for API keys and configuration
- SQLite database for development (configurable for production)

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