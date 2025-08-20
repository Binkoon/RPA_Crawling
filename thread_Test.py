### 테스트용 스레드 기반 병렬 크롤링 ###
# 목적: 스레드 성능 향상 효과 확인 (시간 단축 테스트)
# 
# 실제 역할:
# - 설정 파일에서 선사 목록 로드
# - 크롤러 팩토리 호출하여 크롤러 생성
# - 개별 크롤러 실행 및 에러 처리 (스레드 기반 병렬 처리)
# - 결과 집계 및 로깅
# - Excel 로그 생성 (test 폴더에 저장)

# 하지 않는 것:
# - 구글 드라이브 업로드 (이미 main.py에서 완료됨)
# - 데이터 정리 및 에러로그 관리
# - 직접 크롤러 인스턴스 생성하지 않음

# 스레드 기반 병렬 처리:
# - 2개 스레드로 선사 2개씩 병렬 처리
# - ThreadPoolExecutor 사용으로 안전한 스레드 관리
# - 기존 time.sleep은 유지 (웹사이트 부하 방지)
# - 예상 성능 향상: 1800초 → 900초 (50% 단축)

# 여기서부터 시작함.
from crawler import base
from crawler import sitc
from crawler import evergreen
from crawler import cosco
from crawler import wanhai
from crawler import one
from crawler import ckline
from crawler import panocean
from crawler import snl
from crawler import smline
from crawler import hmm
from crawler import fdt
from crawler import ial # 완료
from crawler import dyline
from crawler import yml  # 완료
from crawler import nss

import traceback
import logging
from datetime import datetime
import os
import sys
import pandas as pd
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# ErrorLog 폴더 구조 생성
def setup_errorlog_folder():
    """ErrorLog 폴더 구조 생성"""
    log_base_dir = os.path.join(os.getcwd(), "ErrorLog")
    if not os.path.exists(log_base_dir):
        os.makedirs(log_base_dir)
    
    # 날짜별 폴더 생성 (YYYY-MM-DD 형식)
    today_log_folder = datetime.now().strftime("%Y-%m-%d")
    today_log_dir = os.path.join(log_base_dir, today_log_folder)
    if not os.path.exists(today_log_dir):
        os.makedirs(today_log_dir)
    
    return today_log_dir

# 테스트용 폴더 설정 (test 폴더에 엑셀 파일 생성)
test_dir = os.path.join(os.getcwd(), "test")
if not os.path.exists(test_dir):
    os.makedirs(test_dir)
today_log_dir = test_dir

# 테스트용으로 주석처리 - 에러로그 구글드라이브 폴더 ID
# ERRORLOG_DRIVE_FOLDER_ID = '1t3P2oofZKnSrVMmDS6-YQcwuZC6PdCz5'

# 메인 로깅 설정 (콘솔만)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# 크롤러 팩토리 import
from crawler_factory import CrawlerFactory

# 설정 파일에서 선사 정보 로드
def load_carriers_config():
    """선사 설정 파일을 로드합니다."""
    try:
        import json
        config_path = os.path.join(os.getcwd(), 'config', 'carriers.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"설정 파일 로드 실패: {str(e)}")
        # 기본값 반환
        return {"carriers": []}

# 엑셀 로그 데이터를 저장할 리스트 (스레드 안전을 위해 Lock 사용)
excel_log_data = []
excel_log_lock = threading.Lock()

def add_to_excel_log(carrier_name, vessel_name, status, reason, duration):
    """엑셀 로그에 기록 추가 (성공/실패 모두) - 스레드 안전"""
    global excel_log_data
    with excel_log_lock:
        now = datetime.now()
        excel_log_data.append({
            '날짜': now.strftime('%Y/%m/%d/%H/%M/%S'),
            '선사': carrier_name,
            '선박': vessel_name,
            '상태': status,
            '사유/결과': reason,
            '소요시간': f"{duration:.2f}초"
        })

# 테스트용으로 주석처리 - ErrorLog 관련 함수들
# def get_errorlog_folders():
#     """ErrorLog 폴더 내의 모든 날짜별 폴더 목록 반환"""
#     errorlog_base_dir = os.path.join(os.getcwd(), "ErrorLog")
#     if not os.path.exists(errorlog_base_dir):
#         return []
#     
#     folders = []
#     for item in os.listdir(errorlog_base_dir):
#         item_path = os.path.join(errorlog_base_dir, item)
#         if os.path.isdir(item_path):
#             # YYYY-MM-DD 형식인지 확인
#             try:
#                 datetime.datetime.strptime(item, '%Y-%m-%d')
#                 folders.append(item)
#             except ValueError:
#                 continue
#     
#     return sorted(folders)

# 테스트용으로 주석처리 - 구글드라이브 업로드 함수
# def upload_errorlog_to_drive(logger):
#     """에러로그를 구글드라이브에 업로드 (오늘 날짜의 _log.xlsx 파일만)"""
#     # ... 함수 내용 생략 ...

# 테스트용으로 주석처리 - 에러로그 정리 함수
# def cleanup_old_errorlogs(days_to_keep=30, logger=None):
#     """30일 기준으로 오래된 에러로그 정리"""
#     # ... 함수 내용 생략 ...

def save_excel_log(crawling_results, total_duration):
    """엑셀 로그 파일 저장 (요약 정보 포함)"""
    if not excel_log_data:
        return
    
    try:
        # 기본 로그 데이터
        df = pd.DataFrame(excel_log_data)
        
        # 요약 정보 계산
        success_count = 0
        fail_count = 0
        total_vessels_success = 0
        total_vessels_fail = 0
        
        for carrier_name, result in crawling_results:
            if result['success']:
                success_count += 1
                if 'success_count' in result:
                    total_vessels_success += result['success_count']
                    total_vessels_fail += result.get('fail_count', 0)
            else:
                fail_count += 1
                if 'total_vessels' in result and 'fail_count' in result:
                    total_vessels_success += result.get('success_count', 0)
                    total_vessels_fail += result['fail_count']
        
        # 요약 행 추가
        summary_rows = [
            {'날짜': '', '선사': '', '선박': '', '상태': '', '사유/결과': '', '소요시간': ''},
            {'날짜': '', '선사': '=== 크롤링 결과 요약 ===', '선박': '', '상태': '', '사유/결과': '', '소요시간': ''},
            {'날짜': '', '선사': f'총 {len(crawling_results)}개 선사 중', '선박': '', '상태': '', '사유/결과': '', '소요시간': ''},
            {'날짜': '', '선사': f'성공: {success_count}개', '선박': '', '상태': '', '사유/결과': '', '소요시간': ''},
            {'날짜': '', '선사': f'실패: {fail_count}개', '선박': '', '상태': '', '사유/결과': '', '소요시간': ''},
            {'날짜': '', '선사': f'총 소요시간: {total_duration:.2f}초', '선박': '', '상태': '', '사유/결과': '', '소요시간': ''},
            {'날짜': '', '선사': '', '선박': '', '상태': '', '사유/결과': '', '소요시간': ''},
            {'날짜': '', '선사': '=== 선박별 상세 결과 ===', '선박': '', '상태': '', '사유/결과': '', '소요시간': ''},
            {'날짜': '', '선사': f'총 선박: {total_vessels_success + total_vessels_fail}개', '선박': '', '상태': '', '사유/결과': '', '소요시간': ''},
            {'날짜': '', '선사': f'성공: {total_vessels_success}개', '선박': '', '상태': '', '사유/결과': '', '소요시간': ''},
            {'날짜': '', '선사': f'실패: {total_vessels_fail}개', '선박': '', '상태': '', '사유/결과': '', '소요시간': ''}
        ]
        
        # 요약 행을 DataFrame에 추가
        summary_df = pd.DataFrame(summary_rows)
        final_df = pd.concat([df, summary_df], ignore_index=True)
        
        today_str = datetime.now().strftime('%Y%m%d')
        excel_filename = f"{today_str}_log.xlsx"
        excel_path = os.path.join(today_log_dir, excel_filename)
        
        final_df.to_excel(excel_path, index=False, engine='openpyxl')
        print(f"엑셀 로그 저장 완료: {excel_path}")
        
    except Exception as e:
        print(f"엑셀 로그 저장 실패: {str(e)}")
        logging.error(f"엑셀 로그 저장 실패: {str(e)}")

def run_crawler_with_error_handling(crawler_name, crawler_instance):
    """크롤러를 실행하고 에러를 처리하는 함수"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"=== {crawler_name} 크롤링 시작 ===")
        start_time = datetime.now()
        
        # 첫 번째 시도
        result = crawler_instance.run()
        
        # 실패한 선박이 있는지 확인하고 재시도
        retry_result = None
        if hasattr(crawler_instance, 'failed_vessels') and crawler_instance.failed_vessels:
                failed_vessels = crawler_instance.failed_vessels.copy()
                failed_reasons = getattr(crawler_instance, 'failed_reasons', {}).copy()
                
                logger.info(f"=== {crawler_name} 실패한 선박 재시도 시작 ===")
                logger.info(f"재시도 대상 선박: {', '.join(failed_vessels)}")
                logger.info(f"재시도 대상 개수: {len(failed_vessels)}개")
                
                # 실패한 선박들만 재시도
                retry_result = crawler_instance.retry_failed_vessels(failed_vessels)
                
                if retry_result:
                    logger.info(f"=== {crawler_name} 재시도 완료 ===")
                    logger.info(f"재시도 성공: {retry_result.get('retry_success', 0)}개")
                    logger.info(f"재시도 실패: {retry_result.get('retry_fail', 0)}개")
                    logger.info(f"재시도 후 최종 성공: {retry_result.get('final_success', 0)}개")
                    logger.info(f"재시도 후 최종 실패: {retry_result.get('final_fail', 0)}개")
                    
                    if 'note' in retry_result:
                        logger.info(f"재시도 참고사항: {retry_result['note']}")
                else:
                    logger.warning(f"=== {crawler_name} 재시도 실패 ===")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 크롤러에 성공/실패 카운트가 있는 경우 선박별 결과 확인
        if hasattr(crawler_instance, 'success_count') and hasattr(crawler_instance, 'fail_count'):
            # 실제 선박 대수는 vessel_name_list의 길이로 계산
            total_vessels = len(getattr(crawler_instance, 'vessel_name_list', []))
            success_count = getattr(crawler_instance, 'success_count', 0)
            fail_count = getattr(crawler_instance, 'fail_count', 0)
            failed_vessels = getattr(crawler_instance, 'failed_vessels', [])
            failed_reasons = getattr(crawler_instance, 'failed_reasons', {})
            
            # 성공한 선박들을 엑셀 로그에 기록
            if hasattr(crawler_instance, 'vessel_name_list'):
                for vessel_name in crawler_instance.vessel_name_list:
                    if vessel_name not in failed_vessels:
                        vessel_duration = getattr(crawler_instance, 'get_vessel_duration', lambda x: duration)(vessel_name)
                        add_to_excel_log(crawler_name, vessel_name, "성공", "크롤링 완료", vessel_duration)
            
            # 실패한 선박들을 엑셀 로그에 기록
            for vessel_name in failed_vessels:
                reason = failed_reasons.get(vessel_name, "알 수 없는 오류")
                vessel_duration = getattr(crawler_instance, 'get_vessel_duration', lambda x: duration)(vessel_name)
                add_to_excel_log(crawler_name, vessel_name, "실패", reason, vessel_duration)
            
            # 재시도 결과가 있는 경우 최종 결과 반영
            final_success_count = success_count
            final_fail_count = fail_count
            final_failed_vessels = failed_vessels.copy()
            
            if retry_result:
                final_success_count = retry_result.get('final_success', success_count)
                final_fail_count = retry_result.get('final_fail', fail_count)
                # 재시도 후 최종 실패한 선박들 업데이트
                if 'final_failed_vessels' in retry_result:
                    final_failed_vessels = retry_result['final_failed_vessels']
            
            # 선박 중 하나라도 실패하면 선사도 실패로 분류
            if final_fail_count > 0:
                logger.error(f"=== {crawler_name} 크롤링 실패 (소요시간: {duration:.2f}초) ===")
                logger.error(f"선박 실패로 인한 선사 실패: 총 {total_vessels}개 선박 중 성공 {final_success_count}개, 실패 {final_fail_count}개")
                if final_failed_vessels:
                    logger.error(f"실패한 선박: {', '.join(final_failed_vessels)}")
                
                return {
                    'success': False,
                    'duration': duration,
                    'start_time': start_time,
                    'end_time': end_time,
                    'total_vessels': total_vessels,
                    'success_count': final_success_count,
                    'fail_count': final_fail_count,
                    'failed_vessels': final_failed_vessels,
                    'error': f'선박 실패로 인한 선사 실패 (실패한 선박: {", ".join(final_failed_vessels)})'
                }
            else:
                logger.info(f"=== {crawler_name} 크롤링 완료 (소요시간: {duration:.2f}초) ===")
                logger.info(f"{crawler_name} 상세 결과: 총 {total_vessels}개 선박 중 성공 {final_success_count}개, 실패 {final_fail_count}개")
                
                return {
                    'success': True,
                    'duration': duration,
                    'start_time': start_time,
                    'end_time': end_time,
                    'total_vessels': total_vessels,
                    'success_count': final_success_count,
                    'fail_count': final_fail_count,
                    'failed_vessels': final_failed_vessels
                }
        else:
            # 성공/실패 카운트가 없는 경우 기존 로직 사용
            if result:
                logger.info(f"=== {crawler_name} 크롤링 완료 (소요시간: {duration:.2f}초) ===")
                return {
                    'success': True,
                    'duration': duration,
                    'start_time': start_time,
                    'end_time': end_time
                }
            else:
                logger.error(f"=== {crawler_name} 크롤링 실패 (소요시간: {duration:.2f}초) ===")
                return {
                    'success': False,
                    'duration': duration,
                    'start_time': start_time,
                    'end_time': end_time,
                    'error': '크롤러 실행 중 오류 발생'
                }
            
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time) if 'start_time' in locals() else 0
        
        logger.error(f"=== {crawler_name} 크롤링 실패 ===")
        logger.error(f"에러 메시지: {str(e)}")
        logger.error(f"상세 에러: {traceback.format_exc()}")
        
        return {
            'success': False,
            'duration': duration.total_seconds() if hasattr(duration, 'total_seconds') else 0,
            'start_time': start_time if 'start_time' in locals() else None,
            'end_time': end_time,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

def try_run_carrier(crawler_name, constructor, results_list):
    """크롤러 인스턴스화 단계에서의 예외도 잡아서 다음 선사로 넘어가도록 처리"""
    logger = logging.getLogger(__name__)
    try:
        # 크롤러 팩토리를 사용하여 인스턴스 생성
        instance = CrawlerFactory.create_crawler(crawler_name)
    except Exception as e:
        end_time = datetime.now()
        logger.error(f"=== {crawler_name} 크롤러 인스턴스 생성 실패 ===")
        logger.error(f"에러 메시지: {str(e)}")
        logger.error(f"상세 에러: {traceback.format_exc()}")
        results_list.append((crawler_name, {
            'success': False,
            'duration': 0,
            'start_time': None,
            'end_time': end_time,
            'error': str(e),
            'traceback': traceback.format_exc()
        }))
        return
    # 인스턴스 생성에 성공하면 실행
    result = run_crawler_with_error_handling(crawler_name, instance)
    results_list.append((crawler_name, result))

def run_carrier_parallel(crawler_name):
    """스레드에서 실행할 크롤러 함수"""
    logger = logging.getLogger(__name__)
    try:
        # 크롤러 인스턴스 생성
        instance = CrawlerFactory.create_crawler(crawler_name)
        # 크롤러 실행
        result = run_crawler_with_error_handling(crawler_name, instance)
        return crawler_name, result
    except Exception as e:
        end_time = datetime.now()
        logger.error(f"=== {crawler_name} 크롤러 실행 실패 ===")
        logger.error(f"에러 메시지: {str(e)}")
        logger.error(f"상세 에러: {traceback.format_exc()}")
        return crawler_name, {
            'success': False,
            'duration': 0,
            'start_time': None,
            'end_time': end_time,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

if __name__ == "__main__":
    print("스레드 기반 병렬 크롤링 시작!")
    print("2개 스레드로 선사 2개씩 병렬 처리")
    print("="*80)
    
    logger = logging.getLogger(__name__)
    
    # 전체 크롤링 시작 시간
    total_start_time = datetime.now()
    logger.info(f"=== 전체 크롤링 시작: {total_start_time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    
    # 실행할 선사 정의 (설정 파일에서 로드)
    carriers_config = load_carriers_config()
    carriers_to_run = []

    for carrier_info in carriers_config['carriers']:
        carrier_name = carrier_info['name']
        carriers_to_run.append(carrier_name)

    print(f"총 {len(carriers_to_run)}개 선사 크롤링 시작")
    print(f"스레드 수: 2개 (선사 2개씩 병렬 처리)")
    print("="*80)

    # 스레드 기반 병렬 실행
    crawling_results = []
    
    # ThreadPoolExecutor를 사용하여 2개 스레드로 병렬 처리
    with ThreadPoolExecutor(max_workers=2) as executor:
        # 모든 선사를 스레드 풀에 제출
        future_to_carrier = {executor.submit(run_carrier_parallel, carrier_name): carrier_name 
                           for carrier_name in carriers_to_run}
        
        # 완료된 작업들을 순서대로 처리
        for future in as_completed(future_to_carrier):
            carrier_name = future_to_carrier[future]
            try:
                result = future.result()
                crawling_results.append(result)
                print(f" {carrier_name} 완료 - 스레드에서 반환됨")
            except Exception as e:
                print(f" {carrier_name} 스레드 실행 중 오류: {str(e)}")
                crawling_results.append((carrier_name, {
                    'success': False,
                    'duration': 0,
                    'start_time': None,
                    'end_time': datetime.now(),
                    'error': f'스레드 실행 중 오류: {str(e)}',
                    'traceback': traceback.format_exc()
                }))

    # 전체 크롤링 종료 시간
    total_end_time = datetime.now()
    total_duration = (total_end_time - total_start_time).total_seconds()
    
    # 크롤링 결과 요약 출력
    print("\n" + "="*80)
    print("스레드 기반 병렬 크롤링 결과 요약")
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
            # 선박별 상세 정보가 있는 경우
            if 'success_count' in result:
                total_vessels_success += result['success_count']
                total_vessels_fail += result['fail_count']
                print(f"  └─ 선박: 성공 {result['success_count']}개, 실패 {result['fail_count']}개")
        else:
            fail_count += 1
            # 선박별 상세 정보가 있는 경우
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
    
    # 기존 순차 처리와 비교 (이론적)
    estimated_sequential_time = total_duration * 2  # 2개 스레드이므로 이론적으로는 절반
    time_saved = estimated_sequential_time - total_duration
    print(f"예상 순차 처리 시간: {estimated_sequential_time:.2f}초")
    print(f"절약된 시간: {time_saved:.2f}초 ({time_saved/estimated_sequential_time*100:.1f}%)")
    
    if total_vessels_success > 0 or total_vessels_fail > 0:
        print(f"\n선박별 상세 결과:")
        print(f"총 선박: {total_vessels_success + total_vessels_fail}개")
        print(f"성공: {total_vessels_success}개")
        print(f"실패: {total_vessels_fail}개")
    
    print("="*80)
    
    # 로그 파일에도 요약 기록
    logger.info(f"=== 전체 크롤링 완료: {total_end_time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    logger.info(f"총 소요시간: {total_duration:.2f}초 (병렬 처리)")
    logger.info(f"성공: {success_count}개 선사, 실패: {fail_count}개 선사")
    if total_vessels_success > 0 or total_vessels_fail > 0:
        logger.info(f"선박별 - 성공: {total_vessels_success}개, 실패: {total_vessels_fail}개")
    
    # 엑셀 로그 저장
    save_excel_log(crawling_results, total_duration)
    
    # 구글드라이브 업로드 이후 로직은 주석처리 (테스트 목적)
    print("\n" + "="*80)
    print("테스트 완료 - 엑셀 로그만 생성됨")
    print("="*80)
    
    # 주석처리된 로직들:
    # - 구글 드라이브 업로드
    # - 오래된 데이터 정리  
    # - 에러로그 자동 업로드 및 정리
    
    print("\n" + "="*80)
    print("스레드 기반 병렬 크롤링 테스트 완료!")
    print(f"총 소요시간: {total_duration:.2f}초 (병렬 처리)")
    print(f"기존 대비 예상 절약 시간: {time_saved:.2f}초")
    print(f"엑셀 로그 저장 위치: {test_dir}")
    print("="*80)
    

    