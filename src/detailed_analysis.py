#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd

def detailed_sheet_analysis():
    """각 시트별 상세 분석 및 예시 제공"""

    file_path = r'C:\Project\CJ_Culture\master_topics_final_v3.xlsx'
    xl = pd.ExcelFile(file_path)

    print("="*80)
    print("DETAILED SHEET-BY-SHEET ANALYSIS WITH EXAMPLES")
    print("="*80)

    for sheet_name in xl.sheet_names:
        if sheet_name == '요약':
            continue

        print(f"\n{'='*60}")
        print(f"ANALYZING: {sheet_name}")
        print(f"{'='*60}")

        df = pd.read_excel(file_path, sheet_name=sheet_name)

        print(f"Total topics: {len(df)}")
        print(f"Columns: {list(df.columns)}")

        # 샘플 데이터 출력 (처음 5개)
        print(f"\nFirst 5 topics:")
        sample_df = df.head()
        for idx, row in sample_df.iterrows():
            print(f"  {idx+1}. 순위: {row['순위']}")
            print(f"     주제: {row['주제']}")
            print(f"     키워드: {row['키워드']}")
            print(f"     설명: {row['설명'][:80]}...")
            print(f"     응답수: {row['응답수']}, 비율: {row['비율(%)']}%")
            print()

        # 품질 체크
        print("QUALITY CHECKS:")

        # 1. 키워드 체크
        keyword_issues = []
        for idx, row in df.iterrows():
            keywords = str(row['키워드']).split(',')
            keyword_count = len([k.strip() for k in keywords if k.strip()])
            if keyword_count != 3:
                keyword_issues.append(f"Row {idx+1}: {keyword_count} keywords")

        if keyword_issues:
            print(f"  Keyword issues: {len(keyword_issues)} items")
            for issue in keyword_issues[:3]:
                print(f"    - {issue}")
            if len(keyword_issues) > 3:
                print(f"    ... and {len(keyword_issues)-3} more")
        else:
            print("  Keyword quality: OK (all have 3 keywords)")

        # 2. 비율 합계 체크
        percentage_sum = df['비율(%)'].sum()
        print(f"  Percentage sum: {percentage_sum:.2f}% (should be 100%)")

        # 3. 중복 주제 체크
        duplicates = df[df['주제'].duplicated(keep=False)]
        if not duplicates.empty:
            print(f"  Duplicate topics: {len(duplicates)} items")
            unique_duplicates = duplicates['주제'].unique()
            for dup in unique_duplicates[:3]:
                print(f"    - '{dup}'")
            if len(unique_duplicates) > 3:
                print(f"    ... and {len(unique_duplicates)-3} more")
        else:
            print("  Duplicate topics: None")

        # 4. 설명 길이 체크
        short_descriptions = df[df['설명'].str.len() < 20]
        long_descriptions = df[df['설명'].str.len() > 200]

        print(f"  Description length:")
        print(f"    - Too short (<20 chars): {len(short_descriptions)} items")
        print(f"    - Too long (>200 chars): {len(long_descriptions)} items")
        print(f"    - Average length: {df['설명'].str.len().mean():.1f} chars")

        # 5. 문맥 관련성 체크 (간단한 키워드 매칭)
        context_check = analyze_context_relevance(df, sheet_name)
        print(f"  Context relevance: {context_check}")

def analyze_context_relevance(df, sheet_name):
    """문맥 관련성 분석"""

    expected_contexts = {
        'Q4': ['VALUE-UP', '전략', '필요성', '공감', '이유'],
        'Q16': ['실천', '준비', '실행', '조직', '미흡'],
        'Q17': ['목표', '달성', '의지', '부족'],
        'Q20': ['프로세스', '효율', '보고', '업무', '비효율'],
        'Q43.1': ['긍정', '인식', '문화', '좋은'],
        'Q43.2': ['개선', '필요', '혁신', '문제']
    }

    if sheet_name not in expected_contexts:
        return "No context check defined"

    context_keywords = expected_contexts[sheet_name]
    contextual_count = 0

    for _, row in df.iterrows():
        description = str(row['설명']).lower()
        topic = str(row['주제']).lower()
        keywords = str(row['키워드']).lower()

        combined_text = f"{description} {topic} {keywords}"

        if any(keyword.lower() in combined_text for keyword in context_keywords):
            contextual_count += 1

    percentage = (contextual_count / len(df)) * 100 if len(df) > 0 else 0
    return f"{contextual_count}/{len(df)} topics ({percentage:.1f}%) contain relevant context"

if __name__ == "__main__":
    detailed_sheet_analysis()