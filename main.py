# 여기서부터 시작함.
from Crawler import base
from Crawler import sitc
from Crawler import evergreen
from Crawler import cosco


if __name__ == "__main__":
    print("Entry Point is Here")
    sitc_data = sitc.SITC_Crawling()
    # evergreen_data = evergreen.EVERGREEN_Crawling()
    # cosco_data = cosco.Cosco_Crawling()

    sitc_data.run()
    # evergreen_data.run()
    # cosco_data.run()