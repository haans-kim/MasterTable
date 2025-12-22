#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CJ그룹 컬처서베이 LLM 기반 주관식 분석 시스템
목표: 24년 CJ 주식회사 주관식 예시와 동일한 형식으로 결과 생성
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 한글 처리
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 한글 형태소 분석
try:
    from konlpy.tag import Okt
    okt = Okt()
    USE_KONLPY = True
except ImportError:
    print("KoNLPy not installed. Install with: pip install konlpy")
    USE_KONLPY = False

# 머신러닝 라이브러리
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity


class LLMSurveyAnalyzer:
    """LLM 기반 주관식 문항 분석기"""

    def __init__(self, raw_data_path: str):
        """
        초기화

        Args:
            raw_data_path: 원본 데이터 파일 경로
        """
        self.raw_data_path = raw_data_path
        self.data = None
        self.companies = []

        # 문항 매핑 (raw data 컬럼 → 분석 문항번호)
        self.question_mapping = {
            'Q_4-1': {
                'number': 4,
                'title': 'VALUE-UP 필요성 공감 어려운 이유',
                'context': '회사의 VALUE-UP 전략 필요성에 공감하기 어려운 이유'
            },
            'Q_16-1': {
                'number': 16,
                'title': '회사의 실천준비 미흡 이유',
                'context': '회사가 목표 실천을 위해 준비되어 있지 않다고 생각하는 이유'
            },
            'Q_17-1': {
                'number': 17,
                'title': '목표달성 의지 부족 이유',
                'context': '회사가 목표를 달성하지 못할 것이라고 생각하는 이유'
            },
            'Q_20-1': {
                'number': 20,
                'title': '프로세스 비효율성',
                'context': '업무시 비효율이 발생한다고 생각했던 부분'
            },
            'Q_43-긍정': {
                'number': 43,
                'title': '긍정적 인식',
                'context': '우리 회사의 시스템 또는 조직문화에서 긍정적으로 인식한 부분'
            },
            'Q_43-개선필요': {
                'number': 43,
                'title': '개선 필요사항',
                'context': '우리 회사의 시스템 또는 조직문화에서 개선되어야 한다고 생각했던 부분'
            }
        }

        # 주제 카테고리 템플릿 (도메인 지식)
        self.topic_templates = {
            '목표 및 비전': ['목표', '비전', '전략', '방향성', '계획'],
            '자원 및 지원 부족': ['자원', '지원', '예산', '인력', '투자'],
            '조직문화 개선': ['문화', '분위기', '소통', '협업', '신뢰'],
            '프로세스 효율화': ['프로세스', '절차', '효율', '간소화', '자동화'],
            '리더십 및 의사결정': ['리더', '의사결정', '책임', '권한', '지시'],
            '보고체계 개선': ['보고', '결재', '승인', '문서', '회의'],
            '시스템 통합': ['시스템', 'IT', '통합', '연동', '디지털'],
            '인사 및 보상': ['인사', '평가', '승진', '급여', '보상'],
            '교육 및 성장': ['교육', '역량', '성장', '개발', '전문성'],
            '복지 및 근무환경': ['복지', '워라밸', '근무', '휴가', '환경']
        }

    def load_data(self):
        """데이터 로드 및 전처리"""
        print("\n=== 데이터 로드 중 ===")

        # 엑셀 파일 읽기
        self.data = pd.read_excel(self.raw_data_path, sheet_name=0)

        # 컬럼명 정리
        self.data.columns = ['company'] + list(self.question_mapping.keys())

        # 텍스트 정제
        for col in self.question_mapping.keys():
            self.data[col] = self.data[col].apply(self.clean_text)

        # 계열사 목록 추출
        self.companies = self.data['company'].unique().tolist()

        print(f"✓ 데이터 로드 완료")
        print(f"  - 총 {len(self.data)}개 응답")
        print(f"  - {len(self.companies)}개 계열사")

        return self.data

    def clean_text(self, text):
        """텍스트 정제"""
        if pd.isna(text) or str(text).strip() == '':
            return ''

        text = str(text)

        # 특수문자 및 노이즈 제거
        text = re.sub(r'_x[0-9A-F]{4}_?', ' ', text)  # 유니코드 이스케이프
        text = re.sub(r'\r\n|\r|\n', ' ', text)  # 줄바꿈
        text = re.sub(r'\s+', ' ', text)  # 중복 공백

        return text.strip()

    def extract_keywords(self, texts: List[str], n_keywords: int = 4) -> List[str]:
        """텍스트에서 키워드 추출"""
        if not texts or all(not t for t in texts):
            return []

        # 형태소 분석 사용 가능한 경우
        if USE_KONLPY:
            all_nouns = []
            for text in texts:
                if text:
                    nouns = okt.nouns(text)
                    all_nouns.extend([n for n in nouns if len(n) >= 2])

            if all_nouns:
                counter = Counter(all_nouns)
                return [word for word, _ in counter.most_common(n_keywords)]

        # 기본 방식 (공백 기반)
        all_words = []
        for text in texts:
            if text:
                words = text.split()
                all_words.extend([w for w in words if len(w) >= 2])

        if all_words:
            counter = Counter(all_words)
            return [word for word, _ in counter.most_common(n_keywords)]

        return []

    def cluster_responses(self, responses: List[str], n_topics: int = 10) -> List[Dict]:
        """응답 클러스터링 및 주제 도출"""
        valid_responses = [r for r in responses if r]

        if len(valid_responses) < n_topics:
            n_topics = max(2, len(valid_responses) // 3)

        if len(valid_responses) < 2:
            return []

        try:
            # TF-IDF 벡터화
            vectorizer = TfidfVectorizer(
                max_features=100,
                min_df=1,
                max_df=0.95
            )
            X = vectorizer.fit_transform(valid_responses)

            # K-means 클러스터링
            kmeans = KMeans(n_clusters=n_topics, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(X)

            # 클러스터별 분석
            topics = []
            for cluster_id in range(n_topics):
                cluster_indices = [i for i, c in enumerate(clusters) if c == cluster_id]

                if not cluster_indices:
                    continue

                cluster_texts = [valid_responses[i] for i in cluster_indices]

                # 주제명 생성 (가장 대표적인 키워드 조합)
                keywords = self.extract_keywords(cluster_texts, n_keywords=4)

                # 주제명 결정
                topic_name = self.determine_topic_name(keywords, cluster_texts)

                # 설명문 생성
                description = self.generate_description(topic_name, keywords, cluster_texts)

                topics.append({
                    'name': topic_name,
                    'keywords': keywords[:4],  # 상위 4개 키워드
                    'description': description,
                    'responses': cluster_texts,
                    'frequency': len(cluster_texts),
                    'percentage': len(cluster_texts) / len(valid_responses) * 100
                })

            # 빈도순 정렬
            topics = sorted(topics, key=lambda x: x['frequency'], reverse=True)

            # 상위 10개만 반환
            return topics[:10]

        except Exception as e:
            print(f"클러스터링 오류: {e}")
            return []

    def determine_topic_name(self, keywords: List[str], texts: List[str]) -> str:
        """주제명 결정"""
        # 템플릿과 매칭
        best_match = None
        best_score = 0

        for template_name, template_keywords in self.topic_templates.items():
            score = sum(1 for kw in keywords if any(tk in kw or kw in tk for tk in template_keywords))
            if score > best_score:
                best_score = score
                best_match = template_name

        # 매칭된 템플릿이 있으면 사용
        if best_match and best_score >= 2:
            return best_match

        # 없으면 키워드 조합으로 생성
        if len(keywords) >= 2:
            return f"{keywords[0]} 및 {keywords[1]}"
        elif keywords:
            return keywords[0]
        else:
            return "기타"

    def generate_description(self, topic_name: str, keywords: List[str], texts: List[str]) -> str:
        """주제 설명문 생성"""
        # 샘플 텍스트에서 공통 패턴 찾기
        common_phrases = []

        # 자주 나타나는 구문 추출
        for text in texts[:5]:  # 상위 5개만 샘플링
            if '부족' in text:
                common_phrases.append('부족')
            if '필요' in text:
                common_phrases.append('필요')
            if '개선' in text:
                common_phrases.append('개선')
            if '어려' in text or '어렵' in text:
                common_phrases.append('어려움')

        # 설명문 템플릿
        if '부족' in common_phrases:
            description = f"{topic_name}이(가) 부족하여 업무 진행에 어려움을 겪고 있습니다."
        elif '개선' in common_phrases:
            description = f"{topic_name} 영역에서 개선이 필요하다는 의견이 많습니다."
        elif '필요' in common_phrases:
            description = f"{topic_name}에 대한 명확한 방향 설정과 실행이 필요합니다."
        elif '어려움' in common_phrases:
            description = f"{topic_name} 관련하여 실무진이 어려움을 호소하고 있습니다."
        else:
            # 기본 템플릿
            keyword_str = ', '.join(keywords[:2]) if keywords else topic_name
            description = f"{keyword_str} 관련 이슈가 지적되었으며 관심이 필요합니다."

        return description

    def analyze_company_question(self, company_name: str, question_key: str) -> Dict:
        """특정 계열사의 특정 문항 분석"""
        # 해당 계열사 데이터 필터링
        company_data = self.data[self.data['company'] == company_name]

        # 해당 문항 응답 추출
        responses = company_data[question_key].tolist()
        valid_responses = [r for r in responses if r]

        if not valid_responses:
            return {
                'question_number': self.question_mapping[question_key]['number'],
                'total_responses': 0,
                'topics': []
            }

        # 주제 수 결정 (응답 수에 따라 조정)
        if len(valid_responses) < 10:
            n_topics = min(3, len(valid_responses))
        elif len(valid_responses) < 50:
            n_topics = 5
        else:
            n_topics = 10

        # 클러스터링 및 주제 도출
        topics = self.cluster_responses(valid_responses, n_topics)

        # "기타" 카테고리 추가 (매칭되지 않은 응답들)
        if topics and topics[-1]['percentage'] < 5:
            # 마지막 몇 개 토픽을 기타로 통합
            other_count = sum(t['frequency'] for t in topics[-3:] if t['percentage'] < 5)
            if other_count > 0:
                other_topic = {
                    'name': '기타',
                    'keywords': ['기타', '의견', '제안', '건의'],
                    'description': '기타 다양한 의견과 제안사항이 있었습니다.',
                    'frequency': other_count,
                    'percentage': other_count / len(valid_responses) * 100
                }
                # 작은 토픽들 제거하고 기타 추가
                topics = [t for t in topics if t['percentage'] >= 5]
                topics.append(other_topic)

        return {
            'question_number': self.question_mapping[question_key]['number'],
            'question_title': self.question_mapping[question_key]['title'],
            'total_responses': len(valid_responses),
            'topics': topics
        }

    def generate_company_report(self, company_name: str) -> pd.DataFrame:
        """계열사별 분석 리포트 생성"""
        print(f"\n분석 중: {company_name}")

        report_data = []

        # 각 문항별 분석
        for question_key in self.question_mapping.keys():
            analysis = self.analyze_company_question(company_name, question_key)

            if not analysis['topics']:
                continue

            # 첫 번째 행 여부
            first_row = True

            # 각 주제별로 행 생성
            for topic in analysis['topics']:
                row = {
                    '회사명': company_name if first_row else '',
                    '문항번호': analysis['question_number'],
                    '주제': topic['name'],
                    '키워드': ', '.join(topic['keywords']) if topic['keywords'] else '',
                    '설명': topic['description'],
                    '빈도수': topic['frequency'],
                    '퍼센트': round(topic['percentage'], 2)
                }
                report_data.append(row)
                first_row = False

        return pd.DataFrame(report_data)

    def run_analysis(self, output_path: str = None):
        """전체 분석 실행"""
        print("\n" + "="*60)
        print("CJ그룹 컬처서베이 LLM 기반 분석 시작")
        print("="*60)

        # 데이터 로드
        self.load_data()

        # 결과 저장용 리스트
        all_reports = []

        # 계열사별 분석
        for company in self.companies:
            company_report = self.generate_company_report(company)
            if not company_report.empty:
                all_reports.append(company_report)
                print(f"  ✓ {company}: {len(company_report)}개 주제 도출")

        # 전체 결과 통합
        if all_reports:
            final_report = pd.concat(all_reports, ignore_index=True)

            # 파일 저장
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"CJ_culture_survey_analysis_{timestamp}.xlsx"

            # 엑셀 파일로 저장
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # 전체 데이터 시트
                final_report.to_excel(writer, sheet_name='전체분석', index=False)

                # 계열사별 시트 (선택적)
                for company in self.companies[:10]:  # 상위 10개 계열사만
                    company_data = final_report[final_report['회사명'] == company]
                    if not company_data.empty:
                        sheet_name = company[:30]  # Excel 시트명 길이 제한
                        sheet_name = re.sub(r'[\\/*?:"<>|]', '', sheet_name)
                        company_data.to_excel(writer, sheet_name=sheet_name, index=False)

            print(f"\n✓ 분석 완료!")
            print(f"✓ 결과 파일: {output_path}")
            print(f"✓ 총 {len(final_report)}개 행 생성")

            # 요약 통계
            print(f"\n=== 분석 요약 ===")
            print(f"분석 계열사 수: {len(self.companies)}개")
            print(f"평균 주제 수: {len(final_report) / len(self.companies):.1f}개")

            return output_path
        else:
            print("분석 결과가 없습니다.")
            return None


def main():
    """메인 실행 함수"""
    # 분석기 초기화
    analyzer = LLMSurveyAnalyzer('주관식 분석 raw data_250929.xlsx')

    # 분석 실행
    output_file = analyzer.run_analysis()

    if output_file:
        print(f"\n분석이 완료되었습니다.")
        print(f"결과 파일을 확인하세요: {output_file}")


if __name__ == "__main__":
    main()