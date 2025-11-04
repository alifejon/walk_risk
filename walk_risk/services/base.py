"""Base Service Class for Walk Risk Services"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime

from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class BaseService(ABC):
    """모든 서비스의 기본 클래스"""

    def __init__(self):
        self.logger = logger
        self._initialized = False

    async def initialize(self):
        """서비스 초기화 (비동기)"""
        if not self._initialized:
            await self._setup()
            self._initialized = True
            self.logger.info(f"{self.__class__.__name__} initialized")

    @abstractmethod
    async def _setup(self):
        """서비스별 초기화 로직"""
        pass

    def _validate_initialized(self):
        """초기화 확인"""
        if not self._initialized:
            raise RuntimeError(f"{self.__class__.__name__} not initialized. Call initialize() first.")

    def _create_response(self, success: bool, data: Any = None, message: str = "", error_code: str = None) -> Dict[str, Any]:
        """표준 응답 형식 생성"""
        response = {
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "message": message
        }

        if error_code:
            response["error_code"] = error_code

        return response

    def _handle_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """에러 처리 및 로깅"""
        error_msg = f"{context}: {str(error)}" if context else str(error)
        self.logger.error(error_msg, exc_info=True)

        return self._create_response(
            success=False,
            message=error_msg,
            error_code=error.__class__.__name__
        )