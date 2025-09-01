# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/08/27
# 역할 : 체크포인트와 타임아웃 시스템이 통합된 개선된 순차처리 크롤링 메인 파일

import traceback
from datetime import datetime
import sys

# 공통 모듈 import
from utils.logging_setup import setup_main_logging, get_today_log_dir
from utils.config_loader import get_carriers_to_run, get_system_config, reload_system_config
from utils.crawler_executor import run_carrier_sequential
from utils.excel_logger import save_excel_log, add_google_upload_logs
from utils.google_upload import run_main_upload, upload_errorlog_to_drive
from utils.data_cleanup import cleanup_old_data, cleanup_old_errorlogs

# 새로운 모듈 import
from utils.checkpoint_manager import CheckpointManager
from utils.safe_executor import SafeExecutor

class EnhancedSequentialCrawlingManager:
    """체크포인트와 타임아웃이 지원되는 순차처리 크롤링 결과 관리자"""
    
    def __init__(self):
        self.crawling_results = []
        self.completed_carriers = []
        self.failed_carriers = []
        self.checkpoint_manager = CheckpointManager()
        self.safe_executor = SafeExecutor()
        
    def add_result(self, carrier_name, result):
        """결과 추가 및 체크포인트 저장"""
        self.crawling_results.append((carrier_name, result))
        
        if result.get('success', False):
            self.completed_carriers.append(carrier_name)
        else:
            self.failed_carriers.append(carrier_name)
        
        # 체크포인트 저장
        self.checkpoint_manager.save_checkpoint(
            completed_carriers=self.completed_carriers,
            failed_carriers=self.failed_carriers,
            current_carrier=None,
            error_info=result.get('error_info', {})
        )
    
    def get_results(self):
        """결과 조회 (복사본 반환)"""
        return self.crawling_results.copy()
    
    def get_results_count(self):
        """결과 개수 조회"""
        return len(self.crawling_results)
    
    def resume_from_checkpoint(self, all_carriers):
        """체크포인트에서 복구"""
        if not self.checkpoint_manager.is_resume_available():
            return all_carriers
        
        # 체크포인트 로드
        checkpoint_data = self.checkpoint_manager.load_checkpoint()
        if checkpoint_data:
            self.completed_carriers = checkpoint_data.get('completed_carriers', [])
            self.failed_carriers = checkpoint_data.get('failed_carriers', [])
            
            # 아직 실행되지 않은 선사들만 반환
            remaining_carriers = self.checkpoint_manager.get_resume_carriers(all_carriers)
            return remaining_carriers
        
        return all_carriers

def auto_resume_strategy():
    """자동 복구 전략 결정"""
    print("\n" + "="*80)
    print("체크포인트가 발견되었습니다!")
    print("자동 복구 모드로 실행합니다.")
    print("실패한 선사들만 재실행하고, 완료된 선사들은 건너뜁니다.")
    print("="*80)
    
    # 자동으로 복구 모드 선택 (1번)
    return '1'

def main():
    """메인 실행 함수"""
    print("체크포인트 지원 순차처리 크롤링 시작!")
    print("공통 모듈 기반 경량화 버전 + 체크포인트 + 타임아웃 시스템")
    print("="*80)
    
    # 로깅 설정
    logger = setup_main_logging()
    today_log_dir = get_today_log_dir()
    
    # 전체 크롤링 시작 시간
    total_start_time = datetime.now()
    print(f"=== 전체 크롤링 시작: {total_start_time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    logger.info(f"=== 전체 크롤링 시작: {total_start_time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    
    # 개선된 크롤링 매니저 생성
    crawling_manager = EnhancedSequentialCrawlingManager()
    
    # 설정 로드
    system_config = get_system_config()
    
    # 설정 정보 로깅
    print(f"현재 환경: {system_config.environment.value}")
    print(f"실행 모드: {system_config.execution.mode}")
    print(f"로깅 레벨: {system_config.logging.level}")
    print(f"구글 드라이브 업로드: {'활성화' if system_config.logging.upload_to_drive else '비활성화'}")
    
    logger.info(f"현재 환경: {system_config.environment.value}")
    logger.info(f"실행 모드: {system_config.execution.mode}")
    logger.info(f"로깅 레벨: {system_config.logging.level}")
    logger.info(f"구글 드라이브 업로드: {'활성화' if system_config.logging.upload_to_drive else '비활성화'}")
    
    # 실행할 선사 목록 가져오기
    all_carriers = get_carriers_to_run()
    
    # 체크포인트 복구 확인 (자동 모드)
    if crawling_manager.checkpoint_manager.is_resume_available():
        # 자동 복구 전략 적용
        carriers_to_run = crawling_manager.resume_from_checkpoint(all_carriers)
        print(f"자동 복구 모드: {len(carriers_to_run)}개 선사 크롤링 예정")
        logger.info(f"자동 복구 모드: {len(carriers_to_run)}개 선사 크롤링 예정")
        
        # 체크포인트 정보 로깅
        checkpoint_data = crawling_manager.checkpoint_manager.load_checkpoint()
        if checkpoint_data:
            completed_count = len(checkpoint_data.get('completed_carriers', []))
            failed_count = len(checkpoint_data.get('failed_carriers', []))
            print(f"이전 완료: {completed_count}개, 이전 실패: {failed_count}개")
            logger.info(f"이전 완료: {completed_count}개, 이전 실패: {failed_count}개")
    else:
        # 체크포인트 없음, 처음부터 시작
        carriers_to_run = all_carriers
        print(f"처음부터 시작: {len(carriers_to_run)}개 선사 크롤링 예정")
        logger.info(f"처음부터 시작: {len(carriers_to_run)}개 선사 크롤링 예정")
    
    print("순차처리로 안정성과 정확성을 보장합니다.")
    print("타임아웃과 자동 체크포인트 시스템이 활성화되어 있습니다.")
    print("작업스케줄러 호환 모드: 자동 복구")
    print("="*80)
    
    logger.info(f"총 {len(carriers_to_run)}개 선사 크롤링 시작")
    logger.info("순차처리로 안정성과 정확성을 보장합니다.")
    logger.info("타임아웃과 자동 체크포인트 시스템이 활성화되어 있습니다.")
    logger.info("작업스케줄러 호환 모드: 자동 복구")
    logger.info("="*80)

    # 순차 실행 (개선된 버전)
    for i, carrier_name in enumerate(carriers_to_run, 1):
        print(f"=== {carrier_name} 크롤링 시작 ({i}/{len(carriers_to_run)}) ===")
        logger.info(f"=== {carrier_name} 크롤링 시작 ({i}/{len(carriers_to_run)}) ===")
        
        try:
            # 체크포인트에 현재 실행 중인 선사 저장
            crawling_manager.checkpoint_manager.save_checkpoint(
                completed_carriers=crawling_manager.completed_carriers,
                failed_carriers=crawling_manager.failed_carriers,
                current_carrier=carrier_name
            )
            
            # 안전한 실행기로 크롤러 실행
            def run_carrier_safe():
                return run_carrier_sequential(carrier_name)
            
            result = crawling_manager.safe_executor.execute_with_timeout(
                func=run_carrier_safe,
                carrier_name=carrier_name
            )
            
            crawling_manager.add_result(carrier_name, result)
            
            if result.get('success', False):
                print(f"=== {carrier_name} 크롤링 완료 (시도: {result.get('attempts', 1)}회) ===")
                logger.info(f"=== {carrier_name} 크롤링 완료 (시도: {result.get('attempts', 1)}회) ===")
            else:
                print(f"=== {carrier_name} 크롤링 실패: {result.get('error', 'Unknown error')} ===")
                logger.error(f"=== {carrier_name} 크롤링 실패: {result.get('error', 'Unknown error')} ===")
                
        except Exception as e:
            error_result = {
                'success': False,
                'duration': 0,
                'start_time': None,
                'end_time': datetime.now(),
                'error': f'크롤링 중 오류: {str(e)}',
                'traceback': traceback.format_exc(),
                'attempts': 1
            }
            crawling_manager.add_result(carrier_name, error_result)
            print(f"=== {carrier_name} 크롤링 중 예외 발생: {str(e)} ===")
            logger.error(f"=== {carrier_name} 크롤링 중 예외 발생: {str(e)} ===")

    # 전체 크롤링 완료
    total_end_time = datetime.now()
    total_duration = (total_end_time - total_start_time).total_seconds()
    
    print("="*80)
    print(f"=== 전체 크롤링 완료: {total_end_time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    print(f"총 소요시간: {total_duration:.2f}초")
    print(f"성공: {len(crawling_manager.completed_carriers)}개")
    print(f"실패: {len(crawling_manager.failed_carriers)}개")
    print("="*80)
    
    logger.info("="*80)
    logger.info(f"=== 전체 크롤링 완료: {total_end_time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    logger.info(f"총 소요시간: {total_duration:.2f}초")
    logger.info(f"성공: {len(crawling_manager.completed_carriers)}개")
    logger.info(f"실패: {len(crawling_manager.failed_carriers)}개")
    logger.info("="*80)
    
    # 체크포인트 정리 (성공적으로 완료된 경우)
    if len(crawling_manager.failed_carriers) == 0:
        crawling_manager.checkpoint_manager.clear_checkpoint()
        print("모든 크롤링이 성공적으로 완료되어 체크포인트를 삭제했습니다.")
        logger.info("모든 크롤링이 성공적으로 완료되어 체크포인트를 삭제했습니다.")
    else:
        print(f"일부 크롤링이 실패했습니다. 체크포인트가 유지되어 다음 실행 시 자동 복구됩니다.")
        logger.info(f"일부 크롤링이 실패했습니다. 체크포인트가 유지되어 다음 실행 시 자동 복구됩니다.")
        print(f"실패한 선사: {', '.join(crawling_manager.failed_carriers)}")
        logger.info(f"실패한 선사: {', '.join(crawling_manager.failed_carriers)}")
    
    # 기존 후처리 로직 (엑셀 로그, 구글 업로드 등)
    # ... (기존 코드와 동일)

if __name__ == "__main__":
    main()
