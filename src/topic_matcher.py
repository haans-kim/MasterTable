#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
토픽 매칭 엔진
- 기존 마스터 토픽을 로드하여 벡터화
- 개별 응답을 코사인 유사도로 마스터 토픽에 매칭
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
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
    print("⚠️ KoNLPy not installed. Using basic tokenization.")
    USE_KONLPY = False

# 머신러닝
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


class TopicMatcher:
    """마스터 토픽 매칭 엔진"""

    def __init__(self, master_topics_path: str, similarity_threshold: float = 0.25):
        """
        Args:
            master_topics_path: 마스터 토픽 엑셀 파일 경로
            similarity_threshold: 유사도 임계값 (기본 0.25)
        """
        self.master_topics_path = master_topics_path
        self.similarity_threshold = similarity_threshold
        self.master_topics = {}
        self.vectorizers = {}
        self.topic_vectors = {}

        # 불용어
        self.stopwords = {
            '것', '수', '등', '및', '또한', '때', '더', '좀', '꽤', '되', '하', '있', '없',
            '이', '그', '저', '위', '아래', '만', '를', '을', '는', '은', '가', '이', '에',
            '의', '과', '와', '로', '으로', '에서', '부터', '까지', '대한', '대해', '통해',
            '위해', '따라', '함께', '같이', '관련', '관한', '경우', '매우', '정말', '너무',
            '많이', '조금', '약간', '모든', '각', '여러', '다양한', '특히', '주로', '보통',
            '없습니다', '없음', '없다', '모르겠습니다', '모름'
        }

        print("📂 마스터 토픽 로드 중...")
        self.load_master_topics()
        print("🔧 토픽 벡터 생성 중...")
        self.build_topic_vectors()
        print("✅ TopicMatcher 초기화 완료\n")

    def load_master_topics(self):
        """마스터 토픽 엑셀 파일 로드"""
        xl = pd.ExcelFile(self.master_topics_path)

        # 문항별 시트 로드
        question_sheets = {
            'Q4': 'Q_4-1',
            'Q16': 'Q_16-1',
            'Q17': 'Q_17-1',
            'Q20': 'Q_20-1',
            'Q43.1': 'Q_43-긍정',
            'Q43.2': 'Q_43-개선점'
        }

        for sheet_name, question_key in question_sheets.items():
            if sheet_name in xl.sheet_names:
                df = pd.read_excel(self.master_topics_path, sheet_name=sheet_name)

                topics = []
                for _, row in df.iterrows():
                    topic = {
                        'id': int(row['순위']),
                        'name': str(row['주제']),
                        'keywords': str(row['키워드']),
                        'description': str(row['설명']) if '설명' in row else '',
                        'question': question_key
                    }
                    topics.append(topic)

                self.master_topics[question_key] = topics
                print(f"  ✓ {question_key}: {len(topics)}개 토픽")

        total_topics = sum(len(topics) for topics in self.master_topics.values())
        print(f"\n  총 {total_topics}개 마스터 토픽 로드 완료")

    def preprocess_text(self, text: str) -> str:
        """텍스트 전처리"""
        if pd.isna(text) or str(text).strip() == '':
            return ''

        text = str(text)

        # 특수문자 제거
        text = re.sub(r'_x[0-9A-F]{4}_?', ' ', text)
        text = re.sub(r'\r\n|\r|\n', ' ', text)
        text = re.sub(r'[^\w\s가-힣]', ' ', text)
        text = re.sub(r'\s+', ' ', text)

        text = text.strip()

        # 무의미한 응답 필터링
        if len(text) < 3 or text in self.stopwords:
            return ''

        # 형태소 분석 (명사 추출)
        if USE_KONLPY:
            try:
                nouns = okt.nouns(text)
                # 2글자 이상, 불용어 제외
                nouns = [n for n in nouns if len(n) >= 2 and n not in self.stopwords]
                return ' '.join(nouns)
            except:
                pass

        return text

    def build_topic_vectors(self):
        """각 문항별 토픽 벡터 생성"""
        for question_key, topics in self.master_topics.items():
            # 토픽별 텍스트 생성 (키워드 + 설명)
            topic_texts = []
            for topic in topics:
                # 키워드를 3번 반복 (중요도 강조)
                keywords = topic['keywords']
                description = topic['description']

                text = f"{keywords} {keywords} {keywords} {description}"
                processed_text = self.preprocess_text(text)
                topic_texts.append(processed_text)

            # TF-IDF 벡터화
            vectorizer = TfidfVectorizer(
                max_features=500,
                min_df=1,
                max_df=0.95,
                ngram_range=(1, 2)
            )

            try:
                topic_vectors = vectorizer.fit_transform(topic_texts)
                self.vectorizers[question_key] = vectorizer
                self.topic_vectors[question_key] = topic_vectors
                print(f"  ✓ {question_key}: {topic_vectors.shape}")
            except Exception as e:
                print(f"  ✗ {question_key} 벡터화 실패: {e}")

    def match_response(self, response_text: str, question_key: str) -> Tuple[Dict, float]:
        """
        개별 응답을 마스터 토픽에 매칭

        Returns:
            (매칭된 토픽, 유사도) 또는 (None, 유사도)
        """
        if question_key not in self.vectorizers:
            return None, 0.0

        # 텍스트 전처리
        processed_text = self.preprocess_text(response_text)
        if not processed_text:
            return None, 0.0

        # 응답 벡터화
        try:
            response_vector = self.vectorizers[question_key].transform([processed_text])
        except:
            return None, 0.0

        # 코사인 유사도 계산
        similarities = cosine_similarity(response_vector, self.topic_vectors[question_key])
        similarities = similarities.flatten()

        # 최고 유사도 토픽 찾기
        best_idx = np.argmax(similarities)
        best_similarity = similarities[best_idx]

        # 임계값 체크
        if best_similarity >= self.similarity_threshold:
            matched_topic = self.master_topics[question_key][best_idx]
            return matched_topic, best_similarity
        else:
            return None, best_similarity

    def match_batch(self, responses: List[str], question_key: str,
                    show_progress: bool = False) -> Dict:
        """
        배치 응답 매칭

        Returns:
            {
                'topic_counts': {topic_id: count},
                'topic_details': {topic_id: topic_dict},
                'unmatched_count': int,
                'total_responses': int,
                'avg_similarity': float
            }
        """
        if question_key not in self.master_topics:
            return {
                'topic_counts': {},
                'topic_details': {},
                'unmatched_count': 0,
                'total_responses': 0,
                'avg_similarity': 0.0
            }

        topic_counts = {}
        unmatched_count = 0
        similarities = []
        total_responses = len(responses)

        # 토픽 딕셔너리 초기화
        topic_details = {
            topic['id']: topic for topic in self.master_topics[question_key]
        }

        for i, response in enumerate(responses):
            if show_progress and i % 500 == 0:
                print(f"  처리 중: {i}/{total_responses} ({i/total_responses*100:.1f}%)", end='\r')

            matched_topic, similarity = self.match_response(response, question_key)
            similarities.append(similarity)

            if matched_topic:
                topic_id = matched_topic['id']
                topic_counts[topic_id] = topic_counts.get(topic_id, 0) + 1
            else:
                unmatched_count += 1

        if show_progress:
            print()  # 줄바꿈

        return {
            'topic_counts': topic_counts,
            'topic_details': topic_details,
            'unmatched_count': unmatched_count,
            'total_responses': total_responses,
            'avg_similarity': np.mean(similarities) if similarities else 0.0
        }

    def format_results(self, match_result: Dict) -> pd.DataFrame:
        """매칭 결과를 DataFrame으로 포맷"""
        topic_counts = match_result['topic_counts']
        topic_details = match_result['topic_details']
        total_responses = match_result['total_responses']

        if total_responses == 0:
            return pd.DataFrame()

        rows = []
        for topic_id, count in topic_counts.items():
            topic = topic_details[topic_id]
            percentage = (count / total_responses) * 100

            rows.append({
                '순위': topic_id,
                '주제': topic['name'],
                '키워드': topic['keywords'],
                '응답수': count,
                '비율(%)': round(percentage, 1)
            })

        # 기타 추가
        if match_result['unmatched_count'] > 0:
            percentage = (match_result['unmatched_count'] / total_responses) * 100
            rows.append({
                '순위': 999,
                '주제': '기타 (매칭 불가)',
                '키워드': '-',
                '응답수': match_result['unmatched_count'],
                '비율(%)': round(percentage, 1)
            })

        df = pd.DataFrame(rows)
        df = df.sort_values('응답수', ascending=False).reset_index(drop=True)

        return df


def test_matcher():
    """매칭 엔진 테스트"""
    print("\n=== TopicMatcher 테스트 ===\n")

    matcher = TopicMatcher('master_topics_final_rebuild.xlsx')

    # 샘플 응답 테스트
    test_responses = [
        "전략에 대한 공감이 부족합니다",
        "업무 프로세스가 비효율적입니다",
        "보고 체계가 너무 복잡합니다"
    ]

    print("\n샘플 응답 매칭 테스트:")
    for response in test_responses:
        matched_topic, similarity = matcher.match_response(response, 'Q_4-1')
        print(f"\n응답: {response}")
        if matched_topic:
            print(f"  → 매칭: {matched_topic['name']} (유사도: {similarity:.3f})")
        else:
            print(f"  → 매칭 안됨 (유사도: {similarity:.3f})")


if __name__ == "__main__":
    test_matcher()
