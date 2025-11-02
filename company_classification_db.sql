-- ============================================
-- 회사 마스터 데이터 개선 설계
-- 규모 및 업종 분류 체계 포함
-- ============================================

-- 1. 회사 규모 분류 기준 테이블
CREATE TABLE company_size_criteria (
    size_code VARCHAR(10) PRIMARY KEY,
    size_name VARCHAR(30) NOT NULL,
    revenue_min BIGINT,        -- 매출액 하한 (백만원)
    revenue_max BIGINT,        -- 매출액 상한 (백만원)
    employee_min INT,           -- 직원수 하한
    employee_max INT,           -- 직원수 상한
    asset_min BIGINT,          -- 자산 하한 (백만원)
    display_order INT,
    description TEXT
);

-- 한국 기준 회사 규모 분류
INSERT INTO company_size_criteria VALUES
('LARGE', '대기업', 150000, NULL, 300, NULL, 500000, 1, 
 '매출 1,500억 이상 또는 직원 300명 이상 또는 자산 5,000억 이상'),
('MID', '중견기업', 40000, 150000, 50, 299, NULL, 2,
 '매출 400억~1,500억 또는 직원 50~299명'),
('SMALL', '중소기업', 10000, 40000, 10, 49, NULL, 3,
 '매출 100억~400억 또는 직원 10~49명'),
('MICRO', '소기업', 0, 10000, 1, 9, NULL, 4,
 '매출 100억 미만 또는 직원 10명 미만'),
('STARTUP', '스타트업', NULL, NULL, 1, 50, NULL, 5,
 '창업 7년 이내 혁신기업');

-- ============================================
-- 2. 업종 분류 체계 (한국표준산업분류 기반 단순화)
-- ============================================

CREATE TABLE industry_categories (
    industry_code VARCHAR(10) PRIMARY KEY,
    industry_name VARCHAR(50) NOT NULL,
    industry_group VARCHAR(30),     -- 대분류
    ksic_code VARCHAR(10),          -- 한국표준산업분류 코드
    description TEXT,
    display_order INT
);

INSERT INTO industry_categories VALUES
-- 제조업
('MFG_ELEC', '전기전자', '제조업', 'C26', '전자부품, 반도체, 디스플레이', 1),
('MFG_AUTO', '자동차', '제조업', 'C30', '자동차 및 부품 제조', 2),
('MFG_CHEM', '화학/제약', '제조업', 'C20', '화학물질, 의약품 제조', 3),
('MFG_FOOD', '식품/음료', '제조업', 'C10', '식료품 및 음료 제조', 4),
('MFG_STEEL', '철강/금속', '제조업', 'C24', '1차 금속 제조업', 5),
('MFG_OTHER', '기타제조', '제조업', 'C', '기타 제조업', 6),

-- 서비스업
('SVC_IT', 'IT/소프트웨어', '서비스업', 'J', '정보통신업', 10),
('SVC_FIN', '금융/보험', '서비스업', 'K', '금융 및 보험업', 11),
('SVC_DIST', '유통/물류', '서비스업', 'G', '도소매 및 운수업', 12),
('SVC_CONS', '컨설팅/전문서비스', '서비스업', 'M', '전문/과학/기술서비스', 13),
('SVC_EDU', '교육', '서비스업', 'P', '교육 서비스업', 14),
('SVC_MED', '의료/헬스케어', '서비스업', 'Q', '보건업 및 사회복지', 15),
('SVC_HOSP', '숙박/외식', '서비스업', 'I', '숙박 및 음식점업', 16),
('SVC_ENT', '엔터테인먼트', '서비스업', 'R', '예술/스포츠/여가', 17),

-- 기타
('CONST', '건설/부동산', '건설업', 'F', '건설업', 20),
('ENERGY', '에너지/인프라', '기간산업', 'D', '전기/가스/수도', 21),
('AGRI', '농업/수산업', '1차산업', 'A', '농업/임업/어업', 22),
('PUBLIC', '공공/공기업', '공공부문', 'O', '공공행정', 23);

-- ============================================
-- 3. 개선된 회사 마스터 테이블
-- ============================================

CREATE TABLE company_master_v2 (
    company_code VARCHAR(10) PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    company_name_en VARCHAR(100),
    
    -- 규모 정보
    company_size VARCHAR(10) NOT NULL,        -- LARGE, MID, SMALL, MICRO
    annual_revenue BIGINT,                    -- 연매출 (백만원)
    total_employees INT,                      -- 총 직원수
    survey_target_employees INT,              -- 설문 대상 직원수
    
    -- 업종 정보
    industry_code VARCHAR(10) NOT NULL,       -- 업종 코드
    industry_detail VARCHAR(100),             -- 세부 업종 설명
    is_listed BOOLEAN DEFAULT FALSE,          -- 상장 여부
    
    -- 조직 특성
    establishment_year INT,                   -- 설립연도
    has_labor_union BOOLEAN DEFAULT FALSE,    -- 노조 유무
    has_global_branch BOOLEAN DEFAULT FALSE,  -- 해외지사 유무
    ownership_type VARCHAR(20),               -- 소유구조: OWNER, PROFESSIONAL, PUBLIC
    
    -- 설문 이력
    first_survey_date DATE,                   -- 첫 설문 실시일
    total_survey_count INT DEFAULT 0,         -- 총 설문 횟수
    last_survey_date DATE,                    -- 최근 설문일
    regular_survey_cycle VARCHAR(20),         -- 정기 설문 주기: ANNUAL, BIANNUAL, QUARTERLY
    
    -- 벤치마킹 그룹
    benchmark_group VARCHAR(50),              -- 커스텀 벤치마킹 그룹
    
    -- 메타데이터
    is_active BOOLEAN DEFAULT TRUE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (company_size) REFERENCES company_size_criteria(size_code),
    FOREIGN KEY (industry_code) REFERENCES industry_categories(industry_code),
    INDEX idx_size_industry (company_size, industry_code),
    INDEX idx_revenue (annual_revenue),
    INDEX idx_employees (total_employees)
);

-- ============================================
-- 4. 회사 연도별 정보 (시계열 관리)
-- ============================================

CREATE TABLE company_yearly_info (
    company_code VARCHAR(10),
    year INT,
    
    -- 해당 연도 정보
    annual_revenue BIGINT,
    total_employees INT,
    company_size VARCHAR(10),        -- 연도별로 규모 변경 가능
    
    -- 주요 이벤트
    major_events TEXT,               -- M&A, 구조조정 등
    
    PRIMARY KEY (company_code, year),
    FOREIGN KEY (company_code) REFERENCES company_master_v2(company_code),
    FOREIGN KEY (company_size) REFERENCES company_size_criteria(size_code)
);

-- ============================================
-- 5. 벤치마킹 그룹 관리
-- ============================================

CREATE TABLE benchmark_groups (
    group_id VARCHAR(30) PRIMARY KEY,
    group_name VARCHAR(100) NOT NULL,
    group_type VARCHAR(20),          -- SIZE, INDUSTRY, CUSTOM
    
    -- 그룹 조건
    size_codes JSON,                 -- ["LARGE", "MID"]
    industry_codes JSON,             -- ["MFG_ELEC", "SVC_IT"]
    custom_company_codes JSON,       -- 수동 지정 회사들
    
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

-- 벤치마킹 그룹 예시
INSERT INTO benchmark_groups VALUES
('LARGE_MFG', '대기업 제조업', 'SIZE_INDUSTRY', 
 '["LARGE"]', '["MFG_ELEC", "MFG_AUTO", "MFG_CHEM"]', NULL,
 '대기업 제조업 벤치마킹 그룹', TRUE),
 
('IT_ALL', 'IT/테크 전체', 'INDUSTRY',
 NULL, '["SVC_IT", "MFG_ELEC"]', NULL,
 'IT 및 전자 산업 전체', TRUE),
 
('MID_SVC', '중견 서비스업', 'SIZE_INDUSTRY',
 '["MID"]', '["SVC_IT", "SVC_FIN", "SVC_CONS"]', NULL,
 '중견기업 서비스업', TRUE);

-- ============================================
-- 6. 통계 분석용 뷰
-- ============================================

-- 규모별 업종별 문항 평균 뷰
CREATE VIEW v_benchmark_by_size_industry AS
SELECT 
    c.company_size,
    s.size_name,
    c.industry_code,
    i.industry_name,
    p.year,
    pq.question_id,
    COUNT(DISTINCT c.company_code) as company_count,
    COUNT(DISTINCT r.respondent_id) as respondent_count,
    AVG(JSON_EXTRACT(sr.response_value, '$.value')) as avg_score,
    STD(JSON_EXTRACT(sr.response_value, '$.value')) as std_score,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY JSON_EXTRACT(sr.response_value, '$.value')) as q1,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY JSON_EXTRACT(sr.response_value, '$.value')) as median,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY JSON_EXTRACT(sr.response_value, '$.value')) as q3
FROM company_master_v2 c
JOIN company_size_criteria s ON c.company_size = s.size_code
JOIN industry_categories i ON c.industry_code = i.industry_code
JOIN projects p ON c.company_code = p.company_code
JOIN project_questions pq ON p.project_id = pq.project_id
JOIN survey_responses sr ON p.project_id = sr.project_id 
    AND pq.question_no = sr.question_no
JOIN respondents r ON sr.respondent_id = r.respondent_id
GROUP BY c.company_size, s.size_name, c.industry_code, 
         i.industry_name, p.year, pq.question_id;

-- 회사 규모 변화 추적 뷰
CREATE VIEW v_company_size_transition AS
SELECT 
    cy1.company_code,
    c.company_name,
    cy1.year as from_year,
    cy1.company_size as from_size,
    cy2.year as to_year,
    cy2.company_size as to_size,
    CASE 
        WHEN cy1.company_size = 'SMALL' AND cy2.company_size = 'MID' THEN '성장'
        WHEN cy1.company_size = 'MID' AND cy2.company_size = 'LARGE' THEN '대기업진입'
        WHEN cy1.company_size = 'LARGE' AND cy2.company_size = 'MID' THEN '규모축소'
        ELSE '유지'
    END as transition_type
FROM company_yearly_info cy1
JOIN company_yearly_info cy2 ON cy1.company_code = cy2.company_code 
    AND cy1.year = cy2.year - 1
JOIN company_master_v2 c ON cy1.company_code = c.company_code
WHERE cy1.company_size != cy2.company_size;

-- ============================================
-- 7. 벤치마킹 함수
-- ============================================

DELIMITER //

-- 특정 회사의 벤치마킹 그룹 대비 위치
CREATE FUNCTION get_company_percentile(
    p_company_code VARCHAR(10),
    p_project_id VARCHAR(30),
    p_question_id VARCHAR(50)
) RETURNS JSON
DETERMINISTIC
BEGIN
    DECLARE v_score FLOAT;
    DECLARE v_size VARCHAR(10);
    DECLARE v_industry VARCHAR(10);
    DECLARE v_percentile FLOAT;
    DECLARE v_result JSON;
    
    -- 해당 회사의 점수
    SELECT AVG(JSON_EXTRACT(sr.response_value, '$.value'))
    INTO v_score
    FROM survey_responses sr
    JOIN project_questions pq ON sr.project_id = pq.project_id 
        AND sr.question_no = pq.question_no
    WHERE sr.project_id = p_project_id 
        AND pq.question_id = p_question_id;
    
    -- 회사 규모/업종
    SELECT company_size, industry_code
    INTO v_size, v_industry
    FROM company_master_v2
    WHERE company_code = p_company_code;
    
    -- 동일 규모/업종 내 백분위
    SELECT PERCENT_RANK() OVER (ORDER BY avg_score) * 100
    INTO v_percentile
    FROM (
        SELECT 
            c.company_code,
            AVG(JSON_EXTRACT(sr.response_value, '$.value')) as avg_score
        FROM company_master_v2 c
        JOIN projects p ON c.company_code = p.company_code
        JOIN project_questions pq ON p.project_id = pq.project_id
        JOIN survey_responses sr ON p.project_id = sr.project_id 
            AND pq.question_no = sr.question_no
        WHERE c.company_size = v_size 
            AND c.industry_code = v_industry
            AND pq.question_id = p_question_id
        GROUP BY c.company_code
    ) AS benchmark_scores
    WHERE company_code = p_company_code;
    
    SET v_result = JSON_OBJECT(
        'score', v_score,
        'percentile', v_percentile,
        'size_group', v_size,
        'industry_group', v_industry
    );
    
    RETURN v_result;
END //

DELIMITER ;

-- ============================================
-- 8. 샘플 데이터
-- ============================================

-- 샘플 회사 데이터
INSERT INTO company_master_v2 (
    company_code, company_name, company_size, annual_revenue, 
    total_employees, industry_code, establishment_year, is_listed
) VALUES
('SAMS', '삼성전자', 'LARGE', 300000000, 280000, 'MFG_ELEC', 1969, TRUE),
('HYUN', '현대자동차', 'LARGE', 150000000, 70000, 'MFG_AUTO', 1967, TRUE),
('LOTT', '롯데그룹', 'LARGE', 80000000, 50000, 'SVC_DIST', 1967, TRUE),
('KAKA', '카카오', 'LARGE', 6000000, 10000, 'SVC_IT', 2014, TRUE),
('MAEIL', '매일유업', 'MID', 2500000, 3500, 'MFG_FOOD', 1969, TRUE),
('KYOCH', '교촌F&B', 'MID', 500000, 1200, 'SVC_HOSP', 1991, FALSE),
('DAED', '대동공업', 'MID', 1000000, 800, 'MFG_OTHER', 1947, TRUE),
('INSG', '인사이트그룹', 'SMALL', 50000, 45, 'SVC_CONS', 2010, FALSE);

-- ============================================
-- 9. 리포팅 쿼리 예시
-- ============================================

-- 업종별 규모별 평균 점수
SELECT 
    i.industry_name,
    s.size_name,
    COUNT(DISTINCT c.company_code) as companies,
    AVG(ps.avg_score) as avg_score
FROM company_master_v2 c
JOIN industry_categories i ON c.industry_code = i.industry_code
JOIN company_size_criteria s ON c.company_size = s.size_code
LEFT JOIN (
    -- 프로젝트별 평균 점수
    SELECT p.company_code, AVG(JSON_EXTRACT(sr.response_value, '$.value')) as avg_score
    FROM projects p
    JOIN survey_responses sr ON p.project_id = sr.project_id
    WHERE p.year = 2024
    GROUP BY p.company_code
) ps ON c.company_code = ps.company_code
GROUP BY i.industry_name, s.size_name
ORDER BY i.display_order, s.display_order;
