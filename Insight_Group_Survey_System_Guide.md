# 📊 Insight Group 통합 설문 시스템 구축 가이드

## 🎯 시스템 개요

효단님의 Insight Group을 위한 통합 설문 데이터 관리 시스템입니다.
- **연간 처리량**: 20개 프로젝트, 100명~20,000명 규모
- **주요 기능**: 다양한 형식의 설문 통합, 마스터 문항 관리, 시계열 분석, 벤치마킹

## 🏗️ 시스템 아키텍처

### 1. 데이터 흐름
```
[Excel/JSON 원본] → [파서] → [표준화] → [PostgreSQL] → [분석/대시보드]
```

### 2. 핵심 구성 요소
- **마스터 문항 DB**: 모든 문항의 표준화된 저장소
- **프로젝트 관리**: 연도-회사-진단 기준 체계적 관리
- **자동 매핑**: 문항 유사도 분석 및 자동 코드 생성
- **통계 엔진**: 실시간 집계 및 벤치마킹

## 🔑 문항 코드 체계

### 코드 구조
```
[타입]-[대분류]-[중분류]-[세부]-v[버전]
```

### 예시
- `OD-VIS-UND-POS-v1`: 조직진단-비전-이해도-긍정문-버전1
- `LD-PER-DEV-360-v2`: 리더십-성과-개발-360평가-버전2
- `MA-COM-LIS-MGR-v1`: 다면평가-소통-경청-관리자용-버전1

### 주요 코드 매핑
| 카테고리 | 코드 | 카테고리 | 코드 |
|---------|------|---------|------|
| 조직진단 | OD | 리더십 | LD |
| 다면평가 | MA | 몰입도 | ES |
| 비전/전략 | VIS | 가치 | VAL |
| 조직문화 | CUL | 인사제도 | HR |
| 협업 | COL | 소통 | COM |

## 📁 데이터베이스 구조

### 핵심 테이블
1. **question_master**: 모든 문항의 마스터 데이터
2. **projects**: 프로젝트 정보 (2024-SAMS-OD-01 형식)
3. **project_questions**: 프로젝트별 실제 사용 문항
4. **survey_responses**: 응답 데이터 (파티셔닝)
5. **project_statistics**: 실시간 통계
6. **benchmark_data**: 업종별 벤치마킹 데이터

### 파티셔닝 전략
- 연도별 파티션 (2023, 2024, 2025...)
- 대규모 프로젝트(1000명+)는 별도 테이블

## 🔄 데이터 처리 프로세스

### 1. 파일 임포트
```python
# 엑셀 파일 처리
parser = ExcelParser()
questions = parser.parse_maeilyou_format("매일유업.xlsx")

# JSON 파일 처리  
json_parser = JsonParser()
questions = json_parser.parse_surveyjs("kyochon.json")
```

### 2. 문항 표준화
```python
# 자동 코드 생성
generator = QuestionCodeGenerator()
code = generator.generate("조직진단", "비전", "이해도")
# 결과: "OD-VIS-UND-v1"

# 유사도 분석
analyzer = QuestionSimilarityAnalyzer()
similar = analyzer.find_similar_questions(new_question, existing)
```

### 3. 프로젝트 생성
```python
db_manager = SurveyDatabaseManager(config)
project_id = db_manager.create_project(
    company_code="SAMS",
    year=2024,
    survey_type="OD",
    project_name="삼성전자 상반기 조직진단"
)
# 결과: "2024-SAMS-OD-01"
```

## 📊 분석 기능

### 1. 시계열 분석
```sql
-- 연도별 변화 추이
SELECT year, AVG(score) as avg_score
FROM v_yearly_trends
WHERE company_code = 'SAMS' 
  AND question_id = 'OD-VIS-UND-v1'
GROUP BY year;
```

### 2. 벤치마킹
```sql
-- 업종 평균 대비 비교
SELECT 
    our.avg_score,
    bench.industry_avg,
    our.avg_score - bench.industry_avg as gap
FROM project_statistics our
JOIN benchmark_data bench ON our.industry = bench.industry;
```

### 3. 대시보드용 집계
```python
# Materialized View 활용
def get_dashboard_data(project_id):
    return db.query("""
        SELECT * FROM project_statistics 
        WHERE project_id = %s
    """, project_id)
```

## 🚀 구축 단계

### Phase 1: 기초 구축 (1-2주)
1. PostgreSQL 설치 및 스키마 생성
2. 마스터 문항 초기 데이터 구축
3. 파일 파서 개발

### Phase 2: 통합 (2-3주)
1. 기존 엑셀/JSON 데이터 임포트
2. 문항 매핑 및 표준화
3. 자동화 스크립트 개발

### Phase 3: 분석 기능 (2-3주)
1. 통계 집계 테이블 구축
2. Materialized View 생성
3. 벤치마킹 데이터 구축

### Phase 4: 대시보드 (3-4주)
1. API 개발 (FastAPI)
2. 대시보드 UI (React)
3. 보고서 생성 기능

## 💡 핵심 고려사항

### 성능 최적화
- BRIN 인덱스: 시계열 데이터
- GIN 인덱스: JSON 필드 검색
- 파티셔닝: 대용량 응답 데이터
- Materialized View: 빈번한 집계 쿼리

### 확장성
- 연 20개 프로젝트 → 100개까지 확장 가능
- 2만명 → 10만명 규모도 처리 가능
- 5년간 데이터 누적 시 약 20GB 예상

### 보안
- Row Level Security: 회사별 데이터 격리
- 응답자 익명화
- 민감 정보 암호화

## 🔧 기술 스택

### 필수
- **Database**: PostgreSQL 15+
- **Backend**: Python 3.9+, FastAPI
- **Parser**: pandas, openpyxl
- **Frontend**: React, TypeScript

### 선택
- **Cache**: Redis (대시보드 성능)
- **Queue**: Celery (대용량 처리)
- **Analytics**: Apache Superset

## 📈 예상 효과

1. **데이터 일관성**: 모든 설문의 표준화된 관리
2. **분석 속도**: 2만명 데이터 집계 30초 → 1초
3. **인사이트**: 시계열 분석, 벤치마킹 자동화
4. **확장성**: 새로운 설문 형식도 쉽게 통합

## 🎯 다음 단계

1. **즉시 시작 가능**: PostgreSQL 설치, 스키마 생성
2. **샘플 데이터**: 제공된 6개 파일로 POC 구축
3. **파일럿**: 1개 고객사로 시작하여 검증
4. **확대 적용**: 전체 고객사로 단계적 확대

---

## 📝 실행 체크리스트

- [ ] PostgreSQL 15 설치 (M4 Max 로컬 또는 Docker)
- [ ] 데이터베이스 스키마 생성 (integrated_survey_db.sql 실행)
- [ ] Python 환경 설정 (pandas, psycopg2-binary 설치)
- [ ] 샘플 파일로 임포트 테스트
- [ ] 마스터 문항 초기 데이터 구축
- [ ] 첫 프로젝트 데이터 임포트
- [ ] 기초 통계 뷰 생성
- [ ] 대시보드 프로토타입 개발

## 💬 문의사항

효단님, 이 시스템으로:
- 매년 반복되는 설문의 변화 추이를 자동 추적
- 업종별 벤치마킹 데이터 자동 생성
- 고객사별 맞춤 대시보드 제공
- 새로운 문항도 기존 체계에 자동 매핑

가능합니다. 어느 부분부터 시작하시겠습니까?
