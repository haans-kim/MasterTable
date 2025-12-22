#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from collections import Counter
import re

def analyze_master_topics_file():
    """마스터 토픽 파일 종합 분석"""

    file_path = r'C:\Project\CJ_Culture\master_topics_final_v3.xlsx'
    print("="*80)
    print("MASTER TOPICS FILE COMPREHENSIVE ANALYSIS")
    print("="*80)

    # 파일 읽기
    try:
        xl = pd.ExcelFile(file_path)
        print(f"[OK] Successfully loaded file: {file_path}")
        print(f"[OK] Total sheets: {len(xl.sheet_names)}")
        print(f"[OK] Sheet names: {', '.join(xl.sheet_names)}")
    except Exception as e:
        print(f"[ERROR] Error loading file: {e}")
        return

    print("\n" + "="*80)
    print("1. STRUCTURE AND CONTENT ANALYSIS")
    print("="*80)

    all_issues = []
    summary_data = {}

    # 각 시트 분석
    for sheet_name in xl.sheet_names:
        print(f"\n--- ANALYZING SHEET: {sheet_name} ---")

        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"[OK] Rows: {len(df)}, Columns: {len(df.columns)}")
            print(f"[OK] Column names: {list(df.columns)}")

            if sheet_name == '요약':
                summary_data = analyze_summary_sheet(df)
                continue

            # 개별 시트 분석
            sheet_issues = analyze_individual_sheet(df, sheet_name)
            all_issues.extend([(sheet_name, issue) for issue in sheet_issues])

        except Exception as e:
            error_msg = f"Error reading sheet {sheet_name}: {e}"
            print(f"[ERROR] {error_msg}")
            all_issues.append((sheet_name, error_msg))

    print("\n" + "="*80)
    print("2. QUALITY ASSESSMENT SUMMARY")
    print("="*80)

    # 전체 이슈 요약
    if all_issues:
        print("\n[ISSUES] IDENTIFIED ISSUES:")
        for sheet_name, issue in all_issues:
            print(f"  [{sheet_name}] {issue}")
    else:
        print("[OK] No major issues identified")

    # 요약 통계
    if summary_data:
        print(f"\n[STATS] SUMMARY STATISTICS:")
        for key, value in summary_data.items():
            print(f"  {key}: {value}")

    print("\n" + "="*80)
    print("3. RECOMMENDATIONS")
    print("="*80)

    recommendations = generate_recommendations(all_issues)
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")

def analyze_summary_sheet(df):
    """요약 시트 분석"""
    print("Summary sheet structure:")
    print(df.head().to_string())

    summary_stats = {
        "Total questions analyzed": len(df) if not df.empty else 0,
        "Summary sheet format": "Standard" if not df.empty else "Empty or Invalid"
    }

    return summary_stats

def analyze_individual_sheet(df, sheet_name):
    """개별 시트 상세 분석"""
    issues = []

    # 1. 필수 컬럼 체크
    required_columns = ['순위', '주제', '키워드', '설명', '응답수', '비율(%)']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        issues.append(f"Missing required columns: {missing_cols}")

    if df.empty:
        issues.append("Sheet is empty")
        return issues

    # 2. 주제명 품질 체크
    topic_issues = check_topic_quality(df, sheet_name)
    issues.extend(topic_issues)

    # 3. 키워드 품질 체크
    keyword_issues = check_keyword_quality(df)
    issues.extend(keyword_issues)

    # 4. 설명 품질 체크
    description_issues = check_description_quality(df, sheet_name)
    issues.extend(description_issues)

    # 5. 비율 합계 체크
    percentage_issues = check_percentage_sum(df)
    issues.extend(percentage_issues)

    # 6. 중복 체크
    duplicate_issues = check_duplicates(df)
    issues.extend(duplicate_issues)

    # 7. 데이터 일관성 체크
    consistency_issues = check_data_consistency(df)
    issues.extend(consistency_issues)

    print(f"  [OK] Topics: {len(df)}")
    print(f"  [INFO] Issues found: {len(issues)}")

    return issues

def check_topic_quality(df, sheet_name):
    """주제명 품질 체크"""
    issues = []

    if '주제' not in df.columns:
        return ["No '주제' column found"]

    topics = df['주제'].dropna()

    # 길이 체크
    too_long = topics[topics.str.len() > 50]
    if not too_long.empty:
        issues.append(f"Topics too long (>50 chars): {len(too_long)} items")

    too_short = topics[topics.str.len() < 3]
    if not too_short.empty:
        issues.append(f"Topics too short (<3 chars): {len(too_short)} items")

    # 번호 패턴 체크 (제거되어야 함)
    numbered_topics = topics[topics.str.contains(r'\(\d+\)$', na=False)]
    if not numbered_topics.empty:
        issues.append(f"Topics still contain numbering: {list(numbered_topics.head(3))}")

    # 일관성 체크 (문항별 특성)
    if sheet_name == 'Q4' and topics.str.contains('VALUE-UP').sum() == 0:
        issues.append("Q4 topics should reference VALUE-UP context")

    return issues

def check_keyword_quality(df):
    """키워드 품질 체크"""
    issues = []

    if '키워드' not in df.columns:
        return ["No '키워드' column found"]

    keywords = df['키워드'].dropna()

    for idx, keyword_str in keywords.items():
        if pd.isna(keyword_str):
            continue

        keyword_list = [k.strip() for k in str(keyword_str).split(',')]

        # 키워드 개수 체크
        if len(keyword_list) != 3:
            issues.append(f"Row {idx+1}: Expected 3 keywords, found {len(keyword_list)}")

        # 키워드 길이 체크
        for kw in keyword_list:
            if len(kw) < 2:
                issues.append(f"Row {idx+1}: Keyword too short: '{kw}'")
            elif len(kw) > 15:
                issues.append(f"Row {idx+1}: Keyword too long: '{kw}'")

    return issues

def check_description_quality(df, sheet_name):
    """설명 품질 체크"""
    issues = []

    if '설명' not in df.columns:
        return ["No '설명' column found"]

    descriptions = df['설명'].dropna()

    # 길이 체크
    too_short = descriptions[descriptions.str.len() < 20]
    if not too_short.empty:
        issues.append(f"Descriptions too short (<20 chars): {len(too_short)} items")

    too_long = descriptions[descriptions.str.len() > 200]
    if not too_long.empty:
        issues.append(f"Descriptions too long (>200 chars): {len(too_long)} items")

    # 문맥 관련성 체크
    context_keywords = {
        'Q4': ['VALUE-UP', '전략', '필요성', '공감'],
        'Q16': ['실천', '준비', '실행', '조직'],
        'Q17': ['목표', '달성', '의지'],
        'Q20': ['프로세스', '효율', '보고', '업무'],
        'Q43.1': ['긍정', '인식', '문화'],
        'Q43.2': ['개선', '필요', '혁신']
    }

    if sheet_name in context_keywords:
        expected_keywords = context_keywords[sheet_name]
        contextual_descriptions = 0

        for desc in descriptions:
            if any(keyword in str(desc) for keyword in expected_keywords):
                contextual_descriptions += 1

        context_ratio = contextual_descriptions / len(descriptions) if len(descriptions) > 0 else 0
        if context_ratio < 0.7:
            issues.append(f"Low contextual relevance: {context_ratio:.1%} of descriptions contain expected keywords")

    return issues

def check_percentage_sum(df):
    """비율 합계 체크"""
    issues = []

    if '비율(%)' not in df.columns:
        return ["No '비율(%)' column found"]

    percentages = df['비율(%)'].dropna()
    total = percentages.sum()

    if abs(total - 100) > 0.1:  # 0.1% 오차 허용
        issues.append(f"Percentage sum is {total:.2f}%, should be 100%")

    # 개별 비율 체크
    invalid_percentages = percentages[(percentages < 0) | (percentages > 100)]
    if not invalid_percentages.empty:
        issues.append(f"Invalid percentage values: {len(invalid_percentages)} items")

    return issues

def check_duplicates(df):
    """중복 체크"""
    issues = []

    if '주제' in df.columns:
        duplicated_topics = df[df['주제'].duplicated(keep=False)]
        if not duplicated_topics.empty:
            issues.append(f"Duplicate topic names: {len(duplicated_topics)} items")

    if '키워드' in df.columns:
        duplicated_keywords = df[df['키워드'].duplicated(keep=False)]
        if not duplicated_keywords.empty:
            issues.append(f"Duplicate keyword sets: {len(duplicated_keywords)} items")

    return issues

def check_data_consistency(df):
    """데이터 일관성 체크"""
    issues = []

    # 순위 연속성 체크
    if '순위' in df.columns:
        ranks = df['순위'].dropna().astype(int)
        expected_ranks = list(range(1, len(ranks) + 1))
        if list(ranks) != expected_ranks:
            issues.append("Rank numbers are not consecutive")

    # 응답수와 비율 일관성 체크
    if '응답수' in df.columns and '비율(%)' in df.columns:
        responses = df['응답수'].dropna()
        percentages = df['비율(%)'].dropna()

        if len(responses) == len(percentages):
            total_responses = responses.sum()
            calculated_percentages = (responses / total_responses * 100).round(2)
            actual_percentages = percentages.round(2)

            # 허용 오차 0.1%
            differences = abs(calculated_percentages - actual_percentages)
            inconsistent = differences > 0.1

            if inconsistent.any():
                issues.append(f"Response count and percentage mismatch: {inconsistent.sum()} items")

    return issues

def generate_recommendations(all_issues):
    """개선 권고사항 생성"""
    recommendations = []

    # 이슈 유형별 분류
    issue_types = {}
    for sheet_name, issue in all_issues:
        issue_type = classify_issue_type(issue)
        if issue_type not in issue_types:
            issue_types[issue_type] = []
        issue_types[issue_type].append((sheet_name, issue))

    # 권고사항 생성
    if 'topic_quality' in issue_types:
        recommendations.append("주제명 표준화: 일관된 명명 규칙 적용 및 길이 조정")

    if 'keyword_quality' in issue_types:
        recommendations.append("키워드 품질 개선: 모든 토픽에 정확히 3개 키워드 확보")

    if 'description_quality' in issue_types:
        recommendations.append("설명 품질 향상: 문맥적 관련성 및 적절한 길이 확보")

    if 'percentage_sum' in issue_types:
        recommendations.append("비율 계산 검증: 모든 문항의 비율 합계가 100%가 되도록 조정")

    if 'duplicates' in issue_types:
        recommendations.append("중복 제거: 동일한 주제명 및 키워드 세트 정리")

    if 'data_consistency' in issue_types:
        recommendations.append("데이터 일관성 확보: 순위, 응답수, 비율 간 논리적 일관성 점검")

    if not recommendations:
        recommendations.append("전반적으로 양호한 품질을 유지하고 있음")

    return recommendations

def classify_issue_type(issue):
    """이슈 유형 분류"""
    issue_lower = issue.lower()

    if 'topic' in issue_lower or '주제' in issue_lower:
        return 'topic_quality'
    elif 'keyword' in issue_lower or '키워드' in issue_lower:
        return 'keyword_quality'
    elif 'description' in issue_lower or '설명' in issue_lower:
        return 'description_quality'
    elif 'percentage' in issue_lower or '비율' in issue_lower:
        return 'percentage_sum'
    elif 'duplicate' in issue_lower or '중복' in issue_lower:
        return 'duplicates'
    elif 'rank' in issue_lower or '순위' in issue_lower or 'response' in issue_lower:
        return 'data_consistency'
    else:
        return 'other'

if __name__ == "__main__":
    analyze_master_topics_file()