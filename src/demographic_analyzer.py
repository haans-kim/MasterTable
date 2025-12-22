#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CJ 컬처서베이 인구통계학적 변수별 분석
- 연령별 분석: 20대, 30대, 40대, 50대 이상
- 성별 분석: 남성, 여성
- 직책별 분석: 리더, 구성원
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd
import numpy as np
from konlpy.tag import Okt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from datetime import datetime


class DemographicAnalyzer:
    def __init__(self):
        self.okt = Okt()

        # 문항 매핑
        self.question_map = {
            'VALUE-UP 필요성 공감 어려운 이유': 'Q_4-1',
            '회사의 실천준비 미흡 이유': 'Q_16-1',
            '목표달성 의지 부족 이유': 'Q_17-1',
            '프로세스 비효율성': 'Q_20-1',
            '긍정적 인식': 'Q_43-긍정',
            '개선 필요사항': 'Q_43-개선점'
        }

        # 마스터 토픽 시트 매핑
        self.master_sheet_map = {
            'VALUE-UP 필요성 공감 어려운 이유': 'Q4',
            '회사의 실천준비 미흡 이유': 'Q16',
            '목표달성 의지 부족 이유': 'Q17',
            '프로세스 비효율성': 'Q20',
            '긍정적 인식': 'Q43.1',
            '개선 필요사항': 'Q43.2'
        }

        # 분석 대상 그룹 정의
        self.demographic_groups = {
            '연령': ['20대', '30대', '40대', '50대 이상'],
            '성별': ['남성', '여성'],
            '직책': ['리더', '구성원']
        }

    def load_data(self):
        """데이터 로드"""
        print("\n=== 데이터 로드 중 ===")

        # Raw 데이터 로드
        self.df = pd.read_excel('2025 CJ Voice On_주관식 분석용_251024.xlsx')
        print(f"✓ 전체 응답: {len(self.df):,}명")

        # 마스터 토픽 로드
        self.master_topics = {}
        master_file = 'master_topics_final_rebuild.xlsx'

        for q_name, sheet_name in self.master_sheet_map.items():
            try:
                df_topic = pd.read_excel(master_file, sheet_name=sheet_name)
                self.master_topics[q_name] = df_topic
                print(f"  ✓ {q_name}: {len(df_topic)}개 마스터 토픽")
            except Exception as e:
                print(f"  ✗ {sheet_name} 시트 로드 실패: {e}")

        # 분포 확인
        print(f"\n=== 인구통계학적 변수 분포 ===")
        print(f"연령: {dict(self.df['연령'].value_counts().sort_index())}")
        print(f"성별: {dict(self.df['성별'].value_counts())}")
        print(f"직책: {dict(self.df['직책'].value_counts())}")

        return True

    def preprocess_text(self, text):
        """텍스트 전처리"""
        if pd.isna(text) or text == '' or text == ' ':
            return ''

        # 특수문자 제거
        text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', str(text))

        # 형태소 분석
        try:
            tokens = self.okt.nouns(text)
            tokens = [t for t in tokens if len(t) > 1]
            return ' '.join(tokens)
        except:
            return ''

    def filter_demographic_data(self, demographic_var, demographic_value):
        """인구통계학적 변수별 데이터 필터링"""
        filtered_df = self.df[self.df[demographic_var] == demographic_value].copy()
        return filtered_df

    def match_to_master_topics(self, texts, question):
        """마스터 토픽에 매칭"""
        master_df = self.master_topics[question]

        # TF-IDF 벡터화
        vectorizer = TfidfVectorizer(max_features=100, ngram_range=(1, 2))

        try:
            # 마스터 토픽 키워드로 벡터 공간 생성
            master_keywords = []
            for _, row in master_df.iterrows():
                keywords = row['키워드'].replace(', ', ' ')
                topic = row['주제'].replace(' ', '')
                master_keywords.append(f"{keywords} {topic}")

            # 전체 텍스트 결합
            all_texts = texts + master_keywords
            tfidf_matrix = vectorizer.fit_transform(all_texts)

            # 각 응답을 마스터 토픽에 할당
            response_vectors = tfidf_matrix[:len(texts)]
            master_vectors = tfidf_matrix[len(texts):]

            # 코사인 유사도 계산
            similarities = cosine_similarity(response_vectors, master_vectors)

            # 각 응답을 가장 유사한 마스터 토픽에 할당
            topic_counts = {}
            for i, sim_scores in enumerate(similarities):
                best_topic_idx = np.argmax(sim_scores)
                topic_name = master_df.iloc[best_topic_idx]['주제']
                topic_keywords = master_df.iloc[best_topic_idx]['키워드']
                topic_description = master_df.iloc[best_topic_idx].get('설명', '')

                if topic_name not in topic_counts:
                    topic_counts[topic_name] = {
                        'count': 0,
                        'keywords': topic_keywords,
                        'description': topic_description
                    }
                topic_counts[topic_name]['count'] += 1

        except:
            # 벡터화 실패 시 기본 처리
            topic_counts = {
                master_df.iloc[0]['주제']: {
                    'count': len(texts),
                    'keywords': master_df.iloc[0]['키워드'],
                    'description': master_df.iloc[0].get('설명', '')
                }
            }

        # 결과 데이터프레임 생성
        results = []
        total = sum(tc['count'] for tc in topic_counts.values())

        for topic, data in topic_counts.items():
            results.append({
                '토픽': topic,
                '키워드': data['keywords'],
                '내용': data.get('description', ''),
                '응답수': data['count'],
                '비율(%)': round(data['count'] / total * 100, 1)
            })

        # 응답수 기준 정렬
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values('응답수', ascending=False)
        results_df['순위'] = range(1, len(results_df) + 1)

        return results_df[['순위', '토픽', '키워드', '내용', '응답수', '비율(%)']]

    def analyze_group(self, data, group_name):
        """그룹 분석"""
        print(f"\n{'='*60}")
        print(f"분석 중: {group_name}")
        print(f"응답자: {len(data):,}명")
        print('='*60)

        results = {}

        for q_name, col_name in self.question_map.items():
            print(f"\n  [{q_name}]")

            # 유효 응답 추출
            responses = data[col_name].dropna()
            responses = responses[responses != ' ']
            responses = responses[responses != '']

            if len(responses) == 0:
                print(f"    ✗ 유효 응답 없음")
                results[q_name] = pd.DataFrame({
                    '순위': [1],
                    '토픽': ['응답 없음'],
                    '키워드': ['-'],
                    '내용': ['해당 문항에 대한 응답이 없음'],
                    '응답수': [0],
                    '비율(%)': [0.0]
                })
                continue

            print(f"    ✓ 유효 응답: {len(responses):,}개")

            # 텍스트 전처리
            processed = [self.preprocess_text(text) for text in responses]
            processed = [p for p in processed if p]

            if len(processed) == 0:
                results[q_name] = pd.DataFrame({
                    '순위': [1],
                    '토픽': ['응답 없음'],
                    '키워드': ['-'],
                    '내용': ['해당 문항에 대한 응답이 없음'],
                    '응답수': [0],
                    '비율(%)': [0.0]
                })
                continue

            # 마스터 토픽 매칭
            topic_results = self.match_to_master_topics(processed, q_name)

            # 상위 10개 + 기타 처리
            if len(topic_results) > 10:
                top10 = topic_results[:10].copy()
                others_count = topic_results[10:]['응답수'].sum()
                others_pct = topic_results[10:]['비율(%)'].sum()

                others_row = pd.DataFrame({
                    '순위': [11],
                    '토픽': ['기타'],
                    '키워드': ['기타 의견'],
                    '내용': ['상위 10개 토픽에 포함되지 않는 기타 의견'],
                    '응답수': [others_count],
                    '비율(%)': [others_pct]
                })

                topic_results = pd.concat([top10, others_row], ignore_index=True)

            # 순위 재정렬
            topic_results['순위'] = range(1, len(topic_results) + 1)

            # 백분율 100% 조정
            total_pct = topic_results['비율(%)'].sum()
            if abs(total_pct - 100.0) > 0.01:
                topic_results['비율(%)'] = topic_results['비율(%)'] * (100.0 / total_pct)
                topic_results['비율(%)'] = topic_results['비율(%)'].round(1)

                diff = 100.0 - topic_results['비율(%)'].sum()
                if abs(diff) > 0.01:
                    max_idx = topic_results['응답수'].idxmax()
                    topic_results.loc[max_idx, '비율(%)'] += diff

            results[q_name] = topic_results
            print(f"    ✓ {len(topic_results)}개 토픽 도출")

        return results

    def run_analysis(self):
        """전체 분석 실행"""
        print("\n" + "="*70)
        print("CJ 컬처서베이 인구통계학적 변수별 분석")
        print("="*70)

        # 데이터 로드
        self.load_data()

        # 결과 파일 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f'CJ_voice_on_demographic_analysis_{timestamp}.xlsx'

        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:

            sheet_num = 1

            # 각 인구통계학적 변수별 분석
            for demo_var, demo_values in self.demographic_groups.items():
                print(f"\n\n" + "="*70)
                print(f"{demo_var}별 분석")
                print("="*70)

                for demo_value in demo_values:
                    print(f"\n[{demo_var}: {demo_value}]")

                    # 데이터 필터링
                    demo_data = self.filter_demographic_data(demo_var, demo_value)

                    if len(demo_data) == 0:
                        print(f"  ✗ 데이터 없음")
                        continue

                    # 그룹 분석
                    group_name = f'{demo_var}_{demo_value}'
                    demo_results = self.analyze_group(demo_data, group_name)

                    # 시트명 생성 (특수문자 제거, 31자 제한)
                    safe_name = f"{sheet_num:02d}_{demo_var}_{demo_value}"
                    safe_name = re.sub(r'[^가-힣a-zA-Z0-9_]', '', safe_name)[:31]

                    self.write_to_sheet(writer, safe_name, group_name,
                                      len(demo_data), demo_results)

                    sheet_num += 1

            # 기본 시트 제거
            if 'Sheet' in writer.book.sheetnames:
                writer.book.remove(writer.book['Sheet'])

        print("\n\n" + "="*70)
        print("✅ 분석 완료!")
        print(f"✅ 결과 파일: {output_file}")
        print("="*70)

        return output_file

    def write_to_sheet(self, writer, sheet_name, group_name, total_count, results):
        """엑셀 시트에 결과 작성"""
        current_row = 0
        worksheet = writer.book.create_sheet(sheet_name)

        # 제목
        title_df = pd.DataFrame([[group_name],
                                [f'응답자: {total_count:,}명'],
                                ['']])
        title_df.to_excel(writer, sheet_name=sheet_name,
                        startrow=current_row, index=False, header=False)
        current_row += 4

        # 각 문항별 결과
        for q_name, df in results.items():
            # 문항 제목
            q_title = pd.DataFrame([[f'■ {q_name}']])
            q_title.to_excel(writer, sheet_name=sheet_name,
                           startrow=current_row, index=False, header=False)
            current_row += 1

            # 데이터
            df.to_excel(writer, sheet_name=sheet_name,
                      startrow=current_row, index=False)
            current_row += len(df) + 1

            # 합계
            total_responses = df['응답수'].sum()
            total_pct = df['비율(%)'].sum()
            stats_df = pd.DataFrame({
                '순위': [''],
                '토픽': ['합계'],
                '키워드': [''],
                '내용': [''],
                '응답수': [total_responses],
                '비율(%)': [round(total_pct, 1)]
            })
            stats_df.to_excel(writer, sheet_name=sheet_name,
                            startrow=current_row, index=False, header=False)
            current_row += 3


def main():
    analyzer = DemographicAnalyzer()
    result_file = analyzer.run_analysis()

    print(f"\n최종 결과: {result_file}")


if __name__ == "__main__":
    main()
