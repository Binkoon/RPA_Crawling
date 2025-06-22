# 여기서부터 시작함.
from Crawler import base
from Crawler import sitc


if __name__ == "__main__":
    print("Entry Point is Here")
    sitc_data = sitc.SITC_Crawling()
    sitc_data.run()