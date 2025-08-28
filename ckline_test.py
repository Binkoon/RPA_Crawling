# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/06/30 (완성)
# 선사 링크 : https://es.ckline.co.kr/
# 선박 리스트 : 
"""
["SKY MOON" , "SKY FLOWER" , "SKY JADE" , "SKY TIARA" , "SUNWIN" , "SKY VICTORIA" , "VICTORY STAR", 
"SKY IRIS" , "SKY SUNSHINE" , "SKY RAINBOW" , "BAL BOAN" , "SKY CHALLENGE" ,"XIN TAI PING" , "SKY ORION"]
"""

# 추가 정보 : 선박이 꽤 많음. 다운로드 받다가 파일명 ReName에서 가끔 꼬일때가 있음. 수정 필요

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# from .base import ParentsClass
from crawler.base import ParentsClass
import time,os
from datetime import datetime
import re
import pandas as pd
import logging
import traceback

class CKLINE_Crawling(ParentsClass):
    def __init__(self):
        super().__init__("CKLINE")
        self.carrier_name = "CKL"
        
        # 로깅 설정
        self.setup_logging()
        
        # 선박 리스트
        self.vessel_name_list = ["SKY MOON", "SKY FLOWER" , "SKY JADE" , "SKY TIARA" , "SUNWIN" , "SKY VICTORIA" , "VICTORY STAR", 
                                "SKY IRIS" , "SKY SUNSHINE" , "SKY RAINBOW" , "BAL BOAN" , "SKY CHALLENGE" ,"XIN TAI PING" , "SKY ORION"]
        
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

    def step1_visit_website_and_handle_popup(self):
        """1단계: 웹사이트 방문 및 팝업 처리"""
        try:
            self.logger.info("=== 1단계: 웹사이트 방문 및 팝업 처리 시작 ===")
            
            # 0. 웹사이트 방문
            self.Visit_Link("https://es.ckline.co.kr/")
            driver = self.driver
            wait = self.wait

            # 1. 로딩 화면 대기
            wait.until(EC.invisibility_of_element_located((By.ID, "mf_grp_loading")))

            # 2. 팝업 닫기 (팝업이 있는 경우) /html/body/div[2]/div[4]/div/div[2]/a/span[2]
            try:
                pop_up_close = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mf_btn_noti"]')))
                pop_up_close.click()
                self.logger.info("팝업 닫기 완료")
            except Exception as e:
                self.logger.info("팝업이 없거나 이미 닫혀있음")

            # 3. 스케줄 메뉴 클릭
            menu1 = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[1]/div[2]/div/div/ul/li[1]')))
            menu1.click()
            time.sleep(0.5)  # 하위 메뉴 표시 대기

            # 4. 선박 메뉴 클릭
            submenu = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[1]/div[2]/div/div/ul/li[1]/ul/li[2]')))
            submenu.click()
            self.logger.info("메뉴 클릭 완료!")
            time.sleep(1)  # 페이지 로드 대기 시간 증가
            
            self.logger.info("=== 1단계: 웹사이트 방문 및 팝업 처리 완료 ===")
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== 1단계: 선사 홈페이지 접속 및 팝업 처리 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False

    def step2_crawl_vessel_data(self):
        """2단계: 선박별 데이터 크롤링 (즉시 파일명 변경 포함)"""
        try:
            self.logger.info("=== 2단계: 선박별 데이터 크롤링 시작 ===")
            
            driver = self.driver
            wait = self.wait
            
            for vessel_name in self.vessel_name_list:
                try:
                    self.logger.info(f"선박 {vessel_name} 크롤링 시작")
                    
                    # 선박별 타이머 시작
                    self.start_vessel_tracking(vessel_name)
                    
                    # 1. 드롭다운(입력창) 클릭해서 리스트 활성화
                    vessel_div = driver.find_element(By.ID, 'mf_wfm_intro_tac_layout_contents_WESSCH002_body_sbx_vessel_button')
                    vessel_div.click()
                    time.sleep(0.5)

                    # 2. 자동완성 리스트에서 tr 순회하며 클릭
                    idx = 1
                    found = False
                    while True:
                        try:
                            row_xpath = f'//*[@id="mf_wfm_intro_tac_layout_contents_WESSCH002_body_sbx_vessel_itemTable_main"]/tbody/tr[{idx}]'
                            row_elem = driver.find_element(By.XPATH, row_xpath)
                            td_elem = row_elem.find_element(By.TAG_NAME, 'td')
                            vessel_text = td_elem.text.strip()
                            if vessel_text == vessel_name:
                                td_elem.click()
                                self.logger.info(f"{vessel_name} 선택 완료 (index: {idx})")
                                found = True
                                break
                            idx += 1
                        except Exception:
                            break  # 더 이상 tr이 없으면 종료
                    
                    if not found:
                        self.logger.warning(f"{vessel_name} 자동완성 리스트에서 찾을 수 없음")
                        
                        # 실패한 경우에도 타이머 종료
                        self.end_vessel_tracking(vessel_name, success=False)
                        vessel_duration = self.get_vessel_duration(vessel_name)
                        self.logger.warning(f"선박 {vessel_name} 크롤링 실패 (소요시간: {vessel_duration:.2f}초)")
                        
                        # 실패한 선박 기록
                        if vessel_name not in self.failed_vessels:
                            self.failed_vessels.append(vessel_name)
                            self.failed_reasons[vessel_name] = "자동완성 리스트에서 해당 선박을 찾을 수 없음"
                        
                        continue
                    
                    time.sleep(1)  # 선택 후 대기

                    # 조회 버튼 클릭
                    search_btn = wait.until(EC.element_to_be_clickable((
                        By.XPATH , '//*[@id="mf_wfm_intro_tac_layout_contents_WESSCH002_body_btn_inquiry"]'
                    )))
                    search_btn.click()
                    time.sleep(1)

                    # 다운로드 버튼 클릭
                    download_btn = wait.until(EC.element_to_be_clickable((
                        By.XPATH ,'//*[@id="mf_wfm_intro_tac_layout_contents_WESSCH002_body_btn_trigger2"]'
                    )))
                    download_btn.click()
                    
                    # 다운로드 완료 대기
                    if self.wait_for_download():
                        # 즉시 파일명 변경 (다른 선박과 겹치지 않도록)
                        if self.rename_downloaded_file_immediately(vessel_name):
                            self.logger.info(f"선박 {vessel_name} 파일명 즉시 변경 완료")
                        else:
                            self.logger.warning(f"선박 {vessel_name} 파일명 변경 실패")
                    else:
                        self.logger.warning(f"선박 {vessel_name} 다운로드 대기 시간 초과")
                    
                    # 선박별 타이머 종료
                    self.end_vessel_tracking(vessel_name, success=True)
                    vessel_duration = self.get_vessel_duration(vessel_name)
                    self.logger.info(f"선박 {vessel_name} 크롤링 완료 (소요시간: {vessel_duration:.2f}초)")
                    
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

    def wait_for_download(self, timeout=30):
        """다운로드 완료 대기"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            files = os.listdir(self.today_download_dir)
            downloading = [f for f in files if f.endswith('.crdownload') or f.endswith('.tmp')]
            if not downloading:
                return True
            time.sleep(1)
        return False

    def rename_downloaded_file_immediately(self, vessel_name):
        """다운로드된 파일을 즉시 선박명으로 변경 (파일 내용 기반 정확한 매칭)"""
        try:
            # 1. 가장 최근에 다운로드된 Vessel*.xlsx 파일 찾기
            files = [f for f in os.listdir(self.today_download_dir)
                    if f.startswith("Vessel") and f.lower().endswith('.xlsx')]
            
            if not files:
                self.logger.warning(f"다운로드된 Vessel*.xlsx 파일을 찾을 수 없음")
                return False
            
            # 2. 각 파일의 내용을 확인하여 정확한 선박명 매칭
            for file in files:
                file_path = os.path.join(self.today_download_dir, file)
                try:
                    df = pd.read_excel(file_path)
                    
                    # 파일 내용에서 선박명 추출
                    if 'undefined' in df.columns:
                        vessel_col = 'undefined'
                    elif 'Vessel Name' in df.columns:
                        vessel_col = 'Vessel Name'
                    else:
                        continue
                    
                    if not df.empty and vessel_col in df.columns:
                        first_vessel = df.iloc[0][vessel_col]
                        if isinstance(first_vessel, str):
                            # "SKY IRIS ABC123" -> "SKY IRIS" 형태로 추출
                            vessel_parts = first_vessel.split()
                            if len(vessel_parts) >= 2:
                                vessel_name_from_file = f"{vessel_parts[0]} {vessel_parts[1]}"
                            else:
                                vessel_name_from_file = first_vessel
                            
                            # 정확한 매칭 확인
                            if vessel_name == vessel_name_from_file:
                                # 파일명 변경
                                old_path = os.path.join(self.today_download_dir, file)
                                new_filename = f"{self.carrier_name}_{vessel_name}.xlsx"
                                new_path = os.path.join(self.today_download_dir, new_filename)
                                
                                # 이미 같은 이름의 파일이 있다면 삭제
                                if os.path.exists(new_path):
                                    os.remove(new_path)
                                    self.logger.info(f"기존 파일 {new_filename} 삭제")
                                
                                os.rename(old_path, new_path)
                                self.logger.info(f"즉시 파일명 변경: {file} → {new_filename}")
                                return True
                                
                except Exception as e:
                    self.logger.error(f"파일 {file} 읽기 실패: {e}")
                    continue
            
            self.logger.warning(f"선박 {vessel_name}에 해당하는 파일을 찾을 수 없음")
            return False
            
        except Exception as e:
            self.logger.error(f"파일명 즉시 변경 실패: {e}")
            return False

    def step3_process_downloaded_files(self):
        """3단계: 다운로드된 파일 처리 및 엑셀 생성 (파일명 변경은 이미 완료됨)"""
        try:
            self.logger.info("=== 3단계: 다운로드된 파일 처리 및 엑셀 생성 시작 ===")
            
            # 파일명 변경은 이미 step2에서 완료되었으므로, 전처리만 진행

            # 3. 파일명 변경 후 전처리
            for vessel_name in self.vessel_name_list:
                fpath = os.path.join(self.today_download_dir, f"{self.carrier_name}_{vessel_name}.xlsx")
                if os.path.exists(fpath):
                    try:
                        df = pd.read_excel(fpath)
                        # 1. 'undefined' 컬럼명을 'Vessel Name'으로 변경
                        if 'undefined' in df.columns:
                            df.rename(columns={'undefined': 'Vessel Name'}, inplace=True)
                        # 2. 선박명/항차번호 분리 (첫 컬럼)
                        if 'Vessel Name' in df.columns:
                            split_df = df['Vessel Name'].str.extract(r'(?P<Vessel_Name>[A-Z\s]+)\s+(?P<D_Voy>[A-Z0-9.\-]+)')
                            df['Vessel Name'] = split_df['Vessel_Name']
                            df.insert(1, 'D-Voy', split_df['D_Voy'])

                        # 3. 컬럼명 한글 → 영문 변경
                        col_map = {
                            '지역': 'Port',
                            '입항일': 'ETA',
                            '출항일': 'ETD'
                        }
                        df.rename(columns=col_map, inplace=True)

                        # 4. 컬럼 순서 재정렬
                        desired_cols = ['Vessel Name', 'D-Voy', 'Port', 'ETA', 'ETD']
                        rest_cols = [col for col in df.columns if col not in desired_cols]
                        final_cols = desired_cols + rest_cols
                        df = df[final_cols]

                        # 5. 전처리된 파일로 덮어쓰기
                        df.to_excel(fpath, index=False)
                        self.logger.info(f"전처리 및 컬럼명 변경 완료: {os.path.basename(fpath)}")
                    except Exception as e:
                        self.logger.error(f"전처리 중 오류({vessel_name}): {e}")
            
            self.logger.info("=== 3단계: 다운로드된 파일 처리 및 엑셀 생성 완료 ===")
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== 3단계: 다운로드된 파일 처리 및 엑셀 생성 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False

    def run(self):
        """메인 실행 함수"""
        try:
            self.logger.info("=== CKLINE 크롤링 시작 ===")
            
            # 1단계: 웹사이트 방문 및 팝업 처리
            if not self.step1_visit_website_and_handle_popup():
                return False
            
            # 2단계: 선박별 데이터 크롤링
            if not self.step2_crawl_vessel_data():
                return False
            
            # 3단계: 다운로드된 파일 처리 및 엑셀 생성
            if not self.step3_process_downloaded_files():
                return False
            
            # 최종 결과 로깅
            self.logger.info("=== CKLINE 크롤링 완료 ===")
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
            self.logger.error(f"=== CKLINE 크롤링 전체 실패 ===")
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
        
        self.logger.info(f"=== CKLINE 실패한 선박 재시도 시작 ===")
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
                
                # 1. 드롭다운(입력창) 클릭해서 리스트 활성화
                vessel_div = self.driver.find_element(By.ID, 'mf_wfm_intro_tac_layout_contents_WESSCH002_body_sbx_vessel_button')
                vessel_div.click()
                time.sleep(1)
                
                # 2. 자동완성 리스트에서 해당 선박 찾기
                vessel_found = False
                for idx in range(1, 21):  # 최대 20개 항목 확인
                    try:
                        row_xpath = f'//*[@id="mf_wfm_intro_tac_layout_contents_WESSCH002_body_sbx_vessel_itemTable_main"]/tbody/tr[{idx}]'
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
                
                time.sleep(2)
                
                # 3. 조회 버튼 클릭
                search_btn = self.wait.until(EC.element_to_be_clickable((
                    By.XPATH, '//*[@id="mf_wfm_intro_tac_layout_contents_WESSCH002_body_btn_inquiry"]'
                )))
                search_btn.click()
                time.sleep(2)
                
                # 4. 다운로드 버튼 클릭
                download_btn = self.wait.until(EC.element_to_be_clickable((
                    By.XPATH, '//*[@id="mf_wfm_intro_tac_layout_contents_WESSCH002_body_btn_trigger2"]'
                )))
                download_btn.click()
                time.sleep(2)
                
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
                self.end_vessel_tracking(vessel_name, success=False)
                vessel_duration = self.get_vessel_duration(vessel_name)
                self.logger.error(f"선박 {vessel_name} 재시도 실패 (소요시간: {vessel_duration:.2f}초)")
                continue
        
        # 재시도 결과 요약
        self.logger.info("="*60)
        self.logger.info("CKLINE 재시도 결과 요약")
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
            'note': f'CKLINE 재시도 완료 - 성공: {retry_success_count}개, 실패: {retry_fail_count}개'
        }

if __name__ == "__main__":
    # 테스트 실행 코드
    crawler = CKLINE_Crawling()
    crawler.run()