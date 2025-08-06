# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/07/01 (완성)
# 선사 링크 : https://www.hmm21.com/e-service/general/schedule/ScheduleMain.do
# 선박 리스트 : ["HMM BANGKOK"]

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

from .base import ParentsClass
import os
import time
import pandas as pd
import logging
import traceback

class HMM_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()
        self.carrier_name = "HMM"
        
        # 로깅 설정
        self.setup_logging()
        
        # 선박 리스트
        self.vessel_name_list = ["HMM BANGKOK"]
        
        # 크롤링 결과 추적
        self.success_count = 0
        self.fail_count = 0
        self.failed_vessels = []

    def setup_logging(self):
        """로깅 설정"""
        # 초기에는 에러가 없으므로 파일 로그 생성하지 않음
        self.logger = self.setup_logging(self.carrier_name, has_error=False)
        
    def setup_logging_with_error(self):
        """에러 발생 시 로깅 설정"""
        # 에러가 발생했으므로 파일 로그 생성
        self.logger = self.setup_logging(self.carrier_name, has_error=True)

    def step1_visit_website_and_click_by_vessel_tab(self):
        """1단계: 선사 홈페이지 접속 후 by vessel 탭 클릭"""
        try:
            self.logger.info("=== 1단계: 선사 홈페이지 접속 및 by vessel 탭 클릭 시작 ===")
            
            # 0. 선사 홈페이지 접속
            self.Visit_Link("https://www.hmm21.com/e-service/general/schedule/ScheduleMain.do")
            driver = self.driver
            wait = self.wait

            # 1. by vessel name 클릭  
            vessel_tab = wait.until(EC.element_to_be_clickable((
                By.XPATH , '/html/body/div[5]/div[3]/div[2]/div/div/ul/li[3]/a/div'
            )))
            vessel_tab.click()
            time.sleep(0.5)
            self.logger.info("by vessel 탭 클릭 완료")
            
            self.logger.info("=== 1단계: 선사 홈페이지 접속 및 by vessel 탭 클릭 완료 ===")
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== 1단계: 선사 홈페이지 접속 및 by vessel 탭 클릭 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False

    def step2_crawl_vessel_data(self):
        """2단계: 지정된 선박별로 조회 루핑 시작"""
        try:
            self.logger.info("=== 2단계: 선박별 데이터 크롤링 시작 ===")
            
            driver = self.driver
            wait = self.wait
            
            for vessel_name in self.vessel_name_list:
                try:
                    self.logger.info(f"선박 {vessel_name} 크롤링 시작")
                    
                    # 2. Vessel name 입력 //*[@id="srchByVesselVslCd"]
                    select_elem = wait.until(EC.presence_of_element_located((
                        By.ID , 'srchByVesselVslCd'
                    )))
                    select_item = Select(select_elem)

                    found = False
                    for option in select_item.options:
                        if vessel_name in option.text:
                            select_item.select_by_visible_text(option.text)
                            self.logger.info(f"선택함 : {option.text}")
                            found = True
                            break

                    if not found:
                        self.logger.warning("없는 선박임")
                        self.fail_count += 1
                        self.failed_vessels.append(vessel_name)
                        continue
                    
                    time.sleep(1)

                    # 3. 조회 버튼 클릭 
                    search_btn = wait.until(EC.element_to_be_clickable((
                        By.XPATH, '//*[@id="tabItem03"]/div/div/div[1]/div[2]/div[3]/div/div[2]/div/button'
                    )))
                    search_btn.click()
                    time.sleep(1.2) # 리스트 기다려줘

                    # columns = ["Vessel Cdoe","Voyage" ,"Port","Terminal", "Rating Date", "ETA","ETB","ETD","Current Location"]
                    # //*[@id="byVesselNameArea"]/tr[1] ~  //*[@id="byVesselNameArea"]/tr[8]
                    # //*[@id="byVesselNextArea"]/div/div/a[2]  (next버튼)
                    # //*[@id="byVesselNameArea"]/tr[1] ~  //*[@id="byVesselNameArea"]/tr[8]
                    # -------------- 테이블 긁기: 페이지 1 --------------
                    all_rows = []
                    table_xpath_base = '//*[@id="byVesselNameArea"]/tr['

                    def extract_table_rows():
                        for idx in range(1, 9):  # tr[1]~tr[8]
                            try:
                                row_xpath = table_xpath_base + f"{idx}]"
                                tr = driver.find_element(By.XPATH, row_xpath)
                                tds = tr.find_elements(By.TAG_NAME, 'td')
                                row_data = [td.text.strip() for td in tds]
                                # 필터링 조건 추가 가능
                                if any(row_data):  # 빈 행 제거
                                    all_rows.append(row_data)
                            except:
                                pass  # 혹시 없는 tr 인덱스는 건너뜀

                    extract_table_rows()

                    # -------------- 페이지 아래로 내리고 next 클릭 --------------
                    driver.execute_script("window.scrollBy(0,150);")
                    time.sleep(1)

                    try:
                        next_btn = driver.find_element(By.XPATH, '//*[@id="byVesselNextArea"]/div/div/a[2]')
                        next_btn.click()
                        time.sleep(1.5)  # 다음 페이지 로딩 대기
                        extract_table_rows()  # 다음 페이지 8줄 추가로 긁기
                        self.logger.info("다음 페이지 데이터 수집 완료")
                    except Exception as e:
                        self.logger.warning(f"다음 페이지 버튼 클릭 실패: {e}")

                    # ----------- 엑셀 파일 저장 -----------
                    columns = ["Vessel Code", "Voyage" ,"Port","Terminal", "Rating Date", "ETA","ETB","ETD","Current Location"]
                    df = pd.DataFrame(all_rows, columns=columns)

                    file_path = self.get_save_path(self.carrier_name, vessel_name, ext="xlsx")
                    df.to_excel(file_path, index=False, engine="openpyxl")
                    self.logger.info(f"엑셀 저장 완료: {file_path}")
                    
                    self.success_count += 1
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

    def step3_process_data_and_save(self):
        """3단계: 데이터 취합 후 다음 페이지 선택 클릭 이후 또 데이터 취합 1회 추가"""
        try:
            self.logger.info("=== 3단계: 데이터 처리 및 추가 수집 시작 ===")
            
            # 이 단계에서는 이미 step2에서 파일이 생성되었으므로 추가 처리가 필요하다면 여기서 수행
            # 예: 파일명 변경, 데이터 검증 등
            
            self.logger.info("=== 3단계: 데이터 처리 및 추가 수집 완료 ===")
            return True
            
        except Exception as e:
            self.logger.error(f"=== 3단계: 데이터 처리 및 추가 수집 실패 ===")
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
            self.logger.info("=== HMM 크롤링 시작 ===")
            
            # 1단계: 선사 홈페이지 접속 및 by vessel 탭 클릭
            if not self.step1_visit_website_and_click_by_vessel_tab():
                return False
            
            # 2단계: 지정된 선박별로 루핑 작업 시작
            if not self.step2_crawl_vessel_data():
                return False
            
            # 3단계: 파일명 규칙 및 저장경로 규칙 적용
            if not self.step3_save_with_naming_rules():
                return False
            
            # 최종 결과 로깅
            self.logger.info("=== HMM 크롤링 완료 ===")
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
            self.logger.error(f"=== HMM 크롤링 전체 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False