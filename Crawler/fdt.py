# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/07/01 (완성)
# 선사 링크 : https://asiaschedule.unifeeder.com/Softship.Schedule/default.aspx
# 선박 리스트 : ["NAVIOS BAHAMAS"]

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import os
import time
import pandas as pd
import logging
import traceback
from .base import ParentsClass

class FDT_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()
        self.carrier_name = "FDT"
        
        # 로깅 설정
        self.setup_logging()
        
        # 선박 리스트
        self.vessel_name_list = ["NAVIOS BAHAMAS"]
        
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

    def step1_visit_website_and_click_vessel_tab(self):
        """1단계: 선사 홈페이지 접속 후 vessel 탭 클릭"""
        try:
            self.logger.info("=== 1단계: 선사 홈페이지 접속 및 vessel 탭 클릭 시작 ===")
            
            # 0. 선사 접속
            self.Visit_Link("https://asiaschedule.unifeeder.com/Softship.Schedule/default.aspx")
            driver = self.driver
            wait = self.wait
            time.sleep(2)  # 충분히 쉬어줘야 함

            # 1. vessel 탭 클릭
            vessel_tab = wait.until(EC.element_to_be_clickable((By.ID, "searchByVesselTabHeader")))
            driver.execute_script("arguments[0].click();", vessel_tab)
            time.sleep(1)
            self.logger.info("vessel 탭 클릭 완료")
            
            self.logger.info("=== 1단계: 선사 홈페이지 접속 및 vessel 탭 클릭 완료 ===")
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== 1단계: 선사 홈페이지 접속 및 vessel 탭 클릭 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False

    def step2_crawl_vessel_data(self):
        """2단계: 지정된 선박별로 루핑 시작"""
        try:
            self.logger.info("=== 2단계: 선박별 데이터 크롤링 시작 ===")
            
            driver = self.driver
            wait = self.wait
            
            for vessel_name in self.vessel_name_list:
                try:
                    self.logger.info(f"선박 {vessel_name} 크롤링 시작")
                    
                    # 선박별 타이머 시작
                    self.start_vessel_timer(vessel_name)
                    
                    # 입력창 찾기
                    input_box = wait.until(EC.presence_of_element_located((
                        By.XPATH, '//*[@id="searchByVesselTab"]/div[1]/div[1]/div[2]//input'
                    )))
                    # 입력 초기화 및 입력 실행
                    driver.execute_script("arguments[0].value = '';", input_box)
                    driver.execute_script("arguments[0].focus();", input_box)
                    time.sleep(0.2)
                    input_box.send_keys(vessel_name)
                    self.logger.info(f"[{vessel_name}] 입력 완료")
                    time.sleep(2)

                    # 자동완성 클릭
                    auto_item = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="BAHAMAS-"]')))
                    auto_item.click()
                    self.logger.info(f"[{vessel_name}] 자동완성 선택 완료")
                    time.sleep(1)

                    # 검색 버튼 클릭
                    search_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_searchByVesselButton"]')))
                    driver.execute_script("arguments[0].click();", search_btn)
                    time.sleep(1.5)

                    # 2. voyage_ports 클래스가 포함된 모든 table 가져오기
                    tables = driver.find_elements(By.CSS_SELECTOR, "table.voyage_ports")
                    # 3. voyage 클래스가 정확히 들어간 테이블도 따로 가져오기 새로 추가된 구문
                    voy_tables = driver.find_elements(By.CSS_SELECTOR, "table.voyage")
                    if not tables:
                        self.logger.warning(f"[{vessel_name}] 테이블 없음 - 스킵")
                        self.record_step_failure(vessel_name, "데이터 크롤링", "테이블이 없음")
                        
                        # 실패한 경우에도 타이머 종료
                        vessel_duration = self.end_vessel_timer(vessel_name)
                        self.logger.warning(f"선박 {vessel_name} 크롤링 실패 (소요시간: {vessel_duration:.2f}초)")
                        continue
                    
                    if len(tables) != len(voy_tables):
                        self.logger.warning(f"[{vessel_name}] 테이블 수({len(tables)})와 Voyage 테이블 수({len(voy_tables)}) 불일치")
                        self.record_step_failure(vessel_name, "데이터 크롤링", "테이블 수 불일치")
                        
                        # 실패한 경우에도 타이머 종료
                        vessel_duration = self.end_vessel_timer(vessel_name)
                        self.logger.warning(f"선박 {vessel_name} 크롤링 실패 (소요시간: {vessel_duration:.2f}초)")
                        continue

                    all_data = []
                    columns = ["Port", "Call ID", "Code", "ETA", "ETD" , "Voy"]

                    for idx, table in enumerate(tables):
                        # 동일한 인덱스의 voyage 테이블
                        try:
                            voy_table = voy_tables[idx]
                            voyage_td = voy_table.find_element(By.XPATH, './/td[@id="VoyageNumber"]')
                            voyage_number = voyage_td.get_attribute("innerHTML").strip()
                        except Exception as e:
                            self.logger.warning(f"[{vessel_name}] voyage_number 추출 실패 (index {idx}): {e}")
                            voyage_number = ""

                        # 기존 데이터 row 추출 방식 유지 (홀수 row만)
                        rows = table.find_elements(By.TAG_NAME, "tr")
                        for row_idx, tr in enumerate(rows):
                            if row_idx % 2 == 0:
                                continue  # 짝수 row는 skip
                            tds = tr.find_elements(By.TAG_NAME, "td")
                            if len(tds) < 5:
                                continue
                            row = [td.text.strip() for td in tds[:5]]
                            row.append(voyage_number)  # 추가된 항차번호
                            all_data.append(row)

                    # 4. DataFrame 저장
                    if all_data:
                        df = pd.DataFrame(all_data, columns=columns)
                        save_path = self.get_save_path(self.carrier_name, vessel_name)
                        df.to_excel(save_path, index=False)
                        self.logger.info(f"[{vessel_name}] 엑셀 저장 완료: {save_path}")
                        self.record_vessel_success(vessel_name)
                        
                        # 선박별 타이머 종료
                        vessel_duration = self.end_vessel_timer(vessel_name)
                        self.logger.info(f"선박 {vessel_name} 크롤링 완료 (소요시간: {vessel_duration:.2f}초)")
                    else:
                        self.logger.warning(f"[{vessel_name}] 추출된 데이터 없음 - 엑셀 저장 생략")
                        self.record_step_failure(vessel_name, "데이터 크롤링", "추출된 데이터가 없음")
                        
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

    def step3_save_with_naming_rules(self):
        """3단계: 파일명 규칙 및 저장경로 규칙 적용"""
        try:
            self.logger.info("=== 3단계: 파일명 규칙 및 저장경로 규칙 적용 시작 ===")
            
            # TODO: 파일명 규칙과 저장 경로 규칙 적용 로직 구현 필요
            # 현재는 기존 change_filename 로직을 활용하되, 향후 개선 예정
            for vessel_name in self.vessel_name_list:
                try:
                    self.change_filename(vessel_name)
                    self.logger.info(f"선박 {vessel_name} 파일명 변경 완료")
                except Exception as e:
                    self.logger.error(f"선박 {vessel_name} 파일명 변경 실패: {str(e)}")
                    continue
            
            self.logger.info("=== 3단계: 파일명 규칙 및 저장경로 규칙 적용 완료 ===")
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== 3단계: 파일명 규칙 및 저장경로 규칙 적용 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False

    def run(self):
        """메인 실행 함수"""
        try:
            self.logger.info("=== FDT 크롤링 시작 ===")
            
            # 1단계: 선사 홈페이지 접속 및 vessel 탭 클릭
            if not self.step1_visit_website_and_click_vessel_tab():
                return False
            
            # 2단계: 지정된 선박별로 루핑 작업 시작
            if not self.step2_crawl_vessel_data():
                return False
            
            # 3단계: 파일명 규칙 및 저장경로 규칙 적용
            if not self.step3_save_with_naming_rules():
                return False
            
            # 최종 결과 로깅
            self.logger.info("=== FDT 크롤링 완료 ===")
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
            self.logger.error(f"=== FDT 크롤링 전체 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False