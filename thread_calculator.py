#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
스레드 안전성 계산기 (Thread Safety Calculator)
시스템 사양을 분석하여 크롤링에 안전한 스레드 수를 계산합니다.
"""

import psutil
import platform
import os
import time
from datetime import datetime

class ThreadCalculator:
    """시스템 사양 기반 안전한 스레드 수 계산기"""
    
    def __init__(self):
        self.system_info = self._get_system_info()
        self.chrome_memory_per_instance = 0.3  # 크롬 1개당 300MB (보수적 추정)
        self.chrome_cpu_per_instance = 0.1     # 크롬 1개당 10% CPU (백그라운드 기준)
        
    def _get_system_info(self):
        """시스템 정보 수집"""
        try:
            # CPU 정보
            cpu_count_physical = psutil.cpu_count(logical=False)
            cpu_count_logical = psutil.cpu_count(logical=True)
            
            # 메모리 정보
            memory = psutil.virtual_memory()
            memory_total_gb = memory.total / (1024**3)
            memory_available_gb = memory.available / (1024**3)
            memory_used_gb = memory.used / (1024**3)
            memory_percent = memory.percent
            
            # 디스크 정보
            disk = psutil.disk_usage('/')
            disk_total_gb = disk.total / (1024**3)
            disk_free_gb = disk.free / (1024**3)
            disk_percent = (disk.used / disk.total) * 100
            
            # OS 정보
            os_name = platform.system()
            os_version = platform.version()
            
            return {
                'cpu_physical': cpu_count_physical,
                'cpu_logical': cpu_count_logical,
                'memory_total_gb': memory_total_gb,
                'memory_available_gb': memory_available_gb,
                'memory_used_gb': memory_used_gb,
                'memory_percent': memory_percent,
                'disk_total_gb': disk_total_gb,
                'disk_free_gb': disk_free_gb,
                'disk_percent': disk_percent,
                'os_name': os_name,
                'os_version': os_version
            }
        except Exception as e:
            print(f"시스템 정보 수집 실패: {str(e)}")
            return None
    
    def calculate_memory_based_threads(self):
        """메모리 기반 안전한 스레드 수 계산"""
        if not self.system_info:
            return 2  # 기본값
        
        available_memory_gb = self.system_info['memory_available_gb']
        
        # 크롬 인스턴스당 필요 메모리로 계산
        theoretical_threads = available_memory_gb / self.chrome_memory_per_instance
        
        # 안전 마진 적용 (70%만 사용)
        safe_threads = int(theoretical_threads * 0.7)
        
        # 최소 1개, 최대 8개로 제한
        safe_threads = max(1, min(safe_threads, 8))
        
        return safe_threads
    
    def calculate_cpu_based_threads(self):
        """CPU 기반 안전한 스레드 수 계산"""
        if not self.system_info:
            return 2  # 기본값
        
        cpu_physical = self.system_info['cpu_physical']
        
        # 물리적 코어 수의 2배까지 허용 (과부하 방지)
        cpu_based_threads = cpu_physical * 2
        
        # 최소 1개, 최대 6개로 제한
        cpu_based_threads = max(1, min(cpu_based_threads, 6))
        
        return cpu_based_threads
    
    def calculate_disk_based_threads(self):
        """디스크 기반 안전한 스레드 수 계산"""
        if not self.system_info:
            return 2  # 기본값
        
        disk_free_gb = self.system_info['disk_free_gb']
        
        # 크롤링 결과 파일 저장 공간 고려
        # 선사당 약 100MB 필요 (보수적 추정)
        space_per_carrier = 0.1  # 100MB
        
        theoretical_threads = disk_free_gb / space_per_carrier
        
        # 안전 마진 적용 (50%만 사용)
        safe_threads = int(theoretical_threads * 0.5)
        
        # 최소 1개, 최대 10개로 제한
        safe_threads = max(1, min(safe_threads, 10))
        
        return safe_threads
    
    def calculate_network_based_threads(self):
        """네트워크 기반 안전한 스레드 수 계산"""
        # 네트워크 대역폭 고려
        # 일반적인 가정: 동시 다운로드 3-5개가 적절
        return 4
    
    def get_optimal_thread_count(self):
        """최적의 스레드 수 계산 (모든 요소 고려)"""
        memory_threads = self.calculate_memory_based_threads()
        cpu_threads = self.calculate_cpu_based_threads()
        disk_threads = self.calculate_disk_based_threads()
        network_threads = self.calculate_network_based_threads()
        
        # 가장 보수적인 값 선택 (안전 우선)
        optimal_threads = min(memory_threads, cpu_threads, disk_threads, network_threads)
        
        return optimal_threads
    
    def get_recommended_thread_count(self):
        """권장 스레드 수 (시스템 메모리 기반)"""
        if not self.system_info:
            return 2
        
        memory_total_gb = self.system_info['memory_total_gb']
        
        if memory_total_gb >= 32:
            return 4      # 32GB 이상: 4개 스레드
        elif memory_total_gb >= 16:
            return 3      # 16GB 이상: 3개 스레드
        elif memory_total_gb >= 8:
            return 2      # 8GB 이상: 2개 스레드
        else:
            return 1      # 8GB 미만: 1개 스레드
    
    def get_safety_level(self, thread_count):
        """주어진 스레드 수의 안전도 평가"""
        if thread_count <= 2:
            return "매우 안전"
        elif thread_count <= 3:
            return "안전"
        elif thread_count <= 4:
            return "주의"
        elif thread_count <= 6:
            return "위험"
        else:
            return "매우 위험"
    
    def get_performance_estimate(self, thread_count):
        """성능 향상 예상치 계산"""
        if thread_count == 1:
            return "기본 (순차 처리)"
        elif thread_count == 2:
            return "50% 향상 (2배 빠름)"
        elif thread_count == 3:
            return "67% 향상 (3배 빠름)"
        elif thread_count == 4:
            return "75% 향상 (4배 빠름)"
        else:
            return f"{(thread_count-1)/thread_count*100:.1f}% 향상"
    
    def print_detailed_analysis(self):
        """상세한 시스템 분석 결과 출력"""
        print("="*80)
        print("시스템 상세 분석 결과")
        print("="*80)
        
        if not self.system_info:
            print("시스템 정보 수집 실패")
            return
        
        # 시스템 기본 정보
        print(f"운영체제: {self.system_info['os_name']} {self.system_info['os_version']}")
        print(f"CPU: {self.system_info['cpu_physical']}개 물리적 코어, {self.system_info['cpu_logical']}개 논리적 코어")
        print(f"메모리: {self.system_info['memory_total_gb']:.1f}GB (사용: {self.system_info['memory_percent']:.1f}%)")
        print(f"디스크: {self.system_info['disk_total_gb']:.1f}GB (여유: {self.system_info['disk_free_gb']:.1f}GB)")
        print()
        
        # 각 요소별 스레드 수 계산
        memory_threads = self.calculate_memory_based_threads()
        cpu_threads = self.calculate_cpu_based_threads()
        disk_threads = self.calculate_disk_based_threads()
        network_threads = self.calculate_network_based_threads()
        
        print("요소별 안전 스레드 수:")
        print(f"  메모리 기반: {memory_threads}개 (가용 메모리: {self.system_info['memory_available_gb']:.1f}GB)")
        print(f"  CPU 기반: {cpu_threads}개 (물리적 코어: {self.system_info['cpu_physical']}개)")
        print(f"  디스크 기반: {disk_threads}개 (여유 공간: {self.system_info['disk_free_gb']:.1f}GB)")
        print(f"  네트워크 기반: {network_threads}개 (동시 연결 고려)")
        print()
        
        # 최적 및 권장 스레드 수
        optimal_threads = self.get_optimal_thread_count()
        recommended_threads = self.get_recommended_thread_count()
        
        print("권장 스레드 수:")
        print(f"  최적 스레드 수: {optimal_threads}개")
        print(f"  권장 스레드 수: {recommended_threads}개")
        print()
        
        # 안전도 및 성능 예상
        optimal_safety = self.get_safety_level(optimal_threads)
        optimal_performance = self.get_performance_estimate(optimal_threads)
        
        print("최적 스레드 수 분석:")
        print(f"  안전도: {optimal_safety}")
        print(f"  성능 향상: {optimal_performance}")
        print()
        
        # 경고사항
        if optimal_threads >= 6:
            print("경고: 높은 스레드 수는 시스템 안정성에 영향을 줄 수 있습니다.")
        elif optimal_threads <= 1:
            print("정보: 시스템 사양이 낮아 순차 처리를 권장합니다.")
        
        print("="*80)

def main():
    """메인 실행 함수"""
    print("스레드 안전성 계산기 시작")
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 계산기 인스턴스 생성
    calculator = ThreadCalculator()
    
    # 상세 분석 실행
    calculator.print_detailed_analysis()
    
    # 간단한 사용 예시
    print("\n사용 예시:")
    print("```python")
    print("# test_main2.py에서 사용")
    print("from thread_calculator import ThreadCalculator")
    print("")
    print("calculator = ThreadCalculator()")
    print("optimal_threads = calculator.get_optimal_thread_count()")
    print("")
    print(f"# 현재 시스템 기준: {calculator.get_optimal_thread_count()}개 스레드 권장")
    print("with ThreadPoolExecutor(max_workers=optimal_threads) as executor:")
    print("    # 안전한 병렬 처리")
    print("```")
    
    print("\n분석 완료!")

if __name__ == "__main__":
    main()
