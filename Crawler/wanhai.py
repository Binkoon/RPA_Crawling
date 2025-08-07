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
                        self.fail_count += 1
                        self.failed_vessels.append(vessel_name)
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
                        self.success_count += 1
                    else:
                        self.logger.warning(f"{vessel_name} 데이터 없음")
                        self.fail_count += 1
                        self.failed_vessels.append(vessel_name)
                    
                    self.logger.info(f"선박 {vessel_name} 크롤링 완료")
                    
                except Exception as e:
                    self.logger.error(f"선박 {vessel_name} 크롤링 실패: {str(e)}")
                    self.fail_count += 1
                    self.failed_vessels.append(vessel_name)
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