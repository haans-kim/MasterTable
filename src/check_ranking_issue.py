#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
응답 순위 동일 여부 확인
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd

# 결과 파일 로드
file_path = 'CJ_voice_on_demographic_analysis_20251024_082242.xlsx'
xl = pd.ExcelFile(file_path)

print("="*70)
print("Q43 문항 응답 순위 비교 (긍정적 인식)")
print("="*70)

# 각 시트에서 Q43 긍정적 인식 부분 추출
q43_results = {}

for sheet_name in xl.sheet_names:
    print(f"\n[{sheet_name}]")

    # 시트 읽기
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

    # "긍정적 인식" 찾기
    positive_idx = None
    for idx, row in df.iterrows():
        if '긍정적 인식' in str(row.values):
            positive_idx = idx
            break

    if positive_idx is not None:
        # 데이터 시작 위치 (제목 다음)
        data_start = positive_idx + 2

        # 데이터 추출 (최대 15행)
        data_df = df.iloc[data_start:data_start+15].copy()
        data_df.columns = ['순위', '토픽', '키워드', '내용', '응답수', '비율(%)']

        # 합계 행 제외
        data_df = data_df[data_df['순위'] != ''].copy()
        data_df = data_df[data_df['토픽'] != '합계'].copy()

        # 상위 5개만 출력
        top5 = data_df.head(5)
        print(f"  상위 5개 토픽:")
        for _, row in top5.iterrows():
            print(f"    {row['순위']}. {row['토픽']} - 응답수: {row['응답수']}, 비율: {row['비율(%)']}%")

        q43_results[sheet_name] = top5

print("\n" + "="*70)
print("순위 비교: 모든 그룹의 1위 토픽이 동일한가?")
print("="*70)

# 1위 토픽 비교
first_ranks = {}
for sheet, df in q43_results.items():
    if len(df) > 0:
        first_topic = df.iloc[0]['토픽']
        first_ranks[sheet] = first_topic
        print(f"{sheet}: {first_topic}")

# 동일 여부 확인
unique_topics = set(first_ranks.values())
if len(unique_topics) == 1:
    print("\n⚠️ 문제 발견: 모든 그룹의 1위 토픽이 동일합니다!")
    print(f"   공통 1위: {list(unique_topics)[0]}")
else:
    print("\n✓ 정상: 그룹별로 다른 1위 토픽이 있습니다.")
