#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
마스터 토픽 주제명 개선 프로그램 v2
- 중복 주제명 해결
- 순위를 응답수 기준으로 재정렬
"""

import pandas as pd
import re

def improve_topic_names_v2():
    """주제명을 개선하는 메인 함수 v2"""

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

        # 응답수 기준으로 정렬 (내림차순)
        df = df.sort_values('응답수', ascending=False).reset_index(drop=True)

        # 문항별 주제명 개선
        improved_names = []
        used_names = set()  # 중복 방지용

        for idx, row in df.iterrows():
            keywords = row['키워드(3개)'].split(', ') if pd.notna(row['키워드(3개)']) else []
            sample1 = row.get('샘플응답1', '')
            sample2 = row.get('샘플응답2', '')

            # 문항별 특화 규칙
            if sheet_name == 'Q4':  # VALUE-UP 필요성 공감 어려운 이유
                if '공감' in keywords and '성장' in keywords:
                    name = 'VALUE-UP 필요성 공감 부족'
                elif '현장' in keywords:
                    name = '현장 실무와의 괴리'
                elif '공유' in keywords:
                    name = '전략 공유 방식 문제'
                elif '시간' in keywords and '부족' in keywords:
                    name = '소통 시간 부족'
                elif '미래' in keywords and '보이지' in keywords:
                    name = '미래 비전 불명확'
                elif '어려움' in keywords:
                    name = '방향성 이해 어려움'
                elif '방향성' in keywords:
                    name = '리더십 방향성 문제'
                elif '고도화' in keywords:
                    name = '성장 전략 구체성 부족'
                elif '전략' in keywords and '사업' in keywords:
                    name = '사업 전략 실효성 의문'
                elif '구성원' in keywords:
                    name = '구성원 공감대 부족'
                else:
                    name = f"{keywords[0]} 관련 이슈" if keywords else "기타 의견"

            elif sheet_name == 'Q16':  # 회사의 실천준비 미흡 이유
                if '전략' in keywords and '조직' in keywords:
                    name = '전략 실행 조직 미비'
                elif '전략' in keywords and '사업' in keywords:
                    name = '사업 실행 준비 부족'
                elif '인재' in keywords:
                    name = '실행 인재 부족'
                elif '달성' in keywords and '목표' in keywords:
                    name = '목표 달성 역량 부족'
                elif '업무' in keywords and '효율' in keywords:
                    name = '업무 프로세스 비효율'
                elif '실행' in keywords:
                    name = '실행 계획 구체성 부족'
                elif '방향성' in keywords:
                    name = '방향성 설정 미흡'
                elif '준비' in keywords:
                    if '생각' in keywords:
                        name = '준비 상태 미흡'
                    else:
                        name = '실천 준비 부족'
                else:
                    name = f"{keywords[0]} 관련 문제" if keywords else "기타 의견"

            elif sheet_name == 'Q17':  # 목표달성 의지 부족 이유
                if '달성' in keywords and '전략' in keywords:
                    name = '목표 달성 의지 부족'
                elif '생각' in keywords and '전략' in keywords:
                    name = '전략 실현 가능성 의문'
                elif '목표' in keywords and '달성' in keywords:
                    name = '목표 설정 과도'
                elif '공감' in keywords:
                    name = '구성원 공감 부족'
                elif '부족' in keywords:
                    name = '실행 의지 부족'
                elif '목표' in keywords and '생각' in keywords:
                    name = '목표 현실성 부족'
                elif '설정' in keywords:
                    name = '목표 설정 문제'
                elif '부재' in keywords or '인재' in keywords:
                    name = '리더십 부재'
                elif '효율' in keywords:
                    name = '업무 효율성 문제'
                elif '회사' in keywords:
                    name = '조직 역량 한계'
                else:
                    name = f"{keywords[0]} 관련 이슈" if keywords else "기타 의견"

            elif sheet_name == 'Q20':  # 프로세스 비효율성
                if '보고' in keywords:
                    if '자료' in keywords:
                        name = '보고 자료 작성 과다'
                    elif '중복' in keywords:
                        name = '중복 보고 문제'
                    elif '시간' in keywords:
                        name = '보고 시간 과다'
                    elif '조직' in keywords:
                        name = '과도한 보고 체계'
                    else:
                        name = '보고 프로세스 비효율'
                elif '업무' in keywords and '중복' in keywords:
                    name = '업무 중복 발생'
                elif '부서' in keywords:
                    name = '부서간 업무 중복'
                elif '프로세스' in keywords:
                    name = '프로세스 복잡성'
                elif '발생' in keywords and '효율' in keywords:
                    name = '비효율 발생 요인'
                elif '효율' in keywords:
                    name = '업무 효율성 저하'
                else:
                    name = f"{keywords[0]} 관련 비효율" if keywords else "기타 의견"

            elif sheet_name == 'Q43.1':  # 긍정적 인식
                if '성장' in keywords:
                    name = '구성원 성장 기회'
                elif '특이' in keywords or '사항' in keywords:
                    name = '특별한 긍정 요소 없음'
                elif '문화' in keywords and '수평' in keywords:
                    name = '수평적 조직문화'
                elif '문화' in keywords:
                    name = '조직문화 긍정적'
                elif '전략' in keywords:
                    name = '전략 방향성 공감'
                elif '도전' in keywords or '시도' in keywords:
                    name = '도전 기회 제공'
                elif '시스템' in keywords:
                    name = '시스템 효율성'
                elif '노력' in keywords:
                    if '변화' in keywords:
                        name = '변화 노력 인정'
                    else:
                        name = '조직 개선 노력'
                elif '긍정' in keywords:
                    name = '전반적 긍정 인식'
                else:
                    name = f"{keywords[0]} 관련 긍정" if keywords else "기타 의견"

            elif sheet_name == 'Q43.2':  # 개선 필요사항
                if '소통' in keywords and '조직' in keywords:
                    name = '조직 소통 개선 필요'
                elif '특이' in keywords or ('사항' in keywords and '당장' in keywords):
                    name = '특별한 개선사항 없음'
                elif '구성원' in keywords:
                    if '회사' in keywords:
                        name = '구성원 처우 개선'
                    elif '개선' in keywords:
                        name = '구성원 복지 개선'
                    else:
                        name = '구성원 관련 개선'
                elif '업무' in keywords and '효율' in keywords:
                    name = '업무 효율화 필요'
                elif '보고' in keywords:
                    if '조직' in keywords:
                        name = '보고 체계 개선'
                    elif '중복' in keywords:
                        name = '보고 중복 해소'
                    elif '간소화' in keywords:
                        name = '보고 간소화 필요'
                    else:
                        name = '보고 프로세스 개선'
                elif '시스템' in keywords:
                    if '필요' in keywords:
                        name = '시스템 개선 필요'
                    elif '통합' in keywords:
                        name = '시스템 통합 필요'
                    else:
                        name = '시스템 업그레이드'
                elif '문화' in keywords:
                    if '개편' in keywords:
                        name = '조직문화 개편 필요'
                    elif '수평' in keywords:
                        name = '수평적 문화 조성'
                    else:
                        name = '문화 개선 필요'
                elif '평가' in keywords or '보상' in keywords:
                    name = '평가/보상 체계 개선'
                elif '인력' in keywords:
                    if '부족' in keywords:
                        name = '인력 충원 필요'
                    else:
                        name = '인력 운영 개선'
                elif '개선' in keywords and '필요' in keywords:
                    name = '전반적 개선 필요'
                elif '생각' in keywords and '개선' in keywords:
                    name = '개선 방향 모색'
                else:
                    name = f"{keywords[0]} 개선 필요" if keywords else "기타 의견"

            else:
                # 기본 규칙
                if len(keywords) >= 2:
                    name = f"{keywords[0]} 관련 {keywords[1]}"
                elif keywords:
                    name = f"{keywords[0]} 관련"
                else:
                    name = "기타 의견"

            # 중복 방지: 같은 이름이 이미 있으면 번호 추가
            original_name = name
            counter = 2
            while name in used_names:
                name = f"{original_name} ({counter})"
                counter += 1

            used_names.add(name)
            improved_names.append(name)

        # 개선된 주제명 적용
        df['주제명'] = improved_names

        # 순위 재설정 (응답수 기준)
        df['순위'] = range(1, len(df) + 1)

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
    print("마스터 토픽 주제명 개선 프로그램 v2")
    print("- 중복 주제명 해결")
    print("- 응답수 기준 순위 정렬")
    print("="*60)

    # 주제명 개선 실행
    output_file = improve_topic_names_v2()

    print("\n완료!")


if __name__ == "__main__":
    main()