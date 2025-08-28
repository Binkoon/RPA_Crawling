# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/08/21
# 역할 : 순차처리 크롤링 메인 파일 (스레드 제거, 순차처리로 변경)
# 특징 : 공통 모듈을 활용하여 코드 중복 제거 및 가독성 향상

import traceback
from datetime import datetime

# 공통 모듈 import
from utils.logging_setup import setup_main_logging, get_today_log_dir
from utils.config_loader import get_carriers_to_run, get_system_config, reload_system_config
from utils.crawler_executor import run_carrier_sequential
from utils.excel_logger import save_excel_log, add_google_upload_logs
from utils.google_upload import run_main_upload, upload_errorlog_to_drive
from utils.data_cleanup import cleanup_old_data, cleanup_old_errorlogs

class SequentialCrawlingManager:
    """순차처리 크롤링 결과 관리자"""
    
    def __init__(self):
        self.crawling_results = []
    
    def add_result(self, carrier_name, result):
        """결과 추가"""
        self.crawling_results.append((carrier_name, result))
    
    def get_results(self):
        """결과 조회 (복사본 반환)"""
        return self.crawling_results.copy()
    
    def get_results_count(self):
        """결과 개수 조회"""
        return len(self.crawling_results)

def main():
    """메인 실행 함수"""
    print("순차처리 크롤링 시작!")
    print("공통 모듈 기반 경량화 버전임 (main2_lightweight.py임)")
    print("="*80)
    
    # 로깅 설정
    logger = setup_main_logging()
    today_log_dir = get_today_log_dir()
    
    # 전체 크롤링 시작 시간
    total_start_time = datetime.now()
    print(f"=== 전체 크롤링 시작: {total_start_time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    logger.info(f"=== 전체 크롤링 시작: {total_start_time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    
    # 순차처리 크롤링 매니저 생성
    crawling_manager = SequentialCrawlingManager()
    
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
    carriers_to_run = get_carriers_to_run()
    
    print(f"총 {len(carriers_to_run)}개 선사 크롤링 시작")
    print("순차처리로 안정성과 정확성을 보장합니다.")
    print("="*80)
    
    logger.info(f"총 {len(carriers_to_run)}개 선사 크롤링 시작")
    logger.info("순차처리로 안정성과 정확성을 보장합니다.")
    logger.info("="*80)

    # 순차 실행
    for carrier_name in carriers_to_run:
        print(f"=== {carrier_name} 크롤링 시작 ===")
        logger.info(f"=== {carrier_name} 크롤링 시작 ===")
        
        try:
            result = run_carrier_sequential(carrier_name)
            crawling_manager.add_result(carrier_name, result)
            print(f"=== {carrier_name} 크롤링 완료 ===")
            logger.info(f"=== {carrier_name} 크롤링 완료 ===")
        except Exception as e:
            error_result = {
                'success': False,
                'duration': 0,
                'start_time': None,
                'end_time': datetime.now(),
                'error': f'크롤링 중 오류: {str(e)}',
                'traceback': traceback.format_exc()
            }
            crawling_manager.add_result(carrier_name, error_result)
            print(f"=== {carrier_name} 크롤링 중 오류: {str(e)} ===")
            logger.error(f"=== {carrier_name} 크롤링 중 오류: {str(e)} ===")

    # 전체 크롤링 종료 시간
    total_end_time = datetime.now()
    total_duration = (total_end_time - total_start_time).total_seconds()
    
    # 결과 조회
    crawling_results = crawling_manager.get_results()
    
    # 크롤링 결과 요약 출력
    print_results_summary(crawling_results, total_duration)
    
    # 엑셀 로그 저장
    if system_config.logging.save_excel:
        save_excel_log(crawling_results, total_duration, today_log_dir)
    
    # 구글 드라이브 업로드 실행
    if system_config.logging.upload_to_drive:
        run_google_upload()
    
    # 오래된 데이터 정리
    if system_config.cleanup.enabled:
        run_data_cleanup(system_config, logger)
    
    # 에러로그 자동 업로드 및 정리
    run_errorlog_management(system_config, logger)
    
    print("="*80)
    print("순차처리 크롤링 완료!")
    print("="*80)

def print_results_summary(crawling_results, total_duration):
    """크롤링 결과 요약 출력"""
    print("\n" + "="*80)
    print("크롤링 결과 요약")
    print("="*80)
    
    success_count = 0
    fail_count = 0
    total_vessels_success = 0
    total_vessels_fail = 0
    
    # 크롤러 팩토리에서 정확한 총 선박 수 가져오기
    from crawler_factory import CrawlerFactory
    expected_total_vessels = CrawlerFactory.get_total_vessel_count()
    
    for carrier_name, result in crawling_results:
        status = "성공" if result['success'] else "실패"
        duration_str = f"({result['duration']:.2f}초)" if 'duration' in result else ""
        print(f"{carrier_name}: {status} {duration_str}")
        
        if result['success']:
            success_count += 1
            if 'success_count' in result:
                total_vessels_success += result['success_count']
                total_vessels_fail += result['fail_count']
                print(f"  └─ 선박: 성공 {result['success_count']}개, 실패 {result['fail_count']}개")
        else:
            fail_count += 1
            if 'total_vessels' in result and 'fail_count' in result:
                total_vessels_success += result.get('success_count', 0)
                total_vessels_fail += result['fail_count']
                print(f"  └─ 선박: 성공 {result.get('success_count', 0)}개, 실패 {result['fail_count']}개")
                if result.get('failed_vessels'):
                    print(f"  └─ 실패한 선박: {', '.join(result['failed_vessels'])}")
            elif 'error' in result:
                print(f"  └─ 에러: {result['error']}")
        
        print(f"\n동시성 처리 결과:")
        print(f"총 {len(crawling_results)}개 선사 중")
        print(f"성공: {success_count}개")
        print(f"실패: {fail_count}개")
        print(f"총 소요시간: {total_duration:.2f}초")
        
        if total_vessels_success > 0 or total_vessels_fail > 0:
            print(f"\n선박별 상세 결과:")
            print(f"예상 총 선박: {expected_total_vessels}개 (고정값)")
            print(f"실제 처리된 선박: {total_vessels_success + total_vessels_fail}개")
            print(f"성공: {total_vessels_success}개")
            print(f"실패: {total_vessels_fail}개")
            
            # 예상값과 실제값 비교
            if total_vessels_success + total_vessels_fail != expected_total_vessels:
                print(f"⚠️  경고: 예상 선박 수({expected_total_vessels}개)와 실제 처리된 선박 수({total_vessels_success + total_vessels_fail}개)가 다릅니다.")
        
        print("="*80)

def run_google_upload():
    """구글 드라이브 업로드 실행"""
    print("\n" + "="*80)
    print("구글 드라이브 업로드 시작")
    print("="*80)
    
    try:
        upload_result = run_main_upload()
        
        if upload_result and isinstance(upload_result, dict):
            success_count = upload_result.get('success_count', 0)
            fail_count = upload_result.get('fail_count', 0)
            total_files = upload_result.get('total_files', 0)
            
            print("="*80)
            if success_count > 0:
                print(f"✅ 구글 드라이브 업로드 완료: {success_count}/{total_files}개 파일")
                if fail_count > 0:
                    print(f"⚠️  실패: {fail_count}개 파일")
            else:
                print("❌ 구글 드라이브 업로드 실패: 모든 파일 업로드 실패")
            print("="*80)
            
            # 구글 업로드 로그를 엑셀에 추가
            add_google_upload_logs(upload_result)
        else:
            print("구글 드라이브 업로드 실패: 결과가 올바르지 않음")
            
    except Exception as e:
        print(f"구글 드라이브 업로드 실패: {str(e)}")
        import traceback
        print(f"상세 에러: {traceback.format_exc()}")

def run_data_cleanup(system_config, logger):
    """데이터 정리 실행"""
    print("\n" + "="*80)
    print("오래된 데이터 정리 시작")
    print("="*80)
    
    try:
        if system_config.cleanup.cleanup_scheduledata:
            cleanup_old_data()
        
        print("="*80)
        print("오래된 데이터 정리 완료")
        print("="*80)
        
    except Exception as e:
        print(f"오래된 데이터 정리 실패: {str(e)}")

def run_errorlog_management(system_config, logger):
    """에러로그 관리 실행"""
    print("\n" + "="*80)
    print("에러로그 자동 업로드 및 정리 시작")
    print("="*80)
    
    try:
        # 1단계: 오래된 에러로그 정리
        if system_config.cleanup.cleanup_errorlogs:
            print("\n1단계: 오래된 에러로그 정리")
            
            days_to_keep = system_config.cleanup.days_to_keep
            errorlog_cleanup_result = cleanup_old_errorlogs(days_to_keep, logger)
            
            if errorlog_cleanup_result['success']:
                print(f"에러로그 정리 완료: {len(errorlog_cleanup_result['deleted_folders'])}개 폴더 삭제")
                if errorlog_cleanup_result['total_size_freed'] > 0:
                    print(f"   └─ 정리된 용량: {errorlog_cleanup_result['total_size_freed'] / (1024*1024):.2f} MB")
            else:
                print(f"에러로그 정리 실패: {errorlog_cleanup_result['message']}")
        
        # 2단계: 에러로그 구글드라이브 업로드
        if system_config.logging.upload_to_drive:
            print("\n2단계: 에러로그 구글드라이브 업로드 (오늘 날짜 로그만)")
            
            errorlog_upload_result = upload_errorlog_to_drive(logger)
            
            if errorlog_upload_result['success']:
                print("오늘 날짜 에러로그 업로드 완료")
            else:
                print(f"에러로그 업로드 실패: {errorlog_upload_result['message']}")
        
        print("="*80)
        print("에러로그 자동 업로드 및 정리 완료")
        print("="*80)
        
    except Exception as e:
        error_msg = f"에러로그 자동 업로드 및 정리 실패: {str(e)}"
        print(error_msg)

if __name__ == "__main__":
    main()
