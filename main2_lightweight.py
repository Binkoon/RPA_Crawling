# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/08/21
# 역할 : 경량화된 병렬 크롤링 메인 파일
# 특징 : 공통 모듈을 활용하여 코드 중복 제거 및 가독성 향상

import traceback
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# 공통 모듈 import
from utils.logging_setup import setup_main_logging, get_today_log_dir
from utils.config_loader import get_carriers_to_run, load_execution_config
from utils.crawler_executor import run_carrier_parallel
from utils.excel_logger import save_excel_log, add_google_upload_logs
from utils.google_upload import run_main_upload, upload_errorlog_to_drive
from utils.data_cleanup import cleanup_old_data, cleanup_old_errorlogs

# 스레드 안전성을 위한 락들
results_lock = threading.Lock()      # 크롤링 결과 저장용 락
log_lock = threading.Lock()          # 로그 기록용 락
file_lock = threading.Lock()         # 파일 시스템 접근용 락
config_lock = threading.RLock()      # 설정 파일 읽기용 락 (재진입 가능)

class ThreadSafeCrawlingManager:
    """스레드 안전한 크롤링 결과 관리자"""
    
    def __init__(self):
        self.crawling_results = []
        self.results_lock = threading.Lock()
    
    def add_result(self, carrier_name, result):
        """스레드 안전한 결과 추가"""
        with self.results_lock:
            self.crawling_results.append((carrier_name, result))
    
    def get_results(self):
        """스레드 안전한 결과 조회 (복사본 반환)"""
        with self.results_lock:
            return self.crawling_results.copy()
    
    def get_results_count(self):
        """스레드 안전한 결과 개수 조회"""
        with self.results_lock:
            return len(self.crawling_results)

def safe_log_write(message, logger=None):
    """스레드 안전한 로그 기록"""
    with log_lock:
        print(message)
        if logger:
            logger.info(message)

def safe_config_load():
    """스레드 안전한 설정 로드"""
    with config_lock:
        return load_execution_config()

def safe_file_operation(operation_func):
    """스레드 안전한 파일 작업"""
    with file_lock:
        return operation_func()

def main():
    """메인 실행 함수"""
    print("병렬 크롤링 시작!")
    print("공통 모듈 기반 경량화 버전")
    print("="*80)
    
    # 로깅 설정
    logger = setup_main_logging()
    today_log_dir = get_today_log_dir()
    
    # 전체 크롤링 시작 시간
    total_start_time = datetime.now()
    safe_log_write(f"=== 전체 크롤링 시작: {total_start_time.strftime('%Y-%m-%d %H:%M:%S')} ===", logger)
    
    # 스레드 안전한 크롤링 매니저 생성
    crawling_manager = ThreadSafeCrawlingManager()
    
    # 설정 로드 (스레드 안전)
    execution_config = safe_config_load()
    max_workers = execution_config['execution']['max_workers']
    
    # 실행할 선사 목록 가져오기
    carriers_to_run = get_carriers_to_run()
    
    safe_log_write(f"총 {len(carriers_to_run)}개 선사 크롤링 시작", logger)
    safe_log_write(f"병렬 처리로 성능 향상 (최대 {max_workers}개 스레드)", logger)
    safe_log_write("="*80, logger)

    # 병렬 실행
    safe_log_write(f"ThreadPoolExecutor 사용 (max_workers={max_workers})", logger)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 모든 선사에 대해 병렬 실행 태스크 제출
        future_to_carrier = {
            executor.submit(run_carrier_parallel, carrier_name, crawling_manager): carrier_name 
            for carrier_name in carriers_to_run
        }
        
        # 완료된 태스크들의 결과 수집
        for future in as_completed(future_to_carrier):
            carrier_name = future_to_carrier[future]
            try:
                carrier_name, result = future.result()
                # 스레드 안전한 결과 추가
                crawling_manager.add_result(carrier_name, result)
                safe_log_write(f"=== {carrier_name} 병렬 실행 완료 ===", logger)
            except Exception as e:
                error_result = {
                    'success': False,
                    'duration': 0,
                    'start_time': None,
                    'end_time': datetime.now(),
                    'error': f'병렬 실행 중 오류: {str(e)}',
                    'traceback': traceback.format_exc()
                }
                crawling_manager.add_result(carrier_name, error_result)
                safe_log_write(f"=== {carrier_name} 병렬 실행 중 오류: {str(e)} ===", logger)

    # 전체 크롤링 종료 시간
    total_end_time = datetime.now()
    total_duration = (total_end_time - total_start_time).total_seconds()
    
    # 스레드 안전한 결과 조회
    crawling_results = crawling_manager.get_results()
    
    # 크롤링 결과 요약 출력
    print_results_summary(crawling_results, total_duration)
    
    # 엑셀 로그 저장 (스레드 안전)
    if execution_config['logging']['save_excel']:
        safe_file_operation(lambda: save_excel_log(crawling_results, total_duration, today_log_dir))
    
    # 구글 드라이브 업로드 실행
    if execution_config['logging']['upload_to_drive']:
        run_google_upload()
    
    # 오래된 데이터 정리 (스레드 안전)
    if execution_config['cleanup']['enabled']:
        run_data_cleanup(execution_config, logger)
    
    # 에러로그 자동 업로드 및 정리 (스레드 안전)
    run_errorlog_management(execution_config, logger)
    
    safe_log_write("="*80, logger)
    safe_log_write("병렬 크롤링 완료!", logger)
    safe_log_write("="*80, logger)

def print_results_summary(crawling_results, total_duration):
    """크롤링 결과 요약 출력 (스레드 안전)"""
    with log_lock:  # 출력 순서 보장을 위한 락
        print("\n" + "="*80)
        print("크롤링 결과 요약")
        print("="*80)
        
        success_count = 0
        fail_count = 0
        total_vessels_success = 0
        total_vessels_fail = 0
        
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
        
        print(f"\n병렬 처리 결과:")
        print(f"총 {len(crawling_results)}개 선사 중")
        print(f"성공: {success_count}개")
        print(f"실패: {fail_count}개")
        print(f"총 소요시간: {total_duration:.2f}초")
        
        if total_vessels_success > 0 or total_vessels_fail > 0:
            print(f"\n선박별 상세 결과:")
            print(f"총 선박: {total_vessels_success + total_vessels_fail}개")
            print(f"성공: {total_vessels_success}개")
            print(f"실패: {total_vessels_fail}개")
        
        print("="*80)

def run_google_upload():
    """구글 드라이브 업로드 실행 (스레드 안전)"""
    with log_lock:  # 출력 순서 보장
        print("\n" + "="*80)
        print("구글 드라이브 업로드 시작")
        print("="*80)
    
    try:
        upload_result = run_main_upload()
        
        if upload_result and isinstance(upload_result, dict):
            with log_lock:
                print("="*80)
                print("구글 드라이브 업로드 완료")
                print("="*80)
            
            # 구글 업로드 로그를 엑셀에 추가 (스레드 안전)
            safe_file_operation(lambda: add_google_upload_logs(upload_result))
        else:
            safe_log_write("구글 드라이브 업로드 실패")
            
    except Exception as e:
        safe_log_write(f"구글 드라이브 업로드 실패: {str(e)}")

def run_data_cleanup(execution_config, logger):
    """데이터 정리 실행 (스레드 안전)"""
    with log_lock:
        print("\n" + "="*80)
        print("오래된 데이터 정리 시작")
        print("="*80)
    
    try:
        if execution_config['cleanup']['cleanup_scheduledata']:
            safe_file_operation(cleanup_old_data)
        
        with log_lock:
            print("="*80)
            print("오래된 데이터 정리 완료")
            print("="*80)
        
    except Exception as e:
        safe_log_write(f"오래된 데이터 정리 실패: {str(e)}")

def run_errorlog_management(execution_config, logger):
    """에러로그 관리 실행 (스레드 안전)"""
    with log_lock:
        print("\n" + "="*80)
        print("에러로그 자동 업로드 및 정리 시작")
        print("="*80)
    
    try:
        # 1단계: 오래된 에러로그 정리
        if execution_config['cleanup']['cleanup_errorlogs']:
            with log_lock:
                print("\n1단계: 오래된 에러로그 정리")
            
            days_to_keep = execution_config['cleanup']['days_to_keep']
            errorlog_cleanup_result = safe_file_operation(
                lambda: cleanup_old_errorlogs(days_to_keep, logger)
            )
            
            if errorlog_cleanup_result['success']:
                with log_lock:
                    print(f"에러로그 정리 완료: {len(errorlog_cleanup_result['deleted_folders'])}개 폴더 삭제")
                    if errorlog_cleanup_result['total_size_freed'] > 0:
                        print(f"   └─ 정리된 용량: {errorlog_cleanup_result['total_size_freed'] / (1024*1024):.2f} MB")
            else:
                safe_log_write(f"에러로그 정리 실패: {errorlog_cleanup_result['message']}")
        
        # 2단계: 에러로그 구글드라이브 업로드
        if execution_config['logging']['upload_to_drive']:
            with log_lock:
                print("\n2단계: 에러로그 구글드라이브 업로드 (오늘 날짜 로그만)")
            
            errorlog_upload_result = safe_file_operation(
                lambda: upload_errorlog_to_drive(logger)
            )
            
            if errorlog_upload_result['success']:
                safe_log_write("오늘 날짜 에러로그 업로드 완료")
            else:
                safe_log_write(f"에러로그 업로드 실패: {errorlog_upload_result['message']}")
        
        with log_lock:
            print("="*80)
            print("에러로그 자동 업로드 및 정리 완료")
            print("="*80)
        
    except Exception as e:
        error_msg = f"에러로그 자동 업로드 및 정리 실패: {str(e)}"
        safe_log_write(error_msg)

if __name__ == "__main__":
    main()
