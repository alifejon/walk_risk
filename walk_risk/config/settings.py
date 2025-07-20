"""
Application settings and configuration
"""
import os
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass, field


@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = "sqlite:///walk_risk.db"
    pool_size: int = 5
    max_overflow: int = 10


@dataclass
class MarketDataConfig:
    """Market data API configuration"""
    primary_source: str = "alphavantage"
    backup_sources: list = field(default_factory=lambda: ["yahoo", "iex"])
    api_keys: Dict[str, str] = field(default_factory=dict)
    update_interval: int = 60  # seconds
    cache_duration: int = 300  # seconds


@dataclass
class RiskConfig:
    """Risk calculation configuration"""
    volatility_window: int = 20
    correlation_threshold: float = 0.7
    vix_high_threshold: float = 30.0
    vix_extreme_threshold: float = 40.0


@dataclass
class GameConfig:
    """Game mechanics configuration"""
    max_concurrent_risks: int = 5
    unlock_cooldown: int = 300  # seconds
    experience_multiplier: float = 1.0
    difficulty_scaling: float = 1.2


@dataclass
class Settings:
    """Main application settings"""
    debug: bool = False
    log_level: str = "INFO"
    secret_key: str = "dev-secret-key"
    
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    market_data: MarketDataConfig = field(default_factory=MarketDataConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
    game: GameConfig = field(default_factory=GameConfig)
    
    @classmethod
    def from_env(cls) -> "Settings":
        """Load settings from environment variables"""
        settings = cls()
        
        # Basic settings
        settings.debug = os.getenv("DEBUG", "false").lower() == "true"
        settings.log_level = os.getenv("LOG_LEVEL", "INFO")
        settings.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")
        
        # Database
        settings.database.url = os.getenv("DATABASE_URL", settings.database.url)
        
        # Market data API keys
        settings.market_data.api_keys = {
            "alphavantage": os.getenv("ALPHAVANTAGE_API_KEY", ""),
            "yahoo": os.getenv("YAHOO_API_KEY", ""),
            "iex": os.getenv("IEX_API_KEY", ""),
        }
        
        return settings


# Global settings instance
settings = Settings.from_env()