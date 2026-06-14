#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复版：使用tushare获取股票市场价并计算折扣率

修复内容：
1. 修复股票代码格式化问题（确保6位）
2. 使用更可靠的交易日获取方法
3. 添加更多调试信息
"""

import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

try:
    import tushare as ts
    TUSHARE_AVAILABLE = True
except ImportError:
    TUSHARE_AVAILABLE = False
    print("警告: tushare未安装，请运行: pip install tushare")


TUSHARE_TOKEN = "83d5cccf004ac22f87e7546feae89653875c33ccbc69daaa1a3e644f"


def get_ts_code(stock_code: str) -> str:
    """将股票代码转换为tushare格式"""
    code = str(stock_code).strip().zfill(6)
    if code.startswith('6'):
        return f"{code}.SH"
    elif code.startswith('8') or code.startswith('4'):
        return f"{code}.BJ"
    else:
        return f"{code}.SZ"


def get_previous_trading_date(publish_date: str, pro) -> Optional[str]:
    """获取公告日前一个交易日"""
    try:
        publish_dt = datetime.strptime(publish_date, "%Y-%m-%d")
        
        for i in range(1, 30):
            check_date = publish_dt - timedelta(days=i)
            check_str = check_date.strftime("%Y%m%d")
            
            try:
                df = pro.trade_cal(exchange='SSE', start_date=check_str, end_date=check_str)
                if len(df) > 0:
                    is_open = df.iloc[0]['is_open']
                    if is_open == 1:
                        return check_str
            except Exception:
                continue
        
        return None
    except Exception as e:
        print(f"获取交易日失败: {e}")
        return None


def get_stock_price(ts_code: str, trade_date: str, pro) -> Optional[float]:
    """获取指定日期的股票收盘价"""
    try:
        df = pro.daily(ts_code=ts_code, start_date=trade_date, end_date=trade_date)
        
        if len(df) > 0:
            close = df.iloc[0]['close']
            return float(close)
        
        return None
    except Exception as e:
        print(f"获取股价失败 {ts_code} {trade_date}: {e}")
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


def read_metadata_publish_dates(metadata_path: str) -> Dict[str, str]:
    """读取metadata.csv中的发布日期"""
    publish_dates = {}
    
    with open(metadata_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            doc_id = row.get("doc_id", "").strip()
            publish_date = row.get("publish_date", "").strip()
            
            if doc_id and publish_date:
                publish_dates[doc_id] = publish_date
    
    return publish_dates


def get_market_prices() -> None:
    """主流程：获取股票市场价并计算折扣率"""
    
    records_path = "records_validated.csv"
    metadata_path = "data/metadata/metadata.csv"
    output_path = "records_with_discount_fixed.csv"
    
    if not TUSHARE_AVAILABLE:
        print("错误: 需要先安装tushare")
        print("运行: pip install tushare")
        return
    
    pro = ts.pro_api(TUSHARE_TOKEN)
    print("Tushare已初始化")
    
    print("读取数据...")
    publish_dates = read_metadata_publish_dates(metadata_path)
    print(f"metadata中共有 {len(publish_dates)} 条记录")
    
    records = []
    with open(records_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(dict(row))
    
    print(f"records_validated中共有 {len(records)} 条记录")
    
    success_count = 0
    fail_count = 0
    total = len(records)
    
    results = []
    
    for i, row in enumerate(records, 1):
        doc_id = row.get("doc_id", "").strip()
        company_name = row.get("company_name", "")
        stock_code = str(row.get("stock_code", "")).strip().zfill(6)
        exercise_price = row.get("exercise_price", "")
        
        print(f"\n[{i}/{total}] {company_name} ({stock_code})")
        
        publish_date = publish_dates.get(doc_id, "")
        
        if not publish_date:
            print(f"  未找到发布日期")
            fail_count += 1
            row['publish_date'] = ''
            row['trade_date'] = ''
            row['market_price'] = ''
            row['discount_rate'] = ''
            results.append(row)
            continue
        
        print(f"  发布日期: {publish_date}")
        
        trade_date = get_previous_trading_date(publish_date, pro)
        
        if not trade_date:
            print(f"  未找到前一个交易日")
            fail_count += 1
            row['publish_date'] = publish_date
            row['trade_date'] = ''
            row['market_price'] = ''
            row['discount_rate'] = ''
            results.append(row)
            continue
        
        trade_date_fmt = f"{trade_date[:4]}-{trade_date[4:6]}-{trade_date[6:]}"
        print(f"  前一个交易日: {trade_date_fmt}")
        
        ts_code = get_ts_code(stock_code)
        print(f"  Tushare代码: {ts_code}")
        
        market_price = get_stock_price(ts_code, trade_date, pro)
        
        if market_price:
            print(f"  市场价: {market_price}")
            success_count += 1
            
            if exercise_price:
                try:
                    exercise_price_float = float(exercise_price)
                    discount_rate = calculate_discount_rate(market_price, exercise_price_float)
                    print(f"  授予价格: {exercise_price_float}")
                    print(f"  折扣率: {discount_rate}%")
                    row['discount_rate'] = discount_rate
                except:
                    print(f"  授予价格格式错误: {exercise_price}")
                    row['discount_rate'] = ''
            else:
                print(f"  无授予价格")
                row['discount_rate'] = ''
            
            row['publish_date'] = publish_date
            row['trade_date'] = trade_date_fmt
            row['market_price'] = market_price
        else:
            print(f"  未获取到股价")
            fail_count += 1
            row['publish_date'] = publish_date
            row['trade_date'] = trade_date_fmt
            row['market_price'] = ''
            row['discount_rate'] = ''
        
        results.append(row)
        
        # 每10条保存一次
        if i % 10 == 0:
            with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
                writer.writeheader()
                writer.writerows(results)
    
    # 最终保存
    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n\n完成！")
    print(f"成功获取股价: {success_count}/{total}")
    print(f"失败: {fail_count}/{total}")
    print(f"结果已保存至: {output_path}")


if __name__ == "__main__":
    get_market_prices()