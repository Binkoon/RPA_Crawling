# Developer : 디지털전략팀/강현빈 사원
# Date : 2025/07/01 (완성)
# 선사 링크 : https://container.panocean.com/
# 선박 리스트 : 
"""
["POS SINGAPORE" , "POS YOKOHAMA" , "POS QINGDAO" , "POS GUANGZHOU",
 "POS HOCHIMINH", , "POS LAEMCHABANG"]
"""
# 추가 정보 : 드랍다운 리스트가  선명/항차 이런식이고 항차는 동적으로 바뀌기 때문에 "선명"을 포함한 애가 있다면

################# User-agent 모듈 ###############
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
############### 셀레니움 기본 + time #####
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import traceback
######## 부모클래스
from .base import ParentsClass

import os

# 다운로드 버튼이 제공되서 파일명이 정해져서 나오는 선사는 이거 쓰셈
def get_latest_file(folder, ext=".xlsx"):
    files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(ext)]
    if not files:
        return None
    return max(files, key=os.path.getctime)

# 파일을 덮어씌우고 있음. 동일한 파일명이라 그런듯. 이 로직도 쓰셈
def get_unique_filename(folder, filename):
    base, ext = os.path.splitext(filename)
    candidate = filename
    i = 1
    while os.path.exists(os.path.join(folder, candidate)):
        candidate = f"{base}_{i}{ext}"
        i += 1
    return candidate

class PANOCEAN_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()
        self.carrier_name = "POS"
        
        # 로깅 설정
        self.setup_logging()
        
        # 선박 리스트
        self.vessel_name_list = ["POS SINGAPORE"
                                , "POS YOKOHAMA" , "POS QINGDAO" , "POS GUANGZHOU",
                                "POS HOCHIMINH", "POS LAEMCHABANG"]
        
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

    def step1_visit_website_and_click_tabs(self):
        """1단계: 선사 홈페이지 접속 + 스케줄 탭 클릭 + 선박 탭 클릭"""
        try:
            self.logger.info("=== 1단계: 선사 홈페이지 접속 및 탭 클릭 시작 ===")
            
            # 0. 선사 홈페이지 접속
            self.Visit_Link("https://container.panocean.com/")
            driver = self.driver
            wait = self.wait

            time.sleep(4)
            # 1. 스케줄 탭 클릭
            schedule_tab = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mf_btn_11000"]')))
            schedule_tab.click()
            time.sleep(1)
            self.logger.info("스케줄 탭 클릭 완료")

            # 2. 선박명 클릭
            vessel_tab = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mf_btn_11002"]')))
            vessel_tab.click()
            time.sleep(3) # 얘 좀 더 잡아주자.
            self.logger.info("선박 탭 클릭 완료")
            
            self.logger.info("=== 1단계: 선사 홈페이지 접속 및 탭 클릭 완료 ===")
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== 1단계: 선사 홈페이지 접속 및 탭 클릭 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False

    def step2_crawl_vessel_data(self):
        """2단계: 지정된 선박별로 루핑 작업 시작"""
        try:
            self.logger.info("=== 2단계: 선박별 데이터 크롤링 시작 ===")
            
            driver = self.driver
            wait = self.wait

            # 3. 선박명 입력 및 자동완성 리스트 수집
            all_vessel_names = [] # 모든 자동완성 선박 담는 리스트

            for vessel_name in self.vessel_name_list:
                try:
                    self.logger.info(f"선박 {vessel_name} 크롤링 시작")
                    
                    # 1. 라벨 클릭해서 input 활성화
                    label = driver.find_element(By.ID, 'mf_tac_layout_contents_11002_body_acb_vslInfo_label')
                    driver.execute_script("arguments[0].click();", label)
                    time.sleep(0.5)

                    # 2. input 요소 대기 및 상태 확인
                    input_box = wait.until(EC.visibility_of_element_located((By.ID, 'mf_tac_layout_contents_11002_body_acb_vslInfo_input')))
                    self.logger.info(f"Displayed: {input_box.is_displayed()}, Enabled: {input_box.is_enabled()}")

                    # 3. send_keys 대신 JS로 값 입력
                    driver.execute_script("""
                        arguments[0].value = arguments[1];
                        arguments[0].dispatchEvent(new Event('input', {bubbles:true}));
                        arguments[0].dispatchEvent(new KeyboardEvent('keydown', {bubbles:true, key:'A', keyCode:65}));
                        arguments[0].dispatchEvent(new KeyboardEvent('keyup', {bubbles:true, key:'A', keyCode:65}));
                    """, input_box, vessel_name)

                    time.sleep(2)

                    # 자동완성 리스트 tr 인덱스별로 접근
                    matched_vessels = []
                    idx = 1
                    while True:
                        try:
                            item = driver.find_element(
                                By.XPATH,
                                f'//*[@id="mf_tac_layout_contents_11002_body_acb_vslInfo_itemTable_main"]/tbody/tr[{idx}]'
                            )
                            if vessel_name in item.text:
                                matched_vessels.append(item.text)
                            idx += 1
                        except Exception:
                            # 더 이상 tr이 없으면 break
                            break

                    self.logger.info(f"자동완성 리스트: {matched_vessels}")

                    all_vessel_names.extend(matched_vessels)

                    for vessel_full_name in matched_vessels:
                        try:
                            # 1. label(라벨) 클릭해서 input 활성화
                            label = driver.find_element(By.ID, 'mf_tac_layout_contents_11002_body_acb_vslInfo_label')
                            driver.execute_script("arguments[0].click();", label)
                            time.sleep(0.3)

                            # 2. input 요소 대기 및 값 입력 (자바스크립트로)
                            input_box = wait.until(EC.visibility_of_element_located((By.ID, 'mf_tac_layout_contents_11002_body_acb_vslInfo_input')))
                            driver.execute_script("""
                                arguments[0].value = arguments[1];
                                arguments[0].dispatchEvent(new Event('input', {bubbles:true}));
                                arguments[0].dispatchEvent(new KeyboardEvent('keydown', {bubbles:true, key:'A', keyCode:65}));
                                arguments[0].dispatchEvent(new KeyboardEvent('keyup', {bubbles:true, key:'A', keyCode:65}));
                            """, input_box, vessel_full_name)
                            time.sleep(1.2)

                            # 3. 자동완성 리스트에서 해당 항목 클릭
                            idx = 1
                            clicked = False
                            while True:
                                try:
                                    item = driver.find_element(
                                        By.XPATH,
                                        f'//*[@id="mf_tac_layout_contents_11002_body_acb_vslInfo_itemTable_main"]/tbody/tr[{idx}]'
                                    )
                                    if item.text == vessel_full_name:
                                        item.click()
                                        clicked = True
                                        break
                                    idx += 1
                                except Exception:
                                    break
                            if not clicked:
                                self.logger.warning(f"{vessel_full_name} 클릭 실패")
                                self.fail_count += 1
                                self.failed_vessels.append(vessel_full_name)
                                continue

                            time.sleep(0.7)

                            # 4. 조회 버튼 클릭
                            search_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mf_tac_layout_contents_11002_body_btn_search"]')))
                            search_btn.click()
                            time.sleep(1.5)  # 결과 로딩 대기

                            # 5. 다운로드 버튼 클릭
                            download_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mf_tac_layout_contents_11002_body_btn_excel"]')))
                            download_btn.click()
                            self.logger.info(f"{vessel_full_name} 다운로드 완료")
                            time.sleep(1.5)  # 다운로드 대기
                            
                            self.success_count += 1
                            
                        except Exception as e:
                            self.logger.error(f"선박 {vessel_full_name} 크롤링 실패: {str(e)}")
                            self.fail_count += 1
                            self.failed_vessels.append(vessel_full_name)
                            continue
                    
                    self.logger.info(f"선박 {vessel_name} 크롤링 완료")
                    
                except Exception as e:
                    self.logger.error(f"선박 {vessel_name} 크롤링 실패: {str(e)}")
                    self.fail_count += 1
                    self.failed_vessels.append(vessel_name)
                    continue
            
            # === 다운로드 완료 후 파일명 일괄 변경 ===
            # 다운로드 폴더에서 ScheduleByVessel_2025_07_14*.xlsx 파일만 추출
            files = [f for f in os.listdir(self.today_download_dir) if f.startswith("ScheduleByVessel_") and f.endswith(".xlsx")]
            files.sort()  # 이름순 정렬: (1), (2), ... 순서대로

            for i, vessel_full_name in enumerate(all_vessel_names):
                if i < len(files):
                    old_path = os.path.join(self.today_download_dir, files[i])
                    new_filename = f"{self.carrier_name}_{vessel_full_name}.xlsx"
                    new_path = os.path.join(self.today_download_dir, new_filename)
                    os.rename(old_path, new_path)
                    self.logger.info(f"파일명 변경 완료: {new_path}")
            
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
            self.logger.info("=== PANOCEAN 크롤링 시작 ===")
            
            # 1단계: 선사 홈페이지 접속 + 스케줄 탭 클릭 + 선박 탭 클릭
            if not self.step1_visit_website_and_click_tabs():
                return False
            
            # 2단계: 지정된 선박별로 루핑 작업 시작
            if not self.step2_crawl_vessel_data():
                return False
            
            # 최종 결과 로깅
            self.logger.info("=== PANOCEAN 크롤링 완료 ===")
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
            self.logger.error(f"=== PANOCEAN 크롤링 전체 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False