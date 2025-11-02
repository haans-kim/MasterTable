-- ============================================
-- 개선된 통합 설문 데이터베이스 설계 v2
-- 진단 유형과 카테고리 계층 구조 명확화
-- ============================================

-- 1. 진단 유형 (최상위 분류)
CREATE TABLE diagnosis_types (
    diagnosis_type_code VARCHAR(10) PRIMARY KEY,
    diagnosis_type_name VARCHAR(50) NOT NULL,
    description TEXT
);

INSERT INTO diagnosis_types VALUES
('OD', '조직진단', '조직 전반의 건강도 및 문화 진단'),
('LD', '리더십진단', '리더의 역량 및 행동 평가 (다면평가)'),
('ES', '몰입도조사', '직원 몰입도 및 만족도 조사');

-- ============================================
-- 2. 계층적 카테고리 구조
-- ============================================

-- 2-1. 조직진단 카테고리 체계
CREATE TABLE od_categories (
    category_id VARCHAR(30) PRIMARY KEY,
    level INT NOT NULL, -- 1:대분류, 2:중분류, 3:소분류
    parent_id VARCHAR(30),
    category_code VARCHAR(10) NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    display_order INT DEFAULT 0,
    
    FOREIGN KEY (parent_id) REFERENCES od_categories(category_id),
    INDEX idx_level (level),
    INDEX idx_parent (parent_id)
);

-- 조직진단 대분류 예시
INSERT INTO od_categories (category_id, level, parent_id, category_code, category_name) VALUES
('OD-VIS', 1, NULL, 'VIS', '비전/전략'),
('OD-VAL', 1, NULL, 'VAL', '가치'),
('OD-CUL', 1, NULL, 'CUL', '조직문화'),
('OD-HR', 1, NULL, 'HR', '인사제도'),
('OD-PROC', 1, NULL, 'PROC', '조직/프로세스'),
('OD-LEAD', 1, NULL, 'LEAD', '리더십'),
('OD-COMM', 1, NULL, 'COMM', '소통'),
('OD-ENG', 1, NULL, 'ENG', '조직몰입');

-- 조직진단 중분류 예시 (비전/전략 하위)
INSERT INTO od_categories (category_id, level, parent_id, category_code, category_name) VALUES
('OD-VIS-UND', 2, 'OD-VIS', 'UND', '이해도'),
('OD-VIS-SHA', 2, 'OD-VIS', 'SHA', '공유도'),
('OD-VIS-ALI', 2, 'OD-VIS', 'ALI', '정렬도'),
('OD-VIS-PRA', 2, 'OD-VIS', 'PRA', '실천성');

-- 조직진단 소분류 예시 (이해도 하위)
INSERT INTO od_categories (category_id, level, parent_id, category_code, category_name) VALUES
('OD-VIS-UND-SELF', 3, 'OD-VIS-UND', 'SELF', '개인이해'),
('OD-VIS-UND-TEAM', 3, 'OD-VIS-UND', 'TEAM', '팀이해'),
('OD-VIS-UND-ORG', 3, 'OD-VIS-UND', 'ORG', '조직이해');

-- 2-2. 리더십진단 카테고리 체계
CREATE TABLE ld_categories (
    category_id VARCHAR(30) PRIMARY KEY,
    level INT NOT NULL, -- 1:평가대상, 2:대분류, 3:중분류, 4:소분류
    parent_id VARCHAR(30),
    category_code VARCHAR(10) NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    display_order INT DEFAULT 0,
    
    FOREIGN KEY (parent_id) REFERENCES ld_categories(category_id),
    INDEX idx_level (level),
    INDEX idx_parent (parent_id)
);

-- 리더십진단 평가대상 (Level 1)
INSERT INTO ld_categories (category_id, level, parent_id, category_code, category_name) VALUES
('LD-GM', 1, NULL, 'GM', 'GM(총괄책임자)'),
('LD-DIV', 1, NULL, 'DIV', 'Division장'),
('LD-TEAM', 1, NULL, 'TEAM', '팀장'),
('LD-PEER', 1, NULL, 'PEER', '동료'),
('LD-SUB', 1, NULL, 'SUB', '부하직원');

-- 리더십진단 대분류 (Level 2)
INSERT INTO ld_categories (category_id, level, parent_id, category_code, category_name) VALUES
-- GM 하위
('LD-GM-COMP', 2, 'LD-GM', 'COMP', '리더십역량'),
('LD-GM-DERA', 2, 'LD-GM', 'DERA', 'Derailer'),
-- 팀장 하위
('LD-TEAM-COMP', 2, 'LD-TEAM', 'COMP', '리더십역량'),
('LD-TEAM-DERA', 2, 'LD-TEAM', 'DERA', 'Derailer');

-- 리더십진단 중분류 (Level 3)
INSERT INTO ld_categories (category_id, level, parent_id, category_code, category_name) VALUES
('LD-GM-COMP-PPL', 3, 'LD-GM-COMP', 'PPL', '사람'),
('LD-GM-COMP-BIZ', 3, 'LD-GM-COMP', 'BIZ', '비즈니스'),
('LD-GM-COMP-CHG', 3, 'LD-GM-COMP', 'CHG', '변화');

-- ============================================
-- 3. 개선된 문항 마스터 테이블
-- ============================================

CREATE TABLE question_master_v2 (
    question_id VARCHAR(50) PRIMARY KEY,
    question_text_kr TEXT NOT NULL,
    question_text_en TEXT,
    
    -- 진단 유형 (최상위)
    diagnosis_type VARCHAR(10) NOT NULL,
    
    -- 카테고리 경로 (계층 저장)
    category_path VARCHAR(100), -- 예: "OD-VIS-UND-SELF" 또는 "LD-GM-COMP-PPL"
    
    -- 개별 레벨 저장 (검색 최적화)
    category_l1 VARCHAR(30), -- 대분류 or 평가대상
    category_l2 VARCHAR(30), -- 중분류 or 대분류
    category_l3 VARCHAR(30), -- 소분류 or 중분류
    category_l4 VARCHAR(30), -- 리더십의 경우 소분류
    
    -- 문항 속성
    response_type VARCHAR(30) NOT NULL DEFAULT 'LIKERT_5',
    is_reverse BOOLEAN DEFAULT FALSE,
    keyword VARCHAR(100),
    
    -- 버전 관리
    version INT DEFAULT 1,
    is_current BOOLEAN DEFAULT TRUE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (diagnosis_type) REFERENCES diagnosis_types(diagnosis_type_code),
    INDEX idx_diagnosis (diagnosis_type),
    INDEX idx_category_path (category_path),
    INDEX idx_categories (category_l1, category_l2, category_l3)
);

-- ============================================
-- 4. 문항 코드 생성 규칙
-- ============================================

-- 조직진단 문항 코드: OD-[대분류]-[중분류]-[소분류]-v[버전]
-- 예: OD-VIS-UND-SELF-v1 (조직진단-비전전략-이해도-개인이해)

-- 리더십진단 문항 코드: LD-[평가대상]-[대분류]-[중분류]-[소분류]-v[버전]  
-- 예: LD-GM-COMP-PPL-DEV-v1 (리더십진단-GM-역량-사람-육성)

-- ============================================
-- 5. 프로젝트별 진단 구성
-- ============================================

CREATE TABLE project_diagnosis_config (
    config_id INT AUTO_INCREMENT PRIMARY KEY,
    project_id VARCHAR(30) NOT NULL,
    diagnosis_type VARCHAR(10) NOT NULL,
    
    -- 리더십진단의 경우 평가대상 설정
    evaluation_targets JSON, -- ["GM", "TEAM", "PEER"]
    
    -- 사용할 카테고리 범위
    included_categories JSON, -- ["OD-VIS", "OD-CUL", "OD-HR"]
    excluded_categories JSON,
    
    -- 설정
    use_standard_questions BOOLEAN DEFAULT TRUE,
    custom_questions_allowed BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (diagnosis_type) REFERENCES diagnosis_types(diagnosis_type_code)
);

-- ============================================
-- 6. 뷰: 계층 구조 통합 조회
-- ============================================

-- 조직진단 문항 계층 뷰
CREATE VIEW v_od_questions_hierarchy AS
SELECT 
    q.question_id,
    q.question_text_kr,
    c1.category_name as major_category,
    c2.category_name as middle_category,
    c3.category_name as minor_category,
    q.response_type,
    q.keyword
FROM question_master_v2 q
LEFT JOIN od_categories c1 ON q.category_l1 = c1.category_id
LEFT JOIN od_categories c2 ON q.category_l2 = c2.category_id
LEFT JOIN od_categories c3 ON q.category_l3 = c3.category_id
WHERE q.diagnosis_type = 'OD';

-- 리더십진단 문항 계층 뷰
CREATE VIEW v_ld_questions_hierarchy AS
SELECT 
    q.question_id,
    q.question_text_kr,
    c1.category_name as evaluation_target,
    c2.category_name as major_category,
    c3.category_name as middle_category,
    c4.category_name as minor_category,
    q.response_type
FROM question_master_v2 q
LEFT JOIN ld_categories c1 ON q.category_l1 = c1.category_id
LEFT JOIN ld_categories c2 ON q.category_l2 = c2.category_id
LEFT JOIN ld_categories c3 ON q.category_l3 = c3.category_id
LEFT JOIN ld_categories c4 ON q.category_l4 = c4.category_id
WHERE q.diagnosis_type = 'LD';

-- ============================================
-- 7. 카테고리 통계 뷰
-- ============================================

CREATE VIEW v_category_statistics AS
SELECT 
    diagnosis_type,
    category_l1,
    COUNT(DISTINCT question_id) as question_count,
    COUNT(DISTINCT category_l2) as subcategory_count
FROM question_master_v2
WHERE is_current = TRUE
GROUP BY diagnosis_type, category_l1;

-- ============================================
-- 8. 샘플 데이터 - 실제 문항 매핑
-- ============================================

-- 조직진단 문항 예시
INSERT INTO question_master_v2 (
    question_id, 
    question_text_kr, 
    diagnosis_type, 
    category_path,
    category_l1, category_l2, category_l3
) VALUES
('OD-VIS-UND-SELF-v1', 
 '나는 우리 회사의 비전/전략과 사업목표를 명확하게 이해하고 있다',
 'OD', 'OD-VIS-UND-SELF', 
 'OD-VIS', 'OD-VIS-UND', 'OD-VIS-UND-SELF'),

('OD-VAL-PRA-PRIDE-v1',
 '나는 우리 회사에 자부심을 느낀다',
 'OD', 'OD-VAL-PRA-PRIDE',
 'OD-VAL', 'OD-VAL-PRA', 'OD-VAL-PRA-PRIDE'),

('OD-LEAD-CHG-UND-v1',
 '나의 직속상위 직책자는 조직문화 개선의 필요성과 의미를 명확히 이해하고 있다',
 'OD', 'OD-LEAD-CHG-UND',
 'OD-LEAD', 'OD-LEAD-CHG', 'OD-LEAD-CHG-UND');

-- 리더십진단 문항 예시  
INSERT INTO question_master_v2 (
    question_id,
    question_text_kr,
    diagnosis_type,
    category_path,
    category_l1, category_l2, category_l3, category_l4
) VALUES
('LD-GM-COMP-PPL-DEV-v1',
 '나의 소속 GM은 구성원 개인별로 개발 필요점을 찾아내 조언하며, 개발을 위해 지원한다',
 'LD', 'LD-GM-COMP-PPL-DEV',
 'LD-GM', 'LD-GM-COMP', 'LD-GM-COMP-PPL', 'LD-GM-COMP-PPL-DEV'),

('LD-TEAM-COMP-BIZ-GOAL-v1',
 '나의 팀장은 도전적인 목표를 수립하고 이를 달성하기 위하여 노력한다',
 'LD', 'LD-TEAM-COMP-BIZ-GOAL',
 'LD-TEAM', 'LD-TEAM-COMP', 'LD-TEAM-COMP-BIZ', 'LD-TEAM-COMP-BIZ-GOAL'),

('LD-GM-DERA-COMM-AVOID-v1',
 '나의 소속 GM은 어려운 대화나 갈등 상황을 회피한다',
 'LD', 'LD-GM-DERA-COMM-AVOID',
 'LD-GM', 'LD-GM-DERA', 'LD-GM-DERA-COMM', 'LD-GM-DERA-COMM-AVOID');
