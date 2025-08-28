# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/08/21
# 역할 : 설정 파일 로드 공통 모듈 (향상된 버전)

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import yaml

class Environment(Enum):
    """환경 타입"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

@dataclass
class DatabaseConfig:
    """데이터베이스 설정"""
    host: str = "localhost"
    port: int = 5432
    database: str = "rpa_crawling"
    username: str = ""
    password: str = ""
    
    def validate(self) -> List[str]:
        """설정 검증"""
        errors = []
        if not self.host:
            errors.append("데이터베이스 호스트가 설정되지 않았습니다")
        if not self.database:
            errors.append("데이터베이스 이름이 설정되지 않았습니다")
        return errors

@dataclass
class LoggingConfig:
    """로깅 설정"""
    level: str = "INFO"
    save_excel: bool = True
    upload_to_drive: bool = True
    log_rotation: bool = True
    max_log_size: int = 10  # MB
    backup_count: int = 5
    
    def validate(self) -> List[str]:
        """설정 검증"""
        errors = []
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.level not in valid_levels:
            errors.append(f"잘못된 로깅 레벨: {self.level}. 유효한 값: {valid_levels}")
        if self.max_log_size <= 0:
            errors.append("최대 로그 크기는 0보다 커야 합니다")
        if self.backup_count < 0:
            errors.append("백업 개수는 0 이상이어야 합니다")
        return errors

@dataclass
class CleanupConfig:
    """정리 설정"""
    enabled: bool = True
    days_to_keep: int = 30
    cleanup_errorlogs: bool = True
    cleanup_scheduledata: bool = True
    cleanup_temp_files: bool = True
    max_file_size: int = 100  # MB
    
    def validate(self) -> List[str]:
        """설정 검증"""
        errors = []
        if self.days_to_keep <= 0:
            errors.append("보관 일수는 0보다 커야 합니다")
        if self.max_file_size <= 0:
            errors.append("최대 파일 크기는 0보다 커야 합니다")
        return errors

@dataclass
class ExecutionConfig:
    """실행 설정"""
    mode: str = "sequential"  # sequential only
    
    timeout: int = 300  # 초
    retry_on_failure: bool = True
    max_retries: int = 1
    delay_between_requests: float = 1.0  # 초
    
    def validate(self) -> List[str]:
        """설정 검증"""
        errors = []
        valid_modes = ["sequential"]
        if self.mode not in valid_modes:
            errors.append(f"잘못된 실행 모드: {self.mode}. 유효한 값: {valid_modes}")

        if self.timeout <= 0:
            errors.append("타임아웃은 0보다 커야 합니다")
        if self.max_retries < 0:
            errors.append("최대 재시도 횟수는 0 이상이어야 합니다")
        if self.delay_between_requests < 0:
            errors.append("요청 간 지연은 0 이상이어야 합니다")
        return errors

@dataclass
class GoogleDriveConfig:
    """구글 드라이브 설정"""
    shared_folder_id: str = ""
    upload_enabled: bool = True
    create_backup: bool = True
    max_file_size: int = 100  # MB
    
    def validate(self) -> List[str]:
        """설정 검증"""
        errors = []
        if self.upload_enabled and not self.shared_folder_id:
            errors.append("구글 드라이브 업로드가 활성화되었지만 공유 폴더 ID가 설정되지 않았습니다")
        if self.max_file_size <= 0:
            errors.append("최대 파일 크기는 0보다 커야 합니다")
        return errors

@dataclass
class SystemConfig:
    """전체 시스템 설정"""
    environment: Environment = Environment.DEVELOPMENT
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    cleanup: CleanupConfig = field(default_factory=CleanupConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    google_drive: GoogleDriveConfig = field(default_factory=GoogleDriveConfig)
    
    def validate(self) -> List[str]:
        """전체 설정 검증"""
        errors = []
        errors.extend(self.database.validate())
        errors.extend(self.logging.validate())
        errors.extend(self.cleanup.validate())
        errors.extend(self.execution.validate())
        errors.extend(self.google_drive.validate())
        return errors

class ConfigManager:
    """설정 관리자"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.config: Optional[SystemConfig] = None
        self._config_cache = {}
        self._last_modified = {}
        self.logger = logging.getLogger(__name__)
        
    def get_environment(self) -> Environment:
        """현재 환경을 감지합니다."""
        env = os.getenv('RPA_ENVIRONMENT', '').lower()
        if env == 'production':
            return Environment.PRODUCTION
        elif env == 'testing':
            return Environment.TESTING
        else:
            return Environment.DEVELOPMENT
    
    def load_config(self, force_reload: bool = False) -> SystemConfig:
        """설정을 로드합니다."""
        if not force_reload and self.config is not None:
            return self.config
            
        try:
            # 환경별 설정 파일 로드
            env = self.get_environment()
            config = self._load_environment_config(env)
            
            # 환경변수로 오버라이드
            self._override_with_env_vars(config)
            
            # 설정 검증
            errors = config.validate()
            if errors:
                self.logger.warning("설정 검증 경고:")
                for error in errors:
                    self.logger.warning(f"  - {error}")
                self.logger.info("기본값을 사용합니다.")
            
            self.config = config
            self.logger.info(f"설정 로드 완료 (환경: {env.value})")
            return config
            
        except Exception as e:
            self.logger.error(f"설정 로드 실패: {str(e)}")
            self.logger.info("기본 설정을 사용합니다.")
            return self._get_default_config()
    
    def _load_environment_config(self, env: Environment) -> SystemConfig:
        """환경별 설정 파일을 로드합니다."""
        config_files = [
            f"config_{env.value}.yaml",
            f"config_{env.value}.json",
            "config.yaml",
            "config.json"
        ]
        
        config = self._get_default_config()
        
        for config_file in config_files:
            config_path = os.path.join(self.config_dir, config_file)
            if os.path.exists(config_path):
                try:
                    if config_file.endswith('.yaml'):
                        with open(config_path, 'r', encoding='utf-8') as f:
                            env_config = yaml.safe_load(f)
                    else:
                        with open(config_path, 'r', encoding='utf-8') as f:
                            env_config = json.load(f)
                    
                    # 설정 병합
                    config = self._merge_config(config, env_config)
                    self.logger.info(f"설정 파일 로드: {config_file}")
                    break
                    
                except Exception as e:
                    self.logger.warning(f"설정 파일 로드 실패 ({config_file}): {str(e)}")
        
        return config
    
    def _override_with_env_vars(self, config: SystemConfig):
        """환경변수로 설정을 오버라이드합니다."""
        # 데이터베이스 설정
        if os.getenv('DB_HOST'):
            config.database.host = os.getenv('DB_HOST')
        if os.getenv('DB_PORT'):
            config.database.port = int(os.getenv('DB_PORT'))
        if os.getenv('DB_NAME'):
            config.database.database = os.getenv('DB_NAME')
        if os.getenv('DB_USER'):
            config.database.username = os.getenv('DB_USER')
        if os.getenv('DB_PASSWORD'):
            config.database.password = os.getenv('DB_PASSWORD')
        
        # 로깅 설정
        if os.getenv('LOG_LEVEL'):
            config.logging.level = os.getenv('LOG_LEVEL')
        if os.getenv('LOG_SAVE_EXCEL'):
            config.logging.save_excel = os.getenv('LOG_SAVE_EXCEL').lower() == 'true'
        
        # 실행 설정
        if os.getenv('EXECUTION_MODE'):
            config.execution.mode = os.getenv('EXECUTION_MODE')

        
        # 구글 드라이브 설정
        if os.getenv('GOOGLE_DRIVE_SHARED_FOLDER_ID'):
            config.google_drive.shared_folder_id = os.getenv('GOOGLE_DRIVE_SHARED_FOLDER_ID')
    
    def _merge_config(self, base_config: SystemConfig, env_config: Dict[str, Any]) -> SystemConfig:
        """설정을 병합합니다."""
        # 간단한 딕셔너리 병합 (중첩된 구조는 지원하지 않음)
        for key, value in env_config.items():
            if hasattr(base_config, key):
                setattr(base_config, key, value)
        return base_config
    
    def _get_default_config(self) -> SystemConfig:
        """기본 설정을 반환합니다."""
        return SystemConfig()
    
    def reload_config(self) -> SystemConfig:
        """설정을 강제로 다시 로드합니다."""
        return self.load_config(force_reload=True)
    
    def get_config(self) -> SystemConfig:
        """현재 설정을 반환합니다."""
        if self.config is None:
            return self.load_config()
        return self.config
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """런타임에 설정을 업데이트합니다."""
        try:
            config = self.get_config()
            
            for key, value in updates.items():
                if hasattr(config, key):
                    setattr(config, key, value)
                else:
                    self.logger.warning(f"알 수 없는 설정 키: {key}")
            
            self.logger.info("설정 업데이트 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"설정 업데이트 실패: {str(e)}")
            return False
    
    def export_config(self, file_path: str, format: str = "json") -> bool:
        """현재 설정을 파일로 내보냅니다."""
        try:
            config = self.get_config()
            config_dict = self._config_to_dict(config)
            
            if format.lower() == "yaml":
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"설정 내보내기 완료: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"설정 내보내기 실패: {str(e)}")
            return False
    
    def _config_to_dict(self, config: SystemConfig) -> Dict[str, Any]:
        """설정 객체를 딕셔너리로 변환합니다."""
        config_dict = {}
        for field_name in config.__dataclass_fields__:
            value = getattr(config, field_name)
            if hasattr(value, '__dataclass_fields__'):
                config_dict[field_name] = self._config_to_dict(value)
            else:
                config_dict[field_name] = value
        return config_dict

# 기존 함수들과의 호환성을 위한 래퍼 함수들
def load_carriers_config():
    """선사 설정 파일을 로드합니다."""
    try:
        config_path = os.path.join(os.getcwd(), 'config', 'carriers.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"설정 파일 로드 실패: {str(e)}")
        return {"carriers": []}

def load_execution_config():
    """실행 모드 설정 파일을 로드합니다."""
    try:
        config_path = os.path.join(os.getcwd(), 'config', 'execution_mode.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"실행 모드 설정 파일 로드 실패: {str(e)}")
        return {
            "execution": {
                "mode": "sequential",
    
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

# 전역 설정 관리자 인스턴스
config_manager = ConfigManager()

def get_system_config() -> SystemConfig:
    """시스템 설정을 반환합니다."""
    return config_manager.get_config()

def reload_system_config() -> SystemConfig:
    """시스템 설정을 다시 로드합니다."""
    return config_manager.reload_config()
