# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/08/21
# 역할 : 설정 검증 및 테스트 유틸리티

import os
import sys
import logging
from typing import Dict, Any, List
from config_loader import ConfigManager, SystemConfig, Environment

class ConfigValidator:
    """설정 검증기"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config_manager = ConfigManager()
    
    def validate_all_configs(self) -> Dict[str, List[str]]:
        """모든 환경의 설정을 검증합니다."""
        results = {}
        
        for env in Environment:
            self.logger.info(f"환경 '{env.value}' 설정 검증 중...")
            try:
                # 환경변수 설정
                os.environ['RPA_ENVIRONMENT'] = env.value
                
                # 설정 로드
                config = self.config_manager.load_config(force_reload=True)
                
                # 검증
                errors = config.validate()
                results[env.value] = errors
                
                if errors:
                    self.logger.warning(f"환경 '{env.value}' 설정 검증 경고: {len(errors)}개")
                    for error in errors:
                        self.logger.warning(f"  - {error}")
                else:
                    self.logger.info(f"환경 '{env.value}' 설정 검증 통과")
                    
            except Exception as e:
                self.logger.error(f"환경 '{env.value}' 설정 검증 실패: {str(e)}")
                results[env.value] = [f"설정 로드 실패: {str(e)}"]
        
        return results
    
    def test_config_loading(self) -> bool:
        """설정 로딩 테스트를 수행합니다."""
        try:
            self.logger.info("설정 로딩 테스트 시작...")
            
            # 기본 설정 로드
            config = self.config_manager.get_config()
            self.logger.info("기본 설정 로드 성공")
            
            # 설정 업데이트 테스트
            test_updates = {
                'execution.max_workers': 5,
                'logging.level': 'DEBUG'
            }
            
            success = self.config_manager.update_config(test_updates)
            if success:
                self.logger.info("설정 업데이트 테스트 성공")
            else:
                self.logger.error("설정 업데이트 테스트 실패")
                return False
            
            # 설정 내보내기 테스트
            export_success = self.config_manager.export_config(
                'config_export_test.json', 'json'
            )
            if export_success:
                self.logger.info("설정 내보내기 테스트 성공")
                # 테스트 파일 삭제
                if os.path.exists('config_export_test.json'):
                    os.remove('config_export_test.json')
            else:
                self.logger.error("설정 내보내기 테스트 실패")
                return False
            
            self.logger.info("설정 로딩 테스트 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"설정 로딩 테스트 실패: {str(e)}")
            return False
    
    def check_environment_variables(self) -> Dict[str, str]:
        """환경변수 상태를 확인합니다."""
        env_vars = {
            'RPA_ENVIRONMENT': os.getenv('RPA_ENVIRONMENT', '설정되지 않음'),
            'DB_HOST': os.getenv('DB_HOST', '설정되지 않음'),
            'DB_PORT': os.getenv('DB_PORT', '설정되지 않음'),
            'DB_NAME': os.getenv('DB_NAME', '설정되지 않음'),
            'DB_USER': os.getenv('DB_USER', '설정되지 않음'),
            'DB_PASSWORD': os.getenv('DB_PASSWORD', '설정되지 않음'),
            'LOG_LEVEL': os.getenv('LOG_LEVEL', '설정되지 않음'),
            'EXECUTION_MODE': os.getenv('EXECUTION_MODE', '설정되지 않음'),
            'MAX_WORKERS': os.getenv('MAX_WORKERS', '설정되지 않음'),
            'GOOGLE_DRIVE_SHARED_FOLDER_ID': os.getenv('GOOGLE_DRIVE_SHARED_FOLDER_ID', '설정되지 않음')
        }
        
        return env_vars
    
    def generate_config_template(self, env: Environment, output_path: str) -> bool:
        """환경별 설정 템플릿을 생성합니다."""
        try:
            config = self.config_manager._get_default_config()
            config.environment = env
            
            # 환경별 기본값 조정
            if env == Environment.DEVELOPMENT:
                config.logging.level = "DEBUG"
                config.execution.mode = "sequential"
                config.execution.max_workers = 1
                config.google_drive.upload_enabled = False
            elif env == Environment.TESTING:
                config.logging.level = "INFO"
                config.execution.mode = "parallel"
                config.execution.max_workers = 2
                config.google_drive.upload_enabled = False
            elif env == Environment.PRODUCTION:
                config.logging.level = "WARNING"
                config.execution.mode = "parallel"
                config.execution.max_workers = 4
                config.google_drive.upload_enabled = True
            
            # 템플릿 생성
            success = self.config_manager.export_config(output_path, 'yaml')
            if success:
                self.logger.info(f"환경 '{env.value}' 설정 템플릿 생성 완료: {output_path}")
            return success
            
        except Exception as e:
            self.logger.error(f"설정 템플릿 생성 실패: {str(e)}")
            return False

def main():
    """메인 함수"""
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    validator = ConfigValidator()
    
    print("=" * 60)
    print("설정 검증 및 테스트 도구")
    print("=" * 60)
    
    # 1. 환경변수 상태 확인
    print("\n1. 환경변수 상태 확인:")
    env_vars = validator.check_environment_variables()
    for key, value in env_vars.items():
        print(f"  {key}: {value}")
    
    # 2. 모든 환경 설정 검증
    print("\n2. 모든 환경 설정 검증:")
    validation_results = validator.validate_all_configs()
    for env, errors in validation_results.items():
        print(f"  {env}: {'통과' if not errors else f'경고 {len(errors)}개'}")
    
    # 3. 설정 로딩 테스트
    print("\n3. 설정 로딩 테스트:")
    test_result = validator.test_config_loading()
    print(f"  결과: {'성공' if test_result else '실패'}")
    
    # 4. 설정 템플릿 생성
    print("\n4. 설정 템플릿 생성:")
    for env in Environment:
        template_path = f"config/config_{env.value}_template.yaml"
        success = validator.generate_config_template(env, template_path)
        print(f"  {env.value}: {'성공' if success else '실패'}")
    
    print("\n" + "=" * 60)
    print("설정 검증 완료!")
    print("=" * 60)

if __name__ == "__main__":
    main() 