# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/06/27 (완료)
# 선사명 : SITC
# 선사링크 : https://ebusiness.sitcline.com/#/topMenu/vesselMovementSearch
# SITC에서 뽑아올 선박 리스트
"""
선박 리스트 : ["SITC DECHENG", "SITC BATANGAS" , "SITC SHENGMING" , "SITC QIMING",
                       "SITC XIN", "SITC YUNCHENG", "SITC MAKASSAR", "SITC CHANGDE", 
                       "SITC HANSHIN", "SITC XINGDE" ,"AMOUREUX"]
"""
############ 셀레니움 ###############
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import logging
import traceback
##############부모 클래스 ##############
from .base import ParentsClass
############# Schedule_Data쪽에 넘겨야함 ###########
import os
import pandas as pd

class SITC_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()
        self.carrier_name = "SITC"
        self.columns = [
            "vessel name", "voy", "port", "terminal", "ETA", "ETB", "ETD", "Rate", "Remark", "Update Date"
        ]
        
        # 로깅 설정
        self.setup_logging()
        
        # 선박 리스트
        self.vessel_name_list = ["SITC DECHENG","SITC BATANGAS"
                                , "SITC SHENGMING" , "SITC QIMING",
                              "SITC XIN", "SITC YUNCHENG", "SITC MAKASSAR", "SITC CHANGDE", 
                              "SITC HANSHIN", "SITC XINGDE","AMOUREUX"]
        
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

     # !!!! 이 로직은 병합셀이 있는 선사의 경우에만 적용함.
    def extract_time_after_weekday(self, cell_text):
        weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        lines = cell_text.split('\n')
        result = []
        for i, line in enumerate(lines):
            if any(day in line for day in weekdays):
                if i + 1 < len(lines):
                    result.append(lines[i + 1].strip())
        return result

    def step1_visit_website(self):
        """1단계: 선사 홈페이지 접속"""
        try:
            self.logger.info("=== 1단계: 선사 홈페이지 접속 시작 ===")
            
            # 0. 사이트 방문 들어가주고
            self.Visit_Link("https://ebusiness.sitcline.com/#/topMenu/vesselMovementSearch")
            driver = self.driver
            wait = self.wait

            time.sleep(0.5)  # 함 멈춰주고
            
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

            for vessel_name in self.vessel_name_list:
                try:
                    self.logger.info(f"선박 {vessel_name} 크롤링 시작")
                    
                    # 선박별 타이머 시작
                    self.start_vessel_timer(vessel_name)
                    
                    # 입력창 (vesselSearch 내 클래스명 el-input__inner 타겟팅 해야함)
                    vessel_input = wait.until(EC.presence_of_element_located((
                        By.XPATH, '//*[@id="app"]/div[1]/div/section/div/div/div/form/div/div[1]/div/div/div/div/input'
                    )))

                    # readonly 걸려있는거 해제해줘
                    driver.execute_script("arguments[0].removeAttribute('readonly');", vessel_input)
                    # vessel_input.clear()
                    # 필드 완전 초기화 (JS)
                    driver.execute_script("arguments[0].value = '';", vessel_input)
                    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", vessel_input)
                    vessel_input.send_keys(vessel_name)
                    self.logger.info(f"입력: {vessel_name}")
                    time.sleep(1)  # 드롭다운 뜨는 시간

                    # 드롭다운 항목 클릭
                    dropdown_xpath = "/html/body/div[2]/div[1]/div[1]/div/div[2]/div[2]/div"
                    dropdown_item = wait.until(EC.element_to_be_clickable((By.XPATH, dropdown_xpath)))
                    dropdown_item.click()
                    self.logger.info("드롭다운 항목 클릭")

                    # Search 버튼 클릭
                    search_button = wait.until(EC.element_to_be_clickable((
                        By.XPATH, '//*[@id="app"]/div[1]/div/section/div/div/div/form/div/div[2]/button'
                    )))
                    search_button.click()
                    self.logger.info("Search 버튼 클릭")
                    time.sleep(4)

                    # 2. 데이터 테이블 추출
                    tbody_xpath = '//*[@id="app"]/div[1]/div/section/div/div[2]/div[2]/div[3]/table/tbody'
                    row_idx = 1
                    data_rows = []
                    while True:
                        try:
                            row_xpath = f'{tbody_xpath}/tr[{row_idx}]'
                            row_elem = driver.find_element(By.XPATH, row_xpath)
                            cells = row_elem.find_elements(By.TAG_NAME, 'td')
                            row_data = [cell.text.strip() for cell in cells]
                            if row_data:
                                data_rows.append(row_data)
                            row_idx += 1
                        except Exception:
                            break

                    self.logger.info(f"{vessel_name} 테이블 row 개수: {len(data_rows)}")

                    # DataFrame으로 저장 및 엑셀로 내보내기
                    if data_rows:
                        df = pd.DataFrame(data_rows,columns=self.columns)
                        for col in ['ETA','ETB', 'ETD']:
                            if col in df.columns:
                                df[col] = df[col].apply(lambda x : '\n'.join(self.extract_time_after_weekday(str(x))))
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

                    time.sleep(1)
                    
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
            self.logger.info("=== SITC 크롤링 시작 ===")
            
            # 1단계: 선사 홈페이지 접속
            if not self.step1_visit_website():
                return False
            
            # 2단계: 지정된 선박별로 루핑 작업 시작
            if not self.step2_crawl_vessel_data():
                return False
            
            # 최종 결과 로깅
            self.logger.info("=== SITC 크롤링 완료 ===")
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
            self.logger.error(f"=== SITC 크롤링 전체 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False