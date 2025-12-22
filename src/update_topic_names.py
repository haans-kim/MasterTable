#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
마스터 토픽 주제명 개선 프로그램
키워드와 샘플 응답을 참조하여 의미 있는 주제명 생성
"""

import pandas as pd
import re
from datetime import datetime

def improve_topic_names():
    """주제명을 개선하는 메인 함수"""

    # 파일 읽기
    input_file = 'master_topics_final.xlsx'
    xl = pd.ExcelFile(input_file)

    # 출력용 딕셔너리
    output_sheets = {}

    # 요약 시트 복사
    output_sheets['요약'] = pd.read_excel(input_file, sheet_name='요약')

    # 각 문항별로 처리
    for sheet_name in xl.sheet_names:
        if sheet_name == '요약':
            continue

        print(f"\n처리 중: {sheet_name}")
        df = pd.read_excel(input_file, sheet_name=sheet_name)

        # 문항별 주제명 개선 규칙
        if sheet_name == 'Q4':  # VALUE-UP 필요성 공감 어려운 이유
            topic_rules = {
                ('공감', '성장', '미래'): 'VALUE-UP 필요성 공감 부족',
                ('현장', '회사', '업무'): '현장 실무와의 괴리',
                ('공유', '방식', '사업'): '전략 공유 방식 문제',
                ('부족', '공감', '시간'): '소통 및 설명 부족',
                ('미래', '그룹', '보이지'): '미래 비전 불명확',
                ('어려움', '공감', '방향성'): '방향성 이해 어려움',
                ('공감', '업무', '구성원'): '구성원 공감대 부족',
                ('방향성', '공감', '구성원'): '리더십 방향성 문제',
                ('미래', '성장', '고도화'): '성장 전략 구체성 부족',
                ('전략', '현장', '사업'): '사업 전략 실효성 의문'
            }

        elif sheet_name == 'Q16':  # 회사의 실천준비 미흡 이유
            topic_rules = {
                ('전략', '조직', '공유'): '전략 실행 조직 미비',
                ('전략', '사업', '준비'): '사업 실행 준비 부족',
                ('전략', '준비', '생각'): '실천 준비 미흡',
                ('부족', '인재', '전략'): '실행 인재 부족',
                ('생각', '전략', '준비'): '전략 실행력 의문',
                ('달성', '전략', '목표'): '목표 달성 역량 부족',
                ('전략', '업무', '사업'): '업무 체계 미비',
                ('실행', '전략', '목표'): '실행 계획 구체성 부족',
                ('전략', '준비', '방향성'): '방향성 설정 미흡',
                ('업무', '효율', '진행'): '업무 프로세스 비효율'
            }

        elif sheet_name == 'Q17':  # 목표달성 의지 부족 이유
            topic_rules = {
                ('전략', '달성', '생각'): '목표 달성 의지 부족',
                ('전략', '생각', '달성'): '전략 실현 가능성 의문',
                ('전략', '달성', '목표'): '목표 설정 과도',
                ('전략', '생각', '공감'): '구성원 공감 부족',
                ('부족', '전략', '공감'): '실행 의지 부족',
                ('목표', '생각', '전략'): '목표 현실성 부족',
                ('목표', '달성', '설정'): '목표 설정 문제',
                ('부재', '전략', '인재'): '리더십 부재',
                ('업무', '구성원', '효율'): '업무 효율성 문제',
                ('달성', '구성원', '회사'): '조직 역량 한계'
            }

        elif sheet_name == 'Q20':  # 프로세스 비효율성
            topic_rules = {
                ('조직', '업무', '보고'): '과도한 보고 체계',
                ('업무', '프로세스', '부서'): '부서간 업무 중복',
                ('보고', '업무', '자료'): '보고서 작성 과다',
                ('보고', '업무', '중복'): '중복 보고 문제',
                ('프로세스', '업무', '보고'): '프로세스 복잡성',
                ('업무', '발생', '중복'): '업무 중복 발생',
                ('발생', '효율', '업무'): '비효율 발생 요인',
                ('업무', '효율', '보고'): '업무 효율성 저하',
                ('보고', '시간', '업무'): '보고 시간 과다',
                ('보고', '업무', '자료'): '자료 준비 부담'
            }

        elif sheet_name == 'Q43.1':  # 긍정적 인식
            topic_rules = {
                ('업무', '구성원', '성장'): '구성원 성장 기회',
                ('부분', '긍정', '사항'): '특별한 긍정 요소 없음',
                ('문화', '부분', '긍정'): '조직문화 긍정적',
                ('공감', '인식', '전략'): '전략 방향성 공감',
                ('생각', '부분', '긍정'): '전반적 긍정 인식',
                ('문화', '조직', '수평'): '수평적 조직문화',
                ('도전', '시도', '기회'): '도전 기회 제공',
                ('업무', '효율', '시스템'): '시스템 효율성',
                ('노력', '조직', '문화'): '조직 개선 노력',
                ('부분', '노력', '변화'): '변화 노력 인정'
            }

        elif sheet_name == 'Q43.2':  # 개선 필요사항
            topic_rules = {
                ('조직', '소통', '구성원'): '조직 소통 개선 필요',
                ('특이', '사항', '당장'): '특별한 개선사항 없음',
                ('구성원', '회사', '조직'): '구성원 처우 개선',
                ('업무', '효율', '보고'): '업무 효율화 필요',
                ('생각', '개선', '부분'): '전반적 개선 필요',
                ('필요', '시스템', '업무'): '시스템 개선 필요',
                ('업무', '조직', '보고'): '보고 체계 개선',
                ('구성원', '개선', '회사'): '구성원 복지 개선',
                ('조직', '문화', '생각'): '조직문화 개편 필요',
                ('개선', '필요', '업무'): '업무 방식 개선'
            }
        else:
            topic_rules = {}

        # 주제명 개선
        improved_names = []
        for _, row in df.iterrows():
            keywords = row['키워드(3개)'].split(', ') if pd.notna(row['키워드(3개)']) else []

            # 키워드 튜플로 매칭
            matched = False
            for keyword_tuple, new_name in topic_rules.items():
                if all(kw in keywords for kw in keyword_tuple[:2]):  # 최소 2개 매칭
                    improved_names.append(new_name)
                    matched = True
                    break

            if not matched:
                # 매칭 안 되면 기존 주제명 개선
                original = row['주제명']
                if '/' in original:
                    # 슬래시 형태를 더 의미 있게
                    parts = original.split('/')
                    if len(parts) == 2:
                        improved_names.append(f"{parts[0]} 관련 {parts[1]}")
                    else:
                        improved_names.append(original)
                elif original == '기타':
                    improved_names.append('기타 의견')
                else:
                    improved_names.append(original)

        # 개선된 주제명 적용
        df['주제명'] = improved_names
        output_sheets[sheet_name] = df

        print(f"  - {len(improved_names)}개 주제명 개선 완료")

    # 파일 저장
    output_file = 'master_topics_updated.xlsx'
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for sheet_name, df in output_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"\n[DONE] 개선된 파일 저장: {output_file}")
    return output_file

def main():
    """메인 실행 함수"""
    print("="*60)
    print("마스터 토픽 주제명 개선 프로그램")
    print("="*60)

    # 주제명 개선 실행
    output_file = improve_topic_names()

    print("\n완료!")

if __name__ == "__main__":
    main()