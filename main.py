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

# ErrorLog 폴더 구조 생성
def setup_main_log_folder():
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

# 메인 로깅 설정
today_log_dir = setup_main_log_folder()
main_log_file = os.path.join(today_log_dir, 'main_crawling_log.txt')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(main_log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def run_crawler_with_error_handling(crawler_name, crawler_instance):
    """크롤러를 실행하고 에러를 처리하는 함수"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"=== {crawler_name} 크롤링 시작 ===")
        start_time = datetime.now()
        
        result = crawler_instance.run()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 크롤러에 성공/실패 카운트가 있는 경우 선박별 결과 확인
        if hasattr(crawler_instance, 'success_count') and hasattr(crawler_instance, 'fail_count'):
            total_vessels = getattr(crawler_instance, 'success_count', 0) + getattr(crawler_instance, 'fail_count', 0)
            success_count = getattr(crawler_instance, 'success_count', 0)
            fail_count = getattr(crawler_instance, 'fail_count', 0)
            failed_vessels = getattr(crawler_instance, 'failed_vessels', [])
            
            # 선박 중 하나라도 실패하면 선사도 실패로 분류
            if fail_count > 0:
                logger.error(f"=== {crawler_name} 크롤링 실패 (소요시간: {duration:.2f}초) ===")
                logger.error(f"선박 실패로 인한 선사 실패: 총 {total_vessels}개 선박 중 성공 {success_count}개, 실패 {fail_count}개")
                if failed_vessels:
                    logger.error(f"실패한 선박: {', '.join(failed_vessels)}")
                
                return {
                    'success': False,
                    'duration': duration,
                    'start_time': start_time,
                    'end_time': end_time,
                    'total_vessels': total_vessels,
                    'success_count': success_count,
                    'fail_count': fail_count,
                    'failed_vessels': failed_vessels,
                    'error': f'선박 실패로 인한 선사 실패 (실패한 선박: {", ".join(failed_vessels)})'
                }
            else:
                logger.info(f"=== {crawler_name} 크롤링 완료 (소요시간: {duration:.2f}초) ===")
                logger.info(f"{crawler_name} 상세 결과: 총 {total_vessels}개 선박 중 성공 {success_count}개, 실패 {fail_count}개")
                
                return {
                    'success': True,
                    'duration': duration,
                    'start_time': start_time,
                    'end_time': end_time,
                    'total_vessels': total_vessels,
                    'success_count': success_count,
                    'fail_count': fail_count,
                    'failed_vessels': failed_vessels
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
        instance = constructor()
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

if __name__ == "__main__":
    print("Entry Point is Here")
    logger = logging.getLogger(__name__)
    
    # 전체 크롤링 시작 시간
    total_start_time = datetime.now()
    logger.info(f"=== 전체 크롤링 시작: {total_start_time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    
    # 크롤링 결과를 저장할 리스트
    crawling_results = []
    
    # 실행할 선사 정의 (필요한 선사는 주석 해제)
    carriers_to_run = [
        ("SITC", lambda: sitc.SITC_Crawling()),
        ("EVERGREEN", lambda: evergreen.EVERGREEN_Crawling()),
        ("COSCO", lambda: cosco.Cosco_Crawling()),
        ("WANHAI", lambda: wanhai.WANHAI_Crawling()),
        ("CKLINE", lambda: ckline.CKLINE_Crawling()),
        ("PANOCEAN", lambda: panocean.PANOCEAN_Crawling()),
        ("SNL", lambda: snl.SNL_Crawling()),
        ("SMLINE", lambda: smline.SMLINE_Crawling()),
        ("HMM", lambda: hmm.HMM_Crawling()),
        ("FDT", lambda: fdt.FDT_Crawling()),
        ("IAL", lambda: ial.IAL_Crawling()),
        ("DYLINE", lambda: dyline.DYLINE_Crawling()),
        ("YML", lambda: yml.YML_Crawling()),
        ("NSS", lambda: nss.NSS_Crawling()),
        ("ONE", lambda: one.ONE_Crawling()),
    ]

    # 순차 실행: 인스턴스 생성 실패/실행 실패 모두 결과에 기록하고 계속 진행
    for carrier_name, ctor in carriers_to_run:
        try_run_carrier(carrier_name, ctor, crawling_results)

    # 전체 크롤링 종료 시간
    total_end_time = datetime.now()
    total_duration = (total_end_time - total_start_time).total_seconds()
    
    # 크롤링 결과 요약 출력
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
            # 선박별 상세 정보가 있는 경우
            if 'success_count' in result:
                total_vessels_success += result['success_count']
                total_vessels_fail += result['fail_count']
                print(f"  └─ 선박: 성공 {result['success_count']}개, 실패 {result['fail_count']}개")
                if result['failed_vessels']:
                    print(f"  └─ 실패한 선박: {', '.join(result['failed_vessels'])}")
        else:
            fail_count += 1
            if 'error' in result:
                print(f"  └─ 에러: {result['error']}")
    
    print(f"\n총 {len(crawling_results)}개 선사 중")
    print(f"성공: {success_count}개")
    print(f"실패: {fail_count}개")
    print(f"총 소요시간: {total_duration:.2f}초")
    
    if total_vessels_success > 0 or total_vessels_fail > 0:
        print(f"\n선박별 상세 결과:")
        print(f"총 선박: {total_vessels_success + total_vessels_fail}개")
        print(f"성공: {total_vessels_success}개")
        print(f"실패: {total_vessels_fail}개")
    
    print("="*80)
    
    # 로그 파일에도 요약 기록
    logger.info(f"=== 전체 크롤링 완료: {total_end_time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    logger.info(f"총 소요시간: {total_duration:.2f}초")
    logger.info(f"성공: {success_count}개 선사, 실패: {fail_count}개 선사")
    if total_vessels_success > 0 or total_vessels_fail > 0:
        logger.info(f"선박별 - 성공: {total_vessels_success}개, 실패: {total_vessels_fail}개")
    
    # 구글 드라이브 업로드 실행 (주석처리)
    """
    print("\n" + "="*80)
    print("구글 드라이브 업로드 시작")
    print("="*80)
    
    try:
        # Google 폴더의 업로드 스크립트 import
        sys.path.append(os.path.join(os.getcwd(), 'Google'))
        from Google.upload_to_drive_oauth import main as upload_to_drive_main
    
        # 업로드 실행
        upload_to_drive_main()
        
        print("="*80)
        print("구글 드라이브 업로드 완료")
        print("="*80)
        
    except Exception as e:
        print(f"구글 드라이브 업로드 실패: {str(e)}")
        logger.error(f"구글 드라이브 업로드 실패: {str(e)}")
        logger.error(f"상세 에러: {traceback.format_exc()}")
    
    # 오래된 데이터 정리
    print("\n" + "="*80)
    print("오래된 데이터 정리 시작")
    print("="*80)
    
    try:
        from cleanup_old_data import cleanup_old_folders
        
        # 1달(30일) 이전 폴더들 정리
        cleanup_old_folders(days_to_keep=30)
        
        print("="*80)
        print("오래된 데이터 정리 완료")
        print("="*80)
        
    except Exception as e:
        print(f"오래된 데이터 정리 실패: {str(e)}")
        logger.error(f"오래된 데이터 정리 실패: {str(e)}")
        logger.error(f"상세 에러: {traceback.format_exc()}")
    """
    

    