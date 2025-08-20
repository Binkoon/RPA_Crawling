# Developer : 디지털전략팀/강현빈 사원
# Date : 2025/07/01 (완성)
# 선사링크 : https://www.wanhai.com/views/Main.xhtml
# 선박 대상 : ["WAN HAI 502","WAN HAI 521","WAN HAI 522","WAN HAI 351","WAN HAI 377","WAN HAI 322"]
# 추가 정보 : wanhai는 크롤링으로 의심되면 CAPTCHA 씀. 처음부터 막는게 아니라, 감시하다 막음. 따라서 잦은 호출은 금지.

############ 셀레니움 ###############
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import logging
import traceback
################# User-agent 모듈 ###############
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
##############부모 클래스 ##############
from .base import ParentsClass
############# Schedule_Data쪽에 넘겨야함 ###########
import os
import pandas as pd
from datetime import datetime

class WANHAI_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()
        self.carrier_name = "WHL"
        self.columns = ["Port", "A-Voy" , "ETA" , "ETA-Time" , 
                        "ETB", "ETB-Time" , "D-Voy", "ETD", "ETD-Time","Status"]
        
        # 로깅 설정
        self.setup_logging()
        
        # 선박 리스트
        self.vessel_name_list = ["WAN HAI 502","WAN HAI 521","WAN HAI 522","WAN HAI 351","WAN HAI 377","WAN HAI 322"]
        
        # 크롤링 결과 추적
        self.success_count = 0
        self.fail_count = 0
        self.failed_vessels = []

    def setup_logging(self):
        """로깅 설정"""
        # 초기에는 에러가 없으므로 파일 로그 생성하지 않음
        self.logger = super().setup_logging(self.carrier_name, has_error=False)
        
    def setup_logging_with_error(self):
        """에러 발생 시 로깅 설정"""
        # 에러가 발생했으므로 파일 로그 생성
        self.logger = super().setup_logging(self.carrier_name, has_error=True)

    def step1_visit_website(self):
        """1단계: 선사 홈페이지 접속"""
        try:
            self.logger.info("=== 1단계: 선사 홈페이지 접속 시작 ===")
            
            # 0. 선사 링크 접속
            self.Visit_Link("https://www.wanhai.com/views/skd/SkdByVsl.xhtml")
            driver = self.driver
            wait = self.wait
            
            time.sleep(0.5)
            
            self.logger.info("=== 1단계: 선사 홈페이지 접속 완료 ===")
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== 1단계: 선사 홈페이지 접속 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False

    def step2_crawl_vessel_data(self):
        """2단계: 지정된 선박별로 루핑 작업 시작"""
        try:
            self.logger.info("=== 2단계: 선박별 데이터 크롤링 시작 ===")
            
            driver = self.driver
            wait = self.wait
            
            # 1. 선박명 루핑 시킴  //*[@id="skdByVslBean"]/select   //*[@id="skdByVslBean"]/select
            for vessel_name in self.vessel_name_list:
                try:
                    self.logger.info(f"선박 {vessel_name} 크롤링 시작")
                    
                    # 선박별 타이머 시작
                    self.start_vessel_timer(vessel_name)
                    
                    # 1. select 박스 찾기 (By.xpath 사용 ㄱㄱ)
                    select_elem = wait.until(lambda d: d.find_element(By.XPATH, '//*[@id="skdByVslBean"]/select'))
                    select_box = Select(select_elem)

                    # 2. 옵션 중에서 vessel_name과 일치하는 항목 선택
                    found = False
                    for option in select_box.options:
                        if option.text.strip() == vessel_name:
                            select_box.select_by_visible_text(option.text)
                            self.logger.info(f"선택된 옵션: {option.text}")
                            found = True
                            break
                    if not found:
                        self.logger.warning(f"{vessel_name} 옵션을 찾을 수 없습니다.")
                        self.record_step_failure(vessel_name, "선박 조회", "드롭다운에서 해당 선박을 찾을 수 없음")
                        
                        # 실패한 경우에도 타이머 종료
                        vessel_duration = self.end_vessel_timer(vessel_name)
                        self.logger.warning(f"선박 {vessel_name} 크롤링 실패 (소요시간: {vessel_duration:.2f}초)")
                        continue

                    time.sleep(0.5)  # 선택 후 대기

                    # 3. 조회 버튼 클릭
                    query_btn = wait.until(lambda d: d.find_element(By.ID, 'Query'))
                    query_btn.click()
                    self.logger.info(f"{vessel_name} 조회 버튼 클릭 완료")

                    time.sleep(2)  # 결과 로딩 대기

                    # 4. 테이블 데이터 추출
                    table_xpath = '//*[@id="popuppane"]/table[3]'
                    row_idx = 1
                    data_rows = []
                    while True:
                        try:
                            row_xpath = f'{table_xpath}/tbody/tr[{row_idx}]'
                            row_elem = driver.find_element(By.XPATH, row_xpath)
                            cells = row_elem.find_elements(By.TAG_NAME, 'td')
                            row_data = [cell.text.strip() for cell in cells]
                            if row_data:  # 빈 행은 제외
                                data_rows.append(row_data)
                            row_idx += 1
                        except Exception:
                            # 더 이상 tr이 없으면 break
                            break

                    self.logger.info(f"{vessel_name} 테이블 row 개수: {len(data_rows)}")

                    # 5. 데이터프레임으로 저장 및 엑셀로 내보내기
                    if data_rows:
                        # 첫 번째 row가 헤더라면 아래 코드로 하기. 근데 WAN HAI는 첫 row부터 데이터임. (=tr)
                        # header = data_rows[0]
                        # df = pd.DataFrame(data_rows[1:], columns=header)
                        # 첫 번째 row가 데이터라면,
                        df = pd.DataFrame(data_rows,columns=self.columns)
                        save_path = self.get_save_path(self.carrier_name, vessel_name)
                        df.to_excel(save_path, index=False, header=True)
                        self.logger.info(f"{vessel_name} 엑셀 저장 완료: {save_path}")
                        self.record_vessel_success(vessel_name)
                        
                        # 선박별 타이머 종료
                        vessel_duration = self.end_vessel_timer(vessel_name)
                        self.logger.info(f"선박 {vessel_name} 크롤링 완료 (소요시간: {vessel_duration:.2f}초)")
                    else:
                        self.logger.warning(f"{vessel_name} 데이터 없음")
                        self.record_step_failure(vessel_name, "데이터 크롤링", "데이터가 없음")
                        
                        # 실패한 경우에도 타이머 종료
                        vessel_duration = self.end_vessel_timer(vessel_name)
                        self.logger.warning(f"선박 {vessel_name} 크롤링 실패 (소요시간: {vessel_duration:.2f}초)")
                    
                except Exception as e:
                    self.logger.error(f"선박 {vessel_name} 크롤링 실패: {str(e)}")
                    self.record_step_failure(vessel_name, "데이터 크롤링", str(e))
                    
                    # 실패한 경우에도 타이머 종료
                    vessel_duration = self.end_vessel_timer(vessel_name)
                    self.logger.error(f"선박 {vessel_name} 크롤링 실패 (소요시간: {vessel_duration:.2f}초)")
                    continue
            
            self.logger.info("=== 2단계: 선박별 데이터 크롤링 완료 ===")
            self.logger.info(f"성공: {self.success_count}개, 실패: {self.fail_count}개")
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== 2단계: 선박별 데이터 크롤링 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False

    def run(self):
        """메인 실행 함수"""
        try:
            self.logger.info("=== WANHAI 크롤링 시작 ===")
            
            # 1단계: 선사 홈페이지 접속
            if not self.step1_visit_website():
                return False
            
            # 2단계: 지정된 선박별로 루핑 작업 시작
            if not self.step2_crawl_vessel_data():
                return False
            
            # 최종 결과 로깅
            self.logger.info("=== WANHAI 크롤링 완료 ===")
            self.logger.info(f"총 {len(self.vessel_name_list)}개 선박 중")
            self.logger.info(f"성공: {self.success_count}개")
            self.logger.info(f"실패: {self.fail_count}개")
            if self.failed_vessels:
                self.logger.info(f"실패한 선박: {', '.join(self.failed_vessels)}")
            
            self.Close()
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== WANHAI 크롤링 전체 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False

    def retry_failed_vessels(self, failed_vessels):
        """
        실패한 선박들에 대해 재시도하는 메서드
        
        Args:
            failed_vessels: 재시도할 선박 이름 리스트
            
        Returns:
            dict: 재시도 결과 (성공/실패 개수 등)
        """
        if not failed_vessels:
            return {
                'retry_success': 0,
                'retry_fail': 0,
                'total_retry': 0,
                'final_success': self.success_count,
                'final_fail': self.fail_count,
                'note': '재시도할 선박이 없습니다.'
            }
        
        self.logger.info(f"=== WANHAI 실패한 선박 재시도 시작 ===")
        self.logger.info(f"재시도 대상 선박: {', '.join(failed_vessels)}")
        self.logger.info(f"재시도 대상 개수: {len(failed_vessels)}개")
        
        # 재시도 전 상태 저장
        original_success_count = self.success_count
        original_fail_count = self.fail_count
        
        # 실패한 선박들만 재시도
        retry_success_count = 0
        retry_fail_count = 0
        
        for vessel_name in failed_vessels:
            try:
                self.logger.info(f"=== {vessel_name} 재시도 시작 ===")
                
                # 선박별 타이머 시작
                self.start_vessel_timer(vessel_name)
                
                # 1. 선박명 입력
                vessel_input = self.driver.find_element(By.ID, 'Vessel')
                vessel_input.clear()
                vessel_input.send_keys(vessel_name)
                time.sleep(1)
                
                # 2. 조회 버튼 클릭
                query_btn = self.wait.until(lambda d: d.find_element(By.ID, 'Query'))
                query_btn.click()
                time.sleep(2)
                
                # 3. 테이블 데이터 추출
                table_xpath = '//*[@id="popuppane"]/table[3]'
                row_idx = 1
                data_rows = []
                while True:
                    try:
                        row_xpath = f'{table_xpath}/tbody/tr[{row_idx}]'
                        row_elem = self.driver.find_element(By.XPATH, row_xpath)
                        cells = row_elem.find_elements(By.TAG_NAME, 'td')
                        row_data = [cell.text.strip() for cell in cells]
                        if row_data:
                            data_rows.append(row_data)
                        row_idx += 1
                    except Exception:
                        break
                
                # 4. DataFrame으로 저장 및 엑셀로 내보내기
                if data_rows:
                    df = pd.DataFrame(data_rows, columns=self.columns)
                    save_path = self.get_save_path(self.carrier_name, vessel_name)
                    df.to_excel(save_path, index=False, header=True)
                    self.logger.info(f"{vessel_name} 재시도 엑셀 저장 완료: {save_path}")
                    
                    # 성공 처리
                    self.record_vessel_success(vessel_name)
                    retry_success_count += 1
                    
                    # 실패 목록에서 제거
                    if vessel_name in self.failed_vessels:
                        self.failed_vessels.remove(vessel_name)
                    if vessel_name in self.failed_reasons:
                        del self.failed_reasons[vessel_name]
                    
                    vessel_duration = self.end_vessel_timer(vessel_name)
                    self.logger.info(f"선박 {vessel_name} 재시도 성공 (소요시간: {vessel_duration:.2f}초)")
                else:
                    self.logger.warning(f"{vessel_name} 재시도 시에도 데이터가 없음")
                    retry_fail_count += 1
                    vessel_duration = self.end_vessel_timer(vessel_name)
                    self.logger.warning(f"선박 {vessel_name} 재시도 실패 (소요시간: {vessel_duration:.2f}초)")
                
            except Exception as e:
                self.logger.error(f"선박 {vessel_name} 재시도 실패: {str(e)}")
                retry_fail_count += 1
                
                # 실패한 경우에도 타이머 종료
                vessel_duration = self.end_vessel_timer(vessel_name)
                self.logger.error(f"선박 {vessel_name} 재시도 실패 (소요시간: {vessel_duration:.2f}초)")
                continue
        
        # 재시도 결과 요약
        self.logger.info("="*60)
        self.logger.info("WANHAI 재시도 결과 요약")
        self.logger.info("="*60)
        self.logger.info(f"재시도 성공: {retry_success_count}개")
        self.logger.info(f"재시도 실패: {retry_fail_count}개")
        self.logger.info(f"재시도 후 최종 성공: {self.success_count}개")
        self.logger.info(f"재시도 후 최종 실패: {self.fail_count}개")
        self.logger.info("="*60)
        
        return {
            'retry_success': retry_success_count,
            'retry_fail': retry_fail_count,
            'total_retry': len(failed_vessels),
            'final_success': self.success_count,
            'final_fail': self.fail_count,
            'final_failed_vessels': self.failed_vessels.copy(),
            'note': f'WANHAI 재시도 완료 - 성공: {retry_success_count}개, 실패: {retry_fail_count}개'
        }