#!/usr/bin/env python3
"""
InvestWalk API Server
FastAPI 개발 서버를 실행하기 위한 엔트리포인트
"""

if __name__ == "__main__":
    from walk_risk.api.main import run_development_server
    run_development_server()