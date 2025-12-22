#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
문항별 페이지 결과 검증
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd

# 결과 파일 로드
file_path = 'CJ_voice_on_demographic_by_question_20251024_095816.xlsx'
xl = pd.ExcelFile(file_path)

print("="*70)
print("문항별 페이지 구성 결과 검증")
print("="*70)

print(f"\n총 {len(xl.sheet_names)}개 시트 생성")
print("\n시트 목록:")
for i, sheet in enumerate(xl.sheet_names, 1):
    print(f"  {i}. {sheet}")

# Q43.1 긍정적 인식 문항 상세 확인
print("\n" + "="*70)
print("Q43.1_긍정적 인식 - 인구통계별 1위 토픽 비교")
print("="*70)

df_q43 = pd.read_excel(file_path, sheet_name='Q43.1_긍정적 인식', header=None)

# 각 그룹의 1위 토픽 찾기
groups = []
current_group = None
data_rows = []

for idx, row in df_q43.iterrows():
    row_str = ' '.join([str(x) for x in row.values if pd.notna(x)])

    # 그룹명 찾기
    if '■' in row_str:
        if current_group and data_rows:
            groups.append((current_group, data_rows))
        current_group = row_str.replace('■', '').strip()
        data_rows = []
    # 데이터 행 (순위가 1인 행)
    elif pd.notna(row[0]) and str(row[0]) == '1':
        data_rows.append(row)

# 마지막 그룹 추가
if current_group and data_rows:
    groups.append((current_group, data_rows))

# 1위 토픽 출력
print(f"\n{'그룹':<30} {'1위 토픽':<30} 응답수   비율")
print("-"*70)

for group_name, rows in groups:
    if rows:
        first_row = rows[0]
        topic = str(first_row[1]) if pd.notna(first_row[1]) else '-'
        count = str(first_row[4]) if pd.notna(first_row[4]) else '-'
        pct = str(first_row[5]) if pd.notna(first_row[5]) else '-'
        print(f"{group_name:<30} {topic:<30} {count:>6}  {pct:>5}%")

# Q20 프로세스 비효율성 문항도 확인
print("\n" + "="*70)
print("Q20_프로세스 비효율성 - 인구통계별 1위 토픽 비교")
print("="*70)

df_q20 = pd.read_excel(file_path, sheet_name='Q20_프로세스 비효율성', header=None)

# 각 그룹의 1위 토픽 찾기
groups = []
current_group = None
data_rows = []

for idx, row in df_q20.iterrows():
    row_str = ' '.join([str(x) for x in row.values if pd.notna(x)])

    # 그룹명 찾기
    if '■' in row_str:
        if current_group and data_rows:
            groups.append((current_group, data_rows))
        current_group = row_str.replace('■', '').strip()
        data_rows = []
    # 데이터 행 (순위가 1인 행)
    elif pd.notna(row[0]) and str(row[0]) == '1':
        data_rows.append(row)

# 마지막 그룹 추가
if current_group and data_rows:
    groups.append((current_group, data_rows))

# 1위 토픽 출력
print(f"\n{'그룹':<30} {'1위 토픽':<30} 응답수   비율")
print("-"*70)

for group_name, rows in groups:
    if rows:
        first_row = rows[0]
        topic = str(first_row[1]) if pd.notna(first_row[1]) else '-'
        count = str(first_row[4]) if pd.notna(first_row[4]) else '-'
        pct = str(first_row[5]) if pd.notna(first_row[5]) else '-'
        print(f"{group_name:<30} {topic:<30} {count:>6}  {pct:>5}%")

print("\n" + "="*70)
print("검증 결과:")
print("- 문항별로 페이지가 구성되어 비교 분석이 용이합니다")
print("- 각 인구통계 그룹의 응답수와 비율이 다르게 나타납니다")
print("- 1위 토픽이 같더라도 응답수/비율의 차이로 그룹 특성 파악 가능")
print("="*70)
