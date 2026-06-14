#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据 employee_count 和 participant_count 计算 participant_ratio
participant_ratio = participant_count / employee_count × 100%

直接修改 final_data_unprocessed.csv
"""

import os
import pandas as pd

def calculate_participant_ratio():
    input_path = "data/final_data_unprocessed.csv"
    
    print(f"读取文件: {input_path}")
    df = pd.read_csv(input_path, encoding='utf-8-sig')
    
    print(f"\n字段列表:")
    print(df.columns.tolist())
    
    print(f"\n样本数: {len(df)}")
    
    required_cols = ['employee_count', 'participant_count']
    for col in required_cols:
        if col not in df.columns:
            print(f"\n错误: 缺少字段 {col}")
            return
    
    emp_notna = df['employee_count'].notna().sum()
    part_notna = df['participant_count'].notna().sum()
    
    print(f"\n数据统计:")
    print(f"  employee_count 非空: {emp_notna}/{len(df)}")
    print(f"  participant_count 非空: {part_notna}/{len(df)}")
    
    if 'participant_ratio' not in df.columns:
        df['participant_ratio'] = None
        print("\n新增 participant_ratio 字段")
    else:
        print("\n已存在 participant_ratio 字段，将重新计算")
    
    calculated_count = 0
    valid_count = 0
    
    for i, row in df.iterrows():
        emp_count = row['employee_count']
        part_count = row['participant_count']
        
        if pd.notna(emp_count) and pd.notna(part_count) and emp_count > 0:
            ratio = (part_count / emp_count) * 100
            df.at[i, 'participant_ratio'] = round(ratio, 4)
            calculated_count += 1
            if ratio > 0:
                valid_count += 1
        else:
            df.at[i, 'participant_ratio'] = None
    
    print(f"\n计算统计:")
    print(f"  成功计算: {calculated_count}/{len(df)}")
    print(f"  有效比例(>0): {valid_count}/{len(df)}")
    
    if calculated_count > 0:
        valid_ratios = df['participant_ratio'].dropna()
        if len(valid_ratios) > 0:
            print(f"\nparticipant_ratio 统计:")
            print(f"  最小值: {valid_ratios.min():.4f}%")
            print(f"  最大值: {valid_ratios.max():.4f}%")
            print(f"  平均值: {valid_ratios.mean():.4f}%")
            print(f"  中位数: {valid_ratios.median():.4f}%")
    
    print(f"\n前10条记录示例:")
    for i in range(min(10, len(df))):
        row = df.iloc[i]
        emp = row['employee_count'] if pd.notna(row['employee_count']) else 'N/A'
        part = row['participant_count'] if pd.notna(row['participant_count']) else 'N/A'
        ratio = f"{row['participant_ratio']:.4f}%" if pd.notna(row['participant_ratio']) else 'N/A'
        print(f"  {i+1}. {row['company_name']}: 授权人数={part}, 总人数={emp}, 占比={ratio}")
    
    df.to_csv(input_path, index=False, encoding='utf-8-sig')
    print(f"\n已更新文件: {input_path}")
    
    print(f"\n更新后的字段:")
    print(df.columns.tolist())


if __name__ == "__main__":
    calculate_participant_ratio()