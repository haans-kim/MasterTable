#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
계열사별 토픽 분석 시스템
- 각 계열사별로 6개 문항 분석
- 문항당 10개 토픽 (나머지는 기타)
- 한 시트에 모든 문항 결과 포함
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

class CompanyTopicAnalyzer:
    def __init__(self):
        self.okt = Okt()
        # 문항 정보는 load_data에서 설정

    def load_data(self):
        """데이터 로드"""
        print("=== 데이터 로드 중 ===")

        # 원본 데이터 로드
        self.df = pd.read_excel('주관식 분석 raw data_250929.xlsx')

        # 컬럼명 매핑 (인코딩 문제 해결)
        self.df.columns = ['company', 'Q4', 'Q16', 'Q17', 'Q20', 'Q43_positive', 'Q43_improve']

        # 문항 매핑 업데이트
        self.questions = {
            'VALUE-UP 필요성 공감 어려운 이유': 'Q4',
            '회사의 실천준비 미흡 이유': 'Q16',
            '목표달성 의지 부족 이유': 'Q17',
            '프로세스 비효율성': 'Q20',
            '긍정적 인식': 'Q43_positive',
            '개선 필요사항': 'Q43_improve'
        }

        # 계열사 목록
        self.companies = self.df['company'].unique()
        print(f"- Total {len(self.companies)} companies found")

        # 마스터 토픽 로드
        self.master_topics = {}
        master_file = 'master_topics_final_rebuild.xlsx'

        for q_name, col_name in self.questions.items():
            sheet_map = {
                'VALUE-UP 필요성 공감 어려운 이유': 'Q4',
                '회사의 실천준비 미흡 이유': 'Q16',
                '목표달성 의지 부족 이유': 'Q17',
                '프로세스 비효율성': 'Q20',
                '긍정적 인식': 'Q43.1',
                '개선 필요사항': 'Q43.2'
            }
            sheet_name = sheet_map[q_name]

            try:
                df_topic = pd.read_excel(master_file, sheet_name=sheet_name)
                self.master_topics[q_name] = df_topic
                print(f"  - {q_name}: {len(df_topic)}개 마스터 토픽")
            except:
                print(f"  ⚠ {sheet_name} 시트 로드 실패")

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
            # 1글자 제거
            tokens = [t for t in tokens if len(t) > 1]
            return ' '.join(tokens)
        except:
            return ''

    def analyze_company(self, company_name):
        """특정 계열사 분석"""
        print(f"\n분석 중: {company_name}")

        # 해당 계열사 데이터 필터링
        company_df = self.df[self.df['company'] == company_name].copy()
        total_count = len(company_df)
        print(f"  전체 응답자: {total_count}명")

        results = {}

        # 각 문항별 분석
        for q_name, col_name in self.questions.items():
            print(f"\n  [{q_name}]")

            # 유효 응답 추출
            responses = company_df[col_name].dropna()
            responses = responses[responses != ' ']
            responses = responses[responses != '']

            if len(responses) == 0:
                print(f"    - 유효 응답 없음")
                results[q_name] = pd.DataFrame({
                    '순위': [1],
                    '토픽': ['응답 없음'],
                    '키워드': ['-'],
                    '내용': ['해당 문항에 대한 응답이 없음'],
                    '응답수': [0],
                    '비율(%)': [0.0]
                })
                continue

            print(f"    - 유효 응답: {len(responses)}개")

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

                # 기타 항목 추가
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

            # 백분율 합 100% 조정
            total_pct = topic_results['비율(%)'].sum()
            if abs(total_pct - 100.0) > 0.01:
                topic_results['비율(%)'] = topic_results['비율(%)'] * (100.0 / total_pct)
                topic_results['비율(%)'] = topic_results['비율(%)'].round(1)

                # 반올림 오차 조정
                diff = 100.0 - topic_results['비율(%)'].sum()
                if abs(diff) > 0.01:
                    max_idx = topic_results['응답수'].idxmax()
                    topic_results.loc[max_idx, '비율(%)'] += diff

            results[q_name] = topic_results
            print(f"    - {len(topic_results)}개 토픽 도출")

        return results

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

    def create_company_report(self, company_name, results):
        """계열사별 리포트 생성"""

        # Excel 파일명 (특수문자 제거)
        safe_name = re.sub(r'[^가-힣a-zA-Z0-9]', '_', company_name)
        filename = f'분석결과_{safe_name}.xlsx'

        with pd.ExcelWriter(filename, engine='openpyxl') as writer:

            # 단일 시트에 모든 문항 결과
            current_row = 0
            worksheet = writer.book.create_sheet('분석결과')

            for q_name, df in results.items():
                # 문항 제목
                title_df = pd.DataFrame({
                    'A': [f'■ {q_name}'],
                    'B': [''],
                    'C': [''],
                    'D': [''],
                    'E': ['']
                })
                title_df.to_excel(writer, sheet_name='분석결과',
                                startrow=current_row, index=False, header=False)
                current_row += 1

                # 컬럼 헤더
                df.to_excel(writer, sheet_name='분석결과',
                          startrow=current_row, index=False)
                current_row += len(df) + 2  # 데이터 + 헤더 + 간격

                # 간격 추가
                current_row += 1

            # 기본 시트 제거
            if 'Sheet' in writer.book.sheetnames:
                writer.book.remove(writer.book['Sheet'])

        return filename

    def analyze_all_companies(self):
        """전체 그룹 및 계열사 분석"""

        print("\n" + "=" * 60)
        print("전체 그룹 및 계열사 분석 시작")
        print("=" * 60)

        # 통합 Excel 파일 생성
        output_file = f'CJ그룹_전체_분석결과_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'

        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:

            # 1. 목차 시트 생성
            toc_data = []
            toc_data.append(['CJ그룹 컬처서베이 주관식 분석 결과'])
            toc_data.append([''])
            toc_data.append(['■ 목차'])
            toc_data.append(['순번', '구분'])
            toc_data.append([1, '전체 그룹 분석'])

            for i, company in enumerate(self.companies, 2):
                toc_data.append([i, company])

            toc_df = pd.DataFrame(toc_data)
            toc_df.to_excel(writer, sheet_name='목차', index=False, header=False)

            # 2. 전체 그룹 분석 (모든 응답자 통합)
            print("\n[전체 그룹 분석]")
            print("-" * 40)
            group_results = self.analyze_group_total()

            # 전체 그룹 시트 생성
            current_row = 0
            worksheet = writer.book.create_sheet('전체그룹')

            # 제목
            title_df = pd.DataFrame([['CJ그룹 전체 분석 결과'],
                                    [f'전체 응답자: {len(self.df)}명'],
                                    ['']])
            title_df.to_excel(writer, sheet_name='전체그룹',
                            startrow=current_row, index=False, header=False)
            current_row += 4

            # 각 문항별 결과
            for q_name, df in group_results.items():
                # 문항 제목
                q_title = pd.DataFrame([[f'■ {q_name}']])
                q_title.to_excel(writer, sheet_name='전체그룹',
                               startrow=current_row, index=False, header=False)
                current_row += 1

                # 데이터
                df.to_excel(writer, sheet_name='전체그룹',
                          startrow=current_row, index=False)
                current_row += len(df) + 1

                # 통계 정보 추가
                total_responses = df['응답수'].sum()
                total_pct = df['비율(%)'].sum()
                stats_df = pd.DataFrame({
                    '순위': [''],
                    '토픽': ['합계'],
                    '키워드': [''],
                    '내용': [''],
                    '응답수': [total_responses],
                    '비율(%)': [total_pct]
                })
                stats_df.to_excel(writer, sheet_name='전체그룹',
                                startrow=current_row, index=False, header=False)
                current_row += 3

            # 3. 각 계열사별 분석
            for i, company in enumerate(self.companies, 1):
                print(f"\n[{i}/{len(self.companies)}] {company}")
                print("-" * 40)

                # 계열사 분석
                results = self.analyze_company(company)

                # 시트명 안전하게 처리 (31자 제한, 특수문자 제거)
                safe_name = re.sub(r'[^가-힣a-zA-Z0-9]', '', company)[:20]
                sheet_name = f'{i:02d}_{safe_name}'

                # 계열사별 시트 생성
                current_row = 0
                worksheet = writer.book.create_sheet(sheet_name)

                # 제목
                company_df = self.df[self.df['company'] == company]
                title_df = pd.DataFrame([[f'{company} 분석 결과'],
                                        [f'응답자: {len(company_df)}명'],
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

                    # 통계 정보 추가
                    total_responses = df['응답수'].sum()
                    total_pct = df['비율(%)'].sum()
                    stats_df = pd.DataFrame({
                        '순위': [''],
                        '토픽': ['합계'],
                        '키워드': [''],
                        '내용': [''],
                        '응답수': [total_responses],
                        '비율(%)': [total_pct]
                    })
                    stats_df.to_excel(writer, sheet_name=sheet_name,
                                    startrow=current_row, index=False, header=False)
                    current_row += 3

                print(f"  ✓ 시트 생성: {sheet_name}")

            # 기본 시트 제거
            if 'Sheet' in writer.book.sheetnames:
                writer.book.remove(writer.book['Sheet'])

        print("\n" + "=" * 60)
        print(f"✓ 전체 분석 완료!")
        print(f"✓ 결과 파일: {output_file}")
        print("=" * 60)

        return output_file

    def analyze_group_total(self):
        """전체 그룹 통합 분석"""
        results = {}

        # 각 문항별 분석
        for q_name, col_name in self.questions.items():
            print(f"  [{q_name}]")

            # 유효 응답 추출
            responses = self.df[col_name].dropna()
            responses = responses[responses != ' ']
            responses = responses[responses != '']

            if len(responses) == 0:
                print(f"    - 유효 응답 없음")
                results[q_name] = pd.DataFrame({
                    '순위': [1],
                    '토픽': ['응답 없음'],
                    '키워드': ['-'],
                    '내용': ['해당 문항에 대한 응답이 없음'],
                    '응답수': [0],
                    '비율(%)': [0.0]
                })
                continue

            print(f"    - 유효 응답: {len(responses)}개")

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

                # 기타 항목 추가
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

            # 백분율 합 100% 조정
            total_pct = topic_results['비율(%)'].sum()
            if abs(total_pct - 100.0) > 0.01:
                topic_results['비율(%)'] = topic_results['비율(%)'] * (100.0 / total_pct)
                topic_results['비율(%)'] = topic_results['비율(%)'].round(1)

                # 반올림 오차 조정
                diff = 100.0 - topic_results['비율(%)'].sum()
                if abs(diff) > 0.01:
                    max_idx = topic_results['응답수'].idxmax()
                    topic_results.loc[max_idx, '비율(%)'] += diff

            results[q_name] = topic_results
            print(f"    - {len(topic_results)}개 토픽 도출")

        return results

def main():
    print("=" * 60)
    print("CJ그룹 계열사별 주관식 문항 분석")
    print("- 전체 그룹 분석 포함")
    print("- 문항당 10개 토픽 추출")
    print("- 나머지는 기타로 분류")
    print("=" * 60)

    analyzer = CompanyTopicAnalyzer()

    # 데이터 로드
    if analyzer.load_data():
        # 전체 계열사 분석
        result_file = analyzer.analyze_all_companies()

        # 결과 요약
        print("\n✓ 분석 완료!")
        print(f"✓ 생성 파일: {result_file}")

if __name__ == "__main__":
    main()