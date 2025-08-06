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
from crawler import pil
from crawler import nss

import traceback
import logging
from datetime import datetime
import os
import sys

# 메인 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('main_crawling_log.txt', encoding='utf-8'),
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
        
        if result:
            logger.info(f"=== {crawler_name} 크롤링 완료 (소요시간: {duration:.2f}초) ===")
            
            # 크롤러별 상세 정보 수집
            detail_info = {
                'success': True,
                'duration': duration,
                'start_time': start_time,
                'end_time': end_time
            }
            
            # 크롤러에 성공/실패 카운트가 있는 경우 추가 정보 수집
            if hasattr(crawler_instance, 'success_count') and hasattr(crawler_instance, 'fail_count'):
                detail_info.update({
                    'total_vessels': getattr(crawler_instance, 'success_count', 0) + getattr(crawler_instance, 'fail_count', 0),
                    'success_count': getattr(crawler_instance, 'success_count', 0),
                    'fail_count': getattr(crawler_instance, 'fail_count', 0),
                    'failed_vessels': getattr(crawler_instance, 'failed_vessels', [])
                })
                logger.info(f"{crawler_name} 상세 결과: 총 {detail_info['total_vessels']}개 선박 중 성공 {detail_info['success_count']}개, 실패 {detail_info['fail_count']}개")
                if detail_info['failed_vessels']:
                    logger.info(f"실패한 선박: {', '.join(detail_info['failed_vessels'])}")
            
            return detail_info
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

if __name__ == "__main__":
    print("Entry Point is Here")
    logger = logging.getLogger(__name__)
    
    # 전체 크롤링 시작 시간
    total_start_time = datetime.now()
    logger.info(f"=== 전체 크롤링 시작: {total_start_time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    
    # 크롤링 결과를 저장할 리스트
    crawling_results = []
    
    # 첫 번째 5개 선사 실행
    print("\n=== 첫 번째 5개 선사 실행 ===")
    
    sitc_data = sitc.SITC_Crawling()
    result = run_crawler_with_error_handling("SITC", sitc_data)
    crawling_results.append(("SITC", result))

    evergreen_data = evergreen.EVERGREEN_Crawling()
    result = run_crawler_with_error_handling("EVERGREEN", evergreen_data)
    crawling_results.append(("EVERGREEN", result))

    cosco_data = cosco.Cosco_Crawling()  # 작업 끝
    result = run_crawler_with_error_handling("COSCO", cosco_data)
    crawling_results.append(("COSCO", result))

    wanhai_data = wanhai.WANHAI_Crawling()
    result = run_crawler_with_error_handling("WANHAI", wanhai_data)
    crawling_results.append(("WANHAI", result))

    ckline_data = ckline.CKLINE_Crawling()
    result = run_crawler_with_error_handling("CKLINE", ckline_data)
    crawling_results.append(("CKLINE", result))
    
    print("=== 첫 번째 5개 선사 완료 ===")
    
    # 나머지 선사들은 주석 처리 (필요시 주석 해제)
    """
    panocean_data = panocean.PANOCEAN_Crawling()
    result = run_crawler_with_error_handling("PANOCEAN", panocean_data)
    crawling_results.append(("PANOCEAN", result))

    snl_data = snl.SNL_Crawling()
    result = run_crawler_with_error_handling("SNL", snl_data)
    crawling_results.append(("SNL", result))

    smline_data = smline.SMLINE_Crawling()
    result = run_crawler_with_error_handling("SMLINE", smline_data)
    crawling_results.append(("SMLINE", result))

    hmm_data = hmm.HMM_Crawling()
    result = run_crawler_with_error_handling("HMM", hmm_data)
    crawling_results.append(("HMM", result))

    fdt_data = fdt.FDT_Crawling()
    result = run_crawler_with_error_handling("FDT", fdt_data)
    crawling_results.append(("FDT", result))

    ial_data = ial.IAL_Crawling()
    result = run_crawler_with_error_handling("IAL", ial_data)
    crawling_results.append(("IAL", result))

    dyline_data = dyline.DYLINE_Crawling()
    result = run_crawler_with_error_handling("DYLINE", dyline_data)
    crawling_results.append(("DYLINE", result))

    yml_data = yml.YML_Crawling()
    result = run_crawler_with_error_handling("YML", yml_data)
    crawling_results.append(("YML", result))

    nss_data = nss.NSS_Crawling()
    result = run_crawler_with_error_handling("NSS", nss_data)
    crawling_results.append(("NSS", result))

    one_data = one.ONE_Crawling()
    result = run_crawler_with_error_handling("ONE", one_data)
    crawling_results.append(("ONE", result))

    # pil_data = pil.PIL_Crawling()
    # result = run_crawler_with_error_handling("PIL", pil_data)
    # crawling_results.append(("PIL", result))
    """

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
    
    # 구글 드라이브 업로드 실행
    print("\n" + "="*80)
    print("구글 드라이브 업로드 시작")
    print("="*80)
    
    try:
        # Google 폴더의 업로드 스크립트 import
        sys.path.append(os.path.join(os.getcwd(), 'Google'))
        from upload_to_drive_oauth import main as upload_to_drive_main
        
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
        
        # 30일 이전 폴더들 정리
        cleanup_old_folders(days_to_keep=30)
        
        print("="*80)
        print("오래된 데이터 정리 완료")
        print("="*80)
        
    except Exception as e:
        print(f"오래된 데이터 정리 실패: {str(e)}")
        logger.error(f"오래된 데이터 정리 실패: {str(e)}")
        logger.error(f"상세 에러: {traceback.format_exc()}")
    

    