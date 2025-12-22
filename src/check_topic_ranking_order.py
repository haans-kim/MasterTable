#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
토픽 순위(순서) 동일 여부 상세 확인
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd

# 결과 파일 로드
file_path = 'CJ_voice_on_demographic_by_question_20251024_095816.xlsx'
xl = pd.ExcelFile(file_path)

print("="*80)
print("Q43.1 긍정적 인식 - 전체 토픽 순위 비교")
print("="*80)

df_q43 = pd.read_excel(file_path, sheet_name='Q43.1_긍정적 인식', header=None)

# 각 그룹의 전체 토픽 순위 추출
groups_data = {}
current_group = None
data_rows = []

for idx, row in df_q43.iterrows():
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
            'topic': str(row[1]) if pd.notna(row[1]) else '-',
            'count': str(row[4]) if pd.notna(row[4]) else '-',
            'pct': str(row[5]) if pd.notna(row[5]) else '-'
        })

# 마지막 그룹 추가
if current_group and data_rows:
    groups_data[current_group] = data_rows

# 상위 5개 토픽 순위 비교
print("\n[상위 5개 토픽 순위 비교]")
print("-"*80)

# 헤더 출력
max_groups = 4  # 한 번에 4개 그룹씩 비교
group_names = list(groups_data.keys())

for batch_start in range(0, len(group_names), max_groups):
    batch_groups = group_names[batch_start:batch_start + max_groups]

    print(f"\n순위", end="")
    for g_name in batch_groups:
        print(f" | {g_name[:25]:<25}", end="")
    print()
    print("-"*80)

    for rank in range(1, 6):
        print(f" {rank}  ", end="")
        for g_name in batch_groups:
            topic_data = groups_data[g_name]
            topic_item = next((t for t in topic_data if t['rank'] == rank), None)
            if topic_item:
                topic_name = topic_item['topic'][:23]
                count = topic_item['count']
                print(f" | {topic_name:<23} ", end="")
            else:
                print(f" | {'-':<23} ", end="")
        print()

# 토픽 순서가 동일한지 확인
print("\n" + "="*80)
print("토픽 순위 동일성 검증")
print("="*80)

# 첫 번째 그룹을 기준으로 비교
reference_group = group_names[0]
reference_topics = [t['topic'] for t in groups_data[reference_group][:10]]

print(f"\n기준 그룹: {reference_group}")
print(f"토픽 순서: {', '.join([f'{i+1}.{t[:15]}' for i, t in enumerate(reference_topics[:5])])}")

differences = []
for g_name in group_names[1:]:
    g_topics = [t['topic'] for t in groups_data[g_name][:10]]

    # 순서가 동일한지 확인
    if g_topics == reference_topics:
        status = "⚠️ 동일"
    else:
        status = "✓ 다름"
        differences.append(g_name)

    print(f"\n{g_name}: {status}")
    if status == "✓ 다름":
        # 차이점 상세 표시
        print(f"  토픽 순서: {', '.join([f'{i+1}.{t[:15]}' for i, t in enumerate(g_topics[:5])])}")

        # 순위가 다른 항목 찾기
        diff_ranks = []
        for i in range(min(len(reference_topics), len(g_topics))):
            if reference_topics[i] != g_topics[i]:
                diff_ranks.append(i+1)

        if diff_ranks:
            print(f"  차이 발생 순위: {', '.join(map(str, diff_ranks[:5]))}")

# 최종 결론
print("\n" + "="*80)
print("최종 결론:")
print("="*80)

if len(differences) == len(group_names) - 1:
    print("✓ 모든 그룹의 토픽 순위가 다릅니다 (정상)")
elif len(differences) == 0:
    print("⚠️ 문제: 모든 그룹의 토픽 순위가 동일합니다!")
    print("   -> 마스터 토픽 매칭이 그룹별로 차별화되지 않고 있습니다.")
else:
    print(f"⚠️ 일부 그룹만 차이가 있습니다 ({len(differences)}/{len(group_names)-1}개 그룹)")

print("\n다른 순위를 가진 그룹 수:", len(differences))
print(f"동일한 순위를 가진 그룹 수: {len(group_names) - 1 - len(differences)}")
