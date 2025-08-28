# Developer : 디지털전략팀/강현빈 사원
# Date : 2025/07/07 (완성)
# 선사 링크 : https://ebiz.pcsline.co.kr/
# 선박 리스트 : ["PEGASUS PETA","PEGASUS TERA","PEGASUS GLORY"]
# 추가 정보 : 스케줄 테이블 조회 시, 스크롤 액션 로직 넣어야함. EX) 실제 행은 10개있는데, <div class='table~~' ~~ > 이 clientHeight 값이 10개를 다 담지 못하고 있어서 눈에 보이는 row까지만 추출하고 멈춤.

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

import os
import time
import pandas as pd
import logging
import traceback

from .base import ParentsClass

class DYLINE_Crawling(ParentsClass):
    def __init__(self):
        super().__init__("DYLINE")
        self.carrier_name = "DYL"
        
        # 로깅 설정
        self.setup_logging()
        
        # 선박 리스트
        self.vessel_name_list = ["PEGASUS TERA","PEGASUS HOPE","PEGASUS PETA"]
        
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

    def step1_visit_website_and_navigate(self):
        """1단계: 선사 홈페이지 접속 후, 스케줄 탭 및 선박 탭 클릭"""
        try:
            self.logger.info("=== 1단계: 선사 홈페이지 접속 및 네비게이션 시작 ===")
            
            # 0. 선사 접속 링크
            self.Visit_Link("https://ebiz.pcsline.co.kr/")
            driver = self.driver
            wait = self.wait

            # 1. 스케줄 클릭
            scheduel_tab = wait.until(EC.element_to_be_clickable((
                By.XPATH , '//*[@id="mf_wfm_header_gen_firstGenerator_0_btn_menu1_Label"]'
            )))
            scheduel_tab.click()
            time.sleep(0.5)
            self.logger.info("스케줄 탭 클릭 완료")

            # 2. 선박별 클릭
            vessel_tab = wait.until(EC.element_to_be_clickable((
                By.XPATH , '//*[@id="mf_wfm_header_grp_ul"]/li[1]/dl/dd[2]/a'
            )))
            vessel_tab.click()
            time.sleep(0.5)
            self.logger.info("선박별 탭 클릭 완료")
            
            self.logger.info("=== 1단계: 선사 홈페이지 접속 및 네비게이션 완료 ===")
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== 1단계: 선사 홈페이지 접속 및 네비게이션 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False

    def step2_crawl_vessel_data(self):
        """2단계: 지정 선박 리스트 별로 반복 조회"""
        try:
            self.logger.info("=== 2단계: 선박별 데이터 크롤링 시작 ===")
            
            driver = self.driver
            wait = self.wait
            
            for vessel_name in self.vessel_name_list:
                try:
                    self.logger.info(f"선박 {vessel_name} 크롤링 시작")
                    
                    # 선박별 타이머 시작
                    self.start_vessel_tracking(vessel_name)
                    
                    all_rows = []
                    vessel_input = wait.until(EC.presence_of_element_located((
                        By.XPATH, '//*[@id="mf_tac_layout_contents_00010004_body_ibx_vsl_input"]'
                    )))
                    driver.execute_script("arguments[0].click();", vessel_input)
                    driver.execute_script("arguments[0].value = '';", vessel_input)
                    driver.execute_script(f"arguments[0].value = '{vessel_name}';", vessel_input)
                    driver.execute_script(
                        "var event = new Event('input', { bubbles: true }); arguments[0].dispatchEvent(event);",
                        vessel_input
                    )
                    time.sleep(1)
                    autocomplete_item = wait.until(EC.element_to_be_clickable((
                        By.XPATH, '//*[@id="mf_tac_layout_contents_00010004_body_ibx_vsl_itemTable_0"]'
                    )))
                    driver.execute_script("arguments[0].click();", autocomplete_item)
                    time.sleep(1)

                    index = 1
                    while True:
                        try:
                            voy_dropdown_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mf_tac_layout_contents_00010004_body_ibx_voy_button"]')))
                            driver.execute_script("arguments[0].click();", voy_dropdown_btn)
                            time.sleep(0.5)

                            tr_xpath = f'//*[@id="mf_tac_layout_contents_00010004_body_ibx_voy_itemTable_main"]/tbody/tr[{index}]'
                            voyage_tr = wait.until(EC.element_to_be_clickable((By.XPATH, tr_xpath)))
                            voyage_text = voyage_tr.text.strip()
                            voyage_tr.click()
                            time.sleep(0.5)

                            search_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mf_tac_layout_contents_00010004_body_btn_inq"]')))
                            search_btn.click()
                            time.sleep(1)

                            # 스크롤 없이 현재 보이는 tr만 추출
                            table_xpath = '//*[@id="mf_tac_layout_contents_00010004_body_grd_cur_body_table"]'
                            table_elem = wait.until(EC.presence_of_element_located((By.XPATH, table_xpath)))
                            tr_list = table_elem.find_elements(By.TAG_NAME, 'tr')
                            for tr in tr_list:
                                row_data = [td.text.strip() for td in tr.find_elements(By.TAG_NAME, 'td')]
                                row_data.append(voyage_text)
                                all_rows.append(row_data)

                            index += 1
                        except Exception:
                            break

                    if all_rows:
                        columns = ['No','Port','Skip','Terminal','ETA-Day','ETA-Date','ETA-Time','ETD-Day','ETD-Date','ETD-Time','Remark','Voy']
                        df = pd.DataFrame(all_rows, columns=columns)
                        save_path = self.get_save_path(self.carrier_name, vessel_name)
                        df.to_excel(save_path, index=False)
                        self.logger.info(f"엑셀 저장 완료: {save_path}")
                        
                        # 파일명은 이미 올바르게 저장됨
                        self.logger.info(f"선박 {vessel_name} 파일 저장 완료")
                        
                        # 성공 카운트는 end_vessel_tracking에서 자동 처리됨
                        
                        # 선박별 타이머 종료
                        self.end_vessel_tracking(vessel_name, success=True)
                        vessel_duration = self.get_vessel_duration(vessel_name)
                        self.logger.info(f"선박 {vessel_name} 크롤링 완료 (소요시간: {vessel_duration:.2f}초)")
                    else:
                        self.logger.warning(f"선박 {vessel_name}에 대한 데이터가 없습니다.")
                        # 실패한 경우에도 타이머 종료
                        self.end_vessel_tracking(vessel_name, success=False)
                        vessel_duration = self.get_vessel_duration(vessel_name)
                        self.logger.warning(f"선박 {vessel_name} 크롤링 실패 (소요시간: {vessel_duration:.2f}초)")
                        
                        # 실패한 선박 기록
                        if vessel_name not in self.failed_vessels:
                            self.failed_vessels.append(vessel_name)
                            self.failed_reasons[vessel_name] = "데이터 없음"
                    
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
            self.logger.info("=== DYLINE 크롤링 시작 ===")
            
            # 1단계: 선사 홈페이지 접속 및 네비게이션
            if not self.step1_visit_website_and_navigate():
                return False
            
            # 2단계: 지정된 선박별로 루핑 작업 시작
            if not self.step2_crawl_vessel_data():
                return False
            
            # 3단계: 파일명 규칙 및 저장경로 규칙 적용
            if not self.step3_save_with_naming_rules():
                return False
            
            # 최종 결과 로깅
            self.logger.info("=== DYLINE 크롤링 완료 ===")
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
            self.logger.error(f"=== DYLINE 크롤링 전체 실패 ===")
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
        
        self.logger.info(f"=== DYLINE 실패한 선박 재시도 시작 ===")
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
                
                # 1. 선박명 입력
                vessel_input = self.driver.find_element(By.ID, 'vessel')
                vessel_input.clear()
                vessel_input.send_keys(vessel_name)
                time.sleep(2)
                
                # 2. Search 버튼 클릭
                search_button = self.driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div/section/div/div[2]/div[2]/div[2]/button')
                search_button.click()
                time.sleep(4)
                
                # 3. 데이터 테이블 추출
                tbody_xpath = '//*[@id="app"]/div[1]/div/section/div/div[2]/div[2]/div[3]/table/tbody'
                row_idx = 1
                all_rows = []
                columns = ['Port', 'ETA', 'ETD']
                
                while True:
                    try:
                        row_xpath = f'{tbody_xpath}/tr[{row_idx}]'
                        row_elem = self.driver.find_element(By.XPATH, row_xpath)
                        cells = row_elem.find_elements(By.TAG_NAME, 'td')
                        row_data = [cell.text.strip() for cell in cells]
                        if row_data:
                            all_rows.append(row_data)
                        row_idx += 1
                    except Exception:
                        break
                
                # 4. DataFrame으로 저장 및 엑셀로 내보내기
                if all_rows:
                    df = pd.DataFrame(all_rows, columns=columns)
                    save_path = self.get_save_path(self.carrier_name, vessel_name)
                    df.to_excel(save_path, index=False)
                    self.logger.info(f"{vessel_name} 재시도 엑셀 저장 완료: {save_path}")
                    
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
                else:
                    self.logger.warning(f"{vessel_name} 재시도 시에도 데이터가 없음")
                    retry_fail_count += 1
                    self.end_vessel_tracking(vessel_name, success=True)
                    vessel_duration = self.get_vessel_duration(vessel_name)
                    self.logger.warning(f"선박 {vessel_name} 재시도 실패 (소요시간: {vessel_duration:.2f}초)")
                
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
        self.logger.info("DYLINE 재시도 결과 요약")
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
            'note': f'DYLINE 재시도 완료 - 성공: {retry_success_count}개, 실패: {retry_fail_count}개'
        }
