# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/06/28 (완성)
# 선사 링크 : https://www.one-line.com/en
# 선박 리스트 : ["ONE REASSURANCE" , "SAN FRANCISCO BRIDGE" ,"ONE MARVEL" , "MARIA C" , "NYK DANIELLA"]
# 추가 정보 : 크롤링 호출 잦을 시, 팝업 띄우고 경고함. 이런 경우는 10초 정도 기다렸다가 다시 돌릴 것.

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base import ParentsClass
import time
import os,re
import logging
import traceback

from datetime import datetime

class ONE_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()
        self.carrier_name = "ONE"
        
        # 로깅 설정
        self.setup_logging()
        
        # 선박 리스트
        self.vessel_name_list = ["MARIA C", "NYK DANIELLA","ONE REASSURANCE" ,"SAN FRANCISCO BRIDGE","ONE MARVEL"]
        
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

    # 선박별 파라미터 매핑 (URL에 맞게 조정)
    vessel_params = {
        "ONE REASSURANCE": {"vslCdParam": "RSCT", "vslEngNmParam": "ONE+REASSURANCE+%28RSCT%29"},
        "SAN FRANCISCO BRIDGE": {"vslCdParam": "SFDT", "vslEngNmParam": "SAN+FRANCISCO+BRIDGE+%28SFDT%29"},
        "ONE MARVEL": {"vslCdParam": "ONMT", "vslEngNmParam": "ONE+MARVEL+%28ONMT%29"},
        "MARIA C": {"vslCdParam": "RCMT", "vslEngNmParam": "MARIA+C+%28RCMT%29"},
        "NYK DANIELLA": {"vslCdParam": "NDLT", "vslEngNmParam": "NYK+DANIELLA+%28NDLT%29"}
    }

    def step1_visit_and_download(self):
        """1단계: 선박별 접속 후 PDF 다운로드"""
        try:
            self.logger.info("=== 1단계: 선박별 접속 및 PDF 다운로드 시작 ===")
            
            for vessel_name in self.vessel_name_list:
                try:
                    self.logger.info(f"선박 {vessel_name} 접속 및 다운로드 시작")
                    
                    # 0. 선사 접속 (동적 URL 생성)
                    params = self.vessel_params[vessel_name]
                    url = f"https://ecomm.one-line.com/one-ecom/schedule/vessel-schedule?vslCdParam={params['vslCdParam']}&vslEngNmParam={params['vslEngNmParam']}&f_cmd="
                    self.Visit_Link(url)
                    driver = self.driver
                    wait = self.wait
                    time.sleep(7)  # 초기 로딩 대기 시간

                    # 1. Download 버튼 클릭 (초기 버튼)
                    download_btn_xpath = wait.until(EC.element_to_be_clickable((
                        By.XPATH, '//*[@id="__next"]/main/div[2]/div[2]/div[7]/div[1]/div[3]/div/div[2]/button'
                    )))  # 
                    driver.execute_script("arguments[0].click();", download_btn_xpath)  # JS로 클릭
                    time.sleep(4)  # 모달 로딩 대기 시간

                    # 2. 모달 팝업 대기 및 Download 버튼 클릭
                    try:
                        # 모달이 나타날 때까지 대기
                        modal = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="headlessui-dialog-:ra:"]')))
                        self.logger.info(f"모달 팝업 감지됨 ({vessel_name})")

                        # PDF 라디오 버튼 클릭 (XPath는 상황에 따라 변수 처리 가능)
                        pdf_radio = wait.until(EC.element_to_be_clickable((
                            By.XPATH, '//*[@id="headlessui-dialog-:ra:"]/div[2]/div[2]/div[2]/label/div'
                        ))) # //*[@id="headlessui-dialog-:ra:"]/div[2]/div[2]/div[2]/label/div
                        # pdf_radio.click()
                        driver.execute_script("arguments[0].click();",pdf_radio)
                        self.logger.info("PDF 다운로드 옵션 선택 완료")
                        time.sleep(2)  # 대기 시간
                        
                        # 추가: 다운로드 범위 설정 (선택적)
                        try:
                            # 현재 페이지만 다운로드 옵션이 있다면 선택
                            current_page_option = driver.find_elements(By.XPATH, '//*[@id="headlessui-dialog-:ra:"]//label[contains(text(), "Current") or contains(text(), "현재")]')
                            if current_page_option:
                                driver.execute_script("arguments[0].click();", current_page_option[0])
                                self.logger.info("현재 페이지만 다운로드 옵션 선택")
                                time.sleep(1)
                        except Exception as e:
                            self.logger.info("현재 페이지 옵션을 찾을 수 없음, 기본 설정 사용")

                        download_pdf = wait.until(EC.element_to_be_clickable((
                            By.XPATH, '//*[@id="headlessui-dialog-:ra:"]/div[2]/div[3]/button[3]'
                        )))
                        driver.execute_script("arguments[0].scrollIntoView(true);", download_pdf)  # 요소를 화면에 보이게
                        driver.execute_script("arguments[0].click();", download_pdf)  # JS로 클릭
                        self.logger.info("PDF 다운로드 버튼 클릭 완료")
                    except Exception as e:
                        self.logger.error(f"모달 또는 Download 버튼 클릭 중 오류 발생 ({vessel_name}): {e}")

                    # 3. 다운로드 대기 - 더 오래 기다림
                    self.logger.info(f"PDF 다운로드 대기 중... ({vessel_name})")
                    time.sleep(15)  # 다운로드 대기 시간
                    
                    self.success_count += 1
                    self.logger.info(f"선박 {vessel_name} PDF 다운로드 완료")
                    
                except Exception as e:
                    self.logger.error(f"선박 {vessel_name} 접속 및 다운로드 실패: {str(e)}")
                    self.fail_count += 1
                    self.failed_vessels.append(vessel_name)
                    continue
            
            self.logger.info("=== 1단계: 선박별 접속 및 PDF 다운로드 완료 ===")
            self.logger.info(f"성공: {self.success_count}개, 실패: {self.fail_count}개")
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== 1단계: 선박별 접속 및 PDF 다운로드 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False

    def step2_apply_naming_rules(self):
        """2단계: 파일명 규칙 + 저장 경로 규칙 적용 (순서별 매핑)"""
        try:
            self.logger.info("=== 2단계: 파일명 규칙 및 저장경로 규칙 적용 시작 ===")
            
            # 전체 다운로드 완료 후 순서대로 매핑
            self.change_all_filenames_by_order()
            
            self.logger.info("=== 2단계: 파일명 규칙 및 저장경로 규칙 적용 완료 ===")
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== 2단계: 파일명 규칙 및 저장경로 규칙 적용 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False

    def change_all_filenames_by_order(self):
        """전체 파일을 순서대로 매핑하여 파일명 변경"""
        # 오늘 날짜 폴더
        target_dir = self.today_download_dir
        self.logger.info(f"대상 폴더: {target_dir}")
        
        # 폴더 내 모든 파일 확인
        all_files = os.listdir(target_dir)
        self.logger.info(f"폴더 내 모든 파일: {all_files}")
        
        # ONE의 다운로드 파일명 패턴 (예: ONE Vessel Schedule 250718.pdf 또는 20250718.pdf, (1) 넘버링 포함)
        today_str_6 = datetime.now().strftime("%y%m%d")
        today_str_8 = datetime.now().strftime("%Y%m%d")
        self.logger.info(f"오늘 날짜(6자리): {today_str_6}, 오늘 날짜(8자리): {today_str_8}")
        
        # 날짜를 YYMMDD 또는 YYYYMMDD 모두 허용하는 패턴
        pattern_exact = re.compile(rf"^ONE Vessel Schedule (?:{today_str_6}|{today_str_8})(\s?\(\d+\))?\.pdf$")
        pattern_loose = re.compile(rf"^ONE Vessel Schedule (?:{today_str_6}|{today_str_8}).*\.pdf$")
        
        # 폴더 내 파일 전체 중 위 패턴과 맞는 것 찾기 (생성 시간순 정렬)
        candidates = []
        for f in all_files:
            if pattern_exact.match(f) or pattern_loose.match(f):
                candidates.append(f)
                self.logger.info(f"패턴 매치 파일 발견: {f}")
        
        if not candidates:
            self.logger.warning(f"오늘자 ONE PDF 파일이 없습니다.")
            self.logger.info(f"시도한 패턴: 'ONE Vessel Schedule ' + {today_str_6} 또는 {today_str_8}")
            return
        
        # 생성 시간순으로 정렬 (가장 오래된 것부터)
        candidates = sorted(candidates, key=lambda f: os.path.getmtime(os.path.join(target_dir, f)))
        
        self.logger.info(f"발견된 PDF 파일들: {candidates}")
        self.logger.info(f"선박 리스트: {self.vessel_name_list}")
        
        # 파일 개수와 선박 개수가 일치하는지 확인
        if len(candidates) != len(self.vessel_name_list):
            self.logger.warning(f"PDF 파일 개수({len(candidates)})와 선박 개수({len(self.vessel_name_list)})가 일치하지 않습니다.")
            # 더 적은 쪽에 맞춰서 처리
            min_count = min(len(candidates), len(self.vessel_name_list))
            candidates = candidates[:min_count]
            vessel_list = self.vessel_name_list[:min_count]
        else:
            vessel_list = self.vessel_name_list
        
        self.logger.info(f"최종 매핑 대상:")
        for i, (file, vessel) in enumerate(zip(candidates, vessel_list)):
            self.logger.info(f"  [{i+1}] {file} → {vessel}")
        
        # 순서대로 매핑하여 파일명 변경
        for i, (old_filename, vessel_name) in enumerate(zip(candidates, vessel_list)):
            try:
                old_file = os.path.join(target_dir, old_filename)
                
                # 선박별 매핑을 위한 파일명 생성
                today_str = datetime.now().strftime("%y%m%d")
                vessel_safe_name = vessel_name.replace(" ", "_").replace("(", "").replace(")", "")
                new_filename = f"ONE_{vessel_safe_name}_{today_str}.pdf"
                
                # 이미 같은 이름의 파일이 있는지 확인하고 넘버링 처리
                base_name = new_filename.replace(".pdf", "")
                counter = 1
                final_filename = new_filename
                
                while os.path.exists(os.path.join(target_dir, final_filename)):
                    final_filename = f"{base_name}_{counter}.pdf"
                    counter += 1
                
                new_file = os.path.join(target_dir, final_filename)
                
                self.logger.info(f"파일명 변경 시도 [{i+1}]:")
                self.logger.info(f"  원본: {old_file}")
                self.logger.info(f"  대상: {new_file}")
                self.logger.info(f"  파일 존재 여부: {os.path.exists(old_file)}")
                
                # 안전: 목표 파일이 우연히 존재하면 삭제
                if os.path.exists(new_file):
                    os.remove(new_file)
                    self.logger.info(f"  기존 파일 삭제: {new_file}")

                os.rename(old_file, new_file)
                self.logger.info(f"파일명 변경 성공 [{i+1}]: {old_filename} → {final_filename}")
                self.logger.info(f"선박 매핑 성공 [{i+1}]: {vessel_name} → {final_filename}")
                
            except Exception as e:
                self.logger.error(f"파일명 변경 실패 [{i+1}]: {old_filename} → {vessel_name}, 오류: {str(e)}")
                self.logger.error(f"상세 에러: {traceback.format_exc()}")
                continue

    def change_filename(self, vessel_name):
        """파일명 변경 함수 (기존 호환성을 위해 유지)"""
        # 이 함수는 기존 호환성을 위해 유지하되, 실제로는 사용하지 않음
        self.logger.info(f"change_filename({vessel_name}) 호출됨 - 순서별 매핑 방식으로 변경됨")

    def run(self, vessel_name=None):
        """메인 실행 함수 (기존 호환성을 위해 vessel_name 파라미터 유지)"""
        return self.run_structured()

    def start_crawling(self):
        """기존 start_crawling 함수 (전체 선박용)"""
        # 선박 리스트 순회
        vessels = ["MARIA C", "NYK DANIELLA","ONE REASSURANCE" ,"SAN FRANCISCO BRIDGE","ONE MARVEL"] 
        for vessel in vessels:
            self.logger.info(f"크롤링 시작: {vessel}")
            self.run(vessel)
            self.change_filename(vessel)
            self.logger.info(f"크롤링 완료: {vessel}, 10초 대기...")
            time.sleep(10)  # 429 에러 방지 및 경고 팝업 대응
        
        self.Close()

    def run_structured(self):
        """구조화된 메인 실행 함수"""
        try:
            self.logger.info("=== ONE 크롤링 시작 ===")
            
            # 1단계: 선박별 접속 후 PDF 다운로드
            if not self.step1_visit_and_download():
                return False
            
            # 2단계: 파일명 규칙 + 저장 경로 규칙 적용
            if not self.step2_apply_naming_rules():
                return False
            
            # 최종 결과 로깅
            self.logger.info("=== ONE 크롤링 완료 ===")
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
            self.logger.error(f"=== ONE 크롤링 전체 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False