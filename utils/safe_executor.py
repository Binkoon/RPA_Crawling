# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/01/27
# 역할 : 크롤러 실행 시 타임아웃과 안전한 재시도를 관리

import signal
import time
import logging
from datetime import datetime, timedelta
from typing import Callable, Any, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import traceback

class TimeoutException(Exception):
    """타임아웃 예외"""
    pass

class SafeExecutor:
    """안전한 크롤러 실행을 위한 실행기"""
    
    def __init__(self, default_timeout: int = 600, max_retries: int = 2):
        """
        Args:
            default_timeout: 기본 타임아웃 시간 (초)
            max_retries: 최대 재시도 횟수
        """
        self.default_timeout = default_timeout
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)
        
        # 선사별 타임아웃 설정 (문제가 있는 선사는 더 긴 타임아웃)
        self.carrier_timeouts = {
            'ONE': 900,        # ONE은 PDF 다운로드로 시간이 오래 걸림
            'EVERGREEN': 600,  # EVERGREEN은 안정적
            'COSCO': 600,      # COSCO는 안정적
            'WANHAI': 600,     # WANHAI는 안정적
            'HMM': 600,        # HMM은 안정적
            'YML': 600,        # YML은 안정적
            # 다른 선사들은 기본값 사용
        }
    
    def get_timeout_for_carrier(self, carrier_name: str) -> int:
        """선사별 타임아웃 시간 반환"""
        return self.carrier_timeouts.get(carrier_name, self.default_timeout)
    
    def execute_with_timeout(self, func: Callable, carrier_name: str, 
                           timeout: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """
        타임아웃과 함께 함수 실행
        
        Args:
            func: 실행할 함수
            carrier_name: 선사명
            timeout: 타임아웃 시간 (None이면 선사별 기본값 사용)
            **kwargs: 함수에 전달할 인자들
            
        Returns:
            실행 결과 딕셔너리
        """
        if timeout is None:
            timeout = self.get_timeout_for_carrier(carrier_name)
        
        start_time = datetime.now()
        self.logger.info(f"=== {carrier_name} 크롤링 시작 (타임아웃: {timeout}초) ===")
        
        # 재시도 로직
        for attempt in range(self.max_retries + 1):
            try:
                self.logger.info(f"=== {carrier_name} 시도 {attempt + 1}/{self.max_retries + 1} ===")
                
                # ThreadPoolExecutor를 사용한 타임아웃 실행
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(func, **kwargs)
                    
                    try:
                        result = future.result(timeout=timeout)
                        end_time = datetime.now()
                        duration = (end_time - start_time).total_seconds()
                        
                        self.logger.info(f"=== {carrier_name} 크롤링 성공 (소요시간: {duration:.2f}초) ===")
                        
                        return {
                            'success': True,
                            'result': result,
                            'duration': duration,
                            'start_time': start_time,
                            'end_time': end_time,
                            'attempts': attempt + 1,
                            'timeout': timeout
                        }
                        
                    except FutureTimeoutError:
                        # 타임아웃 발생
                        self.logger.warning(f"=== {carrier_name} 타임아웃 발생 (시도 {attempt + 1}) ===")
                        
                        if attempt < self.max_retries:
                            # 재시도 전 대기
                            wait_time = min(30, (attempt + 1) * 10)  # 점진적 대기
                            self.logger.info(f"=== {carrier_name} 재시도 대기: {wait_time}초 ===")
                            time.sleep(wait_time)
                            continue
                        else:
                            # 최대 재시도 횟수 초과
                            end_time = datetime.now()
                            duration = (end_time - start_time).total_seconds()
                            
                            self.logger.error(f"=== {carrier_name} 최종 타임아웃 실패 ===")
                            
                            return {
                                'success': False,
                                'error': 'Timeout',
                                'error_type': 'timeout',
                                'duration': duration,
                                'start_time': start_time,
                                'end_time': end_time,
                                'attempts': attempt + 1,
                                'timeout': timeout
                            }
                
            except Exception as e:
                # 기타 예외 발생
                self.logger.error(f"=== {carrier_name} 예외 발생 (시도 {attempt + 1}): {str(e)} ===")
                
                if attempt < self.max_retries:
                    # 재시도 전 대기
                    wait_time = min(30, (attempt + 1) * 10)
                    self.logger.info(f"=== {carrier_name} 재시도 대기: {wait_time}초 ===")
                    time.sleep(wait_time)
                    continue
                else:
                    # 최대 재시도 횟수 초과
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    
                    self.logger.error(f"=== {carrier_name} 최종 실패 ===")
                    
                    return {
                        'success': False,
                        'error': str(e),
                        'error_type': 'exception',
                        'traceback': traceback.format_exc(),
                        'duration': duration,
                        'start_time': start_time,
                        'end_time': end_time,
                        'attempts': attempt + 1,
                        'timeout': timeout
                    }
    
    def is_recoverable_error(self, error_type: str, error_message: str) -> bool:
        """
        에러가 복구 가능한지 판단
        
        Args:
            error_type: 에러 타입
            error_message: 에러 메시지
            
        Returns:
            복구 가능 여부
        """
        # 복구 불가능한 에러들
        non_recoverable_errors = [
            'blocked_error',
            'validation_error',
            'system_error'
        ]
        
        # 복구 불가능한 키워드들
        non_recoverable_keywords = [
            'blocked',
            'forbidden',
            'access denied',
            'invalid',
            'bad request'
        ]
        
        # 에러 타입 체크
        if error_type in non_recoverable_errors:
            return False
        
        # 에러 메시지 키워드 체크
        error_lower = error_message.lower()
        if any(keyword in error_lower for keyword in non_recoverable_keywords):
            return False
        
        return True
    
    def get_retry_delay(self, attempt: int, base_delay: int = 10) -> int:
        """
        재시도 간 대기 시간 계산 (지수 백오프)
        
        Args:
            attempt: 현재 시도 횟수
            base_delay: 기본 대기 시간
            
        Returns:
            대기 시간 (초)
        """
        delay = base_delay * (2 ** attempt)
        return min(delay, 300)  # 최대 5분
