#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
계열사별 토픽 분석 테스트 (3개 계열사만)
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd
import numpy as np
from datetime import datetime

# 데이터 로드
df = pd.read_excel('주관식 분석 raw data_250929.xlsx')
df.columns = ['company', 'Q4', 'Q16', 'Q17', 'Q20', 'Q43_positive', 'Q43_improve']

# 계열사 목록 확인
companies = df['company'].unique()
print(f"전체 계열사 수: {len(companies)}")
print(f"계열사 목록 (앞 5개): {companies[:5].tolist()}")

# 각 계열사의 응답 수 확인
for i, company in enumerate(companies[:5], 1):
    company_df = df[df['company'] == company]
    print(f"{i}. {company}: {len(company_df)}명")

# 데이터 구조 확인
print("\n데이터 샘플:")
print(df.head())