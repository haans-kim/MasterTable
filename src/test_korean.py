#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
한글 출력 테스트 및 마스터 토픽 확인
"""

import pandas as pd
import sys
import io

# 표준 출력 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_master_topics():
    """마스터 토픽 파일 확인"""

    # 파일 읽기
    file = 'master_topics_final_rebuild.xlsx'

    print("=" * 60)
    print("마스터 토픽 파일 검토")
    print("=" * 60)

    # Q16 시트 확인
    df = pd.read_excel(file, sheet_name='Q16')

    print("\n[Q16: 회사의 실천준비 미흡 이유] - 상위 5개")
    print("-" * 60)

    for idx in range(min(5, len(df))):
        row = df.iloc[idx]
        print(f"\n{row['순위']}. {row['주제']}")
        print(f"   키워드: {row['키워드']}")
        print(f"   설명: {row['설명'][:50]}...")
        print(f"   응답수: {row['응답수']}명 ({row['비율(%)']}%)")

    # Q4 시트 확인
    df_q4 = pd.read_excel(file, sheet_name='Q4')

    print("\n\n[Q4: VALUE-UP 필요성 공감 어려운 이유] - 상위 5개")
    print("-" * 60)

    for idx in range(min(5, len(df_q4))):
        row = df_q4.iloc[idx]
        print(f"\n{row['순위']}. {row['주제']}")
        print(f"   키워드: {row['키워드']}")
        print(f"   설명: {row['설명'][:50]}...")
        print(f"   응답수: {row['응답수']}명 ({row['비율(%)']}%)")

if __name__ == "__main__":
    check_master_topics()