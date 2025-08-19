"""
크롤러 팩토리 클래스
크롤러 인스턴스 생성을 최적화하고 중복 생성을 방지합니다.
"""

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
        'ONE': ('one', 'ONE_Crawling'),
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
            return crawler_class()
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
    

