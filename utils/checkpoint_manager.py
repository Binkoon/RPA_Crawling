# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/01/27
# 역할 : 크롤링 진행 상황을 저장하고 복구하는 체크포인트 시스템

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import logging

class CheckpointManager:
    """크롤링 진행 상황을 관리하는 체크포인트 매니저"""
    
    def __init__(self, checkpoint_dir: str = "checkpoints"):
        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_file = os.path.join(checkpoint_dir, f"crawling_checkpoint_{datetime.now().strftime('%Y%m%d')}.json")
        self.logger = logging.getLogger(__name__)
        
        # 체크포인트 디렉토리 생성
        self._ensure_checkpoint_dir()
    
    def _ensure_checkpoint_dir(self):
        """체크포인트 디렉토리 생성"""
        if not os.path.exists(self.checkpoint_dir):
            os.makedirs(self.checkpoint_dir)
            self.logger.info(f"체크포인트 디렉토리 생성: {self.checkpoint_dir}")
    
    def save_checkpoint(self, completed_carriers: List[str], failed_carriers: List[str], 
                       current_carrier: Optional[str] = None, error_info: Optional[Dict] = None):
        """
        현재 진행 상황을 체크포인트에 저장
        
        Args:
            completed_carriers: 완료된 선사 목록
            failed_carriers: 실패한 선사 목록
            current_carrier: 현재 실행 중인 선사 (선택사항)
            error_info: 에러 정보 (선택사항)
        """
        checkpoint_data = {
            'timestamp': datetime.now().isoformat(),
            'completed_carriers': completed_carriers,
            'failed_carriers': failed_carriers,
            'current_carrier': current_carrier,
            'error_info': error_info or {},
            'total_completed': len(completed_carriers),
            'total_failed': len(failed_carriers)
        }
        
        try:
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"체크포인트 저장 완료: {self.checkpoint_file}")
            self.logger.info(f"완료: {len(completed_carriers)}개, 실패: {len(failed_carriers)}개")
            
        except Exception as e:
            self.logger.error(f"체크포인트 저장 실패: {str(e)}")
    
    def load_checkpoint(self) -> Optional[Dict]:
        """
        체크포인트에서 진행 상황 로드
        
        Returns:
            체크포인트 데이터 또는 None
        """
        try:
            if not os.path.exists(self.checkpoint_file):
                self.logger.info("체크포인트 파일이 없습니다. 처음부터 시작합니다.")
                return None
            
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
            
            self.logger.info(f"체크포인트 로드 완료: {self.checkpoint_file}")
            self.logger.info(f"이전 완료: {len(checkpoint_data.get('completed_carriers', []))}개")
            self.logger.info(f"이전 실패: {len(checkpoint_data.get('failed_carriers', []))}개")
            
            return checkpoint_data
            
        except Exception as e:
            self.logger.error(f"체크포인트 로드 실패: {str(e)}")
            return None
    
    def is_resume_available(self) -> bool:
        """복구 가능한 체크포인트가 있는지 확인"""
        return os.path.exists(self.checkpoint_file)
    
    def clear_checkpoint(self):
        """체크포인트 파일 삭제"""
        try:
            if os.path.exists(self.checkpoint_file):
                os.remove(self.checkpoint_file)
                self.logger.info("체크포인트 파일 삭제 완료")
        except Exception as e:
            self.logger.error(f"체크포인트 파일 삭제 실패: {str(e)}")
    
    def get_resume_carriers(self, all_carriers: List[str]) -> List[str]:
        """
        복구 시 실행해야 할 선사 목록 반환
        
        Args:
            all_carriers: 전체 선사 목록
            
        Returns:
            아직 실행되지 않은 선사 목록
        """
        checkpoint_data = self.load_checkpoint()
        if not checkpoint_data:
            return all_carriers
        
        completed = set(checkpoint_data.get('completed_carriers', []))
        failed = set(checkpoint_data.get('failed_carriers', []))
        
        # 완료되거나 실패한 선사들을 제외한 목록 반환
        remaining_carriers = [carrier for carrier in all_carriers 
                            if carrier not in completed and carrier not in failed]
        
        self.logger.info(f"복구 대상 선사: {len(remaining_carriers)}개")
        self.logger.info(f"복구 대상: {', '.join(remaining_carriers)}")
        
        return remaining_carriers
