# Developer : 디지털전략팀/강현빈 사원
# Date : 2025/07/01 (완성)
# 선사 링크 : https://container.panocean.com/
# 선박 리스트 : 
"""
["POS SINGAPORE"
                                , "HONOR BRIGHT" , "POS QINGDAO" , "POS GUANGZHOU",
                                "POS HOCHIMINH", "POS LAEMCHABANG"]
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
import pandas as pd

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
        super().__init__("PANOCEAN")
        self.carrier_name = "POS"
        
        # 로깅 설정
        self.setup_logging()
        
        # 선박 리스트
        self.vessel_name_list = ["POS SINGAPORE"
                                , "HONOR BRIGHT" , "POS QINGDAO" , "POS GUANGZHOU",
                                "POS HOCHIMINH", "POS LAEMCHABANG"]
        
        # 크롤링 결과 추적
        self.success_count = 0
        self.fail_count = 0
        self.failed_vessels = []
        self.failed_reasons = {}

    def setup_logging(self):
        """로깅 설정"""
        # 초기에는 에러가 없으므로 파일 로그 생성하지 않음
        self.logger = super().setup_logging(self.carrier_name, has_error=False)
        
    def setup_logging_with_error(self):
        """에러 발생 시 로깅 설정"""
        # 에러가 발생했으므로 파일 로그 생성
        self.logger = super().setup_logging(self.carrier_name, has_error=True)

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
                    
                    # 선박별 타이머 시작
                    self.start_vessel_tracking(vessel_name)
                    
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
                            self.logger.info(f"{vessel_full_name} 다운로드 시작")
                            
                            # 다운로드 완료 대기 및 즉시 파일명 변경
                            if self.wait_for_download_and_rename(vessel_full_name):
                                self.logger.info(f"선박 {vessel_full_name} Excel 다운로드 및 파일명 변경 완료")
                                self.success_count += 1
                            else:
                                self.logger.error(f"선박 {vessel_full_name} 파일명 변경 실패")
                                self.fail_count += 1
                                if vessel_full_name not in self.failed_vessels:
                                    self.failed_vessels.append(vessel_full_name)
                                    self.failed_reasons[vessel_full_name] = "파일명 변경 실패"
                            
                            time.sleep(1.5)  # 다운로드 대기
                            
                            # 선박별 타이머 종료
                            self.end_vessel_tracking(vessel_name, success=True)
                            vessel_duration = self.get_vessel_duration(vessel_name)
                            self.logger.info(f"선박 {vessel_full_name} 크롤링 완료 (소요시간: {vessel_duration:.2f}초)")
                            
                        except Exception as e:
                            self.logger.error(f"선박 {vessel_full_name} 크롤링 실패: {str(e)}")
                            # 실패한 경우에도 타이머 종료
                            self.end_vessel_tracking(vessel_name, success=False)
                            vessel_duration = self.get_vessel_duration(vessel_name)
                            self.logger.error(f"선박 {vessel_full_name} 크롤링 실패 (소요시간: {vessel_duration:.2f}초)")
                            
                            # 실패한 선박 기록
                            if vessel_name not in self.failed_vessels:
                                self.failed_vessels.append(vessel_name)
                                self.failed_reasons[vessel_name] = str(e)
                            
                            continue
                    
                    # 기본 선박명에 대한 처리 완료 (넘버링된 실제 선박들은 이미 개별 처리됨)
                    self.logger.info(f"기본 선박 {vessel_name} 처리 완료 - 실제 생성된 선박: {len(matched_vessels)}개")
                    
                except Exception as e:
                    self.logger.error(f"선박 {vessel_name} 크롤링 실패: {str(e)}")
                    # 실패한 경우에도 타이머 종료
                    self.end_vessel_tracking(vessel_name, success=False)
                    vessel_duration = self.get_vessel_duration(vessel_name)
                    self.logger.error(f"선박 {vessel_name} 크롤링 실패 (소요시간: {vessel_duration:.2f}초)")
                    
                    # 실패한 선박 기록
                    if vessel_name not in self.failed_vessels:
                        self.failed_vessels.append(vessel_name)
                        self.failed_reasons[vessel_name] = str(e)
                    
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
        
        self.logger.info(f"=== PANOCEAN 실패한 선박 재시도 시작 ===")
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
                self.start_vessel_tracking(vessel_name)
                
                # 1. 드롭다운 클릭해서 리스트 활성화
                vessel_div = self.driver.find_element(By.ID, 'mf_tac_layout_contents_11002_body_sbx_vessel')
                vessel_div.click()
                time.sleep(0.7)
                
                # 2. 자동완성 리스트에서 해당 선박 찾기
                vessel_found = False
                for idx in range(1, 21):  # 최대 20개 항목 확인
                    try:
                        row_xpath = f'//*[@id="mf_tac_layout_contents_11002_body_sbx_vessel_itemTable_main"]/tbody/tr[{idx}]'
                        row_elem = self.driver.find_element(By.XPATH, row_xpath)
                        td_elem = row_elem.find_element(By.TAG_NAME, 'td')
                        vessel_text = td_elem.text.strip()
                        
                        if vessel_name in vessel_text:
                            td_elem.click()
                            self.logger.info(f"{vessel_name} 선택 완료 (재시도)")
                            vessel_found = True
                            break
                    except Exception:
                        continue
                
                if not vessel_found:
                    self.logger.warning(f"{vessel_name} 자동완성 리스트에서 찾을 수 없음 (재시도)")
                    retry_fail_count += 1
                    continue
                
                time.sleep(0.7)
                
                # 3. 조회 버튼 클릭
                search_btn = self.wait.until(EC.element_to_be_clickable((
                    By.XPATH, '//*[@id="mf_tac_layout_contents_11002_body_btn_search"]'
                )))
                search_btn.click()
                time.sleep(1.5)
                
                # 4. 다운로드 버튼 클릭
                download_btn = self.wait.until(EC.element_to_be_clickable((
                    By.XPATH, '//*[@id="mf_tac_layout_contents_11002_body_btn_excel"]'
                )))
                download_btn.click()
                time.sleep(1.5)
                
                # 성공 처리
                # 성공 카운트는 end_vessel_tracking에서 자동 처리됨
                retry_success_count += 1
                
                # 실패 목록에서 제거
                if vessel_name in self.failed_vessels:
                    self.failed_vessels.remove(vessel_name)
                if vessel_name in self.failed_reasons:
                    del self.failed_reasons[vessel_name]
                
                self.end_vessel_tracking(vessel_name, success=True)
                vessel_duration = self.get_vessel_duration(vessel_name)
                self.logger.info(f"선박 {vessel_name} 재시도 성공 (소요시간: {vessel_duration:.2f}초)")
                
            except Exception as e:
                self.logger.error(f"선박 {vessel_name} 재시도 실패: {str(e)}")
                retry_fail_count += 1
                
                # 실패한 경우에도 타이머 종료
                self.end_vessel_tracking(vessel_name, success=True)
                vessel_duration = self.get_vessel_duration(vessel_name)
                self.logger.error(f"선박 {vessel_name} 재시도 실패 (소요시간: {vessel_duration:.2f}초)")
                continue
        
        # 재시도 결과 요약
        self.logger.info("="*60)
        self.logger.info("PANOCEAN 재시도 결과 요약")
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
            'note': f'PANOCEAN 재시도 완료 - 성공: {retry_success_count}개, 실패: {retry_fail_count}개'
        }

    def step3_save_with_naming_rules(self):
        """3단계: 파일명 변경 확인 및 누락 파일 체크"""
        try:
            self.logger.info("=== 3단계: 파일명 변경 확인 및 누락 파일 체크 시작 ===")
            
            # 이미 파일명이 변경된 파일들 확인
            renamed_files = [f for f in os.listdir(self.today_download_dir) 
                           if f.startswith(f"{self.carrier_name}_") and f.lower().endswith('.xlsx')]
            
            # 원본 파일들 확인 (아직 변경되지 않은 파일)
            original_files = [f for f in os.listdir(self.today_download_dir) 
                            if f.startswith("ScheduleByVessel_") and f.lower().endswith('.xlsx')]
            
            self.logger.info(f"파일명 변경 완료: {len(renamed_files)}개")
            self.logger.info(f"아직 변경되지 않은 파일: {len(original_files)}개")
            
            # 변경된 파일명들 로깅
            for renamed_file in renamed_files:
                self.logger.info(f"파일명 변경 완료: {renamed_file}")
            
            # 아직 변경되지 않은 파일이 있다면 경고
            if original_files:
                self.logger.warning(f"아직 파일명이 변경되지 않은 파일들: {original_files}")
                
                # 필요시 수동으로 파일명 변경 시도
                for original_file in original_files:
                    try:
                        # 파일명에서 날짜 정보 추출하여 임시 파일명 생성
                        old_path = os.path.join(self.today_download_dir, original_file)
                        temp_filename = f"{self.carrier_name}_UNKNOWN_{original_file}"
                        temp_path = os.path.join(self.today_download_dir, temp_filename)
                        
                        os.rename(old_path, temp_path)
                        self.logger.info(f"임시 파일명 변경: {original_file} → {temp_filename}")
                        
                    except Exception as e:
                        self.logger.error(f"임시 파일명 변경 실패 ({original_file}): {e}")
            
            # 파일명 변경 성공률 계산
            total_expected = len([f for f in os.listdir(self.today_download_dir) if f.lower().endswith('.xlsx')])
            renamed_count = len(renamed_files)
            success_rate = (renamed_count / total_expected) * 100 if total_expected > 0 else 0
            
            self.logger.info(f"파일명 변경 성공률: {success_rate:.1f}% ({renamed_count}/{total_expected})")
            
            self.logger.info("=== 3단계: 파일명 변경 확인 및 누락 파일 체크 완료 ===")
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== 3단계: 파일명 변경 확인 및 누락 파일 체크 실패 ===")
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
            
            # 3단계: 파일명 규칙 및 저장경로 규칙 적용
            if not self.step3_save_with_naming_rules():
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

    def wait_for_download_and_rename(self, vessel_full_name, timeout=30):
        """다운로드 완료 대기 및 즉시 파일명 변경"""
        try:
            start_time = time.time()
            renamed = False
            
            while time.time() - start_time < timeout:
                # 다운로드 디렉토리에서 가장 최근 Excel 파일 찾기
                excel_files = [f for f in os.listdir(self.today_download_dir) 
                             if f.startswith("ScheduleByVessel_") and f.lower().endswith('.xlsx')]
                
                if excel_files:
                    # 가장 최근 파일 선택 (수정 시간 기준)
                    latest_file = max(excel_files, key=lambda x: os.path.getmtime(os.path.join(self.today_download_dir, x)))
                    latest_path = os.path.join(self.today_download_dir, latest_file)
                    
                    # 파일명이 이미 변경되었는지 확인
                    if os.path.basename(latest_file).startswith(f"{self.carrier_name}_{vessel_full_name}"):
                        self.logger.info(f"선박 {vessel_full_name}: 파일명이 이미 올바르게 설정됨")
                        return True
                    
                    # 파일이 아직 다운로드 중인지 확인 (.crdownload, .tmp 파일)
                    if latest_file.endswith('.crdownload') or latest_file.endswith('.tmp'):
                        time.sleep(1)
                        continue
                    
                    # 새 파일명 생성 (특수문자 처리)
                    safe_vessel_name = vessel_full_name.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
                    new_filename = f"{self.carrier_name}_{safe_vessel_name}.xlsx"
                    new_filepath = os.path.join(self.today_download_dir, new_filename)
                    
                    # 기존 파일이 있으면 삭제
                    if os.path.exists(new_filepath):
                        os.remove(new_filepath)
                        self.logger.info(f"선박 {vessel_full_name}: 기존 파일 삭제됨")
                    
                    # 파일명 변경
                    try:
                        os.rename(latest_path, new_filepath)
                        self.logger.info(f"선박 {vessel_full_name}: 파일명 즉시 변경 완료 - {latest_file} → {new_filename}")
                        
                        renamed = True
                        break
                    except PermissionError:
                        # 파일이 사용 중인 경우 잠시 대기
                        self.logger.info(f"선박 {vessel_full_name}: 파일이 사용 중입니다. 잠시 대기...")
                        time.sleep(2)
                        continue
                    except Exception as e:
                        self.logger.error(f"선박 {vessel_full_name}: 파일명 변경 중 오류 - {str(e)}")
                        time.sleep(1)
                        continue
                
                time.sleep(1)
            
            if not renamed:
                self.logger.warning(f"선박 {vessel_full_name}: 파일명 변경 실패 - Excel 파일을 찾을 수 없음")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"선박 {vessel_full_name}: 파일명 변경 중 오류 발생 - {str(e)}")
            return False
