#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 마스터 토픽 파일 읽기
sheets = ['Q4', 'Q16', 'Q17', 'Q20', 'Q43.1', 'Q43.2']

for sheet in sheets:
    df = pd.read_excel('master_topics_final_rebuild.xlsx', sheet_name=sheet)
    print(f'\n{"="*60}')
    print(f'{sheet} - 총 {len(df)}개 마스터 토픽')
    print("="*60)
    print(df.to_string(index=False))
    print()
