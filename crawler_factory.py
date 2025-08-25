### 해당 코드 역할 요약 ###
# 실제 역할:
# - 선사명에 따른 크롤러 클래스 동적 로딩
# - 크롤러 인스턴스 생성
# - 모듈명과 클래스명 매핑 관리

# 하지 않는 것:
# - 크롤러 실행하지 않음
# - 데이터 파이프라인 관리하지 않음
# - base.py 직접 실행하지 않음

import importlib
from typing import Dict, Type, Any

class CrawlerFactory:
    """크롤러 인스턴스를 생성하고 관리하는 팩토리 클래스"""
    
    # 크롤러 클래스 정보 (모듈명: 클래스명)
    _crawler_classes = {
        'SITC': ('sitc', 'SITC_Crawling'),
        'EVERGREEN': ('evergreen', 'EVERGREEN_Crawling'),
        'COSCO': ('cosco', 'Cosco_Crawling'),
        'WANHAI': ('wanhai', 'WANHAI_Crawling'),
        'CKLINE': ('ckline', 'CKLINE_Crawling'),
        'PANOCEAN': ('panocean', 'PANOCEAN_Crawling'),
        'SNL': ('snl', 'SNL_Crawling'),
        'SMLINE': ('smline', 'SMLINE_Crawling'),
        'HMM': ('hmm', 'HMM_Crawling'),
        'FDT': ('fdt', 'FDT_Crawling'),
        'IAL': ('ial', 'IAL_Crawling'),
        'DYLINE': ('dyline', 'DYLINE_Crawling'),
        'YML': ('yml', 'YML_Crawling'),
        'NSS': ('nss', 'NSS_Crawling'),
        'ONE': ('one', 'ONE_Crawling')
    }
    
    @classmethod
    def create_crawler(cls, carrier_name: str) -> Any:
        """
        지정된 선사명에 해당하는 크롤러 인스턴스를 생성합니다.
        
        Args:
            carrier_name: 선사명 (예: 'SITC', 'EVERGREEN')
            
        Returns:
            크롤러 인스턴스
            
        Raises:
            ValueError: 알 수 없는 선사명인 경우
        """
        if carrier_name not in cls._crawler_classes:
            raise ValueError(f"Unknown carrier: {carrier_name}")
        
        try:
            module_name, class_name = cls._crawler_classes[carrier_name]
            module = importlib.import_module(f'crawler.{module_name}')
            crawler_class = getattr(module, class_name)
            
            # 크롤러 인스턴스 생성 (선박 리스트는 크롤러 자체에서 관리)
            crawler_instance = crawler_class()
            
            return crawler_instance
            
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Failed to create crawler for {carrier_name}: {str(e)}")
    
    @classmethod
    def get_all_carrier_names(cls) -> list:
        """모든 지원 선사명 목록을 반환합니다."""
        return list(cls._crawler_classes.keys())
    
    @classmethod
    def get_carrier_info(cls, carrier_name: str) -> dict:
        """지정된 선사의 정보를 반환합니다."""
        if carrier_name not in cls._crawler_classes:
            return None
        
        module_name, class_name = cls._crawler_classes[carrier_name]
        
        return {
            'name': carrier_name,
            'module': module_name,
            'class': class_name
        }
    
    @classmethod
    def is_supported_carrier(cls, carrier_name: str) -> bool:
        """지정된 선사가 지원되는지 확인합니다."""
        return carrier_name in cls._crawler_classes
    
    @classmethod
    def get_vessel_list(cls, carrier_name: str) -> list:
        """지정된 선사의 선박 리스트를 반환합니다."""
        try:
            crawler = cls.create_crawler(carrier_name)
            return getattr(crawler, 'vessel_name_list', []).copy()
        except Exception:
            return []
    
    @classmethod
    def get_total_vessel_count(cls) -> int:
        """모든 선사의 총 선박 수를 반환합니다."""
        total = 0
        for carrier_name in cls._crawler_classes.keys():
            try:
                vessel_list = cls.get_vessel_list(carrier_name)
                total += len(vessel_list)
            except Exception:
                continue
        return total
    
    @classmethod
    def print_vessel_summary(cls):
        """선사별 선박 수 요약을 출력합니다."""
        print("=== 선사별 선박 수 요약 ===")
        total_vessels = 0
        
        for carrier_name in sorted(cls._crawler_classes.keys()):
            try:
                vessel_list = cls.get_vessel_list(carrier_name)
                vessel_count = len(vessel_list)
                total_vessels += vessel_count
                print(f"{carrier_name}: {vessel_count}개")
            except Exception as e:
                print(f"{carrier_name}: 오류 발생 ({str(e)})")
        
        print(f"총 선박 수: {total_vessels}개")
        print("=" * 30)
    

