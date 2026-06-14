#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用网页抓取获取北交所股票价格

对于tushare无法获取的北交所股票，尝试从新浪财经获取数据
"""

import csv
import re
import requests
from typing import Optional

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def get_stock_price_sina(stock_code: str) -> Optional[float]:
    """从新浪财经获取股票价格"""
    # 新浪财经的股票代码格式
    if stock_code.startswith('8') or stock_code.startswith('4'):
        url = f"https://finance.sina.com.cn/stock/company/bj{stock_code}/c/2025.html"
    elif stock_code.startswith('6'):
        url = f"https://finance.sina.com.cn/stock/company/sh{stock_code}/c/2025.html"
    else:
        url = f"https://finance.sina.com.cn/stock/company/sz{stock_code}/c/2025.html"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # 搜索价格数据
        # 新浪财经的价格格式可能是：<strong class="stock-price">xx.xx</strong>
        match = re.search(r'<strong[^>]*class="stock-price[^"]*"[^>]*>([\d.]+)</strong>', response.text)
        if match:
            return float(match.group(1))
        
        # 另一种格式
        match = re.search(r'<span[^>]*class="price[^"]*"[^>]*>([\d.]+)</span>', response.text)
        if match:
            return float(match.group(1))
        
        # 搜索页面中的价格数字
        matches = re.findall(r'"price":\s*"([\d.]+)"', response.text)
        if matches:
            return float(matches[0])
        
        return None
    except Exception as e:
        print(f"新浪财经获取失败 {stock_code}: {e}")
        return None


def get_stock_price_sohu(stock_code: str) -> Optional[float]:
    """从搜狐财经获取股票价格"""
    if stock_code.startswith('6'):
        market = 'sh'
    else:
        market = 'sz'
    
    url = f"https://q.stock.sohu.com/cn/{market}/{stock_code}/gsgk.shtml"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # 搜索价格
        match = re.search(r'<div[^>]*class="stock-price[^"]*"[^>]*>([\d.]+)</div>', response.text)
        if match:
            return float(match.group(1))
        
        return None
    except Exception as e:
        print(f"搜狐财经获取失败 {stock_code}: {e}")
        return None


def get_stock_price_10jqka(stock_code: str) -> Optional[float]:
    """从同花顺获取股票价格"""
    url = f"https://basic.10jqka.com.cn/{stock_code}/"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # 搜索价格
        match = re.search(r'<span[^>]*class="price"[^>]*>([\d.]+)</span>', response.text)
        if match:
            return float(match.group(1))
        
        return None
    except Exception as e:
        print(f"同花顺获取失败 {stock_code}: {e}")
        return None


def fix_bj_stocks_web() -> None:
    """使用网页抓取修复北交所股票的数据"""
    
    input_path = "records_with_discount_fixed.csv"
    output_path = "records_with_discount_final.csv"
    
    records = []
    with open(input_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(dict(row))
    
    print(f"总记录数: {len(records)}")
    
    fixed_count = 0
    fail_count = 0
    
    for row in records:
        stock_code = str(row.get("stock_code", "")).strip().zfill(6)
        market_price = row.get("market_price", "").strip()
        
        # 如果已经有市场价，跳过
        if market_price:
            continue
        
        # 如果不是北交所股票，跳过
        if not (stock_code.startswith('8') or stock_code.startswith('4')):
            continue
        
        company_name = row.get("company_name", "")
        exercise_price = row.get("exercise_price", "")
        
        print(f"\n处理北交所股票: {company_name} ({stock_code})")
        
        # 尝试多个数据源
        price = None
        
        # 1. 尝试新浪财经
        print("  尝试新浪财经...")
        price = get_stock_price_sina(stock_code)
        
        # 2. 如果失败，尝试搜狐财经
        if price is None:
            print("  尝试搜狐财经...")
            price = get_stock_price_sohu(stock_code)
        
        # 3. 如果失败，尝试同花顺
        if price is None:
            print("  尝试同花顺...")
            price = get_stock_price_10jqka(stock_code)
        
        if price:
            print(f"  ✓ 成功获取股价: {price}")
            row['market_price'] = price
            fixed_count += 1
            
            if exercise_price:
                try:
                    discount = (price - float(exercise_price)) / price * 100
                    row['discount_rate'] = round(discount, 2)
                    print(f"  折扣率: {row['discount_rate']}%")
                except:
                    row['discount_rate'] = ''
        else:
            print(f"  ✗ 所有数据源都失败")
            fail_count += 1
    
    # 保存结果
    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)
    
    # 统计
    success_count = sum(1 for r in records if r.get("market_price"))
    
    print(f"\n\n完成！")
    print(f"成功修复: {fixed_count} 条")
    print(f"失败: {fail_count} 条")
    print(f"总成功数: {success_count}")
    print(f"结果已保存至: {output_path}")


if __name__ == "__main__":
    fix_bj_stocks_web()