#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
모든 문항의 토픽 순위 동일 여부 확인
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd

# 결과 파일 로드
file_path = 'CJ_voice_on_demographic_by_question_20251024_095816.xlsx'
xl = pd.ExcelFile(file_path)

def extract_groups_data(df):
    """시트에서 그룹별 토픽 데이터 추출"""
    groups_data = {}
    current_group = None
    data_rows = []

    for idx, row in df.iterrows():
        row_str = ' '.join([str(x) for x in row.values if pd.notna(x)])

        # 그룹명 찾기
        if '■' in row_str:
            if current_group and data_rows:
                groups_data[current_group] = data_rows
            current_group = row_str.replace('■', '').strip()
            data_rows = []
        # 데이터 행 (순위가 숫자인 행)
        elif pd.notna(row[0]) and str(row[0]).isdigit():
            data_rows.append({
                'rank': int(row[0]),
                'topic': str(row[1]) if pd.notna(row[1]) else '-'
            })

    # 마지막 그룹 추가
    if current_group and data_rows:
        groups_data[current_group] = data_rows

    return groups_data

def check_ranking_differences(groups_data):
    """그룹 간 토픽 순위 차이 확인"""
    if not groups_data or len(groups_data) < 2:
        return 0, 0

    group_names = list(groups_data.keys())
    reference_group = group_names[0]
    reference_topics = [t['topic'] for t in groups_data[reference_group][:10]]

    different_count = 0
    for g_name in group_names[1:]:
        g_topics = [t['topic'] for t in groups_data[g_name][:10]]
        if g_topics != reference_topics:
            different_count += 1

    return different_count, len(group_names) - 1

print("="*80)
print("전체 문항별 토픽 순위 차이 검증")
print("="*80)

total_result = {}

for sheet_name in xl.sheet_names:
    print(f"\n{'='*80}")
    print(f"문항: {sheet_name}")
    print('='*80)

    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    groups_data = extract_groups_data(df)

    if not groups_data:
        print("  ⚠️ 데이터 추출 실패")
        continue

    # 상위 5개 토픽만 비교 표시
    print(f"\n{'그룹':<35} {'1위':<20} {'2위':<20} {'3위':<20}")
    print("-"*80)

    for g_name, topics in groups_data.items():
        # 그룹명 짧게
        short_name = g_name.split('(')[0].strip()
        top5_topics = [t['topic'][:18] for t in topics[:5]]

        if len(top5_topics) >= 3:
            print(f"{short_name:<35} {top5_topics[0]:<20} {top5_topics[1]:<20} {top5_topics[2]:<20}")

    # 차이 검증
    different_count, total_count = check_ranking_differences(groups_data)
    total_result[sheet_name] = (different_count, total_count)

    print(f"\n결과: {different_count}/{total_count}개 그룹이 서로 다른 순위")

    if different_count == total_count:
        print("✓ 모든 그룹의 토픽 순위가 다릅니다 (정상)")
    elif different_count == 0:
        print("⚠️ 모든 그룹의 토픽 순위가 동일합니다 (문제 가능성)")
    else:
        print(f"⚠️ 일부 그룹만 차이가 있습니다")

# 전체 요약
print("\n" + "="*80)
print("전체 요약")
print("="*80)

for sheet_name, (diff, total) in total_result.items():
    status = "✓" if diff == total else "⚠️"
    print(f"{status} {sheet_name:<40} {diff}/{total}개 그룹 차이")

# 최종 결론
all_different = all(diff == total for diff, total in total_result.values())

print("\n" + "="*80)
print("최종 결론:")
print("="*80)

if all_different:
    print("✓ 모든 문항에서 그룹별 토픽 순위가 정상적으로 차별화되어 있습니다.")
    print("  각 인구통계 그룹의 특성이 제대로 반영되고 있습니다.")
else:
    print("⚠️ 일부 문항에서 그룹 간 토픽 순위가 동일합니다.")
    print("  마스터 토픽 매칭 로직 검토가 필요할 수 있습니다.")
