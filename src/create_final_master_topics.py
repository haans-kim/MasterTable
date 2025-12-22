#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
최종 마스터 토픽 파일 생성
- 24년 CJ 주식회사 예시 형식과 동일하게
- 주제명 중복 번호 제거
- 상세 설명 컬럼 추가
"""

import pandas as pd
import re

def create_final_master_topics():
    """최종 마스터 토픽 파일 생성"""

    # 기존 파일 읽기 (최신 버전 사용)
    import glob
    import os

    # 가장 최신 마스터 토픽 파일 찾기
    analysis_files = glob.glob('master_topics_v2_*.xlsx')
    if analysis_files:
        # 가장 최신 파일 선택
        input_file = sorted(analysis_files)[-1]
        print(f"입력 파일: {input_file}")
    else:
        print("Error: 마스터 토픽 분석 파일을 찾을 수 없습니다.")
        return None

    xl = pd.ExcelFile(input_file)

    # 출력용 딕셔너리
    output_sheets = {}

    # 요약 시트 복사
    output_sheets['요약'] = pd.read_excel(input_file, sheet_name='요약')

    # 각 문항별 처리
    for sheet_name in xl.sheet_names:
        if sheet_name == '요약':
            continue

        print(f"\n처리 중: {sheet_name}")
        df = pd.read_excel(input_file, sheet_name=sheet_name)

        # 새로운 데이터프레임 생성
        new_data = []

        for _, row in df.iterrows():
            # 주제명에서 (2), (3) 등 제거
            original_topic = re.sub(r'\s*\(\d+\)$', '', row['주제명'])
            keywords = row['키워드(3개)'].split(', ') if pd.notna(row['키워드(3개)']) else []
            sample1 = row.get('샘플응답1', '')
            sample2 = row.get('샘플응답2', '')

            # Q4는 키워드 기반 간결한 주제명 생성
            if sheet_name == 'Q4':
                topic_name = generate_simple_topic_name(keywords)
                description = generate_q4_description(topic_name, keywords, sample1, sample2)
            else:
                topic_name = original_topic
                # 문항별 상세 설명 생성
                if sheet_name == 'Q16':  # 회사의 실천준비 미흡 이유
                    description = generate_q16_description(topic_name, keywords, sample1, sample2)
                elif sheet_name == 'Q17':  # 목표달성 의지 부족 이유
                    description = generate_q17_description(topic_name, keywords, sample1, sample2)
                elif sheet_name == 'Q20':  # 프로세스 비효율성
                    description = generate_q20_description(topic_name, keywords, sample1, sample2)
                elif sheet_name == 'Q43.1':  # 긍정적 인식
                    description = generate_q43_1_description(topic_name, keywords, sample1, sample2)
                elif sheet_name == 'Q43.2':  # 개선 필요사항
                    description = generate_q43_2_description(topic_name, keywords, sample1, sample2)
                else:
                    description = f"{', '.join(keywords[:2])} 관련 의견"

            new_data.append({
                '순위': row['순위'],
                '주제': topic_name,
                '키워드': ', '.join(keywords),
                '설명': description,
                '응답수': row['응답수'],
                '비율(%)': row['비율(%)']
            })

        output_sheets[sheet_name] = pd.DataFrame(new_data)
        print(f"  - {len(new_data)}개 항목 처리 완료")

    # 파일 저장
    output_file = 'master_topics_final_v3.xlsx'
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for sheet_name, df in output_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"\n[DONE] 최종 파일 저장: {output_file}")
    return output_file

def generate_simple_topic_name(keywords):
    """키워드 기반으로 간결한 주제명 생성"""
    keyword_list = keywords if isinstance(keywords, list) else keywords.split(', ')

    # 키워드 조합별 주제명
    if '공감' in keyword_list and '필요' in keyword_list:
        return '공감 및 필요성 부족'
    elif '현장' in keyword_list and '실무' in keyword_list:
        return '현장 실무 괴리'
    elif '전략' in keyword_list and '공유' in keyword_list:
        return '전략 공유 미흡'
    elif '소통' in keyword_list and '설명' in keyword_list:
        return '소통 및 설명 부족'
    elif '미래' in keyword_list and '비전' in keyword_list:
        return '미래 비전 불명확'
    elif '방향' in keyword_list or '방향성' in keyword_list:
        return '방향성 이해 어려움'
    elif '리더' in keyword_list or '리더십' in keyword_list:
        return '리더십 방향성 문제'
    elif '성장' in keyword_list and ('전략' in keyword_list or '투자' in keyword_list):
        return '성장 전략 문제'
    elif '사업' in keyword_list and ('전략' in keyword_list or '구조' in keyword_list):
        return '사업 전략 문제'
    elif '공감' in keyword_list and ('환경' in keyword_list or '체감' in keyword_list):
        return '공감 및 체감 부족'
    elif '직접' in keyword_list and ('사업' in keyword_list or '구조' in keyword_list):
        return '직접 연관성 부족'
    elif '회사' in keyword_list:
        return '회사 차원 문제'
    elif '실행' in keyword_list or '밸류업' in keyword_list:
        return '실행 방안 불명확'
    elif '기적' in keyword_list or '성공' in keyword_list or '사례' in keyword_list:
        return '성공 사례 부재'
    elif '여유' in keyword_list or '말단' in keyword_list:
        return '여유 및 참여 부족'
    else:
        # 기본값: 첫 두 키워드 조합
        if len(keyword_list) >= 2:
            return f"{keyword_list[0]}/{keyword_list[1]} 문제"
        elif len(keyword_list) == 1:
            return f"{keyword_list[0]} 관련 문제"
        else:
            return "기타 의견"

def generate_q4_description(topic_name, keywords, sample1, sample2):
    """Q4: VALUE-UP 필요성 공감 어려운 이유 - 설명 생성"""

    # 키워드 기반으로 간결한 주제명 생성
    keyword_list = keywords if isinstance(keywords, list) else keywords.split(', ')

    # 키워드 조합별 설명 생성
    if '공감' in keyword_list and '필요' in keyword_list:
        return 'VALUE-UP 전략의 필요성을 공감하기 어려운 이유로 전략과 실무의 연관성이 불명확하고 구체적인 실행방안이 제시되지 않음'
    elif '현장' in keyword_list or '실무' in keyword_list:
        return 'VALUE-UP 전략이 현장 실무와 동떨어져 있어 실제 업무에 적용하기 어렵고 현실성이 부족하다고 느낌'
    elif '전략' in keyword_list and '공유' in keyword_list:
        return 'VALUE-UP 전략 공유 과정에서 일방적 전달 위주로 진행되어 구성원의 이해도가 낮고 참여 기회가 부족함'
    elif '소통' in keyword_list or '설명' in keyword_list:
        return 'VALUE-UP 전략에 대한 충분한 설명과 소통 시간이 부족하여 구성원들이 전략을 제대로 이해하지 못함'
    elif '미래' in keyword_list or '비전' in keyword_list:
        return 'VALUE-UP을 통한 회사의 미래 비전과 성장 방향성이 구체적으로 제시되지 않아 확신을 갖기 어려움'
    elif '방향' in keyword_list or '방향성' in keyword_list:
        return 'VALUE-UP 전략의 복잡한 내용으로 인해 전체적인 방향성을 이해하기 어렵고 우선순위가 불명확함'
    elif '리더' in keyword_list or '리더십' in keyword_list:
        return 'VALUE-UP 추진에 대한 리더십의 일관된 방향 제시와 실행 의지가 부족하다고 느껴 공감하기 어려움'
    elif '성장' in keyword_list and '전략' in keyword_list:
        return 'VALUE-UP을 통한 성장 전략의 구체적인 실행 계획과 로드맵이 불명확하여 실현 가능성에 의문을 가짐'
    elif '사업' in keyword_list and ('전략' in keyword_list or '구조' in keyword_list):
        return 'VALUE-UP 전략이 현재 사업 환경과 구조에 맞지 않아 실효성과 달성 가능성에 의문이 있음'
    elif '투자' in keyword_list or '의사결정' in keyword_list:
        return 'VALUE-UP 실행을 위한 투자와 의사결정 과정이 불명확하여 전략의 실현 가능성을 공감하기 어려움'
    elif '환경' in keyword_list or '체감' in keyword_list:
        return 'VALUE-UP 전략이 실제 업무 환경에서 체감되지 않아 필요성을 느끼지 못하고 동기부여가 되지 않음'
    elif '직접' in keyword_list:
        return 'VALUE-UP 전략이 직접적인 업무와 연관성이 부족하여 실무자들이 필요성을 공감하기 어려움'
    elif '회사' in keyword_list:
        return 'VALUE-UP에 대한 회사 차원의 명확한 비전과 실행 의지가 보이지 않아 구성원들이 공감하기 어려움'
    elif '실행' in keyword_list or '밸류업' in keyword_list:
        return 'VALUE-UP 실행 방안이 구체적이지 않고 추상적이어서 실제 어떻게 달성할지 이해하기 어려움'
    elif '기적' in keyword_list or '성공' in keyword_list or '사례' in keyword_list:
        return 'VALUE-UP의 성공 사례나 구체적인 성과가 제시되지 않아 실현 가능성을 믿기 어려움'
    elif '여유' in keyword_list or '말단' in keyword_list:
        return 'VALUE-UP 추진을 위한 시간적 여유와 일선 직원들의 의견 반영이 부족하여 공감대 형성이 어려움'
    else:
        # 기본값: 키워드를 활용한 설명
        return f'VALUE-UP 전략의 필요성 공감이 어려운 이유로 {keyword_list[0]}과 관련된 문제가 지적되며, 구성원들의 이해와 공감을 위한 개선이 필요함'

def generate_q16_description(topic_name, keywords, sample1, sample2):
    """Q16: 회사의 실천준비 미흡 이유 - 설명 생성"""

    descriptions = {
        '전략 실행 조직 미비': '전략 실행을 위한 전담 조직과 체계적인 실행 프로세스가 구축되지 않음',
        '사업 실행 준비 부족': '사업 전략 실행에 필요한 인프라와 시스템 준비가 미흡함',
        '실행 인재 부족': '전략을 실행할 수 있는 전문 인력과 역량이 부족한 상태',
        '목표 달성 역량 부족': '설정된 목표를 달성하기 위한 조직 역량과 자원이 부족함',
        '업무 프로세스 비효율': '현재 업무 프로세스가 비효율적이어서 새로운 전략 실행이 어려움',
        '실행 계획 구체성 부족': '전략의 구체적인 실행 계획과 단계별 로드맵이 부재함',
        '방향성 설정 미흡': '명확한 실행 방향과 우선순위 설정이 되어있지 않음',
        '준비 상태 미흡': '전반적인 조직의 준비 상태와 실행 의지가 부족함',
        '실천 준비 부족': '실제 실천을 위한 구체적인 준비와 계획이 미비함'
    }

    if topic_name in descriptions:
        return descriptions[topic_name]
    elif '인재' in keywords or '인력' in keywords:
        return '전략 실행에 필요한 핵심 인재와 전문 인력이 부족한 상황'
    elif '조직' in keywords:
        return '조직 구조와 업무 체계가 전략 실행에 적합하지 않음'
    elif '준비' in keywords:
        return '전략 실행을 위한 사전 준비와 기반 조성이 미흡함'
    else:
        return '전략 실행을 위한 조직의 준비도가 전반적으로 부족함'

def generate_q17_description(topic_name, keywords, sample1, sample2):
    """Q17: 목표달성 의지 부족 이유 - 설명 생성"""

    descriptions = {
        '목표 달성 의지 부족': '구성원들의 목표 달성에 대한 의지와 동기부여가 부족한 상태',
        '전략 실현 가능성 의문': '현실적으로 전략 목표 달성이 어렵다고 판단하여 회의적임',
        '목표 설정 과도': '비현실적으로 높은 목표 설정으로 인해 달성 가능성이 낮다고 느낌',
        '구성원 공감 부족': '목표에 대한 구성원의 공감과 합의가 부족하여 실행 동력이 약함',
        '실행 의지 부족': '목표는 인지하나 실제 실행하려는 의지와 노력이 부족함',
        '목표 현실성 부족': '시장 상황과 조직 역량을 고려하지 않은 비현실적 목표 설정',
        '목표 설정 문제': '목표 설정 과정의 문제로 인해 달성 가능성이 낮음',
        '리더십 부재': '목표 달성을 이끌 리더십과 추진력이 부족함',
        '업무 효율성 문제': '비효율적인 업무 체계로 인해 목표 달성이 어려움',
        '조직 역량 한계': '현재 조직의 역량으로는 설정된 목표 달성이 어렵다고 판단'
    }

    if topic_name in descriptions:
        return descriptions[topic_name]
    elif '달성' in keywords and '의지' in keywords:
        return '목표 달성을 위한 조직 전체의 의지와 추진력이 부족함'
    elif '현실' in keywords:
        return '목표가 현실과 동떨어져 있어 달성 가능성이 낮다고 인식'
    elif '리더' in keywords:
        return '목표 달성을 주도할 리더십의 부재와 추진력 부족'
    else:
        return '목표 달성에 대한 확신과 의지가 부족한 상황'

def generate_q20_description(topic_name, keywords, sample1, sample2):
    """Q20: 프로세스 비효율성 - 설명 생성"""

    descriptions = {
        '과도한 보고 체계': '불필요하게 복잡하고 반복적인 보고 체계로 인해 업무 효율성이 저하됨',
        '부서간 업무 중복': '부서 간 업무 영역이 불명확하여 중복 업무가 발생하고 책임 소재가 모호함',
        '보고 자료 작성 과다': '과도한 보고 자료 작성으로 실제 업무 시간이 부족함',
        '중복 보고 문제': '동일한 내용을 여러 차례 다른 형식으로 보고해야 하는 비효율 발생',
        '보고 시간 과다': '보고 준비와 회의에 소요되는 시간이 과도하여 실무 시간 부족',
        '업무 중복 발생': '명확한 R&R 부재로 동일 업무를 여러 부서에서 중복 수행',
        '비효율 발생 요인': '불필요한 승인 단계와 복잡한 절차로 인한 업무 지연',
        '업무 효율성 저하': '비효율적인 프로세스로 인해 전반적인 업무 생산성 저하',
        '프로세스 복잡성': '과도하게 복잡한 업무 프로세스로 인한 처리 시간 증가',
        '보고 프로세스 비효율': '보고 라인이 복잡하고 승인 단계가 많아 의사결정 지연',
        '보고 중복 해소': '유사한 보고서를 여러 부서에 중복 제출해야 하는 문제',
        '보고 간소화 필요': '형식적인 보고를 줄이고 핵심 내용 중심으로 간소화 필요'
    }

    if topic_name in descriptions:
        return descriptions[topic_name]
    elif '보고' in keywords and '자료' in keywords:
        return '보고 자료 작성에 과도한 시간이 소요되어 실무 집중도가 떨어짐'
    elif '중복' in keywords:
        return '업무와 보고의 중복으로 인한 비효율과 자원 낭비 발생'
    elif '시간' in keywords:
        return '불필요한 프로세스로 인해 업무 처리 시간이 지연됨'
    elif '부서' in keywords:
        return '부서 간 협업 프로세스가 비효율적이고 소통이 원활하지 않음'
    else:
        return '업무 프로세스의 비효율로 인한 생산성 저하'

def generate_q43_1_description(topic_name, keywords, sample1, sample2):
    """Q43.1: 긍정적 인식 - 설명 생성"""

    descriptions = {
        '구성원 성장 기회': '다양한 교육과 경력 개발 기회가 제공되어 구성원의 성장을 지원함',
        '특별한 긍정 요소 없음': '현재 특별히 긍정적으로 인식되는 부분이 없다는 의견',
        '조직문화 긍정적': '개방적이고 수평적인 조직문화로 자유로운 의견 제시가 가능함',
        '전략 방향성 공감': '회사의 전략과 비전에 대해 공감하며 미래 성장 가능성을 긍정적으로 평가',
        '전반적 긍정 인식': '회사의 전반적인 시스템과 문화에 대해 긍정적으로 인식함',
        '수평적 조직문화': '수직적 위계보다 수평적 소통을 중시하는 문화가 정착됨',
        '도전 기회 제공': '새로운 도전과 혁신을 장려하는 문화로 성장 기회가 많음',
        '시스템 효율성': '업무 시스템과 프로세스가 효율적으로 운영되고 있음',
        '조직 개선 노력': '지속적인 조직 개선과 혁신을 위한 노력이 인정됨',
        '변화 노력 인정': '조직의 긍정적 변화를 위한 노력과 시도가 지속되고 있음'
    }

    if topic_name in descriptions:
        return descriptions[topic_name]
    elif '성장' in keywords:
        return '구성원의 성장과 발전을 위한 지원이 활발함'
    elif '문화' in keywords and '수평' in keywords:
        return '수평적이고 자율적인 조직문화가 긍정적으로 평가됨'
    elif '소통' in keywords:
        return '부서 간, 직급 간 원활한 소통이 이루어지고 있음'
    elif '기회' in keywords:
        return '다양한 기회 제공으로 구성원의 동기부여가 높음'
    else:
        return '조직의 긍정적인 측면에 대한 인식'

def generate_q43_2_description(topic_name, keywords, sample1, sample2):
    """Q43.2: 개선 필요사항 - 설명 생성"""

    descriptions = {
        '조직 소통 개선 필요': '부서 간, 계층 간 소통 부족으로 정보 공유와 협업에 어려움이 있어 개선 필요',
        '특별한 개선사항 없음': '현재 시점에서 특별히 개선이 필요한 사항이 없다는 의견',
        '구성원 처우 개선': '급여, 복지 등 구성원 처우 개선을 통한 만족도 향상 필요',
        '업무 효율화 필요': '비효율적인 업무 프로세스 개선과 자동화를 통한 생산성 향상 필요',
        '개선 방향 모색': '전반적인 개선이 필요하나 구체적인 방향 설정이 필요한 상황',
        '시스템 개선 필요': '노후화된 시스템 업그레이드와 디지털 전환 가속화 필요',
        '보고 체계 개선': '복잡한 보고 체계 간소화와 효율적인 의사결정 구조 확립 필요',
        '구성원 복지 개선': '워라밸, 휴가 사용 등 구성원 복지 제도의 실질적 개선 필요',
        '조직문화 개편 필요': '경직된 조직문화를 유연하고 창의적인 문화로 전환 필요',
        '전반적 개선 필요': '조직 전반에 걸친 체계적이고 종합적인 개선이 요구됨',
        '회사 전략 개선': '현실적이고 실행 가능한 전략 수립과 명확한 방향 제시 필요',
        '문화 개선 필요': '보수적이고 경직된 문화에서 혁신적이고 도전적인 문화로 변화 필요',
        '평가/보상 체계 개선': '공정하고 투명한 평가 시스템과 성과에 따른 적절한 보상 체계 구축 필요',
        '인력 충원 필요': '업무량 대비 인력 부족 문제 해결을 위한 적정 인력 확보 필요',
        '인력 운영 개선': '효율적인 인력 배치와 운영을 통한 조직 생산성 향상 필요',
        '시스템 통합 필요': '분산된 시스템 통합을 통한 업무 효율성 제고 필요',
        '시스템 업그레이드': '노후 시스템 교체와 최신 기술 도입을 통한 경쟁력 확보 필요',
        '수평적 문화 조성': '수직적 의사결정 구조를 수평적 협업 문화로 전환 필요',
        '보고 프로세스 개선': '불필요한 보고 절차 제거와 핵심 위주의 간결한 보고 체계 구축',
        '프로세스 개선 필요': '전반적인 업무 프로세스 재설계를 통한 효율성 극대화 필요'
    }

    if topic_name in descriptions:
        return descriptions[topic_name]
    elif '소통' in keywords and '조직' in keywords:
        return '조직 내 소통 채널 다양화와 투명한 정보 공유 체계 구축 필요'
    elif '업무' in keywords and '효율' in keywords:
        return '업무 프로세스 표준화와 자동화를 통한 효율성 제고 필요'
    elif '시스템' in keywords:
        return 'IT 시스템 현대화와 통합을 통한 업무 효율성 향상 필요'
    elif '문화' in keywords:
        return '조직문화 혁신을 통한 창의적이고 도전적인 분위기 조성 필요'
    elif '개선' in keywords and '필요' in keywords:
        return '지속적인 개선과 혁신을 위한 체계적인 접근 필요'
    elif '보고' in keywords:
        return '보고 문화 개선을 통한 실무 중심의 업무 환경 조성 필요'
    else:
        return '해당 영역의 체계적인 개선과 혁신이 필요한 상황'

def main():
    """메인 실행 함수"""
    print("="*60)
    print("최종 마스터 토픽 파일 생성")
    print("- 중복 번호 제거")
    print("- 상세 설명 추가")
    print("="*60)

    # 최종 파일 생성
    output_file = create_final_master_topics()

    print("\n완료!")

if __name__ == "__main__":
    main()