#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用东方财富API提取公司员工总数（带重试机制）

功能：从东方财富API获取公司员工总数，带重试机制确保高成功率
输出：employee_counts.csv
"""

import csv
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests


def read_metadata(csv_path: str) -> List[Dict[str, str]]:
    """读取metadata.csv"""
    companies = []
    seen = set()
    
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            stock_code = row.get("stock_code", "").strip()
            company_name = row.get("company_name", "").strip()
            
            if not stock_code or not company_name:
                continue
            
            if stock_code not in seen:
                seen.add(stock_code)
                companies.append({
                    "stock_code": stock_code,
                    "company_name": company_name
                })
    
    print(f"共读取 {len(companies)} 个公司")
    return companies


def get_employee_count(stock_code: str, max_retries: int = 3, initial_delay: float = 1.0) -> Optional[int]:
    """从东方财富API获取员工总数（带重试机制）"""
    # 判断市场
    if stock_code.startswith("6"):
        secid = f"1.{stock_code}"
    else:
        secid = f"0.{stock_code}"
    
    url = f"https://push2.eastmoney.com/api/qt/stock/get?secid={secid}&fields=f57,f58,f174"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.eastmoney.com/"
    }
    
    delay = initial_delay
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            if data.get("rc") == 0 and data.get("data"):
                employee_count = data["data"].get("f174")
                if employee_count and 100 <= employee_count <= 100000:
                    return int(employee_count)
            
            return None
        
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                print(f"  第{attempt+1}次请求失败，{delay}秒后重试: {str(e)[:50]}")
                time.sleep(delay)
                delay *= 2  # 指数退避
            else:
                print(f"  API请求失败: {e}")
                return None


def crawl_employee_counts(metadata_path: str, output_path: str) -> None:
    """主流程"""
    companies = read_metadata(metadata_path)
    
    results = []
    success_count = 0
    fail_count = 0
    
    for i, company in enumerate(companies, 1):
        stock_code = company["stock_code"]
        company_name = company["company_name"]
        
        print(f"\n[{i}/{len(companies)}] {company_name} ({stock_code})")
        
        employee_count = get_employee_count(stock_code)
        
        if employee_count:
            print(f"  ✓ 员工总数: {employee_count}")
            success_count += 1
            status = "成功"
        else:
            print(f"  ✗ 未能获取员工数")
            fail_count += 1
            status = "未找到"
        
        results.append({
            "stock_code": stock_code,
            "company_name": company_name,
            "employee_count": employee_count,
            "status": status
        })
        
        # 请求间隔
        time.sleep(0.3)
    
    # 保存结果
    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path_obj, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "stock_code", "company_name", "employee_count", "status"
        ])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n\n处理完成！")
    print(f"成功提取: {success_count}/{len(companies)}")
    print(f"失败: {fail_count}/{len(companies)}")
    print(f"结果已保存至: {output_path}")


if __name__ == "__main__":
    crawl_employee_counts("data/metadata/metadata.csv", "data/metadata/employee_counts.csv")