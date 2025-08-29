# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/06/30 (완성) - 2025/07/14 (디버깅 완료)
# 선사 링크 : https://e-solution.yangming.com/e-service/Vessel_Tracking/SearchByVessel.aspx
# 선박 리스트 : ["YM CREDENTIAL" , "YM COOPERATION" ,"YM INITIATIVE"]

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import logging
import traceback

from .base import ParentsClass
import os,time
from datetime import datetime

import pandas as pd

# 쿠키 agree : /html/body/div/div/a
class YML_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()
        self.carrier_name = "YML"  # 선사명 정확히!
        # self.columns는 필요시 사용
        
        # 로깅 설정
        self.setup_logging()
        
        # 선박 리스트
        self.vessel_name_list = ["YM CREDENTIAL", "YM COOPERATION", "YM INITIATIVE"]
        
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
            
            driver = self.driver
            wait = self.wait

            columns = ["Port", "Terminal", "ETA", "ETA-Status", "ETB", "ETB-Status", "ETD", "ETD-Status", "Voy"]

            for vessel_name in self.vessel_name_list:
                try:
                    self.logger.info(f"선박 {vessel_name} 접속 시작")
                    
                    # 선박별 타이머 시작
                    self.start_vessel_timer(vessel_name)
                    
                    vessel_name_param = vessel_name.replace(" ", "%20")
                    vessel_code = {
                        "YM CREDENTIAL": "YCDL",
                        "YM COOPERATION": "YCPR",
                        "YM INITIATIVE": "YINT"
                    }[vessel_name]
                    url = f'https://e-solution.yangming.com/e-service/Vessel_Tracking/vessel_tracking_detail.aspx?vessel={vessel_name_param}|{vessel_code}&&func=current&&LocalSite='
                    self.Visit_Link(url)
                    time.sleep(2)

                    # 쿠키 팝업 있으면 클릭
                    try:
                        cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/a')))
                        cookie_button.click()
                        self.logger.info("쿠키 팝업 클릭 완료")
                    except Exception:
                        pass
                    
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

    def step2_crawl_vessel_data(self):
        """2단계: 지정된 선박별로 루핑 작업 시작"""
        try:
            self.logger.info("=== 2단계: 선박별 데이터 크롤링 시작 ===")
            
            driver = self.driver
            wait = self.wait

            columns = ["Port", "Terminal", "ETA", "ETA-Status", "ETB", "ETB-Status", "ETD", "ETD-Status", "Voy"]

            for vessel_name in self.vessel_name_list:
                try:
                    self.logger.info(f"선박 {vessel_name} 크롤링 시작")
                    
                    # 선박별 타이머 시작
                    self.start_vessel_timer(vessel_name)
                    
                    vessel_name_param = vessel_name.replace(" ", "%20")
                    vessel_code = {
                        "YM CREDENTIAL": "YCDL",
                        "YM COOPERATION": "YCPR",
                        "YM INITIATIVE": "YINT"
                    }[vessel_name]
                    url = f'https://e-solution.yangming.com/e-service/Vessel_Tracking/vessel_tracking_detail.aspx?vessel={vessel_name_param}|{vessel_code}&&func=current&&LocalSite='
                    self.Visit_Link(url)
                    time.sleep(2)

                    # 쿠키 팝업 있으면 클릭
                    try:
                        cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/a')))
                        cookie_button.click()
                        self.logger.info("쿠키 팝업 클릭 완료")
                    except Exception:
                        pass

                    # 항차번호 추출 //*[@id="ContentPlaceHolder1_lblComn"]
                    try:
                        voyage_no_elem = wait.until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="ContentPlaceHolder1_lblComn"]'))
                        )
                        voyage_no = voyage_no_elem.text.strip()
                    except Exception:
                        voyage_no = ""
                        self.logger.warning("항차번호 추출 실패")

                    # 스크롤 Y 100px 내리기
                    driver.execute_script("window.scrollBy(0, 100);")
                    time.sleep(0.5)

                    all_rows = []
                    row_idx = 1
                    while True:
                        xpath = f'//*[@id="ContentPlaceHolder1_gvLast"]/tbody/tr[{row_idx}]'
                        try:
                            tr = driver.find_element(By.XPATH, xpath)
                            tds = tr.find_elements(By.TAG_NAME, "td")
                            row = [td.text.strip() for td in tds]  # TD 개수 제한 없이 전체 긁어오기
                            all_rows.append(row)
                            row_idx += 1
                        except Exception:
                            break

                    # 스크롤 Y 100px 올리기
                    driver.execute_script("window.scrollBy(0, -100);")
                    time.sleep(0.5)

                    # 다음 버튼 클릭
                    try:
                        next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ContentPlaceHolder1_btnNext"]')))
                        next_btn.click()
                        time.sleep(1.5)
                    except Exception:
                        self.logger.warning("다음 페이지 버튼 없음 또는 클릭 실패")

                    # 두 번째 페이지 데이터도 추가로 긁어서 같은 리스트에 저장
                    row_idx = 1
                    while True:
                        xpath = f'//*[@id="ContentPlaceHolder1_gvLast"]/tbody/tr[{row_idx}]'
                        try:
                            tr = driver.find_element(By.XPATH, xpath)
                            tds = tr.find_elements(By.TAG_NAME, "td")
                            row = [td.text.strip() for td in tds]
                            all_rows.append(row)
                            row_idx += 1
                        except Exception:
                            break

                    # DataFrame으로 저장 (columns 없이 저장)
                    df = pd.DataFrame(all_rows)

                    # Port/Terminal/ETA/ETA-Status/ETB/ETB-Status/ETD/ETD-Status 열만 남기고, Voy 칼럼 오른쪽에 추가
                    try:
                        df.drop(columns=[0, 2], inplace=True)
                    except Exception:
                        self.logger.warning("DataFrame drop 실패 - 인덱스를 확인하세요.")
                    df.columns = columns[:-1]
                    df["Voy"] = voyage_no  # 맨 오른쪽 Voy 칼럼

                    save_path = self.get_save_path(self.carrier_name, vessel_name)
                    df.to_excel(save_path, index=False, header=True)
                    self.logger.info(f"[{vessel_name}] 테이블 원본 저장 완료: {save_path}")
                    time.sleep(1)
                    self.record_vessel_success(vessel_name)
                    
                    # 선박별 타이머 종료
                    vessel_duration = self.end_vessel_timer(vessel_name)
                    self.logger.info(f"선박 {vessel_name} 크롤링 완료 (소요시간: {vessel_duration:.2f}초)")
                    
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
            self.logger.info("=== YML 크롤링 시작 ===")
            
            # 1단계: 지정된 선박별로 url param값만 변경하는 식으로 선사 홈페이지 접속
            if not self.step1_visit_website_with_vessel_params():
                return False
            
            # 2단계: 지정된 선박별로 루핑 작업 시작
            if not self.step2_crawl_vessel_data():
                return False
            
            # 최종 결과 로깅
            self.logger.info("=== YML 크롤링 완료 ===")
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
            self.logger.error(f"=== YML 크롤링 전체 실패 ===")
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
        
        self.logger.info(f"=== YML 실패한 선박 재시도 시작 ===")
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
                
                # 1. 선박별 URL 접속
                vessel_url = f"https://www.yangming.com/e-service/Vessel_Schedule/Vessel_Schedule.aspx?vessel={vessel_name}"
                self.Visit_Link(vessel_url)
                time.sleep(3)
                
                # 2. 데이터 테이블 추출
                all_rows = []
                columns = ['Port', 'Terminal', 'ETA', 'ETA-Status', 'ETB', 'ETB-Status', 'ETD', 'ETD-Status', 'Voy']
                
                # 첫 번째 페이지 데이터 추출
                row_idx = 1
                while True:
                    xpath = f'//*[@id="ContentPlaceHolder1_gvLast"]/tbody/tr[{row_idx}]'
                    try:
                        tr = self.driver.find_element(By.XPATH, xpath)
                        tds = tr.find_elements(By.TAG_NAME, "td")
                        row = [td.text.strip() for td in tds]
                        all_rows.append(row)
                        row_idx += 1
                    except Exception:
                        break
                
                # 3. DataFrame으로 저장 및 엑셀로 내보내기
                if all_rows:
                    df = pd.DataFrame(all_rows)
                    
                    # Port/Terminal/ETA/ETA-Status/ETB/ETB-Status/ETD/ETD-Status 열만 남기고, Voy 칼럼 오른쪽에 추가
                    try:
                        df.drop(columns=[0, 2], inplace=True)
                    except Exception:
                        self.logger.warning("DataFrame drop 실패 - 인덱스를 확인하세요.")
                    df.columns = columns[:-1]
                    df["Voy"] = vessel_name  # 맨 오른쪽 Voy 칼럼
                    
                    save_path = self.get_save_path(self.carrier_name, vessel_name)
                    df.to_excel(save_path, index=False, header=True)
                    self.logger.info(f"{vessel_name} 재시도 테이블 원본 저장 완료: {save_path}")
                    
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
                
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"선박 {vessel_name} 재시도 실패: {str(e)}")
                retry_fail_count += 1
                
                # 실패한 경우에도 타이머 종료
                vessel_duration = self.end_vessel_timer(vessel_name)
                self.logger.error(f"선박 {vessel_name} 재시도 실패 (소요시간: {vessel_duration:.2f}초)")
                continue
        
        # 재시도 결과 요약
        self.logger.info("="*60)
        self.logger.info("YML 재시도 결과 요약")
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
            'note': f'YML 재시도 완료 - 성공: {retry_success_count}개, 실패: {retry_fail_count}개'
        }