"""
개선된 문항 분류 및 코드 생성 시스템 v2
진단 유형과 카테고리 계층 구조 명확화
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import re

# ============================================
# 진단 유형 정의
# ============================================

class DiagnosisType(Enum):
    """진단 유형 (최상위 분류)"""
    OD = "조직진단"
    LD = "리더십진단"  # 다면평가 포함
    ES = "몰입도조사"

# ============================================
# 카테고리 구조 정의
# ============================================

# 조직진단 카테고리 매핑
OD_CATEGORIES = {
    # 대분류
    "비전": "VIS", "전략": "VIS", "비전/전략": "VIS",
    "가치": "VAL", "가치실천": "VAL", "가치인식": "VAL",
    "조직문화": "CUL", "문화": "CUL",
    "인사제도": "HR", "인사": "HR",
    "조직운영": "PROC", "프로세스": "PROC", "조직/프로세스": "PROC",
    "리더십": "LEAD", "리더": "LEAD", "리더의 변화노력": "LEAD",
    "소통": "COMM", "의사소통": "COMM", "커뮤니케이션": "COMM",
    "조직몰입": "ENG", "몰입": "ENG", "몰입도": "ENG",
    "협업": "COOP", "협력": "COOP",
    "변화": "CHG", "변화준비도": "CHG",
    "업무": "WRK", "업무방식": "WRK",
    
    # 중분류
    "이해도": "UND", "이해": "UND",
    "공유": "SHA", "공유도": "SHA",
    "실천": "PRA", "실천성": "PRA",
    "공정성": "FAIR", "공정": "FAIR",
    "만족": "SAT", "만족도": "SAT",
    "신뢰": "TRS", "믿음": "TRS",
    "성장": "GRW", "개발": "DEV", "육성": "DEV",
    "평가": "EVAL", "평가제도": "EVAL",
    "보상": "REW", "보상제도": "REW",
    "승진": "PROM",
    
    # 소분류
    "자부심": "PRIDE",
    "동료애": "PEER",
    "개인": "SELF", "자기인식": "SELF",
    "팀": "TEAM", "팀워크": "TEAM",
    "조직": "ORG",
    "권한": "AUTH",
    "참여": "PAR", "참여의지": "PAR"
}

# 리더십진단 카테고리 매핑
LD_CATEGORIES = {
    # Level 1: 평가대상
    "GM": "GM", "총괄": "GM",
    "Division장": "DIV", "본부장": "DIV",
    "팀장": "TEAM", "팀리더": "TEAM",
    "동료": "PEER",
    "부하": "SUB", "부하직원": "SUB",
    "팀내상급자": "SENIOR",
    
    # Level 2: 대분류
    "리더십역량": "COMP", "역량": "COMP",
    "Derailer": "DERA", "디레일러": "DERA",
    
    # Level 3: 중분류
    "사람": "PPL", "구성원": "PPL",
    "비즈니스": "BIZ", "사업": "BIZ", "성과": "BIZ",
    "변화": "CHG", "혁신": "CHG",
    
    # Level 4: 소분류
    "육성": "DEV", "개발": "DEV",
    "동기부여": "MOT", "격려": "MOT",
    "소통": "COMM", "대화": "COMM",
    "목표": "GOAL", "목표설정": "GOAL",
    "실행": "EXEC", "추진": "EXEC",
    "협력": "COOP", "팀워크": "COOP",
    "회피": "AVOID", "방어": "AVOID"
}

# ============================================
# 문항 분류기
# ============================================

class QuestionClassifier:
    """문항을 진단 유형과 카테고리로 분류"""
    
    def __init__(self):
        self.od_patterns = [
            "회사", "조직", "우리 회사", "부서", "팀",
            "문화", "제도", "시스템", "프로세스"
        ]
        self.ld_patterns = [
            "GM", "상사", "리더", "팀장", "직속상위",
            "나의 소속", "직책자", "상급자"
        ]
        
    def classify_diagnosis_type(self, question_text: str, 
                               metadata: Dict = None) -> DiagnosisType:
        """문항의 진단 유형 판별"""
        
        # 메타데이터가 있으면 우선 참조
        if metadata:
            if metadata.get('survey_type') == '리더십':
                return DiagnosisType.LD
            elif metadata.get('evaluation_target'):  # 평가대상이 있으면 리더십
                return DiagnosisType.LD
                
        # 문항 텍스트로 판별
        text_lower = question_text.lower()
        
        # 리더십 패턴 체크
        for pattern in self.ld_patterns:
            if pattern.lower() in text_lower:
                return DiagnosisType.LD
                
        # 기본값은 조직진단
        return DiagnosisType.OD
    
    def classify_od_categories(self, question_text: str, 
                              metadata: Dict = None) -> Tuple[str, str, str]:
        """조직진단 문항의 카테고리 분류"""
        
        major = None
        middle = None
        minor = None
        
        # 메타데이터에서 추출
        if metadata:
            major = self._map_to_code(metadata.get('major_category'), OD_CATEGORIES)
            middle = self._map_to_code(metadata.get('middle_category'), OD_CATEGORIES)
            minor = self._map_to_code(metadata.get('minor_category'), OD_CATEGORIES)
        
        # 텍스트 분석으로 보완
        if not major:
            major = self._extract_category_from_text(question_text, OD_CATEGORIES)
            
        return major or "GEN", middle, minor
    
    def classify_ld_categories(self, question_text: str,
                              metadata: Dict = None) -> Tuple[str, str, str, str]:
        """리더십진단 문항의 카테고리 분류"""
        
        target = None
        major = None
        middle = None
        minor = None
        
        # 메타데이터에서 추출
        if metadata:
            target = self._map_to_code(metadata.get('evaluation_target'), LD_CATEGORIES)
            major = self._map_to_code(metadata.get('major_category'), LD_CATEGORIES)
            middle = self._map_to_code(metadata.get('middle_category'), LD_CATEGORIES)
            minor = self._map_to_code(metadata.get('minor_category'), LD_CATEGORIES)
            
        # 기본값 설정
        if not target:
            target = "GM"  # 기본 평가대상
        if not major:
            if "derailer" in str(metadata).lower():
                major = "DERA"
            else:
                major = "COMP"
                
        return target, major, middle, minor
    
    def _map_to_code(self, text: str, mapping: Dict[str, str]) -> Optional[str]:
        """텍스트를 코드로 매핑"""
        if not text:
            return None
            
        text_clean = str(text).strip()
        
        # 정확한 매칭
        if text_clean in mapping:
            return mapping[text_clean]
            
        # 부분 매칭
        for key, code in mapping.items():
            if key in text_clean or text_clean in key:
                return code
                
        return None
    
    def _extract_category_from_text(self, text: str, 
                                   mapping: Dict[str, str]) -> Optional[str]:
        """문항 텍스트에서 카테고리 추출"""
        for keyword, code in mapping.items():
            if keyword in text:
                return code
        return None

# ============================================
# 문항 코드 생성기 v2
# ============================================

class QuestionCodeGeneratorV2:
    """개선된 문항 코드 생성"""
    
    def __init__(self):
        self.classifier = QuestionClassifier()
        
    def generate(self, question_text: str, metadata: Dict = None) -> str:
        """문항 코드 자동 생성
        
        Returns:
            문항 코드 (예: OD-VIS-UND-SELF-v1, LD-GM-COMP-PPL-DEV-v1)
        """
        
        # 진단 유형 판별
        diagnosis_type = self.classifier.classify_diagnosis_type(
            question_text, metadata
        )
        
        # 진단 유형별 코드 생성
        if diagnosis_type == DiagnosisType.OD:
            return self._generate_od_code(question_text, metadata)
        elif diagnosis_type == DiagnosisType.LD:
            return self._generate_ld_code(question_text, metadata)
        else:
            return self._generate_es_code(question_text, metadata)
    
    def _generate_od_code(self, question_text: str, metadata: Dict = None) -> str:
        """조직진단 문항 코드 생성"""
        major, middle, minor = self.classifier.classify_od_categories(
            question_text, metadata
        )
        
        parts = ["OD", major]
        if middle:
            parts.append(middle)
        if minor:
            parts.append(minor)
        parts.append("v1")
        
        return "-".join(parts)
    
    def _generate_ld_code(self, question_text: str, metadata: Dict = None) -> str:
        """리더십진단 문항 코드 생성"""
        target, major, middle, minor = self.classifier.classify_ld_categories(
            question_text, metadata
        )
        
        parts = ["LD", target, major]
        if middle:
            parts.append(middle)
        if minor:
            parts.append(minor)
        parts.append("v1")
        
        return "-".join(parts)
    
    def _generate_es_code(self, question_text: str, metadata: Dict = None) -> str:
        """몰입도조사 문항 코드 생성"""
        # 간단한 구현
        return f"ES-GEN-v1"

# ============================================
# 실제 사용 예시
# ============================================

def demonstrate_code_generation():
    """코드 생성 시연"""
    
    generator = QuestionCodeGeneratorV2()
    
    # 테스트 문항들
    test_questions = [
        {
            "text": "나는 우리 회사의 비전/전략과 사업목표를 명확하게 이해하고 있다",
            "metadata": {
                "major_category": "비전/전략",
                "middle_category": "이해도",
                "minor_category": "개인"
            }
        },
        {
            "text": "나의 소속 GM은 구성원 개인별로 개발 필요점을 찾아내 조언한다",
            "metadata": {
                "evaluation_target": "GM",
                "major_category": "리더십역량",
                "middle_category": "사람",
                "minor_category": "육성"
            }
        },
        {
            "text": "나의 직속상위 직책자는 조직문화 개선의 필요성을 이해하고 있다",
            "metadata": {
                "major_category": "리더의 변화노력",
                "middle_category": "이해도"
            }
        },
        {
            "text": "우리 팀은 서로 협력이 잘 이루어진다",
            "metadata": {
                "major_category": "조직문화",
                "middle_category": "협업"
            }
        }
    ]
    
    print("="*60)
    print("문항 코드 생성 예시")
    print("="*60)
    
    for i, item in enumerate(test_questions, 1):
        code = generator.generate(item["text"], item["metadata"])
        
        print(f"\n[문항 {i}]")
        print(f"텍스트: {item['text'][:50]}...")
        print(f"메타데이터: {item['metadata']}")
        print(f"생성된 코드: {code}")
        
        # 코드 해석
        parts = code.split("-")
        if parts[0] == "OD":
            print(f"→ 조직진단 - {parts[1]} - {parts[2] if len(parts) > 2 else ''}")
        elif parts[0] == "LD":
            print(f"→ 리더십진단 - {parts[1]}(평가대상) - {parts[2]}(대분류)")

# ============================================
# 파일별 분류 통계
# ============================================

def analyze_question_distribution():
    """실제 파일의 문항 분포 분석"""
    
    print("\n" + "="*60)
    print("파일별 문항 분류 통계")
    print("="*60)
    
    # 실제 분석 결과 기반
    stats = {
        "매일유업 (41문항)": {
            "OD": 41,  # 모두 조직진단
            "주요 카테고리": ["가치실천(14)", "인사제도(6)", "리더의 변화노력(5)", "조직몰입(5)"]
        },
        "리더십 문항 샘플 (131문항)": {
            "LD": 131,  # 모두 리더십진단
            "주요 카테고리": ["GM(26)", "본부장(26)", "팀장(26)", "리더십역량(90)", "Derailer(40)"]
        },
        "조직진단 EOS (77문항)": {
            "OD": 77,  # 모두 조직진단
            "주요 카테고리": ["Value(2)", "비전/전략(1)", "조직프로세스(1)", "인사제도(1)"]
        },
        "교촌 F&B (104문항)": {
            "OD": 104,  # 조직진단
            "주요 카테고리": ["조직문화", "비전/전략", "인사제도"]
        },
        "Daedong Leadership (48문항)": {
            "LD": 48,  # 리더십진단
            "주요 카테고리": ["Director 평가", "리더십역량"]
        },
        "Daedong Culture (17문항)": {
            "OD": 17,  # 조직진단
            "주요 카테고리": ["조직문화"]
        }
    }
    
    total_od = 0
    total_ld = 0
    
    for filename, data in stats.items():
        print(f"\n{filename}:")
        if "OD" in data:
            print(f"  - 조직진단: {data['OD']}개")
            total_od += data['OD']
        if "LD" in data:
            print(f"  - 리더십진단: {data['LD']}개")
            total_ld += data['LD']
        print(f"  - 주요 카테고리: {', '.join(data['주요 카테고리'])}")
    
    print(f"\n총계:")
    print(f"  - 조직진단(OD): {total_od}개 ({total_od/418*100:.1f}%)")
    print(f"  - 리더십진단(LD): {total_ld}개 ({total_ld/418*100:.1f}%)")
    print(f"  - 전체: {total_od + total_ld}개")

if __name__ == "__main__":
    # 코드 생성 시연
    demonstrate_code_generation()
    
    # 분류 통계
    analyze_question_distribution()
