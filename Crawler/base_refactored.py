# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/01/27
# 역할 : 리팩토링된 base.py - Composition 패턴 사용

import logging
import time
from enum import Enum
from typing import Callable, Any

# 별도 모듈에서 관리자 클래스들 import
from utils.webdriver_manager import WebDriverManager
from utils.folder_manager import FolderManager
from utils.vessel_tracker import VesselTracker

class ErrorType(Enum):
    """에러 타입 분류"""
    NETWORK_ERROR = "network_error"
    TIMEOUT_ERROR = "timeout_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    BLOCKED_ERROR = "blocked_error"
    VALIDATION_ERROR = "validation_error"
    SYSTEM_ERROR = "system_error"
    UNKNOWN_ERROR = "unknown_error"

class BaseCrawler:
    """리팩토링된 기본 크롤러 클래스 - Composition 패턴 사용"""
    
    def __init__(self, carrier_name: str):
        """크롤러 초기화 - 책임 분리"""
        self.carrier_name = carrier_name
        
        # 각 관리자 클래스 초기화 (Composition)
        self.folder_manager = FolderManager()
        self.folder_manager.create_all_directories()
        
        self.webdriver_manager = WebDriverManager(
            self.folder_manager.get_download_dir()
        )
        self.webdriver_manager.create_driver()
        
        self.vessel_tracker = VesselTracker(carrier_name)
        
        # 로깅 설정
        self.setup_logging()
    
    def setup_logging(self):
        """로깅 설정"""
        self.logger = logging.getLogger(self.carrier_name)
        self.logger.setLevel(logging.INFO)
        
        # 콘솔 핸들러 추가
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    # WebDriver 관련 메서드들 (위임)
    def visit_link(self, url: str):
        """URL 방문"""
        self.webdriver_manager.visit_link(url)
    
    def close(self):
        """WebDriver 종료"""
        self.webdriver_manager.close_driver()
    
    @property
    def driver(self):
        """WebDriver 접근자"""
        return self.webdriver_manager.driver
    
    @property
    def wait(self):
        """WebDriverWait 접근자"""
        return self.webdriver_manager.wait
    
    # 폴더 관련 메서드들 (위임)
    def get_save_path(self, vessel_name: str) -> str:
        """파일 저장 경로 생성"""
        return self.folder_manager.get_save_path(self.carrier_name, vessel_name)
    
    # 선박 추적 관련 메서드들 (위임)
    def start_vessel_tracking(self, vessel_name: str):
        """선박별 크롤링 시작 시간 기록"""
        self.vessel_tracker.start_vessel_tracking(vessel_name)
    
    def end_vessel_tracking(self, vessel_name: str, success: bool = True):
        """선박별 크롤링 종료 시간 기록"""
        self.vessel_tracker.end_vessel_tracking(vessel_name, success)
    
    def get_vessel_duration(self, vessel_name: str) -> float:
        """선박별 개별 소요시간 조회"""
        return self.vessel_tracker.get_vessel_duration(vessel_name)
    
    def record_vessel_failure(self, vessel_name: str, reason: str, error_type: str = None):
        """선박 실패 기록"""
        self.vessel_tracker.record_vessel_failure(vessel_name, reason, error_type)
    
    # 결과 조회 메서드들 (위임)
    @property
    def success_count(self) -> int:
        return self.vessel_tracker.success_count
    
    @property
    def fail_count(self) -> int:
        return self.vessel_tracker.fail_count
    
    @property
    def failed_vessels(self) -> list:
        return self.vessel_tracker.failed_vessels
    
    @property
    def vessel_name_list(self) -> list:
        return self.vessel_tracker.vessel_name_list
    
    # 유틸리티 메서드들
    def smart_retry(self, func: Callable, max_retries: int = 2, base_delay: float = 1) -> Any:
        """스마트 재시도 로직"""
        for attempt in range(max_retries + 1):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries:
                    raise e
                
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
                continue
    
    def analyze_error(self, error) -> ErrorType:
        """에러 분석 및 타입 분류"""
        error_str = str(error).lower()
        
        if any(keyword in error_str for keyword in ['connection', 'timeout', 'network']):
            return ErrorType.NETWORK_ERROR
        elif any(keyword in error_str for keyword in ['timeout', 'timed out']):
            return ErrorType.TIMEOUT_ERROR
        elif any(keyword in error_str for keyword in ['rate limit', 'too many requests', '429']):
            return ErrorType.RATE_LIMIT_ERROR
        elif any(keyword in error_str for keyword in ['blocked', 'forbidden', '403', 'access denied']):
            return ErrorType.BLOCKED_ERROR
        elif any(keyword in error_str for keyword in ['validation', 'invalid', 'bad request', '400']):
            return ErrorType.VALIDATION_ERROR
        elif any(keyword in error_str for keyword in ['internal server error', '500', 'service unavailable']):
            return ErrorType.SYSTEM_ERROR
        
        return ErrorType.UNKNOWN_ERROR
    
    def get_summary(self) -> dict:
        """크롤링 결과 요약"""
        return self.vessel_tracker.get_summary()
