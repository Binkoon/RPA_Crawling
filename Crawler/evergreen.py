from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from .base import ParentsClass
import time

class EVERGREEN_Crawling(ParentsClass):
    def run(self):
        self.Visit_Link("https://ss.shipmentlink.com/tvs2/jsp/TVS2_VesselSchedule.jsp")
        driver = self.driver
        wait = self.wait  # 20초 대기

        # 선박명 드롭다운 선택
        vessel_dropdown = wait.until(EC.presence_of_element_located((
            By.ID, "vslCode"
        )))
        select = Select(vessel_dropdown)

        # "EVER LASTING" 선택
        try:
            select.select_by_visible_text("EVER LASTING")
            print("선박 'EVER LASTING' 선택 성공")
        except:
            print("선박 'EVER LASTING'을 드롭다운에서 찾을 수 없습니다. 사용 가능한 옵션 확인 필요.")
            # 드롭다운에 있는 옵션 출력 (디버깅용)
            options = [option.text for option in select.options]
            print("사용 가능한 옵션:", options)

        time.sleep(1)  # 선택 후 대기

        # Submit 버튼 클릭
        submit_button = wait.until(EC.element_to_be_clickable((
            By.ID, "submitButton"
        )))
        submit_button.click()
        print("Submit 버튼 클릭")

        # 페이지 로드 대기
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(2)  # 결과 로드 대기
        print("검색 완료")

        self.Close()