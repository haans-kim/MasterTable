# 자동 태깅 시스템 구현 전략

**작성일**: 2025-11-15  
**버전**: 1.0  
**상태**: 초안  
**목적**: 설문 문항 자동 분류 시스템의 단계별 구현 전략 및 기술 가이드

---

## 📋 목차

1. [Executive Summary](#executive-summary)
2. [시스템 개요](#시스템-개요)
3. [Phase 1: MVP (2-3주)](#phase-1-mvp-2-3주)
4. [Phase 2: 자동화 강화 (4-6주)](#phase-2-자동화-강화-4-6주)
5. [Phase 3: 고도화 (8-12주)](#phase-3-고도화-8-12주)
6. [기술 스택 상세](#기술-스택-상세)
7. [데이터 파이프라인](#데이터-파이프라인)
8. [품질 관리](#품질-관리)
9. [모니터링 및 개선](#모니터링-및-개선)
10. [업데이트 로그](#업데이트-로그)

---

## Executive Summary

### 핵심 목표
설문 문항 텍스트를 입력받아 자동으로 의미론적 태그를 생성하는 시스템 구축

### 주요 기능
1. **규칙 기반 태깅**: 키워드 매칭 (정확도: 70-80%)
2. **임베딩 기반 태깅**: 의미론적 유사도 (정확도: 80-90%)
3. **온톨로지 확장**: 관계 기반 태그 추가 (재현율: +20-30%)
4. **신뢰도 평가**: 자동/수동 검토 분기

### 예상 성과
- 수동 태깅 시간: 문항당 3-5분 → 30초 (90% 감소)
- 태깅 일관성: 60-70% → 85-95%
- 신규 개념 발견: 수동 → 자동 제안

---

## 시스템 개요

### 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                    입력 레이어                            │
│  • 신규 문항 텍스트                                       │
│  • 기존 문항 (재태깅)                                     │
│  • 벌크 업로드 (Excel/CSV)                               │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│                 전처리 레이어                             │
│  1. 텍스트 정규화                                        │
│  2. 형태소 분석 (KoNLPy)                                 │
│  3. 불용어 제거                                          │
│  4. 핵심 키워드 추출                                     │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│                 태깅 엔진 (3-Layer)                       │
│                                                          │
│  Layer 1: 규칙 기반 태깅                                 │
│  ├─ 키워드 사전 매칭                                     │
│  ├─ 정규표현식 패턴                                      │
│  └─ 구조적 메타데이터 추출                               │
│                                                          │
│  Layer 2: 임베딩 기반 태깅                               │
│  ├─ 문장 임베딩 생성                                     │
│  ├─ 온톨로지 용어 유사도 계산                            │
│  └─ Top-K 후보 선정                                      │
│                                                          │
│  Layer 3: 온톨로지 확장                                  │
│  ├─ 관계 그래프 탐색                                     │
│  ├─ 부모/자식 개념 추가                                  │
│  └─ 관련 개념 보강                                       │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│              신뢰도 평가 및 검증                          │
│  • 명시적 매칭 비율                                      │
│  • 임베딩 유사도 점수                                    │
│  • 태그 개수 및 분포                                     │
│  • 일관성 검증                                           │
│  → Confidence Score (0.0 - 1.0)                        │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│                  의사결정 레이어                          │
│                                                          │
│  Confidence ≥ 0.8  →  자동 승인                         │
│  0.5 ≤ Confidence < 0.8  →  수동 검토 추천              │
│  Confidence < 0.5  →  수동 태깅 필요                    │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│                  저장 및 피드백                           │
│  • PostgreSQL 저장                                       │
│  • 수동 수정사항 학습                                    │
│  • 온톨로지 업데이트                                     │
│  • 성능 메트릭 기록                                      │
└─────────────────────────────────────────────────────────┘
```

### 핵심 컴포넌트

| 컴포넌트 | 역할 | 기술 스택 |
|---------|------|----------|
| **텍스트 전처리** | 한글 형태소 분석, 정규화 | KoNLPy (Okt), regex |
| **규칙 엔진** | 키워드 매칭, 패턴 인식 | Python dict, regex |
| **임베딩 모델** | 의미론적 유사도 계산 | Sentence-Transformers |
| **온톨로지 DB** | 개념 관계 저장/조회 | PostgreSQL + JSONB |
| **그래프 엔진** | 관계 탐색 및 확장 | NetworkX |
| **학습 루프** | 피드백 기반 개선 | Custom Python |

---

## Phase 1: MVP (2-3주)

### 목표
**기본 규칙 기반 태깅 + 간단한 임베딩 검색**으로 60-70% 정확도 달성

### 구현 범위

#### 1.1 온톨로지 기본 구축
```sql
-- 핵심 테이블 생성
CREATE TABLE survey.taxonomy (
    taxonomy_id SERIAL PRIMARY KEY,
    term VARCHAR(100) UNIQUE NOT NULL,
    term_type VARCHAR(20) NOT NULL,
    aliases JSONB,
    description TEXT,
    usage_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 기본 분류 용어 삽입 (50-100개)
INSERT INTO survey.taxonomy (term, term_type, aliases) VALUES
    ('비전', 'CONCEPT', '{"ko": ["비전", "vision", "미래상"]}'),
    ('리더십', 'CONCEPT', '{"ko": ["리더십", "leadership", "리더쉽"]}'),
    ('소통', 'CONCEPT', '{"ko": ["소통", "커뮤니케이션", "의사소통"]}'),
    ('조직문화', 'THEME', '{"ko": ["조직문화", "문화", "organizational culture"]}'),
    -- ... 50-100개 핵심 용어
;
```

#### 1.2 규칙 기반 태깅 엔진
```python
# auto_tagger_v1.py

import re
import json
from typing import Dict, List, Set

class RuleBasedTagger:
    """규칙 기반 태깅 엔진 (MVP)"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.keyword_map = self._load_keywords()
        self.patterns = self._load_patterns()
    
    def _load_keywords(self) -> Dict[str, List[str]]:
        """온톨로지에서 키워드 사전 로드"""
        result = self.db.execute("""
            SELECT term, aliases
            FROM survey.taxonomy
        """).fetchall()
        
        keyword_map = {}
        for row in result:
            term = row['term']
            aliases = row['aliases'].get('ko', []) if row['aliases'] else []
            
            # 본명 + 별칭 모두 매핑
            for keyword in [term] + aliases:
                if keyword not in keyword_map:
                    keyword_map[keyword] = []
                keyword_map[keyword].append(term)
        
        return keyword_map
    
    def _load_patterns(self) -> Dict[str, str]:
        """정규표현식 패턴 사전"""
        return {
            # 측정 측면 패턴
            'understanding': r'이해|알고|인지',
            'satisfaction': r'만족|긍정적|좋다',
            'importance': r'중요|필수|핵심',
            'practice': r'실천|실행|수행',
            
            # 대상 패턴
            'individual': r'나는|나의|개인',
            'team': r'우리 팀|팀원|팀의',
            'organization': r'회사|조직|우리 회사',
            'leader': r'리더|상사|임원|팀장',
        }
    
    def tag_question(self, question_text: str) -> Dict:
        """문항 태깅"""
        tags = {
            'concepts': set(),
            'aspects': set(),
            'subjects': set(),
            'themes': set()
        }
        
        # 1. 키워드 매칭
        for keyword, terms in self.keyword_map.items():
            if keyword in question_text:
                for term in terms:
                    # 온톨로지에서 term_type 조회
                    term_type = self._get_term_type(term)
                    category = self._type_to_category(term_type)
                    tags[category].add(term)
        
        # 2. 패턴 매칭
        aspect_tags = self._match_patterns(question_text, self.patterns)
        tags['aspects'].update(aspect_tags)
        
        # 3. Set을 List로 변환
        result = {k: list(v) for k, v in tags.items()}
        
        # 4. 신뢰도 계산
        confidence = self._calculate_confidence(result, question_text)
        
        return {
            'tags': result,
            'confidence': confidence,
            'method': 'rule_based'
        }
    
    def _get_term_type(self, term: str) -> str:
        """용어 타입 조회"""
        result = self.db.execute("""
            SELECT term_type FROM survey.taxonomy WHERE term = %s
        """, (term,)).fetchone()
        
        return result['term_type'] if result else 'CONCEPT'
    
    def _type_to_category(self, term_type: str) -> str:
        """term_type → 태그 카테고리"""
        mapping = {
            'THEME': 'themes',
            'CONCEPT': 'concepts',
            'ASPECT': 'aspects',
            'SUBJECT': 'subjects'
        }
        return mapping.get(term_type, 'concepts')
    
    def _match_patterns(self, text: str, patterns: Dict) -> Set[str]:
        """패턴 매칭으로 aspect 추출"""
        matched = set()
        
        if re.search(patterns['understanding'], text):
            matched.add('이해도')
        if re.search(patterns['satisfaction'], text):
            matched.add('만족도')
        if re.search(patterns['importance'], text):
            matched.add('중요도')
        if re.search(patterns['practice'], text):
            matched.add('실천성')
        
        return matched
    
    def _calculate_confidence(self, tags: Dict, text: str) -> float:
        """신뢰도 계산 (간단 버전)"""
        total_tags = sum(len(v) for v in tags.values())
        
        if total_tags == 0:
            return 0.0
        
        # 명시적 매칭된 태그 수
        explicit_matches = sum(
            1 for cat_tags in tags.values()
            for tag in cat_tags
            if tag in text
        )
        
        # 명시적 매칭 비율
        ratio = explicit_matches / total_tags if total_tags > 0 else 0
        
        # 간단한 휴리스틱
        if ratio >= 0.7:
            return 0.85
        elif ratio >= 0.4:
            return 0.65
        else:
            return 0.45


# 사용 예시
if __name__ == '__main__':
    import psycopg2
    
    conn = psycopg2.connect("dbname=survey user=postgres")
    tagger = RuleBasedTagger(conn)
    
    question = "나는 우리 회사의 비전을 명확히 이해하고 있다"
    result = tagger.tag_question(question)
    
    print(f"태그: {result['tags']}")
    print(f"신뢰도: {result['confidence']:.2f}")
    
    # 출력 예상:
    # 태그: {
    #     'concepts': ['비전'],
    #     'aspects': ['이해도'],
    #     'subjects': ['개인', '조직'],
    #     'themes': []
    # }
    # 신뢰도: 0.85
```

#### 1.3 간단한 웹 인터페이스 (선택사항)
```python
# app.py (FastAPI)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2

app = FastAPI(title="Auto Tagging API")

class QuestionInput(BaseModel):
    question_text: str
    diagnosis_type: str = 'OD'
    year: int = 2024

class TaggingResult(BaseModel):
    tags: dict
    confidence: float
    method: str

@app.post("/api/tag", response_model=TaggingResult)
async def tag_question(input: QuestionInput):
    """문항 자동 태깅"""
    conn = psycopg2.connect("dbname=survey user=postgres")
    tagger = RuleBasedTagger(conn)
    
    result = tagger.tag_question(input.question_text)
    conn.close()
    
    return result

@app.get("/api/taxonomy/terms")
async def get_taxonomy_terms(term_type: str = None):
    """온톨로지 용어 조회"""
    conn = psycopg2.connect("dbname=survey user=postgres")
    
    if term_type:
        query = "SELECT * FROM survey.taxonomy WHERE term_type = %s"
        params = (term_type,)
    else:
        query = "SELECT * FROM survey.taxonomy"
        params = None
    
    with conn.cursor() as cur:
        cur.execute(query, params)
        results = cur.fetchall()
    
    conn.close()
    return results
```

### MVP 성공 기준
- [ ] 50-100개 핵심 온톨로지 용어 등록
- [ ] 규칙 기반 태깅 엔진 동작
- [ ] 100개 샘플 문항 테스트
- [ ] 정확도 60-70% 달성
- [ ] 평균 처리 시간 < 1초

### MVP 일정 (2-3주)
```
Week 1:
  Day 1-2: 온톨로지 설계 및 핵심 용어 50-100개 정리
  Day 3-4: 데이터베이스 스키마 구축 및 용어 등록
  Day 5: 규칙 기반 태깅 엔진 개발 시작

Week 2:
  Day 1-3: 규칙 엔진 완성 및 테스트
  Day 4: 100개 샘플 문항으로 검증
  Day 5: 버그 수정 및 정확도 개선

Week 3 (선택):
  Day 1-2: 간단한 API 개발
  Day 3-4: 문서화 및 사용 가이드
  Day 5: 팀 데모 및 피드백 수집
```

---

## Phase 2: 자동화 강화 (4-6주)

### 목표
**임베딩 기반 의미론적 태깅 추가**로 정확도 80-85% 달성

### 추가 기능

#### 2.1 임베딩 모델 통합
```python
# embedding_tagger.py

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class EmbeddingTagger:
    """임베딩 기반 태깅 엔진"""
    
    def __init__(self, db_connection, model_name='jhgan/ko-sroberta-multitask'):
        self.db = db_connection
        # 한국어 특화 모델
        self.model = SentenceTransformer(model_name)
        
        # 온톨로지 용어 임베딩 캐시
        self.term_embeddings = None
        self.term_list = None
        self._build_term_embeddings()
    
    def _build_term_embeddings(self):
        """온톨로지 용어 임베딩 미리 계산"""
        print("📊 온톨로지 용어 임베딩 생성 중...")
        
        result = self.db.execute("""
            SELECT term, description
            FROM survey.taxonomy
            ORDER BY term
        """).fetchall()
        
        self.term_list = [row['term'] for row in result]
        
        # 용어 + 설명 결합으로 더 풍부한 임베딩
        texts = [
            f"{row['term']} {row['description']}" if row['description'] 
            else row['term']
            for row in result
        ]
        
        self.term_embeddings = self.model.encode(
            texts, 
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        print(f"✅ {len(self.term_list)}개 용어 임베딩 완료")
    
    def tag_question(self, question_text: str, top_k=5, threshold=0.5) -> Dict:
        """의미론적 유사도 기반 태깅"""
        
        # 1. 문항 임베딩
        question_embedding = self.model.encode([question_text])
        
        # 2. 모든 용어와 유사도 계산
        similarities = cosine_similarity(
            question_embedding, 
            self.term_embeddings
        )[0]
        
        # 3. 상위 k개 선택
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        tags = {
            'concepts': [],
            'aspects': [],
            'subjects': [],
            'themes': []
        }
        
        similarity_scores = {}
        
        for idx in top_indices:
            if similarities[idx] >= threshold:
                term = self.term_list[idx]
                score = float(similarities[idx])
                
                # term_type 조회
                term_type = self._get_term_type(term)
                category = self._type_to_category(term_type)
                
                tags[category].append(term)
                similarity_scores[term] = score
        
        # 4. 신뢰도 = 평균 유사도
        confidence = np.mean([s for s in similarity_scores.values()]) if similarity_scores else 0.0
        
        return {
            'tags': tags,
            'confidence': float(confidence),
            'method': 'embedding',
            'similarity_scores': similarity_scores
        }
    
    def _get_term_type(self, term: str) -> str:
        """용어 타입 조회 (캐시 가능)"""
        result = self.db.execute("""
            SELECT term_type FROM survey.taxonomy WHERE term = %s
        """, (term,)).fetchone()
        return result['term_type'] if result else 'CONCEPT'
    
    def _type_to_category(self, term_type: str) -> str:
        """term_type → 카테고리"""
        mapping = {
            'THEME': 'themes',
            'CONCEPT': 'concepts',
            'ASPECT': 'aspects',
            'SUBJECT': 'subjects'
        }
        return mapping.get(term_type, 'concepts')


# 하이브리드 태거 (규칙 + 임베딩)
class HybridTagger:
    """규칙 기반 + 임베딩 기반 결합"""
    
    def __init__(self, db_connection):
        self.rule_tagger = RuleBasedTagger(db_connection)
        self.embedding_tagger = EmbeddingTagger(db_connection)
    
    def tag_question(self, question_text: str) -> Dict:
        """하이브리드 태깅"""
        
        # 1. 규칙 기반 태깅
        rule_result = self.rule_tagger.tag_question(question_text)
        
        # 2. 임베딩 기반 태깅
        embedding_result = self.embedding_tagger.tag_question(question_text)
        
        # 3. 결과 병합 (Union)
        merged_tags = {}
        for category in ['concepts', 'aspects', 'subjects', 'themes']:
            merged_tags[category] = list(set(
                rule_result['tags'].get(category, []) +
                embedding_result['tags'].get(category, [])
            ))
        
        # 4. 신뢰도 계산 (가중 평균)
        # 규칙 기반이 더 정확하므로 가중치 높임
        confidence = (
            0.6 * rule_result['confidence'] +
            0.4 * embedding_result['confidence']
        )
        
        return {
            'tags': merged_tags,
            'confidence': confidence,
            'method': 'hybrid',
            'rule_confidence': rule_result['confidence'],
            'embedding_confidence': embedding_result['confidence']
        }
```

#### 2.2 온톨로지 관계 기반 확장
```python
# ontology_expander.py

import networkx as nx

class OntologyExpander:
    """온톨로지 관계를 활용한 태그 확장"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.graph = self._build_graph()
    
    def _build_graph(self) -> nx.DiGraph:
        """온톨로지 그래프 구축"""
        graph = nx.DiGraph()
        
        # 노드 추가
        terms = self.db.execute("""
            SELECT term, term_type FROM survey.taxonomy
        """).fetchall()
        
        for row in terms:
            graph.add_node(row['term'], term_type=row['term_type'])
        
        # 엣지 추가 (관계)
        relations = self.db.execute("""
            SELECT from_term, to_term, relation_type, strength
            FROM survey.taxonomy_relations
        """).fetchall()
        
        for rel in relations:
            graph.add_edge(
                rel['from_term'],
                rel['to_term'],
                relation=rel['relation_type'],
                weight=rel['strength']
            )
        
        return graph
    
    def expand_tags(self, tags: Dict, max_depth=1) -> Dict:
        """
        태그 확장
        
        Args:
            tags: 기존 태그
            max_depth: 확장 깊이 (1=직계만, 2=손자까지)
        
        Returns:
            확장된 태그
        """
        expanded = {k: list(v) for k, v in tags.items()}
        
        # concepts만 확장 (themes는 너무 추상적, aspects는 구체적)
        for concept in tags.get('concepts', []):
            if concept not in self.graph:
                continue
            
            # 부모 개념 추가 → themes에
            parents = list(self.graph.predecessors(concept))
            for parent in parents:
                parent_type = self.graph.nodes[parent].get('term_type')
                if parent_type == 'THEME' and parent not in expanded['themes']:
                    expanded['themes'].append(parent)
            
            # 자식 개념 추가 → concepts에
            if max_depth >= 2:
                children = list(self.graph.successors(concept))
                for child in children:
                    if child not in expanded['concepts']:
                        expanded['concepts'].append(child)
            
            # 관련 개념 추가 (RELATED 관계)
            related = [
                n for n in self.graph.neighbors(concept)
                if self.graph.edges[concept, n].get('relation') == 'RELATED'
            ]
            for rel_term in related:
                if rel_term not in expanded['concepts']:
                    expanded['concepts'].append(rel_term)
        
        return expanded


# 최종 통합 태거
class AutoTagger:
    """완전 자동 태깅 시스템 (Phase 2)"""
    
    def __init__(self, db_connection):
        self.hybrid_tagger = HybridTagger(db_connection)
        self.expander = OntologyExpander(db_connection)
        self.db = db_connection
    
    def tag_question(self, question_text: str, expand=True) -> Dict:
        """완전 자동 태깅"""
        
        # 1. 하이브리드 태깅
        result = self.hybrid_tagger.tag_question(question_text)
        
        # 2. 온톨로지 확장
        if expand:
            result['tags'] = self.expander.expand_tags(result['tags'])
        
        # 3. 최종 검증
        validation = self._validate_tags(result['tags'])
        result['validation'] = validation
        
        # 4. 최종 신뢰도 조정
        if not validation['passed']:
            result['confidence'] *= 0.8  # 패널티
        
        return result
    
    def _validate_tags(self, tags: Dict) -> Dict:
        """태그 검증"""
        issues = []
        
        # 최소 태그 수
        total = sum(len(v) for v in tags.values())
        if total < 2:
            issues.append("태그 수 부족")
        
        # 필수 카테고리
        if not tags.get('concepts'):
            issues.append("핵심 개념 누락")
        
        # 최대 태그 수 (너무 많으면 노이즈)
        if total > 15:
            issues.append("태그 과다")
        
        return {
            'passed': len(issues) == 0,
            'issues': issues
        }
    
    def tag_and_save(self, question_id: str, question_text: str, 
                     diagnosis_type: str, year: int, company_code: str = None):
        """태깅 후 DB 저장"""
        
        result = self.tag_question(question_text)
        
        # DB 저장
        self.db.execute("""
            INSERT INTO survey.question_tags 
            (question_id, question_text, diagnosis_type, year, company_code, 
             tags, auto_tagged, tag_confidence)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (question_id) DO UPDATE
            SET tags = EXCLUDED.tags,
                tag_confidence = EXCLUDED.tag_confidence,
                updated_at = NOW()
        """, (
            question_id, question_text, diagnosis_type, year, company_code,
            json.dumps(result['tags'], ensure_ascii=False),
            True,
            result['confidence']
        ))
        
        return result
```

### Phase 2 성공 기준
- [ ] 임베딩 모델 통합 완료
- [ ] 온톨로지 관계 그래프 구축 (최소 100개 관계)
- [ ] 하이브리드 태깅 엔진 동작
- [ ] 500개 문항 테스트
- [ ] 정확도 80-85% 달성
- [ ] 처리 시간 < 2초

---

## Phase 3: 고도화 (8-12주)

### 목표
**학습 기반 자동 개선 + 대량 처리** 시스템으로 정확도 90%+ 달성

### 추가 기능

#### 3.1 피드백 학습 루프
```python
# feedback_learner.py

class FeedbackLearner:
    """수동 수정사항 학습"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def record_correction(self, question_id: str, 
                         auto_tags: Dict, manual_tags: Dict, 
                         corrected_by: str):
        """수정 기록"""
        
        # 차이 분석
        added_tags = self._find_differences(manual_tags, auto_tags)
        removed_tags = self._find_differences(auto_tags, manual_tags)
        
        # 피드백 기록
        self.db.execute("""
            INSERT INTO survey.tagging_feedback 
            (question_id, auto_tags, manual_tags, added_tags, removed_tags,
             corrected_by, corrected_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """, (
            question_id,
            json.dumps(auto_tags),
            json.dumps(manual_tags),
            json.dumps(added_tags),
            json.dumps(removed_tags),
            corrected_by
        ))
    
    def analyze_patterns(self) -> Dict:
        """피드백 패턴 분석"""
        
        # 1. 자주 추가되는 태그
        frequently_added = self.db.execute("""
            SELECT 
                jsonb_array_elements_text(
                    jsonb_path_query_array(added_tags, '$.*[*]')
                ) as tag,
                COUNT(*) as frequency
            FROM survey.tagging_feedback
            GROUP BY tag
            ORDER BY frequency DESC
            LIMIT 20
        """).fetchall()
        
        # 2. 자주 제거되는 태그
        frequently_removed = self.db.execute("""
            SELECT 
                jsonb_array_elements_text(
                    jsonb_path_query_array(removed_tags, '$.*[*]')
                ) as tag,
                COUNT(*) as frequency
            FROM survey.tagging_feedback
            GROUP BY tag
            ORDER BY frequency DESC
            LIMIT 20
        """).fetchall()
        
        return {
            'frequently_added': frequently_added,
            'frequently_removed': frequently_removed
        }
    
    def suggest_improvements(self) -> List[Dict]:
        """개선 제안"""
        patterns = self.analyze_patterns()
        suggestions = []
        
        # 자주 누락되는 태그 → 규칙 추가 제안
        for item in patterns['frequently_added'][:10]:
            if item['frequency'] > 5:
                suggestions.append({
                    'type': 'ADD_RULE',
                    'tag': item['tag'],
                    'reason': f"{item['frequency']}번 수동 추가됨",
                    'action': f"'{item['tag']}' 감지 규칙 추가"
                })
        
        # 자주 오탐되는 태그 → 제거/수정 제안
        for item in patterns['frequently_removed'][:10]:
            if item['frequency'] > 5:
                suggestions.append({
                    'type': 'REMOVE_RULE',
                    'tag': item['tag'],
                    'reason': f"{item['frequency']}번 수동 제거됨",
                    'action': f"'{item['tag']}' 규칙 수정/제거"
                })
        
        return suggestions
    
    def _find_differences(self, dict1: Dict, dict2: Dict) -> Dict:
        """두 태그 딕셔너리의 차이"""
        diff = {}
        
        for category in ['concepts', 'aspects', 'subjects', 'themes']:
            set1 = set(dict1.get(category, []))
            set2 = set(dict2.get(category, []))
            diff_items = set1 - set2
            
            if diff_items:
                diff[category] = list(diff_items)
        
        return diff
```

#### 3.2 배치 처리 시스템
```python
# batch_processor.py

from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

class BatchProcessor:
    """대량 문항 배치 처리"""
    
    def __init__(self, db_connection, max_workers=4):
        self.db = db_connection
        self.tagger = AutoTagger(db_connection)
        self.max_workers = max_workers
    
    def process_batch(self, questions: List[Dict], 
                     save_to_db=True) -> List[Dict]:
        """
        배치 태깅
        
        Args:
            questions: [
                {'question_id': '...', 'question_text': '...', 
                 'diagnosis_type': 'OD', 'year': 2024},
                ...
            ]
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(
                    self._process_single, 
                    q, 
                    save_to_db
                ): q for q in questions
            }
            
            for future in tqdm(
                as_completed(futures), 
                total=len(questions),
                desc="태깅 진행"
            ):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    question = futures[future]
                    print(f"❌ 오류: {question['question_id']} - {e}")
                    results.append({
                        'question_id': question['question_id'],
                        'error': str(e)
                    })
        
        return results
    
    def _process_single(self, question: Dict, save_to_db: bool) -> Dict:
        """단일 문항 처리"""
        
        if save_to_db:
            result = self.tagger.tag_and_save(
                question_id=question['question_id'],
                question_text=question['question_text'],
                diagnosis_type=question['diagnosis_type'],
                year=question['year'],
                company_code=question.get('company_code')
            )
        else:
            result = self.tagger.tag_question(question['question_text'])
        
        result['question_id'] = question['question_id']
        return result
    
    def process_from_csv(self, csv_path: str) -> List[Dict]:
        """CSV 파일에서 배치 처리"""
        import pandas as pd
        
        df = pd.read_csv(csv_path)
        
        questions = df.to_dict('records')
        
        return self.process_batch(questions)
    
    def generate_report(self, results: List[Dict]) -> Dict:
        """배치 처리 리포트"""
        
        total = len(results)
        errors = len([r for r in results if 'error' in r])
        success = total - errors
        
        confidences = [
            r['confidence'] for r in results 
            if 'confidence' in r
        ]
        
        high_conf = len([c for c in confidences if c >= 0.8])
        medium_conf = len([c for c in confidences if 0.5 <= c < 0.8])
        low_conf = len([c for c in confidences if c < 0.5])
        
        return {
            'total': total,
            'success': success,
            'errors': errors,
            'confidence_distribution': {
                'high (≥0.8)': high_conf,
                'medium (0.5-0.8)': medium_conf,
                'low (<0.5)': low_conf
            },
            'avg_confidence': np.mean(confidences) if confidences else 0,
            'needs_review': medium_conf + low_conf
        }
```

#### 3.3 성능 모니터링
```python
# monitoring.py

class PerformanceMonitor:
    """태깅 성능 모니터링"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def log_tagging(self, question_id: str, result: Dict, 
                   processing_time: float):
        """태깅 로그 기록"""
        
        self.db.execute("""
            INSERT INTO survey.tagging_performance_log 
            (question_id, confidence, method, processing_time, 
             tag_count, logged_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (
            question_id,
            result['confidence'],
            result['method'],
            processing_time,
            sum(len(v) for v in result['tags'].values())
        ))
    
    def get_metrics(self, days=7) -> Dict:
        """성능 메트릭 조회"""
        
        result = self.db.execute("""
            SELECT 
                COUNT(*) as total_tagged,
                AVG(confidence) as avg_confidence,
                AVG(processing_time) as avg_time,
                AVG(tag_count) as avg_tags,
                COUNT(CASE WHEN confidence >= 0.8 THEN 1 END) as high_conf_count,
                COUNT(CASE WHEN confidence < 0.5 THEN 1 END) as low_conf_count
            FROM survey.tagging_performance_log
            WHERE logged_at >= NOW() - INTERVAL '%s days'
        """, (days,)).fetchone()
        
        return dict(result)
    
    def get_accuracy_over_time(self, days=30) -> List[Dict]:
        """시간별 정확도 추이"""
        
        results = self.db.execute("""
            SELECT 
                DATE(logged_at) as date,
                AVG(confidence) as avg_confidence,
                COUNT(*) as count
            FROM survey.tagging_performance_log
            WHERE logged_at >= NOW() - INTERVAL '%s days'
            GROUP BY DATE(logged_at)
            ORDER BY date
        """, (days,)).fetchall()
        
        return [dict(r) for r in results]
```

### Phase 3 성공 기준
- [ ] 피드백 학습 시스템 구축
- [ ] 배치 처리 시스템 (1000+ 문항/시간)
- [ ] 성능 모니터링 대시보드
- [ ] 1000+ 문항 테스트
- [ ] 정확도 90%+ 달성
- [ ] 자동 개선 제안 기능

---

## 기술 스택 상세

### Python 라이브러리

```python
# requirements.txt

# 핵심 NLP
sentence-transformers==2.2.2
transformers==4.35.0
torch==2.1.0

# 한국어 처리
konlpy==0.6.0
soynlp==0.0.493

# 데이터베이스
psycopg2-binary==2.9.9
SQLAlchemy==2.0.23

# 그래프 처리
networkx==3.2.1

# 유틸리티
numpy==1.24.3
pandas==2.1.3
scikit-learn==1.3.2
tqdm==4.66.1

# API (선택)
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0

# 테스트
pytest==7.4.3
pytest-cov==4.1.0
```

### 데이터베이스 스키마

```sql
-- 피드백 테이블
CREATE TABLE survey.tagging_feedback (
    feedback_id SERIAL PRIMARY KEY,
    question_id VARCHAR(50),
    auto_tags JSONB,
    manual_tags JSONB,
    added_tags JSONB,
    removed_tags JSONB,
    corrected_by VARCHAR(50),
    corrected_at TIMESTAMP DEFAULT NOW()
);

-- 성능 로그 테이블
CREATE TABLE survey.tagging_performance_log (
    log_id SERIAL PRIMARY KEY,
    question_id VARCHAR(50),
    confidence FLOAT,
    method VARCHAR(20),
    processing_time FLOAT,
    tag_count INT,
    logged_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_feedback_question ON survey.tagging_feedback(question_id);
CREATE INDEX idx_performance_logged_at ON survey.tagging_performance_log(logged_at);
CREATE INDEX idx_performance_confidence ON survey.tagging_performance_log(confidence);
```

---

## 데이터 파이프라인

### 전체 흐름

```
[Excel 업로드]
      ↓
[CSV 파싱]
      ↓
[배치 처리]
      ↓
┌─────────────────────┐
│ 자동 태깅           │
│ Confidence ≥ 0.8   │ → 자동 승인 → DB 저장
└─────────────────────┘
      ↓
┌─────────────────────┐
│ 수동 검토 필요      │
│ Confidence < 0.8   │ → 검토 큐 → 수동 수정
└─────────────────────┘
      ↓
[피드백 학습]
      ↓
[온톨로지 업데이트]
```

---

## 품질 관리

### 정확도 측정

```python
# accuracy_evaluator.py

class AccuracyEvaluator:
    """태깅 정확도 평가"""
    
    def evaluate(self, auto_tags: Dict, ground_truth: Dict) -> Dict:
        """정확도 계산"""
        
        metrics = {}
        
        for category in ['concepts', 'aspects', 'subjects', 'themes']:
            auto_set = set(auto_tags.get(category, []))
            truth_set = set(ground_truth.get(category, []))
            
            # Precision, Recall, F1
            tp = len(auto_set & truth_set)  # True Positive
            fp = len(auto_set - truth_set)  # False Positive
            fn = len(truth_set - auto_set)  # False Negative
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) \
                 if (precision + recall) > 0 else 0
            
            metrics[category] = {
                'precision': precision,
                'recall': recall,
                'f1': f1
            }
        
        # 전체 평균
        avg_precision = np.mean([m['precision'] for m in metrics.values()])
        avg_recall = np.mean([m['recall'] for m in metrics.values()])
        avg_f1 = np.mean([m['f1'] for m in metrics.values()])
        
        return {
            'by_category': metrics,
            'overall': {
                'precision': avg_precision,
                'recall': avg_recall,
                'f1': avg_f1
            }
        }
```

### 품질 기준

| 메트릭 | MVP (Phase 1) | Phase 2 | Phase 3 |
|--------|---------------|---------|---------|
| **Precision** | ≥ 0.60 | ≥ 0.75 | ≥ 0.85 |
| **Recall** | ≥ 0.55 | ≥ 0.70 | ≥ 0.80 |
| **F1 Score** | ≥ 0.55 | ≥ 0.72 | ≥ 0.82 |
| **처리 시간** | < 1초 | < 2초 | < 3초 |

---

## 모니터링 및 개선

### 주간 리뷰 체크리스트

- [ ] 자동 태깅 정확도 확인 (F1 score)
- [ ] 수동 검토 비율 확인 (목표: < 30%)
- [ ] 처리 시간 확인
- [ ] 피드백 패턴 분석
- [ ] 온톨로지 업데이트 필요 여부
- [ ] 신규 개념 발견 검토

### 월간 개선 사항

- [ ] 정확도 낮은 카테고리 분석 및 개선
- [ ] 자주 오류나는 패턴 규칙 추가
- [ ] 임베딩 모델 업데이트 검토
- [ ] 온톨로지 중복 용어 정리
- [ ] 성능 최적화

---

## 업데이트 로그

### v1.0 (2025-11-15)
- 초안 작성
- Phase 1-3 구현 전략 수립
- 기본 코드 스켈레톤 작성

### 다음 업데이트 예정
- [ ] Phase 1 구현 결과 반영
- [ ] 실제 정확도 데이터 추가
- [ ] 최적 하이퍼파라미터 문서화
- [ ] 실전 예시 추가

---

## 참고 자료

### 한국어 NLP 모델
- [jhgan/ko-sroberta-multitask](https://huggingface.co/jhgan/ko-sroberta-multitask) - 한국어 문장 임베딩 (추천)
- [BM-K/KoSimCSE-roberta](https://huggingface.co/BM-K/KoSimCSE-roberta) - 대안 모델
- [KoNLPy](https://konlpy.org/) - 한국어 형태소 분석

### 온톨로지 관련
- [WordNet](https://wordnet.princeton.edu/) - 영어 온톨로지 참고
- [Korean WordNet](http://wordnet.kaist.ac.kr/) - 한국어 온톨로지

### 기타
- [PostgreSQL JSONB](https://www.postgresql.org/docs/current/datatype-json.html)
- [NetworkX Documentation](https://networkx.org/)

---

**문서 관리**
- 위치: `/Users/hanskim/Projects/MasterTable/auto_tagging_implementation_strategy.md`
- 담당: AI Lab
- 최종 수정: 2025-11-15
