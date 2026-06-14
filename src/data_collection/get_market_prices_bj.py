#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理北交所股票的价格获取

失败的8家公司都是北交所股票（代码以8或4开头），需要使用不同的接口获取数据
"""

import csv
from datetime import datetime, timedelta
from typing import Dict, Optional

import pandas as pd

try:
    import tushare as ts
    TUSHARE_AVAILABLE = True
except ImportError:
    TUSHARE_AVAILABLE = False
    print("警告: tushare未安装，请运行: pip install tushare")


TUSHARE_TOKEN = "83d5cccf004ac22f87e7546feae89653875c33ccbc69daaa1a3e644f"


def get_stock_price_bj(ts_code: str, trade_date: str, pro) -> Optional[float]:
    """获取北交所股票的收盘价"""
    try:
        # 尝试北交所接口
        df = pro.bk_daily(ts_code=ts_code, start_date=trade_date, end_date=trade_date)
        
        if len(df) > 0:
            close = df.iloc[0]['close']
            return float(close)
        
        return None
    except Exception as e:
        print(f"北交所接口失败 {ts_code} {trade_date}: {e}")
        return None


def get_stock_price_main(ts_code: str, trade_date: str, pro) -> Optional[float]:
    """获取沪深交易所股票的收盘价"""
    try:
        df = pro.daily(ts_code=ts_code, start_date=trade_date, end_date=trade_date)
        
        if len(df) > 0:
            close = df.iloc[0]['close']
            return float(close)
        
        return None
    except Exception as e:
        print(f"沪深接口失败 {ts_code} {trade_date}: {e}")
        return None


def calculate_discount_rate(market_price: float, exercise_price: float) -> Optional[float]:
    """计算折扣率"""
    try:
        if market_price and exercise_price and market_price > 0:
            discount = (market_price - float(exercise_price)) / market_price * 100
            return round(discount, 2)
        return None
    except:
        return None


def fix_bj_stocks() -> None:
    """修复北交所股票的数据"""
    
    input_path = "records_with_discount_fixed.csv"
    output_path = "records_with_discount_final.csv"
    
    if not TUSHARE_AVAILABLE:
        print("错误: 需要先安装tushare")
        return
    
    pro = ts.pro_api(TUSHARE_TOKEN)
    print("Tushare已初始化")
    
    records = []
    with open(input_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(dict(row))
    
    print(f"总记录数: {len(records)}")
    
    bj_fixed = 0
    
    for row in records:
        stock_code = str(row.get("stock_code", "")).strip().zfill(6)
        market_price = row.get("market_price", "").strip()
        trade_date = row.get("trade_date", "").strip()
        
        # 如果已经有市场价，跳过
        if market_price:
            continue
        
        # 如果是北交所股票（8或4开头）且交易日不为空
        if (stock_code.startswith('8') or stock_code.startswith('4')) and trade_date:
            company_name = row.get("company_name", "")
            exercise_price = row.get("exercise_price", "")
            
            print(f"\n处理北交所股票: {company_name} ({stock_code})")
            print(f"  交易日: {trade_date}")
            
            # 转换日期格式
            trade_date_fmt = trade_date.replace('-', '')
            ts_code = f"{stock_code}.BJ"
            
            # 尝试北交所接口
            price = get_stock_price_bj(ts_code, trade_date_fmt, pro)
            
            if price:
                print(f"  成功获取股价: {price}")
                row['market_price'] = price
                bj_fixed += 1
                
                if exercise_price:
                    try:
                        discount = calculate_discount_rate(price, float(exercise_price))
                        row['discount_rate'] = discount
                        print(f"  折扣率: {discount}%")
                    except:
                        row['discount_rate'] = ''
            else:
                # 尝试主接口作为备用
                print("  北交所接口失败，尝试主接口...")
                price = get_stock_price_main(ts_code, trade_date_fmt, pro)
                if price:
                    print(f"  主接口成功获取股价: {price}")
                    row['market_price'] = price
                    bj_fixed += 1
                    
                    if exercise_price:
                        try:
                            discount = calculate_discount_rate(price, float(exercise_price))
                            row['discount_rate'] = discount
                        except:
                            row['discount_rate'] = ''
                else:
                    print(f"  未能获取股价")
    
    # 保存结果
    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)
    
    # 统计
    success_count = sum(1 for r in records if r.get("market_price"))
    fail_count = len(records) - success_count
    
    print(f"\n\n完成！")
    print(f"修复北交所股票: {bj_fixed} 条")
    print(f"总成功数: {success_count}")
    print(f"仍未找到: {fail_count}")
    print(f"结果已保存至: {output_path}")


if __name__ == "__main__":
    fix_bj_stocks()