#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
마스터 토픽 전면 재구축
- 키워드 → 주제 → 설명의 자연스러운 흐름
- 각 문항 맥락에 맞는 주제명과 설명
"""

import pandas as pd
import numpy as np

def rebuild_master_topics():
    """마스터 토픽 재구축"""

    # 입력 파일
    input_file = 'master_topics_final_fixed.xlsx'

    # 각 시트 읽기
    xl = pd.ExcelFile(input_file)
    output_sheets = {}

    # 요약 시트는 그대로
    output_sheets['요약'] = pd.read_excel(input_file, sheet_name='요약')

    # 각 문항별 처리
    for sheet_name in xl.sheet_names:
        if sheet_name == '요약':
            continue

        print(f"\n처리 중: {sheet_name}")
        df = pd.read_excel(input_file, sheet_name=sheet_name)

        # 각 문항별로 주제와 설명 재생성
        if sheet_name == 'Q4':
            df = rebuild_q4(df)
        elif sheet_name == 'Q16':
            df = rebuild_q16(df)
        elif sheet_name == 'Q17':
            df = rebuild_q17(df)
        elif sheet_name == 'Q20':
            df = rebuild_q20(df)
        elif sheet_name == 'Q43.1':
            df = rebuild_q43_1(df)
        elif sheet_name == 'Q43.2':
            df = rebuild_q43_2(df)

        output_sheets[sheet_name] = df
        print(f"  - {len(df)}개 항목 처리 완료")

    # 파일 저장
    output_file = 'master_topics_final_rebuild.xlsx'
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for sheet_name, df in output_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"\n[완료] 재구축된 파일: {output_file}")
    return output_file

def rebuild_q4(df):
    """Q4: VALUE-UP 필요성 공감 어려운 이유 재구축"""

    for idx, row in df.iterrows():
        keywords = row['키워드'].split(', ')

        # 키워드 기반 주제명과 설명 생성
        topic, desc = generate_q4_topic_and_desc(keywords)

        df.loc[idx, '주제'] = topic
        df.loc[idx, '설명'] = desc

    return df

def generate_q4_topic_and_desc(keywords):
    """Q4 키워드 → 주제 → 설명 생성"""

    k1, k2, k3 = keywords[0], keywords[1] if len(keywords) > 1 else '', keywords[2] if len(keywords) > 2 else ''

    # 키워드 조합별 주제와 설명
    if '공감' in keywords and '성장' in keywords:
        topic = "공감대 형성 부족"
        desc = "VALUE-UP 전략의 필요성을 공감하기 어려운 이유로, 성장 전략과 현업의 연관성이 불명확하여 구성원들의 공감대가 형성되지 못함"
    elif '공감' in keywords and '미래' in keywords:
        topic = "미래 비전 공감 부족"
        desc = "VALUE-UP이 그리는 미래 비전이 구체적이지 않아 구성원들이 전략의 필요성을 공감하기 어려움"
    elif '현장' in keywords and ('회사' in keywords or '업무' in keywords):
        topic = "현장 실무와의 괴리"
        desc = "VALUE-UP 전략이 현장 실무와 동떨어져 있어 일선 직원들이 필요성을 체감하지 못함"
    elif '공유' in keywords and '방식' in keywords:
        topic = "전략 공유 방식 문제"
        desc = "VALUE-UP 전략 공유가 일방향 전달 위주로 이루어져 구성원의 이해와 공감을 얻지 못함"
    elif '부족' in keywords and '공감' in keywords:
        topic = "소통 기회 부족"
        desc = "VALUE-UP에 대한 충분한 설명과 소통 기회가 부족하여 구성원들이 필요성을 이해하지 못함"
    elif '미래' in keywords and '그룹' in keywords:
        topic = "그룹 비전 불명확"
        desc = "VALUE-UP을 통한 그룹의 미래상과 성장 방향이 명확하지 않아 공감하기 어려움"
    elif '어려움' in keywords and '공감' in keywords:
        topic = "전략 이해의 어려움"
        desc = "VALUE-UP 전략이 복잡하고 추상적이어서 구성원들이 이해하고 공감하기 어려움"
    elif '방향성' in keywords:
        topic = "방향성 이해 부족"
        desc = "VALUE-UP의 전체적인 방향성과 우선순위가 불명확하여 필요성을 공감하기 어려움"
    elif '전략' in keywords and '현장' in keywords:
        topic = "전략-현장 연결 부족"
        desc = "VALUE-UP 전략과 현장 업무의 연결고리가 약하여 실무자들이 필요성을 느끼지 못함"
    elif '환경' in keywords or '체감' in keywords:
        topic = "변화 체감 부족"
        desc = "VALUE-UP으로 인한 긍정적 변화를 체감하지 못해 전략의 필요성에 의문을 가짐"
    elif '투자' in keywords or '의사결정' in keywords:
        topic = "실행 의지 의문"
        desc = "VALUE-UP 실행을 위한 투자와 의사결정이 보이지 않아 회사의 진정성을 의심함"
    elif '직접' in keywords and '사업' in keywords:
        topic = "사업 연관성 부족"
        desc = "VALUE-UP이 현재 사업과 직접적 연관성이 부족하여 필요성을 공감하기 어려움"
    elif '회사' in keywords:
        topic = "회사 비전 불일치"
        desc = "VALUE-UP과 회사의 실제 운영 방향이 일치하지 않아 구성원들이 혼란스러워함"
    elif '실행' in keywords or '밸류업' in keywords:
        topic = "실행 방안 불명확"
        desc = "VALUE-UP의 구체적 실행 방안이 제시되지 않아 실현 가능성에 의문을 가짐"
    elif '성공' in keywords or '사례' in keywords:
        topic = "성공 사례 부재"
        desc = "VALUE-UP의 성공 사례나 벤치마크가 없어 실현 가능성을 믿기 어려움"
    else:
        # 키워드 조합으로 자연스러운 주제 생성
        if k1 and k2:
            topic = f"{k1}-{k2} 연계 부족"
            desc = f"VALUE-UP 전략에서 {k1}과 {k2}의 연계가 불명확하여 구성원들이 필요성을 공감하기 어려움"
        else:
            topic = f"{k1} 관련 이슈"
            desc = f"VALUE-UP 전략의 {k1} 측면에서 구성원들의 이해와 공감을 얻지 못함"

    return topic, desc

def rebuild_q16(df):
    """Q16: 회사의 실천준비 미흡 이유 재구축"""

    for idx, row in df.iterrows():
        keywords = row['키워드'].split(', ')

        # 키워드 기반 주제명과 설명 생성
        topic, desc = generate_q16_topic_and_desc(keywords)

        df.loc[idx, '주제'] = topic
        df.loc[idx, '설명'] = desc

    return df

def generate_q16_topic_and_desc(keywords):
    """Q16 키워드 → 주제 → 설명 생성"""

    k1, k2, k3 = keywords[0], keywords[1] if len(keywords) > 1 else '', keywords[2] if len(keywords) > 2 else ''

    # 키워드 조합별 주제와 설명
    if '전략' in keywords and '조직' in keywords and '공유' in keywords:
        topic = "전략 공유 체계 부족"
        desc = "회사의 실천준비가 미흡한 이유로, 전략을 조직 전체에 효과적으로 공유하고 실행할 체계가 구축되지 않음"
    elif '전략' in keywords and '사업' in keywords:
        topic = "사업 실행 준비 부족"
        desc = "VALUE-UP 전략을 사업 단위에서 실행할 준비가 되어있지 않아 실천이 어려움"
    elif '전략' in keywords and '준비' in keywords:
        topic = "전략 실행 준비 미흡"
        desc = "전략 실행을 위한 구체적 준비와 계획이 부족하여 회사가 실천할 준비가 안됨"
    elif '부족' in keywords and '인재' in keywords:
        topic = "실행 인재 부족"
        desc = "VALUE-UP을 실행할 핵심 인재와 전문 인력이 부족하여 실천 준비가 미흡함"
    elif '생각' in keywords and '전략' in keywords:
        topic = "실행 가능성 의구심"
        desc = "구성원들이 전략의 실행 가능성에 의구심을 가져 회사의 실천 준비가 어려움"
    elif '달성' in keywords and '목표' in keywords:
        topic = "목표 달성 역량 부족"
        desc = "설정된 목표를 달성할 조직 역량이 부족하여 실천 준비가 미흡한 상태"
    elif '전략' in keywords and '업무' in keywords:
        topic = "업무 체계 미정립"
        desc = "전략 실행을 위한 업무 체계와 프로세스가 정립되지 않아 실천 준비가 부족함"
    elif '실행' in keywords and '목표' in keywords:
        topic = "실행 계획 부재"
        desc = "목표 달성을 위한 구체적 실행 계획이 부재하여 회사의 실천 준비가 미흡함"
    elif '준비' in keywords and '방향성' in keywords:
        topic = "실행 방향성 불명확"
        desc = "VALUE-UP 실행의 명확한 방향성이 설정되지 않아 준비가 제대로 되지 않음"
    elif '업무' in keywords and '효율' in keywords:
        topic = "업무 효율성 문제"
        desc = "현재 업무 체계의 비효율로 인해 새로운 전략을 실행할 여력이 부족함"
    elif '조직' in keywords and '구조' in keywords:
        topic = "조직 구조 개편 필요"
        desc = "현 조직 구조가 VALUE-UP 실행에 적합하지 않아 구조 개편이 필요한 상태"
    elif '인력' in keywords and '부족' in keywords:
        topic = "인력 충원 필요"
        desc = "전략 실행에 필요한 인력이 절대적으로 부족하여 충원 없이는 실천이 어려움"
    elif '시스템' in keywords or '프로세스' in keywords:
        topic = "시스템 인프라 부족"
        desc = "VALUE-UP 실행에 필요한 시스템과 인프라가 구축되지 않아 준비가 미흡함"
    elif '역량' in keywords:
        topic = "조직 역량 강화 필요"
        desc = "전략 실행에 필요한 조직 역량이 부족하여 역량 강화가 선행되어야 함"
    elif '계획' in keywords and '구체' in keywords:
        topic = "구체적 계획 부재"
        desc = "VALUE-UP의 구체적 실행 계획이 수립되지 않아 실천 준비가 되지 않음"
    else:
        # 키워드 조합으로 자연스러운 주제 생성
        if k1 and k2 and k3:
            topic = f"{k1} {k2} 준비 부족"
            desc = f"회사의 실천준비가 미흡한 이유로, {k1}과 {k2} 측면의 {k3}이 부족함"
        elif k1 and k2:
            topic = f"{k1}-{k2} 준비 미흡"
            desc = f"VALUE-UP 실천을 위한 {k1}과 {k2} 측면의 준비가 미흡한 상태"
        else:
            topic = f"{k1} 준비 부족"
            desc = f"회사의 {k1} 측면에서 VALUE-UP 실천 준비가 부족함"

    return topic, desc

def rebuild_q17(df):
    """Q17: 목표달성 의지 부족 이유 재구축"""

    for idx, row in df.iterrows():
        keywords = row['키워드'].split(', ')

        # 키워드 기반 주제명과 설명 생성
        topic, desc = generate_q17_topic_and_desc(keywords)

        df.loc[idx, '주제'] = topic
        df.loc[idx, '설명'] = desc

    return df

def generate_q17_topic_and_desc(keywords):
    """Q17 키워드 → 주제 → 설명 생성"""

    k1, k2, k3 = keywords[0], keywords[1] if len(keywords) > 1 else '', keywords[2] if len(keywords) > 2 else ''

    # 키워드 조합별 주제와 설명
    if '전략' in keywords and '달성' in keywords:
        topic = "전략 달성 의지 부족"
        desc = "VALUE-UP 전략 목표 달성에 대한 구성원들의 의지와 동기부여가 부족한 상태"
    elif '전략' in keywords and '생각' in keywords:
        topic = "달성 가능성 회의"
        desc = "구성원들이 전략 목표의 달성 가능성에 회의적이어서 의지가 약화됨"
    elif '전략' in keywords and '목표' in keywords:
        topic = "목표 설정 과도"
        desc = "VALUE-UP 목표가 지나치게 높게 설정되어 달성 의지를 상실함"
    elif '부족' in keywords and '공감' in keywords:
        topic = "목표 공감대 부족"
        desc = "설정된 목표에 대한 구성원의 공감대가 형성되지 않아 달성 의지가 부족함"
    elif '목표' in keywords and '달성' in keywords:
        topic = "목표 현실성 부족"
        desc = "목표가 현실과 동떨어져 있어 구성원들이 달성 의지를 갖기 어려움"
    elif '목표' in keywords and '설정' in keywords:
        topic = "목표 설정 문제"
        desc = "목표 설정 과정의 문제로 구성원들이 달성 의지를 갖지 못함"
    elif '부재' in keywords and '인재' in keywords:
        topic = "실행 인력 부재"
        desc = "목표 달성을 위한 핵심 인재가 부재하여 의지만으로는 달성이 어려움"
    elif '업무' in keywords and '효율' in keywords:
        topic = "업무 과부하 문제"
        desc = "현재 업무 과부하로 인해 새로운 목표 달성에 집중할 여력이 없음"
    elif '달성' in keywords and '구성원' in keywords:
        topic = "구성원 동기 부족"
        desc = "구성원들의 목표 달성에 대한 동기부여와 인센티브가 부족함"
    elif '조직' in keywords:
        topic = "조직 역량 한계"
        desc = "현 조직 역량으로는 설정된 목표 달성이 어렵다고 판단하여 의지가 약함"
    elif '실행' in keywords and '의지' in keywords:
        topic = "실행 동력 부족"
        desc = "목표는 인지하나 실제 실행을 위한 동력과 추진력이 부족함"
    elif '리더십' in keywords:
        topic = "리더십 추진력 부족"
        desc = "목표 달성을 이끌 리더십의 추진력과 솔선수범이 부족함"
    elif '역량' in keywords:
        topic = "역량 개발 필요"
        desc = "목표 달성에 필요한 역량이 부족하여 역량 개발이 선행되어야 함"
    else:
        # 키워드 조합으로 자연스러운 주제 생성
        if k1 and k2:
            topic = f"{k1} {k2} 문제"
            desc = f"목표달성 의지가 부족한 이유로, {k1}과 {k2} 측면에서 문제가 있음"
        else:
            topic = f"{k1} 관련 문제"
            desc = f"VALUE-UP 목표 달성에 대한 {k1} 측면의 문제로 의지가 부족함"

    return topic, desc

def rebuild_q20(df):
    """Q20: 프로세스 비효율성 재구축"""

    for idx, row in df.iterrows():
        keywords = row['키워드'].split(', ')

        # 키워드 기반 주제명과 설명 생성
        topic, desc = generate_q20_topic_and_desc(keywords)

        df.loc[idx, '주제'] = topic
        df.loc[idx, '설명'] = desc

    return df

def generate_q20_topic_and_desc(keywords):
    """Q20 키워드 → 주제 → 설명 생성"""

    k1, k2, k3 = keywords[0], keywords[1] if len(keywords) > 1 else '', keywords[2] if len(keywords) > 2 else ''

    # 키워드 조합별 주제와 설명
    if '조직' in keywords and '업무' in keywords and '보고' in keywords:
        topic = "과도한 보고 체계"
        desc = "조직 간 중복되는 보고와 과도한 보고 요구로 인해 실제 업무 시간이 부족하여 비효율 발생"
    elif '업무' in keywords and '프로세스' in keywords:
        topic = "업무 프로세스 복잡"
        desc = "복잡한 업무 프로세스와 불필요한 절차로 인해 업무 처리 시간이 지연되는 비효율 발생"
    elif '보고' in keywords and '자료' in keywords:
        topic = "보고 자료 작성 과다"
        desc = "과도한 보고 자료 작성 요구로 실제 업무보다 보고에 더 많은 시간을 소비하는 비효율"
    elif '보고' in keywords and '중복' in keywords:
        topic = "중복 보고 체계"
        desc = "여러 부서에 중복으로 보고해야 하는 체계로 인한 시간과 자원의 낭비"
    elif '업무' in keywords and '발생' in keywords:
        topic = "불필요 업무 발생"
        desc = "계획되지 않은 불필요한 업무가 자주 발생하여 본연의 업무에 집중하기 어려움"
    elif '발생' in keywords and '효율' in keywords:
        topic = "비효율 요소 상존"
        desc = "업무 프로세스 곳곳에 비효율적 요소가 상존하여 전반적인 생산성 저하"
    elif '보고' in keywords and '시간' in keywords:
        topic = "보고 시간 과다"
        desc = "보고 준비와 회의에 과도한 시간이 소요되어 실제 업무 시간이 부족함"
    elif '소통' in keywords and '부족' in keywords:
        topic = "부서간 소통 단절"
        desc = "부서 간 소통 부족으로 업무 중복과 재작업이 빈번하게 발생하는 비효율"
    elif '시스템' in keywords:
        topic = "시스템 통합 부족"
        desc = "통합되지 않은 시스템으로 인해 데이터 중복 입력과 정보 불일치 문제 발생"
    elif '협업' in keywords:
        topic = "협업 체계 미흡"
        desc = "부서 간 협업 체계가 미흡하여 업무 진행이 원활하지 못하고 지연됨"
    elif '의사결정' in keywords:
        topic = "의사결정 지연"
        desc = "복잡한 결재 라인과 의사결정 지연으로 업무 진행이 정체되는 비효율"
    elif '권한' in keywords or '책임' in keywords:
        topic = "권한-책임 불일치"
        desc = "권한과 책임이 명확하지 않아 의사결정이 지연되고 업무 진행이 비효율적"
    elif '정보' in keywords and '공유' in keywords:
        topic = "정보 공유 미흡"
        desc = "부서 간 정보 공유가 원활하지 않아 중복 작업과 재확인이 빈번함"
    elif '프로세스' in keywords and '보고' in keywords:
        topic = "보고 프로세스 개선 필요"
        desc = "현재 보고 프로세스가 비효율적이어서 간소화와 개선이 시급함"
    else:
        # 키워드 조합으로 자연스러운 주제 생성
        if '보고' in keywords:
            topic = f"보고 관련 비효율"
            desc = f"보고 체계와 관련된 {k2} 측면에서 비효율이 발생하여 업무 생산성 저하"
        elif '업무' in keywords:
            topic = f"업무 {k2} 문제"
            desc = f"업무의 {k2} 측면에서 비효율이 발생하여 프로세스 개선이 필요함"
        else:
            topic = f"{k1} 프로세스 문제"
            desc = f"{k1} 관련 프로세스의 비효율로 인해 업무 처리에 문제 발생"

    return topic, desc

def rebuild_q43_1(df):
    """Q43.1: 긍정적 인식 재구축"""

    for idx, row in df.iterrows():
        keywords = row['키워드'].split(', ')

        # 키워드 기반 주제명과 설명 생성
        topic, desc = generate_q43_1_topic_and_desc(keywords)

        df.loc[idx, '주제'] = topic
        df.loc[idx, '설명'] = desc

    return df

def generate_q43_1_topic_and_desc(keywords):
    """Q43.1 키워드 → 주제 → 설명 생성"""

    k1, k2, k3 = keywords[0], keywords[1] if len(keywords) > 1 else '', keywords[2] if len(keywords) > 2 else ''

    # 키워드 조합별 주제와 설명
    if '업무' in keywords and '구성원' in keywords and '성장' in keywords:
        topic = "구성원 성장 기회"
        desc = "구성원들의 성장과 발전을 위한 다양한 기회가 제공되고, 업무를 통해 역량을 개발할 수 있는 환경"
    elif '부분' in keywords and '긍정' in keywords:
        topic = "전반적 긍정 평가"
        desc = "회사의 여러 부분에서 긍정적인 변화와 개선이 이루어지고 있다고 평가"
    elif '문화' in keywords and ('부분' in keywords or '조직' in keywords):
        topic = "조직 문화 우수"
        desc = "수평적이고 개방적인 조직 문화가 형성되어 있어 구성원들이 만족함"
    elif '공감' in keywords and '인식' in keywords:
        topic = "전략 공감대 형성"
        desc = "회사의 비전과 전략에 대한 구성원들의 공감대가 잘 형성되어 있음"
    elif '생각' in keywords and '부분' in keywords:
        topic = "긍정적 변화 인식"
        desc = "회사가 긍정적인 방향으로 변화하고 있다고 생각하며 미래에 대한 기대감 보유"
    elif '문화' in keywords and '수평' in keywords:
        topic = "수평적 문화 정착"
        desc = "상하 구분 없이 자유롭게 의견을 개진할 수 있는 수평적 문화가 정착됨"
    elif '도전' in keywords and '시도' in keywords:
        topic = "도전 문화 장려"
        desc = "새로운 도전과 혁신적 시도를 장려하고 실패를 용인하는 문화가 조성됨"
    elif '시스템' in keywords and '효율' in keywords:
        topic = "시스템 효율성 개선"
        desc = "업무 시스템과 프로세스가 지속적으로 개선되어 효율성이 향상됨"
    elif '노력' in keywords and ('조직' in keywords or '변화' in keywords):
        topic = "혁신 노력 지속"
        desc = "조직의 혁신과 변화를 위한 지속적인 노력이 이루어지고 있음을 인정"
    elif '복지' in keywords or '처우' in keywords:
        topic = "복지 처우 개선"
        desc = "구성원들의 복지와 처우가 개선되고 일과 삶의 균형을 지원하는 제도 마련"
    elif '소통' in keywords:
        topic = "소통 활성화"
        desc = "조직 내 소통이 활성화되어 정보 공유와 협업이 원활하게 이루어짐"
    elif '리더십' in keywords:
        topic = "리더십 신뢰"
        desc = "리더십의 솔선수범과 진정성 있는 소통으로 구성원들의 신뢰를 얻음"
    elif '성과' in keywords:
        topic = "성과 창출 우수"
        desc = "회사가 지속적으로 우수한 성과를 창출하고 있어 자부심을 느낌"
    elif '교육' in keywords or '훈련' in keywords:
        topic = "교육 기회 풍부"
        desc = "다양한 교육과 훈련 기회가 제공되어 구성원들의 역량 개발을 지원"
    else:
        # 키워드 조합으로 자연스러운 주제 생성
        if k1 and k2:
            topic = f"{k1}-{k2} 우수"
            desc = f"회사의 {k1}과 {k2} 측면에서 긍정적인 평가를 받고 있음"
        else:
            topic = f"{k1} 측면 긍정"
            desc = f"{k1} 관련하여 긍정적인 변화와 개선이 이루어지고 있음"

    return topic, desc

def rebuild_q43_2(df):
    """Q43.2: 개선 필요사항 재구축"""

    for idx, row in df.iterrows():
        keywords = row['키워드'].split(', ')

        # 키워드 기반 주제명과 설명 생성
        topic, desc = generate_q43_2_topic_and_desc(keywords)

        df.loc[idx, '주제'] = topic
        df.loc[idx, '설명'] = desc

    return df

def generate_q43_2_topic_and_desc(keywords):
    """Q43.2 키워드 → 주제 → 설명 생성"""

    k1, k2, k3 = keywords[0], keywords[1] if len(keywords) > 1 else '', keywords[2] if len(keywords) > 2 else ''

    # 키워드 조합별 주제와 설명
    if '조직' in keywords and '소통' in keywords:
        topic = "조직 소통 개선"
        desc = "조직 내 수직적, 수평적 소통이 원활하지 않아 정보 공유와 협업 체계 개선이 필요함"
    elif '특이' in keywords and '사항' in keywords:
        topic = "특별 개선사항 없음"
        desc = "현재 특별히 개선이 필요한 사항은 없으나 지속적인 모니터링과 개선 노력은 필요"
    elif '구성원' in keywords and ('회사' in keywords or '조직' in keywords):
        topic = "구성원 처우 개선"
        desc = "구성원들의 급여, 복지, 근무환경 등 전반적인 처우 개선이 필요함"
    elif '업무' in keywords and '효율' in keywords:
        topic = "업무 효율화 필요"
        desc = "비효율적인 업무 프로세스와 중복 업무를 개선하여 생산성 향상이 필요"
    elif '생각' in keywords and '개선' in keywords:
        topic = "전반적 개선 필요"
        desc = "회사 운영 전반에 걸쳐 체계적인 개선과 혁신이 필요한 상황"
    elif '필요' in keywords and '시스템' in keywords:
        topic = "시스템 고도화 필요"
        desc = "업무 시스템의 통합과 고도화를 통해 효율성 향상이 필요"
    elif '업무' in keywords and '조직' in keywords and '보고' in keywords:
        topic = "보고 체계 간소화"
        desc = "복잡한 보고 체계를 간소화하고 실질적인 업무에 집중할 수 있는 환경 조성 필요"
    elif '구성원' in keywords and '개선' in keywords:
        topic = "구성원 만족도 제고"
        desc = "구성원들의 만족도를 높이기 위한 다양한 제도와 프로그램 개선 필요"
    elif '조직' in keywords and '문화' in keywords:
        topic = "조직 문화 혁신"
        desc = "기존의 경직된 조직 문화를 개선하여 창의적이고 혁신적인 문화 조성 필요"
    elif '개선' in keywords and '필요' in keywords and '업무' in keywords:
        topic = "업무 프로세스 개선"
        desc = "현재 업무 프로세스의 비효율적 요소를 제거하고 표준화가 필요"
    elif '소통' in keywords and '부족' in keywords:
        topic = "소통 채널 확대"
        desc = "다양한 소통 채널을 마련하고 활성화하여 구성원 간 소통 강화 필요"
    elif '인력' in keywords and ('충원' in keywords or '부족' in keywords):
        topic = "인력 충원 시급"
        desc = "업무량 대비 인력이 부족하여 적정 인력 충원이 시급함"
    elif '교육' in keywords or '훈련' in keywords:
        topic = "교육 체계 강화"
        desc = "구성원 역량 개발을 위한 체계적인 교육과 훈련 프로그램 강화 필요"
    elif '평가' in keywords or '보상' in keywords:
        topic = "평가보상 체계 개선"
        desc = "공정하고 투명한 평가와 성과에 따른 적절한 보상 체계 구축 필요"
    elif '리더십' in keywords:
        topic = "리더십 역량 강화"
        desc = "중간 관리자 및 리더들의 리더십 역량 강화와 소통 능력 향상 필요"
    else:
        # 키워드 조합으로 자연스러운 주제 생성
        if '조직' in keywords:
            topic = f"조직 {k2} 개선"
            desc = f"조직의 {k2} 측면에서 개선이 필요하여 구성원 만족도 향상을 위한 노력 필요"
        elif '업무' in keywords:
            topic = f"업무 {k2} 개선"
            desc = f"업무의 {k2} 관련 문제를 개선하여 효율성과 생산성 향상 필요"
        else:
            topic = f"{k1} 개선 필요"
            desc = f"{k1} 측면에서 개선이 필요하여 전반적인 조직 운영 효율화 필요"

    return topic, desc

if __name__ == "__main__":
    print("=" * 60)
    print("마스터 토픽 전면 재구축")
    print("- 키워드 → 주제 → 설명 자연스러운 흐름")
    print("- 각 문항 맥락에 맞는 설명")
    print("=" * 60)

    rebuild_master_topics()
    print("\n재구축 완료!")