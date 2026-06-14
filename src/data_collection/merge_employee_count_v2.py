#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 data_no_process.csv 中的 employee_count 字段合并到 final_data_unprocessed.csv 中
直接修改 final_data_unprocessed.csv，不生成新文件
"""

import os
import pandas as pd

def merge_employee_count():
    data_no_process_path = "data/data_no_process.csv"
    final_data_path = "data/final_data_unprocessed.csv"
    
    print(f"读取文件: {data_no_process_path}")
    data_no_process = pd.read_csv(data_no_process_path, encoding='utf-8-sig')
    
    print(f"读取文件: {final_data_path}")
    final_data = pd.read_csv(final_data_path, encoding='utf-8-sig')
    
    print(f"\ndata_no_process.csv 字段:")
    print(data_no_process.columns.tolist())
    
    print(f"\nfinal_data_unprocessed.csv 字段:")
    print(final_data.columns.tolist())
    
    print(f"\ndata_no_process.csv 样本数: {len(data_no_process)}")
    print(f"final_data_unprocessed.csv 样本数: {len(final_data)}")
    
    if 'employee_count' not in data_no_process.columns:
        print("\n错误: data_no_process.csv 中没有 employee_count 字段!")
        return
    
    print(f"\ndata_no_process.csv 中 employee_count 非空值数: {data_no_process['employee_count'].notna().sum()}")
    
    key_fields = ['doc_id', 'company_name', 'stock_code']
    key_field = None
    
    for field in key_fields:
        if field in data_no_process.columns and field in final_data.columns:
            overlap = len(set(data_no_process[field].dropna()) & set(final_data[field].dropna()))
            print(f"\n使用 {field} 作为匹配键的重叠数: {overlap}")
            if overlap > 0:
                key_field = field
                break
    
    if key_field is None:
        print("\n错误: 无法找到合适的匹配键!")
        return
    
    print(f"\n匹配键: {key_field}")
    
    employee_map = {}
    for _, row in data_no_process.iterrows():
        key_val = row[key_field]
        emp_count = row['employee_count']
        if pd.notna(key_val) and pd.notna(emp_count):
            employee_map[str(key_val)] = emp_count
    
    print(f"\n从 data_no_process.csv 建立的 employee_count 映射数量: {len(employee_map)}")
    
    if 'employee_count' not in final_data.columns:
        final_data['employee_count'] = None
        print("\n在 final_data_unprocessed.csv 中新增 employee_count 字段")
    else:
        print("\nfinal_data_unprocessed.csv 中已存在 employee_count 字段")
    
    matched_count = 0
    updated_count = 0
    
    for i, row in final_data.iterrows():
        key_val = str(row[key_field]) if pd.notna(row[key_field]) else None
        old_value = row['employee_count'] if 'employee_count' in row and pd.notna(row['employee_count']) else None
        
        if key_val in employee_map:
            new_value = employee_map[key_val]
            matched_count += 1
            
            if old_value != new_value:
                final_data.at[i, 'employee_count'] = new_value
                updated_count += 1
                if i < 10:
                    print(f"  {row['company_name']}: {old_value} -> {new_value}")
    
    print(f"\n匹配统计:")
    print(f"  找到匹配的记录数: {matched_count}")
    print(f"  更新的记录数: {updated_count}")
    
    final_data['employee_count'] = pd.to_numeric(final_data['employee_count'], errors='coerce')
    
    print(f"\nfinal_data_unprocessed.csv 中 employee_count 非空值数: {final_data['employee_count'].notna().sum()}")
    
    final_data.to_csv(final_data_path, index=False, encoding='utf-8-sig')
    print(f"\n已更新文件: {final_data_path}")
    
    print(f"\n更新后的字段:")
    print(final_data.columns.tolist())


if __name__ == "__main__":
    merge_employee_count()