# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/01/27
# 역할 : 선박별 크롤링 추적을 담당하는 클래스

import logging
from datetime import datetime
from typing import Dict, List

class VesselTracker:
    """선박별 크롤링 추적을 담당하는 클래스"""
    
    def __init__(self, carrier_name: str):
        self.carrier_name = carrier_name
        self.logger = logging.getLogger(__name__)
        
        # 크롤링 결과 추적
        self.success_count = 0
        self.fail_count = 0
        self.failed_vessels = []
        self.failed_reasons = {}
        self.vessel_name_list = []
        
        # 선박별 개별 시간 추적
        self.vessel_timings = {}
        self.vessel_start_times = {}
    
    def start_vessel_tracking(self, vessel_name: str):
        """선박별 크롤링 시작 시간 기록"""
        self.vessel_start_times[vessel_name] = datetime.now()
        if vessel_name not in self.vessel_name_list:
            self.vessel_name_list.append(vessel_name)
    
    def end_vessel_tracking(self, vessel_name: str, success: bool = True):
        """선박별 크롤링 종료 시간 기록 및 소요시간 계산"""
        if vessel_name in self.vessel_start_times:
            start_time = self.vessel_start_times[vessel_name]
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 선박별 개별 소요시간 저장
            self.vessel_timings[vessel_name] = duration
            
            # 성공/실패 카운트 업데이트
            if success:
                self.success_count += 1
                self.logger.info(f"선박 {vessel_name} 크롤링 완료 (소요시간: {duration:.2f}초)")
            else:
                self.fail_count += 1
                self.logger.warning(f"선박 {vessel_name} 크롤링 실패 (소요시간: {duration:.2f}초)")
            
            # 시작 시간 제거 (메모리 정리)
            del self.vessel_start_times[vessel_name]
        else:
            # 시작 시간이 없는 경우 기본값 설정
            self.vessel_timings[vessel_name] = 0.0
            if success:
                self.success_count += 1
            else:
                self.fail_count += 1
    
    def get_vessel_duration(self, vessel_name: str) -> float:
        """선박별 개별 소요시간 조회"""
        return self.vessel_timings.get(vessel_name, 0.0)
    
    def record_vessel_failure(self, vessel_name: str, reason: str, error_type: str = None, retryable: bool = False):
        """선박 실패 기록"""
        if vessel_name not in self.failed_vessels:
            self.failed_vessels.append(vessel_name)
            self.failed_reasons[vessel_name] = reason
        
        # 에러 타입에 따른 로그 레벨 결정
        if error_type == 'blocked_error':
            self.logger.error(f"선박 {vessel_name} 크롤링 차단: {reason}")
        else:
            self.logger.warning(f"선박 {vessel_name} 크롤링 실패 (재시도 가능): {reason}")
    
    def get_summary(self) -> Dict:
        """크롤링 결과 요약 반환"""
        return {
            'carrier_name': self.carrier_name,
            'success_count': self.success_count,
            'fail_count': self.fail_count,
            'failed_vessels': self.failed_vessels.copy(),
            'failed_reasons': self.failed_reasons.copy(),
            'vessel_timings': self.vessel_timings.copy(),
            'total_vessels': len(self.vessel_name_list)
        }
    
    def reset(self):
        """추적 데이터 초기화"""
        self.success_count = 0
        self.fail_count = 0
        self.failed_vessels.clear()
        self.failed_reasons.clear()
        self.vessel_timings.clear()
        self.vessel_start_times.clear()
        self.vessel_name_list.clear()
