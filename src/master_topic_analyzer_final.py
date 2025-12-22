#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CJ그룹 컬처서베이 마스터 토픽 분석 시스템 v2
- 키워드 5개 이내로 제한
- 전체 백분율 100% 보장
- 더 정교한 클러스터링
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
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
    print("KoNLPy not installed")
    USE_KONLPY = False

# 머신러닝
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class ImprovedMasterTopicAnalyzer:
    """개선된 마스터 토픽 분석기"""

    def __init__(self, raw_data_path: str):
        self.raw_data_path = raw_data_path
        self.data = None

        # 문항 정보
        self.questions = {
            'Q_4-1': {
                'number': 4,
                'title': 'VALUE-UP 필요성 공감 어려운 이유',
                'n_topics': 20  # 문항별 목표 토픽 수
            },
            'Q_16-1': {
                'number': 16,
                'title': '회사의 실천준비 미흡 이유',
                'n_topics': 25
            },
            'Q_17-1': {
                'number': 17,
                'title': '목표달성 의지 부족 이유',
                'n_topics': 25
            },
            'Q_20-1': {
                'number': 20,
                'title': '프로세스 비효율성',
                'n_topics': 25
            },
            'Q_43-긍정': {
                'number': 43.1,
                'title': '긍정적 인식',
                'n_topics': 30
            },
            'Q_43-개선필요': {
                'number': 43.2,
                'title': '개선 필요사항',
                'n_topics': 30
            }
        }

        # 불용어 확장
        self.stopwords = {
            '것', '수', '등', '및', '또한', '때', '더', '좀', '꽤', '되', '하', '있', '없',
            '이', '그', '저', '위', '아래', '만', '를', '을', '는', '은', '가', '이', '에',
            '의', '과', '와', '로', '으로', '에서', '부터', '까지', '대한', '대해', '통해',
            '위해', '따라', '함께', '같이', '관련', '관한', '경우', '매우', '정말', '너무',
            '많이', '조금', '약간', '모든', '각', '여러', '다양한', '특히', '주로', '보통'
        }

        # 주제 템플릿 (도메인 지식 기반)
        self.topic_templates = {
            '전략/비전': ['전략', '비전', '목표', '방향', '계획', '중기'],
            '조직/인력': ['조직', '인력', '인재', '구성원', '팀', '부서'],
            '업무/프로세스': ['업무', '프로세스', '절차', '과정', '진행', '처리'],
            '시스템/효율': ['시스템', '효율', '개선', '최적화', '간소화'],
            '소통/협업': ['소통', '협업', '공유', '협력', '커뮤니케이션'],
            '성과/평가': ['성과', '평가', '결과', '실적', '달성'],
            '투자/자원': ['투자', '자원', '예산', '비용', '리소스'],
            '문화/분위기': ['문화', '분위기', '환경', '풍토', '분위기'],
            '리더십': ['리더', '리더십', '경영', '임원', '관리자'],
            '교육/성장': ['교육', '성장', '학습', '개발', '역량'],
            '보상/복지': ['보상', '복지', '급여', '인센티브', '처우'],
            '고객/시장': ['고객', '시장', '경쟁', '서비스', '품질']
        }

        self.master_topics = {}

    def load_data(self):
        """데이터 로드"""
        print("\n=== 데이터 로드 중 ===")
        self.data = pd.read_excel(self.raw_data_path, sheet_name=0)
        self.data.columns = ['company'] + list(self.questions.keys())

        # 텍스트 정제
        for col in self.questions.keys():
            self.data[col] = self.data[col].apply(self.clean_text)

        print(f"✓ 총 {len(self.data)}개 응답 로드 완료")

        # 문항별 유효 응답 수 출력
        print("\n문항별 유효 응답 수:")
        for q_key, q_info in self.questions.items():
            valid_count = (self.data[q_key] != '').sum()
            print(f"  - {q_info['title']}: {valid_count}개")

        return self.data

    def clean_text(self, text):
        """텍스트 정제"""
        if pd.isna(text) or str(text).strip() == '':
            return ''

        text = str(text)

        # 특수문자 제거
        text = re.sub(r'_x[0-9A-F]{4}_?', ' ', text)
        text = re.sub(r'\r\n|\r|\n', ' ', text)
        text = re.sub(r'\s+', ' ', text)

        # 무의미한 응답 제거
        meaningless = ['없습니다', '없음', '없다', '모르겠습니다', '모름',
                      '특이사항 없음', '특이사항없음', '딱히 없음', '특별히 없음']

        text = text.strip()
        if text in meaningless or len(text) < 3:
            return ''

        return text

    def extract_keywords(self, texts: List[str], max_keywords: int = 3) -> List[str]:
        """텍스트에서 핵심 키워드 추출 (최대 3개)"""
        if not texts:
            return []

        # 형태소 분석
        if USE_KONLPY:
            all_nouns = []
            for text in texts[:50]:  # 샘플링
                try:
                    nouns = okt.nouns(text)
                    # 2글자 이상, 불용어 제외
                    filtered = [n for n in nouns if len(n) >= 2 and n not in self.stopwords]
                    all_nouns.extend(filtered)
                except:
                    pass

            if all_nouns:
                counter = Counter(all_nouns)
                # 상위 키워드만 반환
                return [word for word, _ in counter.most_common(max_keywords)]

        # 폴백: TF-IDF 기반
        try:
            vectorizer = TfidfVectorizer(
                max_features=100,
                min_df=1,
                max_df=0.95
            )
            tfidf_matrix = vectorizer.fit_transform(texts[:100])  # 샘플링
            feature_names = vectorizer.get_feature_names_out()

            # 중요도 점수
            scores = tfidf_matrix.sum(axis=0).A1
            top_indices = scores.argsort()[-max_keywords:][::-1]

            return [feature_names[i] for i in top_indices]
        except:
            # 최종 폴백: 빈도 기반
            all_words = ' '.join(texts[:50]).split()
            all_words = [w for w in all_words if len(w) >= 2 and w not in self.stopwords]
            counter = Counter(all_words)
            return [word for word, _ in counter.most_common(max_keywords)]

    def improved_clustering(self, texts: List[str], n_topics: int) -> List[Dict]:
        """개선된 클러스터링 (응답을 정확히 n_topics개로 분할)"""
        valid_texts = [t for t in texts if t]
        n_valid = len(valid_texts)

        if n_valid == 0:
            return []

        # 실제 클러스터 수 조정
        actual_n_topics = min(n_topics, max(5, n_valid // 20))

        print(f"  클러스터링: {n_valid}개 응답 → {actual_n_topics}개 토픽")

        try:
            # TF-IDF 벡터화
            vectorizer = TfidfVectorizer(
                max_features=200,
                min_df=1,
                max_df=0.95,
                ngram_range=(1, 2)  # 바이그램 포함
            )
            X = vectorizer.fit_transform(valid_texts)

            # K-means 클러스터링
            kmeans = KMeans(
                n_clusters=actual_n_topics,
                random_state=42,
                n_init=10,
                max_iter=300
            )
            cluster_labels = kmeans.fit_predict(X)

            # 각 응답을 클러스터에 할당
            clusters = defaultdict(list)
            for idx, label in enumerate(cluster_labels):
                clusters[label].append(idx)

            # 토픽 생성
            topics = []
            total_assigned = 0

            for cluster_id in range(actual_n_topics):
                cluster_indices = clusters[cluster_id]
                cluster_texts = [valid_texts[i] for i in cluster_indices]

                if not cluster_texts:
                    continue

                # 키워드 추출 (최대 3개)
                keywords = self.extract_keywords(cluster_texts, max_keywords=3)

                # 주제명 생성
                topic_name = self.generate_topic_name(keywords, cluster_texts)

                # 비율 계산
                count = len(cluster_texts)
                percentage = (count / n_valid) * 100
                total_assigned += count

                topics.append({
                    'topic_id': cluster_id + 1,
                    'name': topic_name,
                    'keywords': keywords,
                    'count': count,
                    'percentage': percentage,
                    'sample_texts': cluster_texts[:2]
                })

            # 크기순 정렬
            topics = sorted(topics, key=lambda x: x['count'], reverse=True)

            # 할당되지 않은 응답이 있으면 기타로 추가
            if total_assigned < n_valid:
                unassigned_count = n_valid - total_assigned
                topics.append({
                    'topic_id': len(topics) + 1,
                    'name': '기타',
                    'keywords': ['기타', '의견', '기타의견'],
                    'count': unassigned_count,
                    'percentage': (unassigned_count / n_valid) * 100,
                    'sample_texts': []
                })

            # 백분율 정규화 (합계 100% 맞추기)
            total_percentage = sum(t['percentage'] for t in topics)
            if total_percentage > 0:
                for topic in topics:
                    topic['percentage'] = (topic['percentage'] / total_percentage) * 100

            return topics

        except Exception as e:
            print(f"  클러스터링 오류: {e}")
            # 폴백: 단순 분할
            return self.simple_split(valid_texts, n_topics)

    def simple_split(self, texts: List[str], n_topics: int) -> List[Dict]:
        """단순 분할 (폴백용)"""
        n_texts = len(texts)
        topics = []

        # 텍스트를 n_topics개로 균등 분할
        texts_per_topic = max(1, n_texts // n_topics)

        for i in range(min(n_topics, n_texts)):
            start_idx = i * texts_per_topic
            end_idx = min(start_idx + texts_per_topic, n_texts)

            if start_idx >= n_texts:
                break

            topic_texts = texts[start_idx:end_idx]
            keywords = self.extract_keywords(topic_texts, max_keywords=3)

            topics.append({
                'topic_id': i + 1,
                'name': f"주제 {i+1}",
                'keywords': keywords,
                'count': len(topic_texts),
                'percentage': (len(topic_texts) / n_texts) * 100,
                'sample_texts': topic_texts[:2]
            })

        return topics

    def generate_topic_name(self, keywords: List[str], texts: List[str]) -> str:
        """키워드 기반 주제명 생성"""
        if not keywords:
            return "기타"

        # 템플릿 매칭
        best_match = None
        best_score = 0

        for template_name, template_keywords in self.topic_templates.items():
            score = 0
            for kw in keywords[:3]:  # 상위 3개 키워드만
                for tk in template_keywords:
                    if tk in kw or kw in tk:
                        score += 1
                        break

            if score > best_score:
                best_score = score
                best_match = template_name

        # 매칭된 템플릿이 있으면 사용
        if best_match and best_score >= 2:
            return best_match

        # 없으면 키워드 조합
        if len(keywords) >= 2:
            return f"{keywords[0]}/{keywords[1]}"
        elif keywords:
            return keywords[0]
        else:
            return "기타"

    def analyze_question(self, question_key: str) -> Dict:
        """문항별 마스터 토픽 분석"""
        q_info = self.questions[question_key]
        print(f"\n{'='*60}")
        print(f"분석 중: {q_info['title']}")
        print(f"문항 번호: {q_info['number']}")
        print('='*60)

        # 전체 응답 수집
        all_responses = self.data[question_key].tolist()
        valid_responses = [r for r in all_responses if r]

        print(f"전체 응답: {len(all_responses)}개")
        print(f"유효 응답: {len(valid_responses)}개")

        if len(valid_responses) < 10:
            print("유효 응답이 너무 적습니다.")
            return None

        # 목표 토픽 수
        target_topics = q_info['n_topics']

        # 개선된 클러스터링
        topics = self.improved_clustering(valid_responses, target_topics)

        # 결과 생성
        result = {
            'question_key': question_key,
            'question_number': q_info['number'],
            'question_title': q_info['title'],
            'total_responses': len(all_responses),
            'valid_responses': len(valid_responses),
            'topics': topics
        }

        # 결과 출력
        print(f"\n✓ 마스터 토픽 {len(topics)}개 도출:")
        total_pct = 0
        for i, topic in enumerate(topics[:10], 1):
            print(f"  {i:2d}. {topic['name']:15s}: {topic['count']:4d}개 ({topic['percentage']:5.1f}%)")
            if topic['keywords']:
                print(f"      키워드: {', '.join(topic['keywords'][:3])}")
            total_pct += topic['percentage']

        # 나머지 토픽이 있으면
        if len(topics) > 10:
            remaining_count = sum(t['count'] for t in topics[10:])
            remaining_pct = sum(t['percentage'] for t in topics[10:])
            print(f"  ... 외 {len(topics)-10}개 토픽: {remaining_count}개 ({remaining_pct:.1f}%)")
            total_pct += remaining_pct

        print(f"\n  전체 비율 합계: {total_pct:.1f}%")

        return result

    def save_results(self):
        """결과를 엑셀 파일로 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"master_topics_v2_{timestamp}.xlsx"

        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 요약 시트
            summary_data = []

            for q_key, result in self.master_topics.items():
                if not result:
                    continue

                total_pct = sum(t['percentage'] for t in result['topics'])
                summary_data.append({
                    '문항번호': result['question_number'],
                    '문항제목': result['question_title'],
                    '전체응답': result['total_responses'],
                    '유효응답': result['valid_responses'],
                    '도출토픽수': len(result['topics']),
                    '비율합계': f"{total_pct:.1f}%"
                })

            if summary_data:
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='요약', index=False)

            # 각 문항별 상세
            for q_key, result in self.master_topics.items():
                if not result:
                    continue

                sheet_name = f"Q{result['question_number']}"

                # 토픽 데이터
                topic_data = []
                cumulative_pct = 0

                for topic in result['topics']:
                    cumulative_pct += topic['percentage']
                    topic_data.append({
                        '순위': topic['topic_id'],
                        '주제명': topic['name'],
                        '키워드(3개)': ', '.join(topic['keywords'][:3]),
                        '응답수': topic['count'],
                        '비율(%)': round(topic['percentage'], 1),
                        '누적비율(%)': round(cumulative_pct, 1),
                        '샘플응답1': topic['sample_texts'][0] if topic['sample_texts'] else '',
                        '샘플응답2': topic['sample_texts'][1] if len(topic['sample_texts']) > 1 else ''
                    })

                pd.DataFrame(topic_data).to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"\n✓ 마스터 토픽 파일 저장: {output_file}")
        return output_file

    def run_analysis(self):
        """전체 분석 실행"""
        print("\n" + "="*70)
        print("CJ그룹 컬처서베이 마스터 토픽 분석 v3")
        print("- 키워드 3개로 제한 (더 명확한 클러스터링)")
        print("- 백분율 100% 보장")
        print("="*70)

        # 데이터 로드
        self.load_data()

        # 각 문항별 분석
        for q_key in self.questions.keys():
            result = self.analyze_question(q_key)
            self.master_topics[q_key] = result

        # 결과 저장
        output_file = self.save_results()

        print("\n" + "="*70)
        print("마스터 토픽 분석 완료!")
        print(f"결과 파일: {output_file}")
        print("="*70)

        return output_file


def main():
    """메인 실행 함수"""
    analyzer = ImprovedMasterTopicAnalyzer('주관식 분석 raw data_250929.xlsx')
    analyzer.run_analysis()


if __name__ == "__main__":
    main()