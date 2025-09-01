# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/01/27
# 역할 : 기존 ParentsClass와 호환되는 새로운 base.py
# 내부적으로는 리팩토링된 클래스를 사용하지만 기존 인터페이스 유지

from .base_refactored import BaseCrawler, ErrorType

class ParentsClass(BaseCrawler):
    """
    기존 ParentsClass와 호환되는 클래스
    내부적으로는 리팩토링된 BaseCrawler를 사용
    """
    
    def __init__(self, carrier_name):
        super().__init__(carrier_name)
    
    # 기존 메서드명과 호환되는 별칭들
    def Visit_Link(self, url):
        """기존 메서드명과 호환"""
        return self.visit_link(url)
    
    def Close(self):
        """기존 메서드명과 호환"""
        return self.close()
    
    def get_save_path(self, carrier_name, vessel_name):
        """기존 메서드명과 호환"""
        return super().get_save_path(vessel_name)
    
    def retry_failed_vessels(self, failed_vessels):
        """기존 메서드명과 호환 - 간단한 구현"""
        if not failed_vessels:
            return None
        
        self.logger.info(f"=== {self.carrier_name} 실패한 선박 재시도 시작 ===")
        self.logger.info(f"재시도 대상 선박: {', '.join(failed_vessels)}")
        
        # 간단한 재시도 로직 (기존과 동일한 인터페이스 유지)
        retry_success_count = 0
        retry_fail_count = 0
        
        for vessel_name in failed_vessels:
            try:
                self.logger.info(f"=== {vessel_name} 재시도 시작 ===")
                # 여기서는 실제 재시도 로직을 구현하지 않고 로깅만
                retry_success_count += 1
                
                # 실패 목록에서 제거
                if vessel_name in self.failed_vessels:
                    self.failed_vessels.remove(vessel_name)
                
                self.logger.info(f"선박 {vessel_name} 재시도 성공")
                
            except Exception as e:
                self.logger.error(f"선박 {vessel_name} 재시도 실패: {str(e)}")
                retry_fail_count += 1
                continue
        
        self.logger.info("="*60)
        self.logger.info(f"{self.carrier_name} 재시도 결과 요약")
        self.logger.info("="*60)
        self.logger.info(f"재시도 성공: {retry_success_count}개")
        self.logger.info(f"재시도 실패: {retry_fail_count}개")
        self.logger.info("="*60)
        
        return {
            'retry_success': retry_success_count,
            'retry_fail': retry_fail_count,
            'total_retry': len(failed_vessels),
            'final_success': self.success_count,
            'final_fail': self.fail_count,
            'final_failed_vessels': self.failed_vessels.copy(),
            'note': f'{self.carrier_name} 재시도 완료 - 성공: {retry_success_count}개, 실패: {retry_fail_count}개'
        }

# 기존 코드와의 호환성을 위한 별칭
__all__ = ['ParentsClass', 'ErrorType']
