# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/08/21
# 역할 : 크롤러 실행 공통 모듈

import traceback
import logging
from datetime import datetime
from crawler_factory import CrawlerFactory
from utils.excel_logger import add_to_excel_log

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
                
                # 실패한 선박들만 재시도 (1회만 - 차단 방지)
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
                        # 선박별 소요시간 계산 (기본값은 전체 크롤링 시간)
                        vessel_duration = duration / total_vessels if total_vessels > 0 else duration
                        add_to_excel_log(crawler_name, vessel_name, "성공", "크롤링 완료", vessel_duration)
            
            # 실패한 선박들을 엑셀 로그에 기록
            for vessel_name in failed_vessels:
                reason = failed_reasons.get(vessel_name, "알 수 없는 오류")
                # 실패한 선박도 동일한 시간 분배
                vessel_duration = duration / total_vessels if total_vessels > 0 else duration
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

def run_carrier_parallel(carrier_name, results_list):
    """병렬 실행을 위한 선사 크롤링 함수"""
    logger = logging.getLogger(__name__)
    try:
        logger.info(f"=== {carrier_name} 병렬 크롤링 시작 ===")
        start_time = datetime.now()
        
        # 크롤러 팩토리를 사용하여 인스턴스 생성
        instance = CrawlerFactory.create_crawler(carrier_name)
        
        # 크롤러 실행
        result = run_crawler_with_error_handling(carrier_name, instance)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"=== {carrier_name} 병렬 크롤링 완료 (소요시간: {duration:.2f}초) ===")
        
        return carrier_name, result
        
    except Exception as e:
        end_time = datetime.now()
        logger.error(f"=== {carrier_name} 병렬 크롤링 실패 ===")
        logger.error(f"에러 메시지: {str(e)}")
        logger.error(f"상세 에러: {traceback.format_exc()}")
        
        return carrier_name, {
            'success': False,
            'duration': 0,
            'start_time': None,
            'end_time': end_time,
            'error': str(e),
            'traceback': traceback.format_exc()
        }
