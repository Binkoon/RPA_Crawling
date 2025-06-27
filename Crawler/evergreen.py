# 선사링크 : https://ss.shipmentlink.com/tvs2/jsp/TVS2_VesselSchedule.jsp
# 선박 리스트 : ["EVER LUCID"]

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from .base import ParentsClass
import time

class EVERGREEN_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()
        
    def run(self):
        # 0. 사이트 방문
        self.Visit_Link("https://ss.shipmentlink.com/tvs2/jsp/TVS2_VesselSchedule.jsp")
        driver = self.driver
        wait = self.wait  # 20초 대기

        vessel_name_list = ["EVER LUCID"]

        for vessel_name in vessel_name_list:
            # 1. 드랍다운 선택
            vessel_select_elem = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="vslCode"]'))
            )
            vessel_select = Select(vessel_select_elem)

            # 2. 드랍다운 옵션 중에서 원하는 선박명 선택
            found = False
            for option in vessel_select.options:
                if vessel_name in option.text:
                    vessel_select.select_by_visible_text(option.text)
                    found = True
                    print(f"선박명 '{vessel_name}' 선택 완료")
                    break

            time.sleep(1)  # 선택 후 잠깐 대기 (필요시)

            # 3. submit 버튼 클릭
            submit_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="submitButton"]'))
            )
            submit_btn.click()
            print(f"Submit 버튼 클릭 완료")

            # 4. 결과 페이지 로딩 대기 (예: 테이블이 나타날 때까지)
            # 여기는 실제 결과 페이지 구조에 따라 수정 필요
            try:
                # 예시: 결과 테이블이 id="resultTable"로 있다고 가정
                wait.until(EC.presence_of_element_located((By.ID, "resultTable")))
                print(f"'{vessel_name}' 결과 로딩 완료")
            except Exception as e:
                print(f"결과 로딩 실패: {e}")

            # 5. 필요시 데이터 추출 및 저장 로직 추가
            # 예) table = driver.find_element(By.ID, "resultTable")
            #     ... 데이터 파싱 및 저장 ...

            # 6. 다음 선박명 조회를 위해 원래 페이지로 돌아가거나, 새로고침
            # driver.refresh()  # 필요시

            time.sleep(2)  # 다음 루프 전 잠깐 대기

        # 크롤링 종료 후 브라우저 닫기
        self.Close()

            
