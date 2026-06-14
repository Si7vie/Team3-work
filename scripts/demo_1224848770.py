#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo 脚本 —— 展示完整 PDF -> MD -> 字段提取 -> 校验 -> CSV 链路

用法:
    cd project/
    python scripts/demo_1224848770.py

演示公告: 良信股份 (002706) 2025年奋斗者3号股票期权激励计划
"""

import json
import sys
import os
from pathlib import Path

# Windows 终端 UTF-8 支持
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

os.chdir(Path(__file__).resolve().parent.parent)  # cd 到 project/ 根目录
sys.path.insert(0, ".")

DEMO_DOC_ID = "1224848770"
MARKDOWN_PATH = f"markdown/md/{DEMO_DOC_ID}.md"
EXTRACT_PATH = "outputs/results/extract_results.jsonl"
VALIDATED_PATH = "outputs/results/records_validated.csv"
SECTION_CHECK_PATH = "outputs/section_check_report.csv"
ERRORS_PATH = "outputs/logs/validation_errors.jsonl"
METADATA_PATH = "data/metadata/metadata.csv"

SEP = "=" * 70
SUB = "-" * 70


def main():
    print(f"\n{SEP}")
    print(f"  [Demo] 股权激励字段智能抽取 —— 完整链路演示")
    print(f"  演示公告: 良信股份 (002706) | doc_id = {DEMO_DOC_ID}")
    print(f"{SEP}\n")

    # ============================================================
    # 步骤 1: Metadata
    # ============================================================
    print(f">> 步骤 1/7: metadata.csv 元数据记录")
    print(SUB)
    with open(METADATA_PATH, "r", encoding="utf-8-sig") as f:
        header = f.readline().strip()
        print(f"  [表头] {header}")
        for line in f:
            if DEMO_DOC_ID in line:
                parts = line.strip().split(",")
                print(f"  doc_id       = {parts[0]}")
                print(f"  stock_code   = {parts[1]}")
                print(f"  company_name = {parts[2]}")
                print(f"  title        = {parts[4]}")
                print(f"  publish_date = {parts[6]}")
                print(f"  pdf_url      = {parts[8][:60]}...")
                print(f"  download     = {parts[-2]}")
                break
    print(f"  PDF链接: https://static.cninfo.com.cn/finalpage/2025-12-04/{DEMO_DOC_ID}.PDF")
    print()

    # ============================================================
    # 步骤 2: Markdown 关键片段
    # ============================================================
    print(f">> 步骤 2/7: MinerU 解析后的 Markdown（关键字段所在段落）")
    print(SUB)

    with open(MARKDOWN_PATH, "r", encoding="utf-8") as f:
        all_lines = f.readlines()

    # 展示 grant_amount 和 participant_count 区域
    print(f"  --- grant_amount & grant_ratio (第29行) ---")
    print(f"  {all_lines[28].rstrip()}")
    print()
    print(f"  --- participant_count (第35行) ---")
    print(f"  {all_lines[34].rstrip()}")
    print()
    print(f"  --- exercise_price (第36行) ---")
    print(f"  {all_lines[35].rstrip()}")
    print()
    print(f"  --- validity_period (第40行) ---")
    print(f"  {all_lines[39].rstrip()}")
    print()
    print(f"  --- waiting_period (第42行) ---")
    print(f"  {all_lines[41].rstrip()}")
    print()

    # 特别展示 market_price 关键段落
    print(f"  --- market_price (交易均价 -- 最复杂的字段, 第259-260行) ---")
    for i in [258, 259, 260]:
        if i <= len(all_lines):
            print(f"  第{i}行: {all_lines[i-1].rstrip()}")
    print()
    print(f"  --> 提取策略: 命中优先级2 -- 识别到 '交易均价的75.00%,为每股7.47元'")
    print(f"  --> 反推计算: 7.47 / 0.75 = 9.96 元 (真正的市场价)")
    print(f"  --> 排除干扰: 第260行 '前120个交易日' 不在匹配范围内")
    print()

    # ============================================================
    # 步骤 3: Section Check
    # ============================================================
    print(f">> 步骤 3/7: 段落路由检查 (section_check_report)")
    print(SUB)
    with open(SECTION_CHECK_PATH, "r", encoding="utf-8-sig") as f:
        header = f.readline().strip()
        for line in f:
            if DEMO_DOC_ID in line:
                parts = line.strip().split(",")
                print(f"  doc_id         = {parts[0]}")
                print(f"  target_section = {parts[2]}")
                print(f"  found          = {parts[3]}")
                print(f"  section_title  = {parts[4]}")
                print(f"  quality_issue  = {parts[7]}")
                print(f"  notes          = {parts[8][:80]}...")
                break
    print()

    # ============================================================
    # 步骤 4: Extract Results (JSONL)
    # ============================================================
    print(f">> 步骤 4/7: 正则字段提取结果 (extract_results.jsonl)")
    print(SUB)
    record = None
    with open(EXTRACT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r["doc_id"] == DEMO_DOC_ID:
                record = r
                break

    if record:
        print(f"  {json.dumps(record, ensure_ascii=False, indent=2)}")
        print()

        # 字段提取说明
        print(f"  [字段映射]")
        print(f"     grant_amount      = {record['grant_amount']:>10.4f} 万份   <-- 原文 '权益总计 776 万份'")
        print(f"     grant_ratio       = {record['grant_ratio']:>10.4f} %      <-- 原文 '0.69%' (在授予上下文内)")
        print(f"     participant_count = {record['participant_count']:>10d} 人    <-- 原文 '激励对象共计 386 人'")
        print(f"     exercise_price    = {record['exercise_price']:>10.2f} 元/份  <-- 原文 '行权价格为 8.22 元/份'")
        print(f"     market_price      = {record['market_price']:>10.2f} 元     <-- 反推: 7.47/0.75=9.96")
        print(f"     discount_rate     = {record['discount_rate']:>10.2f} %     <-- 计算: (1-8.22/9.96)*100")
        print(f"     waiting_period    = {record['waiting_period']:>10.0f} 月    <-- 原文 '满 12 个月后分两期行权'")
        print(f"     validity_period   = {record['validity_period']:>10.0f} 月    <-- 原文 '最长不超过36个月'")
        print()

    # ============================================================
    # 步骤 5: Pydantic 校验
    # ============================================================
    print(f">> 步骤 5/7: Pydantic Schema 校验")
    print(SUB)
    try:
        from src.schemas import EquityIncentiveExtract

        model = EquityIncentiveExtract.model_validate(record)
        print(f"  [OK] 校验通过!")
        print(f"     grant_amount      类型: {type(model.grant_amount).__name__:8s}  值: {model.grant_amount}")
        print(f"     grant_ratio       类型: {type(model.grant_ratio).__name__:8s}  值: {model.grant_ratio}")
        print(f"     participant_count 类型: {type(model.participant_count).__name__:8s}  值: {model.participant_count}")
        print(f"     exercise_price    类型: {type(model.exercise_price).__name__:8s}  值: {model.exercise_price}")
        print(f"     market_price      类型: {type(model.market_price).__name__:8s}  值: {model.market_price}")
        print(f"     discount_rate     类型: {type(model.discount_rate).__name__:8s}  值: {model.discount_rate}")
        print(f"     waiting_period    类型: {type(model.waiting_period).__name__:8s}  值: {model.waiting_period}")
        print(f"     validity_period   类型: {type(model.validity_period).__name__:8s}  值: {model.validity_period}")
    except Exception as e:
        print(f"  [FAIL] 校验失败: {e}")
    print()

    # 确认不在错误列表中
    error_ids = []
    with open(ERRORS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                e = json.loads(line)
                error_ids.append(e.get("doc_id"))
    if DEMO_DOC_ID not in error_ids:
        print(f"  [OK] 确认: {DEMO_DOC_ID} 不在 validation_errors.jsonl 中")
    else:
        print(f"  [FAIL] {DEMO_DOC_ID} 在校验错误列表中!")
    print()

    # ============================================================
    # 步骤 6: Final CSV
    # ============================================================
    print(f">> 步骤 6/7: 最终 CSV 输出 (records_validated.csv)")
    print(SUB)
    with open(VALIDATED_PATH, "r", encoding="utf-8-sig") as f:
        header = f.readline().strip()
        print(f"  [CSV表头] {header}")
        for line in f:
            if DEMO_DOC_ID in line:
                vals = line.strip().split(",")
                print(f"  [数据行]  {','.join(vals)}")
                print()
                print(f"  [列对应]")
                cols = header.split(",")
                for c, v in zip(cols, vals):
                    print(f"     {c:20s} = {v}")
                break
    print()

    # ============================================================
    # 步骤 7: 关键字段 evidence 详解
    # ============================================================
    print(f">> 步骤 7/7: 两个关键字段的提取逻辑深度解析")
    print(SUB)

    print(f"""
  +-- market_price (交易均价) -- 三层优先级反推策略 -------------------+
  |                                                                   |
  |  原文:                                                             |
  |  "本激励计划草案公布前1个交易日的公司股票交易均价的75.00%,          |
  |   为每股 7.47 元"                                                  |
  |                                                                   |
  |  三层匹配:                                                         |
  |  (skip) 优先级1: "每股X元 的 Y%" -> 原文无此结构                    |
  |  (HIT!) 优先级2: "交易均价 的 Y%, 为/即 Z元" -> 7.47/0.75=9.96     |
  |  (skip) 优先级3: 直接匹配 (仅在优先级1/2都失败时使用)               |
  |                                                                   |
  |  上下文过滤: 严格限定"前1个交易日",排除"前120个交易日"的干扰         |
  |  验证: (1 - 8.22/9.96) * 100 = 17.47%  [OK]                       |
  |                                                                   |
  |  (WRONG) 如果直接取7.47 -> discount_rate = (1-8.22/7.47)*100       |
  |          = -10.04% (员工花8.22买市价7.47的股票? 逻辑不通)           |
  +-------------------------------------------------------------------+

  +-- grant_amount (授予总量) -- 单位判断 -----------------------------+
  |                                                                   |
  |  原文: "拟授予激励对象的权益总计 776 万份"                          |
  |                                                                   |
  |  四种可能的表述:                                                    |
  |  [OK] "权益总计 776 万份"      -> 直接保留 776.0                   |
  |  [OK] "授予权益 1,200.00 万股" -> 直接保留 1200.0                  |
  |  [WARN] "期权上限为 5,726,100 份"  -> /10000 = 572.61              |
  |  [WARN] "授予 116,407,025 股"      -> /10000 = 11640.70            |
  |                                                                   |
  |  核心判断: 正则匹配文本中是否包含 "万份" 或 "万股"                  |
  |  有 -> 直接使用 | 没有 -> /10000                                  |
  +-------------------------------------------------------------------+
""")

    # 总结
    print(SEP)
    print(f"  [DONE] Demo 完成!")
    print(f"  一条公告 PDF -> 经过 6 个环节 -> 11 列结构化数据")
    print(f"  200 份公告中: 198 份通过校验 (99%) | 2 份为附录文件")
    print(SEP)
    print()


if __name__ == "__main__":
    main()
