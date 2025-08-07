# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/07/02 (완성)
# 선사 링크 : https://www.interasia.cc/Service/Form?servicetype=1
# 선박 리스트 : ["INTERASIA PROGRESS" ,"INTERASIA ENGAGE" , "INTERASIA HORIZON"]

# https://www.interasia.cc/Service/BoatList?ShipName=INTERASIA%20PROGRESS&StartDate=2025-07-01
# https://www.interasia.cc/Service/BoatList?ShipName=INTERASIA%20ENGAGE&StartDate=2025-07-01
# https://www.interasia.cc/Service/BoatList?ShipName=INTERASIA%20HORIZON&StartDate=2025-07-01

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

from .base import ParentsClass
import os,time
from datetime import datetime
import logging
import traceback

import pandas as pd

class IAL_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()
        self.carrier_name = "IAL"
        
        # 로깅 설정
        self.setup_logging()
        
        # 선박 리스트
        self.vessel_name_list = ["INTERASIA PROGRESS" ,"INTERASIA ENGAGE" , "INTERASIA HORIZON"]
        
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

    def step1_visit_website_with_vessel_params(self):
        """1단계: 지정된 선박별로 url param값만 변경하는 식으로 선사 홈페이지 접속"""
        try:
            self.logger.info("=== 1단계: 선박별 URL 파라미터로 홈페이지 접속 시작 ===")
            
            today = datetime.today().strftime("%Y-%m-%d")
            driver = self.driver
            wait = self.wait

            for vessel_name in self.vessel_name_list:
                try:
                    self.logger.info(f"선박 {vessel_name} 접속 시작")
                    
                    vessel_param = vessel_name.replace(" ","%20")
                    url = f'https://www.interasia.cc/Service/BoatList?ShipName={vessel_param}&StartDate={today}'
                    self.Visit_Link(url)
                    
                    self.logger.info(f"선박 {vessel_name} 접속 완료")
                    
                except Exception as e:
                    self.logger.error(f"선박 {vessel_name} 접속 실패: {str(e)}")
                    self.fail_count += 1
                    self.failed_vessels.append(vessel_name)
                    continue
            
            self.logger.info("=== 1단계: 선박별 URL 파라미터로 홈페이지 접속 완료 ===")
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== 1단계: 선박별 URL 파라미터로 홈페이지 접속 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False

    def step2_collect_data(self):
        """2단계: 데이터 수집"""
        try:
            self.logger.info("=== 2단계: 데이터 수집 시작 ===")
            
            today = datetime.today().strftime("%Y-%m-%d")
            driver = self.driver
            wait = self.wait

            for vessel_name in self.vessel_name_list:
                try:
                    self.logger.info(f"선박 {vessel_name} 데이터 수집 시작")
                    
                    vessel_param = vessel_name.replace(" ","%20")
                    url = f'https://www.interasia.cc/Service/BoatList?ShipName={vessel_param}&StartDate={today}'
                    self.Visit_Link(url)

                    # 1) 테이블 헤더 가져오기
                    thead_xpath = '//*[@id="wrapper"]/main/section[2]/div/div[2]/div[2]/table/thead'
                    thead = driver.find_element(By.XPATH, thead_xpath)
                    headers = [th.text.strip() for th in thead.find_elements(By.TAG_NAME, "th")]

                    header_map = {
                        "Arrival":"ETA",
                        "Berth":"ETB",
                        "Departure":"ETD"
                    }

                    new_headers = []
                    for h in headers:
                        new_headers.append(header_map.get(h,h))
                    
                    new_headers = ["Vessel Name"] + new_headers

                    # 2) 테이블 바디에서 모든 행 가져오기
                    tbody_xpath = '//*[@id="wrapper"]/main/section[2]/div/div[2]/div[2]/table/tbody'
                    tbody = driver.find_element(By.XPATH, tbody_xpath)

                    rows_data = []
                    row_index = 1

                    while True:
                        try:
                            # 각 행 XPath (인덱스 1부터 시작)
                            row_xpath = f'//*[@id="wrapper"]/main/section[2]/div/div[2]/div[2]/table/tbody/tr[{row_index}]'
                            row = driver.find_element(By.XPATH, row_xpath)
                            cells = row.find_elements(By.TAG_NAME, "td")
                            row_values = [cell.text.strip() for cell in cells]
                            rows_data.append(row_values)
                            row_index += 1
                        except Exception as e:
                            # 더 이상 행이 없으면 종료
                            break
                    
                    row_data_with_vessel = [[vessel_name] + row for row in rows_data]

                    # 3) pandas DataFrame 생성
                    df = pd.DataFrame(row_data_with_vessel, columns=new_headers)
                    # 4) 엑셀 저장 (파일명에 선박명과 날짜 포함)
                    filename = self.get_save_path(self.carrier_name, vessel_name)
                    df.to_excel(filename, index=False, header=True)
                    self.logger.info(f"엑셀 저장 완료: {filename}")
                    
                    self.success_count += 1
                    self.logger.info(f"선박 {vessel_name} 데이터 수집 완료")
                    
                except Exception as e:
                    self.logger.error(f"선박 {vessel_name} 데이터 수집 실패: {str(e)}")
                    self.fail_count += 1
                    self.failed_vessels.append(vessel_name)
                    continue
            
            self.logger.info("=== 2단계: 데이터 수집 완료 ===")
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
            self.logger.info("=== IAL 크롤링 시작 ===")
            
            # 1단계: 지정된 선박별로 url param값만 변경하는 식으로 선사 홈페이지 접속
            if not self.step1_visit_website_with_vessel_params():
                return False
            
            # 2단계: 지정된 선박별로 루핑 작업 시작
            if not self.step2_collect_data():
                return False
            
            # 3단계: 파일명 규칙 및 저장경로 규칙 적용
            if not self.step3_save_with_naming_rules():
                return False
            
            # 최종 결과 로깅
            self.logger.info("=== IAL 크롤링 완료 ===")
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
            self.logger.error(f"=== IAL 크롤링 전체 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False