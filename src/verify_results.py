#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 결과 파일 검증
xl = pd.ExcelFile('CJ_voice_on_demographic_analysis_20251024_082242.xlsx')

print(f'총 {len(xl.sheet_names)}개 시트 생성\n')
print('='*60)
print('시트 목록')
print('='*60)

for i, sheet in enumerate(xl.sheet_names, 1):
    print(f'{i:2d}. {sheet}')

# 샘플 시트 확인
print('\n'+'='*60)
print('샘플 데이터 확인: 01_연령_20대')
print('='*60)

df_sample = pd.read_excel('CJ_voice_on_demographic_analysis_20251024_082242.xlsx',
                          sheet_name='01_연령_20대', header=None)
print(df_sample.head(30).to_string(index=False))
