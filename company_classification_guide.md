# 📊 회사 분류 체계 및 벤치마킹 가이드

## 1. 회사 규모 분류 기준

### 📏 한국 기준 분류 체계

| 구분 | 매출액 기준 | 직원수 기준 | 자산 기준 | 특징 |
|-----|------------|-----------|----------|------|
| **대기업** | 1,500억원 이상 | 300명 이상 | 5,000억원 이상 | 3개 기준 중 1개 충족 |
| **중견기업** | 400억~1,500억원 | 50~299명 | - | 대기업 미만 |
| **중소기업** | 100억~400억원 | 10~49명 | - | 중견 미만 |
| **소기업** | 100억원 미만 | 10명 미만 | - | 영세 규모 |
| **스타트업** | - | 50명 이하 | - | 창업 7년 이내 |

### 💡 분류 로직
```sql
-- 회사 규모 자동 판정
CASE 
    WHEN annual_revenue >= 150000 OR total_employees >= 300 THEN 'LARGE'
    WHEN annual_revenue >= 40000 OR total_employees >= 50 THEN 'MID'
    WHEN annual_revenue >= 10000 OR total_employees >= 10 THEN 'SMALL'
    ELSE 'MICRO'
END
```

---

## 2. 업종 분류 체계

### 🏭 제조업 (Manufacturing)
- **MFG_ELEC**: 전기전자 (삼성전자, LG전자)
- **MFG_AUTO**: 자동차 (현대차, 기아)
- **MFG_CHEM**: 화학/제약 (LG화학, 삼성바이오)
- **MFG_FOOD**: 식품/음료 (매일유업, CJ제일제당)
- **MFG_STEEL**: 철강/금속 (포스코, 현대제철)
- **MFG_OTHER**: 기타제조

### 🏢 서비스업 (Services)
- **SVC_IT**: IT/소프트웨어 (카카오, 네이버)
- **SVC_FIN**: 금융/보험 (KB, 삼성생명)
- **SVC_DIST**: 유통/물류 (롯데, 신세계, CJ대한통운)
- **SVC_CONS**: 컨설팅/전문서비스 (인사이트그룹)
- **SVC_EDU**: 교육
- **SVC_MED**: 의료/헬스케어
- **SVC_HOSP**: 숙박/외식 (교촌F&B)
- **SVC_ENT**: 엔터테인먼트

### 🏗️ 기타
- **CONST**: 건설/부동산
- **ENERGY**: 에너지/인프라
- **PUBLIC**: 공공/공기업

---

## 3. 벤치마킹 활용 시나리오

### 📈 시나리오 1: 동종업계 비교
```sql
-- 매일유업(중견/식품)과 동일 규모 식품업계 비교
SELECT 
    company_name,
    AVG(score) as avg_score,
    RANK() OVER (ORDER BY AVG(score) DESC) as ranking
FROM benchmark_data
WHERE company_size = 'MID' 
    AND industry_code = 'MFG_FOOD'
GROUP BY company_name;
```

**결과 예시**
| 회사명 | 평균점수 | 순위 |
|-------|---------|------|
| 오뚜기 | 4.2 | 1 |
| 매일유업 | 4.1 | 2 |
| 빙그레 | 3.9 | 3 |
| 서울우유 | 3.8 | 4 |

### 📊 시나리오 2: 규모 전환기 분석
```sql
-- 중소→중견 성장 회사들의 조직문화 변화
SELECT 
    company_name,
    '중소→중견' as transition,
    before.avg_score as before_score,
    after.avg_score as after_score,
    (after.avg_score - before.avg_score) as change
FROM company_transitions
WHERE from_size = 'SMALL' AND to_size = 'MID';
```

### 🎯 시나리오 3: 백분위 분석
```sql
-- "우리 회사는 상위 몇 %인가?"
SELECT get_company_percentile('MAEIL', '2024-MAEIL-OD-01', 'OD-VIS-UND-v1');
```

**결과**
```json
{
    "score": 4.1,
    "percentile": 75.5,
    "size_group": "MID",
    "industry_group": "MFG_FOOD",
    "interpretation": "중견 식품업계 상위 24.5%"
}
```

---

## 4. 통계 분석 활용

### 📊 규모별 주요 이슈 분석
```sql
-- 규모별 가장 낮은 점수 문항 TOP 5
SELECT 
    size_name,
    question_text,
    avg_score,
    gap_from_large
FROM v_size_weakness_analysis
WHERE rank <= 5
ORDER BY size_name, rank;
```

**인사이트 예시**
- **대기업**: 의사결정 속도, 수평적 소통 취약
- **중견기업**: 복지제도, 경력개발 부족
- **중소기업**: 비전 공유, 체계적 평가 미흡

### 🔄 업종 전환 트렌드
```sql
-- IT 전환 기업들의 성과
SELECT 
    company_name,
    from_industry,
    'SVC_IT' as to_industry,
    culture_score_change,
    performance_change
FROM industry_transitions
WHERE to_industry = 'SVC_IT'
    AND transition_year >= 2020;
```

---

## 5. 실제 적용 예시

### 🏢 회사 등록 시
```python
def classify_company(revenue, employees, industry):
    """회사 규모 및 업종 자동 분류"""
    
    # 규모 판정
    if revenue >= 150000 or employees >= 300:
        size = 'LARGE'
    elif revenue >= 40000 or employees >= 50:
        size = 'MID'
    elif revenue >= 10000 or employees >= 10:
        size = 'SMALL'
    else:
        size = 'MICRO'
    
    # 업종 매핑
    industry_map = {
        '전자': 'MFG_ELEC',
        '자동차': 'MFG_AUTO',
        'IT': 'SVC_IT',
        '식품': 'MFG_FOOD',
        '컨설팅': 'SVC_CONS'
    }
    
    industry_code = industry_map.get(industry, 'OTHER')
    
    return {
        'size': size,
        'industry': industry_code,
        'benchmark_groups': get_benchmark_groups(size, industry_code)
    }
```

### 📈 대시보드 활용
```javascript
// 벤치마킹 차트 데이터
const benchmarkData = {
    company: "매일유업",
    score: 4.1,
    benchmarks: [
        { group: "전체", avg: 3.8, percentile: 70 },
        { group: "중견기업", avg: 3.9, percentile: 65 },
        { group: "식품업계", avg: 4.0, percentile: 60 },
        { group: "중견+식품", avg: 3.95, percentile: 75 }
    ]
};
```

---

## 6. 벤치마킹 그룹 설정

### 🎯 자동 그룹
1. **동일 규모**: 같은 규모 전체 회사
2. **동일 업종**: 같은 업종 전체 회사
3. **동일 규모+업종**: 가장 정밀한 비교

### 🎨 커스텀 그룹
```sql
-- 고성장 IT 그룹 (카카오, 쿠팡, 토스 등)
INSERT INTO benchmark_groups VALUES
('HIGH_GROWTH_IT', '고성장 IT기업', 'CUSTOM',
 NULL, NULL, '["KAKA", "COUP", "TOSS"]',
 '최근 5년 매출 성장률 30% 이상 IT기업', TRUE);
```

---

## 7. 연도별 변화 추적

### 📅 규모 변화 이력
```sql
-- 회사 성장 궤적
SELECT 
    year,
    company_size,
    annual_revenue,
    total_employees,
    major_events
FROM company_yearly_info
WHERE company_code = 'KAKA'
ORDER BY year;
```

**예시: 카카오 성장사**
| 연도 | 규모 | 매출(억) | 직원수 | 주요 이벤트 |
|-----|-----|---------|-------|-----------|
| 2014 | SMALL | 500 | 500 | 다음 합병 |
| 2018 | MID | 2,500 | 3,000 | 카카오뱅크 출범 |
| 2022 | LARGE | 7,000 | 10,000 | 대기업 진입 |

---

## 8. 주요 SQL 쿼리

### 🔍 빈도 높은 분석
```sql
-- 1. 우리 회사 위치 확인
SELECT * FROM v_company_position WHERE company_code = 'MAEIL';

-- 2. 벤치마킹 그룹 평균
SELECT * FROM v_benchmark_averages WHERE group_id = 'MID_FOOD';

-- 3. 업종별 베스트 프랙티스
SELECT * FROM v_industry_best_practices WHERE industry_code = 'MFG_FOOD';

-- 4. 규모 전환 시 주의사항
SELECT * FROM v_size_transition_insights WHERE from_size = 'SMALL' AND to_size = 'MID';
```

---

## 9. 보고서 템플릿

### 📑 벤치마킹 리포트 구성
1. **회사 개요**
   - 규모: 중견기업 (매출 2,500억, 직원 3,500명)
   - 업종: 식품제조업 (MFG_FOOD)
   
2. **벤치마킹 결과**
   - 전체 순위: 상위 30%
   - 중견기업 내: 상위 25%
   - 식품업계 내: 상위 35%
   - 중견+식품 내: 상위 20%
   
3. **강점 영역** (상위 20%)
   - 품질 자부심
   - 제품 신뢰도
   
4. **개선 영역** (하위 30%)
   - 경력개발 지원
   - 성과 보상 체계

5. **액션 플랜**
   - 동종업계 우수사례 벤치마킹
   - 규모 성장 대비 조직문화 개선

---

## 10. 기대 효과

### ✅ 정량적 효과
- **비교 정확도**: 동일 조건 기업과 정밀 비교
- **인사이트 도출**: 규모/업종별 특성 파악
- **성장 예측**: 규모 전환 시 예상 이슈

### ✅ 정성적 효과
- 객관적 위치 파악
- 맞춤형 개선 방향 제시
- 데이터 기반 의사결정

---

효단님, 이제 회사 분류 체계가 완성되었습니다. 
매출액/직원수 기준 규모 분류와 한국 실정에 맞는 업종 분류로
정밀한 벤치마킹과 통계 분석이 가능합니다.
