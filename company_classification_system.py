"""
회사 분류 및 벤치마킹 시스템
Company Classification and Benchmarking System
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
import statistics

# ============================================
# 회사 규모 분류
# ============================================

class CompanySize(Enum):
    """회사 규모 분류"""
    LARGE = "대기업"      # 매출 1500억↑ or 직원 300명↑
    MID = "중견기업"       # 매출 400-1500억 or 직원 50-299명  
    SMALL = "중소기업"     # 매출 100-400억 or 직원 10-49명
    MICRO = "소기업"       # 매출 100억 미만 or 직원 10명 미만
    STARTUP = "스타트업"   # 창업 7년 이내

@dataclass
class SizeCriteria:
    """규모 판정 기준"""
    code: str
    name: str
    revenue_min: int  # 백만원 단위
    revenue_max: Optional[int]
    employee_min: int
    employee_max: Optional[int]
    asset_min: Optional[int]

# 한국 기준 규모 분류
SIZE_CRITERIA = {
    CompanySize.LARGE: SizeCriteria(
        "LARGE", "대기업", 150000, None, 300, None, 500000
    ),
    CompanySize.MID: SizeCriteria(
        "MID", "중견기업", 40000, 150000, 50, 299, None
    ),
    CompanySize.SMALL: SizeCriteria(
        "SMALL", "중소기업", 10000, 40000, 10, 49, None
    ),
    CompanySize.MICRO: SizeCriteria(
        "MICRO", "소기업", 0, 10000, 1, 9, None
    )
}

# ============================================
# 업종 분류
# ============================================

class IndustryType(Enum):
    """업종 분류"""
    # 제조업
    MFG_ELEC = "전기전자"
    MFG_AUTO = "자동차"
    MFG_CHEM = "화학/제약"
    MFG_FOOD = "식품/음료"
    MFG_STEEL = "철강/금속"
    MFG_OTHER = "기타제조"
    
    # 서비스업
    SVC_IT = "IT/소프트웨어"
    SVC_FIN = "금융/보험"
    SVC_DIST = "유통/물류"
    SVC_CONS = "컨설팅/전문서비스"
    SVC_EDU = "교육"
    SVC_MED = "의료/헬스케어"
    SVC_HOSP = "숙박/외식"
    SVC_ENT = "엔터테인먼트"
    
    # 기타
    CONST = "건설/부동산"
    ENERGY = "에너지/인프라"
    PUBLIC = "공공/공기업"

# ============================================
# 회사 분류기
# ============================================

class CompanyClassifier:
    """회사 규모 및 업종 분류"""
    
    @staticmethod
    def classify_size(revenue: int = None, employees: int = None, 
                     assets: int = None, years_since_founding: int = None) -> CompanySize:
        """
        회사 규모 분류
        
        Args:
            revenue: 연매출 (백만원)
            employees: 직원수
            assets: 자산 (백만원)
            years_since_founding: 창업 연수
            
        Returns:
            CompanySize: 회사 규모
        """
        
        # 스타트업 체크
        if years_since_founding and years_since_founding <= 7:
            if employees and employees <= 50:
                return CompanySize.STARTUP
        
        # 대기업 체크
        if revenue and revenue >= 150000:
            return CompanySize.LARGE
        if employees and employees >= 300:
            return CompanySize.LARGE
        if assets and assets >= 500000:
            return CompanySize.LARGE
            
        # 중견기업 체크
        if revenue and revenue >= 40000:
            return CompanySize.MID
        if employees and employees >= 50:
            return CompanySize.MID
            
        # 중소기업 체크
        if revenue and revenue >= 10000:
            return CompanySize.SMALL
        if employees and employees >= 10:
            return CompanySize.SMALL
            
        # 나머지는 소기업
        return CompanySize.MICRO
    
    @staticmethod
    def classify_industry(industry_name: str) -> IndustryType:
        """업종 분류"""
        
        industry_map = {
            # 제조업
            "전자": IndustryType.MFG_ELEC,
            "반도체": IndustryType.MFG_ELEC,
            "디스플레이": IndustryType.MFG_ELEC,
            "자동차": IndustryType.MFG_AUTO,
            "화학": IndustryType.MFG_CHEM,
            "제약": IndustryType.MFG_CHEM,
            "식품": IndustryType.MFG_FOOD,
            "음료": IndustryType.MFG_FOOD,
            "철강": IndustryType.MFG_STEEL,
            
            # 서비스업
            "IT": IndustryType.SVC_IT,
            "소프트웨어": IndustryType.SVC_IT,
            "금융": IndustryType.SVC_FIN,
            "보험": IndustryType.SVC_FIN,
            "은행": IndustryType.SVC_FIN,
            "유통": IndustryType.SVC_DIST,
            "물류": IndustryType.SVC_DIST,
            "컨설팅": IndustryType.SVC_CONS,
            "교육": IndustryType.SVC_EDU,
            "의료": IndustryType.SVC_MED,
            "외식": IndustryType.SVC_HOSP,
            
            # 기타
            "건설": IndustryType.CONST,
            "에너지": IndustryType.ENERGY,
            "공공": IndustryType.PUBLIC
        }
        
        for keyword, industry_type in industry_map.items():
            if keyword in industry_name:
                return industry_type
                
        return IndustryType.MFG_OTHER  # 기본값

# ============================================
# 벤치마킹 분석
# ============================================

@dataclass
class Company:
    """회사 정보"""
    code: str
    name: str
    size: CompanySize
    industry: IndustryType
    revenue: int
    employees: int
    avg_score: float = 0.0

class BenchmarkAnalyzer:
    """벤치마킹 분석기"""
    
    def __init__(self, companies: List[Company]):
        self.companies = companies
        
    def get_percentile(self, target_company: Company, 
                       group_type: str = "ALL") -> Dict:
        """백분위 계산"""
        
        # 비교 그룹 선택
        if group_type == "SIZE":
            group = [c for c in self.companies 
                    if c.size == target_company.size]
        elif group_type == "INDUSTRY":
            group = [c for c in self.companies 
                    if c.industry == target_company.industry]
        elif group_type == "SIZE_INDUSTRY":
            group = [c for c in self.companies 
                    if c.size == target_company.size 
                    and c.industry == target_company.industry]
        else:  # ALL
            group = self.companies
            
        if not group:
            return {"error": "No comparison group found"}
            
        # 점수 정렬
        scores = sorted([c.avg_score for c in group])
        target_score = target_company.avg_score
        
        # 백분위 계산
        below_count = sum(1 for s in scores if s < target_score)
        percentile = (below_count / len(scores)) * 100
        
        return {
            "company": target_company.name,
            "score": target_score,
            "percentile": round(percentile, 1),
            "ranking": f"{len(scores) - below_count}/{len(scores)}",
            "group_type": group_type,
            "group_size": len(group),
            "group_avg": round(statistics.mean(scores), 2),
            "group_median": round(statistics.median(scores), 2),
            "interpretation": self._interpret_percentile(percentile)
        }
    
    def _interpret_percentile(self, percentile: float) -> str:
        """백분위 해석"""
        if percentile >= 90:
            return "최우수 (상위 10%)"
        elif percentile >= 75:
            return "우수 (상위 25%)"
        elif percentile >= 50:
            return "평균 이상"
        elif percentile >= 25:
            return "평균 이하"
        else:
            return "개선 필요 (하위 25%)"
    
    def get_benchmark_report(self, target_company: Company) -> Dict:
        """종합 벤치마킹 리포트"""
        
        return {
            "company_info": {
                "name": target_company.name,
                "size": target_company.size.value,
                "industry": target_company.industry.value,
                "revenue": f"{target_company.revenue:,}백만원",
                "employees": f"{target_company.employees:,}명"
            },
            "benchmarks": {
                "전체": self.get_percentile(target_company, "ALL"),
                "동일규모": self.get_percentile(target_company, "SIZE"),
                "동일업종": self.get_percentile(target_company, "INDUSTRY"),
                "동일규모+업종": self.get_percentile(target_company, "SIZE_INDUSTRY")
            }
        }

# ============================================
# 실제 사용 예시
# ============================================

def demo_classification():
    """분류 시스템 데모"""
    
    # 샘플 회사 데이터
    sample_companies = [
        # 대기업
        ("SAMS", "삼성전자", 300000000, 280000, "전자"),
        ("HYUN", "현대자동차", 150000000, 70000, "자동차"),
        ("LOTT", "롯데그룹", 80000000, 50000, "유통"),
        
        # 중견기업
        ("MAEIL", "매일유업", 2500000, 3500, "식품"),
        ("KYOCH", "교촌F&B", 500000, 1200, "외식"),
        ("DAED", "대동공업", 1000000, 800, "제조"),
        
        # 중소기업
        ("INSG", "인사이트그룹", 50000, 45, "컨설팅"),
        ("ABC", "ABC전자", 300000, 35, "전자"),
        
        # 소기업
        ("XYZ", "XYZ푸드", 8000, 8, "식품")
    ]
    
    classifier = CompanyClassifier()
    companies = []
    
    print("="*60)
    print("회사 분류 결과")
    print("="*60)
    
    for code, name, revenue, employees, industry in sample_companies:
        size = classifier.classify_size(revenue, employees)
        ind = classifier.classify_industry(industry)
        
        # 임의의 평균 점수 생성 (실제는 DB에서 계산)
        avg_score = 3.5 + (revenue / 100000000) * 0.5  # 매출 비례
        if avg_score > 4.5:
            avg_score = 4.5
            
        company = Company(code, name, size, ind, revenue, employees, avg_score)
        companies.append(company)
        
        print(f"\n[{name}]")
        print(f"  규모: {size.value}")
        print(f"  업종: {ind.value}")
        print(f"  매출: {revenue:,}백만원")
        print(f"  직원: {employees:,}명")
        print(f"  평균점수: {avg_score:.2f}")
    
    # 벤치마킹 분석
    print("\n" + "="*60)
    print("벤치마킹 분석 - 매일유업")
    print("="*60)
    
    analyzer = BenchmarkAnalyzer(companies)
    maeil = companies[3]  # 매일유업
    
    report = analyzer.get_benchmark_report(maeil)
    
    for group_name, result in report["benchmarks"].items():
        print(f"\n[{group_name} 그룹]")
        print(f"  백분위: {result['percentile']}% (상위 {100-result['percentile']:.1f}%)")
        print(f"  순위: {result['ranking']}")
        print(f"  그룹평균: {result['group_avg']}")
        print(f"  평가: {result['interpretation']}")

# ============================================
# 규모 전환 분석
# ============================================

class SizeTransitionAnalyzer:
    """회사 규모 전환 분석"""
    
    @staticmethod
    def analyze_transition(from_size: CompanySize, 
                          to_size: CompanySize) -> Dict:
        """규모 전환 시 주요 이슈 분석"""
        
        transitions = {
            (CompanySize.SMALL, CompanySize.MID): {
                "type": "성장",
                "challenges": [
                    "조직 체계화 필요",
                    "중간관리층 육성",
                    "프로세스 표준화",
                    "성과관리 체계 구축"
                ],
                "opportunities": [
                    "규모의 경제 실현",
                    "전문인력 영입 가능",
                    "R&D 투자 확대"
                ]
            },
            (CompanySize.MID, CompanySize.LARGE): {
                "type": "대기업 진입",
                "challenges": [
                    "의사결정 속도 저하",
                    "조직 경직성 증가",
                    "혁신 동력 유지",
                    "대기업 규제 대응"
                ],
                "opportunities": [
                    "글로벌 진출",
                    "M&A 기회",
                    "브랜드 파워 강화"
                ]
            }
        }
        
        key = (from_size, to_size)
        if key in transitions:
            return transitions[key]
        else:
            return {"type": "유지", "challenges": [], "opportunities": []}

if __name__ == "__main__":
    # 데모 실행
    demo_classification()
    
    # 규모 전환 분석
    print("\n" + "="*60)
    print("규모 전환 분석")
    print("="*60)
    
    analyzer = SizeTransitionAnalyzer()
    transition = analyzer.analyze_transition(
        CompanySize.SMALL, 
        CompanySize.MID
    )
    
    print(f"\n[중소기업 → 중견기업 전환]")
    print(f"전환 유형: {transition['type']}")
    print("\n주요 도전과제:")
    for challenge in transition['challenges']:
        print(f"  • {challenge}")
    print("\n기회 요인:")
    for opportunity in transition['opportunities']:
        print(f"  • {opportunity}")
