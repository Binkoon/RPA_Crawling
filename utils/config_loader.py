# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/08/21
# 역할 : 설정 파일 로드 공통 모듈

import os
import json

def load_carriers_config():
    """선사 설정 파일을 로드합니다."""
    try:
        config_path = os.path.join(os.getcwd(), 'config', 'carriers.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"설정 파일 로드 실패: {str(e)}")
        # 기본값 반환
        return {"carriers": []}

def load_execution_config():
    """실행 모드 설정 파일을 로드합니다."""
    try:
        config_path = os.path.join(os.getcwd(), 'config', 'execution_mode.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"실행 모드 설정 파일 로드 실패: {str(e)}")
        # 기본값 반환
        return {
            "execution": {
                "mode": "parallel",
                "max_workers": 2
            },
            "logging": {
                "level": "INFO",
                "save_excel": True,
                "upload_to_drive": True
            },
            "cleanup": {
                "enabled": True,
                "days_to_keep": 30,
                "cleanup_errorlogs": True,
                "cleanup_scheduledata": True
            }
        }

def get_carriers_to_run():
    """실행할 선사 목록을 반환합니다."""
    carriers_config = load_carriers_config()
    carriers_to_run = []
    
    for carrier_info in carriers_config['carriers']:
        carrier_name = carrier_info['name']
        carriers_to_run.append(carrier_name)
    
    return carriers_to_run
