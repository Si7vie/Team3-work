#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式 Demo 脚本 —— 现场演示专用，每步按 Enter 继续

用法:
    cd project/
    python scripts/demo_interactive.py

演示公告: 良信股份 (002706) 2025年奋斗者3号股票期权激励计划
"""

import json
import os
import sys
from pathlib import Path

# Windows 终端 UTF-8 支持
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

os.chdir(Path(__file__).resolve().parent.parent)
sys.path.insert(0, ".")

DEMO_DOC_ID = "1224848770"
SEP = "=" * 70


def wait():
    input("\n  >>> 按 Enter 继续下一步...")


def title(n, text):
    print(f"\n\n{SEP}")
    print(f"  步骤 {n}/7: {text}")
    print(f"{SEP}\n")


def show_file(path, label, grep_id=None):
    """展示文件内容"""
    if grep_id and os.path.exists(path):
        with open(path, "r", encoding="utf-8-sig") as f:
            header = f.readline().strip()
            print(f"  [文件] {label}")
            print(f"  [表头] {header}")
            for line in f:
                if grep_id in line:
                    vals = line.strip().split(",")
                    cols = header.split(",")
                    for c, v in zip(cols, vals):
                        print(f"    {c:20s} = {v}")
                    break
    elif os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read(600)
            print(f"  [文件] {label}")
            print(f"  {content[:400]}...")


def main():
    print(f"\n{'='*70}")
    print(f"  股权激励字段智能抽取 —— 现场交互式 Demo")
    print(f"  演示公告: 良信股份 (002706) | doc_id = {DEMO_DOC_ID}")
    print(f"  操作方式: 每步自动展示结果，按 Enter 进入下一步")
    print(f"{'='*70}")
    wait()

    # ========================
    title(1, "原始 PDF 公告 & metadata.csv 元数据记录")

    print(f"  [操作] 浏览器打开 PDF:")
    print(f"  https://static.cninfo.com.cn/finalpage/2025-12-04/{DEMO_DOC_ID}.PDF")
    print()
    print(f"  这是巨潮资讯网上的原始公告 PDF —— 复杂排版、Logo、表格")
    print(f"  人读没问题，但计算机无法直接处理 -> 需要 MinerU 转换")
    print()

    show_file("data/metadata/metadata.csv", "metadata.csv 中的元数据记录", DEMO_DOC_ID)

    print(f"\n  metadata.csv 是整个流水线的「输入清单」")
    print(f"  200 行 = 200 份公告，每行包含: 股票代码、公司名、PDF下载地址")
    wait()

    # ========================
    title(2, "MinerU 解析后的 Markdown 文本")

    with open(f"markdown/md/{DEMO_DOC_ID}.md", "r", encoding="utf-8") as f:
        lines = f.readlines()

    snippets = [
        (28, "grant_amount (授予总量) + grant_ratio (占比)"),
        (34, "participant_count (激励人数)"),
        (35, "exercise_price (行权价格)"),
        (39, "validity_period (有效期)"),
        (41, "waiting_period (等待期)"),
    ]

    print(f"  PDF 被 MinerU 转成了纯文本 Markdown (共 {len(lines)} 行)")
    print(f"  以下是我们要抓的 6 个字段在原文中的位置:\n")

    for line_no, desc in snippets:
        text = lines[line_no].strip()
        # 截断过长行
        if len(text) > 150:
            text = text[:150] + "..."
        print(f"  第{line_no+1}行 [{desc}]")
        print(f"  -> {text}\n")

    print(f"  --- 关键: market_price (交易均价) 在第259-260行 ---")
    for i in [258, 259]:
        print(f"  第{i+1}行: {lines[i].strip()}")
    print()
    print(f"  !!! 注意: 7.47 不是市场价! '均价的 75%' -> 反推: 7.47 / 0.75 = 9.96")
    print(f"  !!! 同时必须忽略第260行 '前120个交易日' 的数据")
    wait()

    # ========================
    title(3, "段落路由检查 (section_check_report)")

    show_file("outputs/section_check_report.csv", "section_check_report.csv", DEMO_DOC_ID)

    print(f"\n  found=true: 成功定位到股权激励段落")
    print(f"  section_title=FULL_DOCUMENT: 使用全文 (激励计划内容完整)")
    print(f"  quality_issue=ok: 文本质量合格, 无截断")
    wait()

    # ========================
    title(4, "正则字段提取结果 (extract_results.jsonl)")

    record = None
    with open("outputs/results/extract_results.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r["doc_id"] == DEMO_DOC_ID:
                record = r
                break

    if record:
        print(f"  [extract_results.jsonl 中的完整 JSON 记录]\n")
        print(f"  {json.dumps(record, ensure_ascii=False, indent=2)}")
        print()
        print(f"  [7个字段的提取来源]")
        print(f"    grant_amount      = {record['grant_amount']:>10.2f} 万份   <-- 第29行 '权益总计 776 万份'")
        print(f"    grant_ratio       = {record['grant_ratio']:>10.2f} %      <-- 第29行 '0.69%'")
        print(f"    participant_count = {record['participant_count']:>10d} 人    <-- 第35行 '激励对象共计 386 人'")
        print(f"    exercise_price    = {record['exercise_price']:>10.2f} 元/份  <-- 第36行 '行权价格为 8.22 元/份'")
        print(f"    market_price      = {record['market_price']:>10.2f} 元     <-- 第259行 反推: 7.47/0.75=9.96")
        print(f"    discount_rate     = {record['discount_rate']:>10.2f} %     <-- 计算: (1-8.22/9.96)*100")
        print(f"    waiting_period    = {record['waiting_period']:>10.0f} 月    <-- 第42行 '满12个月后'")
        print(f"    validity_period   = {record['validity_period']:>10.0f} 月    <-- 第40行 '最长不超过36个月'")
        print()
        print(f"  evidence.text = 公告全文前500字符, 用于人工核验追溯")
    wait()

    # ========================
    title(5, "Pydantic Schema 校验")

    try:
        from src.schemas import EquityIncentiveExtract
        model = EquityIncentiveExtract.model_validate(record)
        print(f"  [OK] Pydantic 校验通过!")
        print(f"  Schema 自动检查了每个字段的类型:")
        print(f"    grant_amount      = {model.grant_amount:>10.2f}  (类型: float) [OK]")
        print(f"    grant_ratio       = {model.grant_ratio:>10.2f}  (类型: float) [OK]")
        print(f"    participant_count = {model.participant_count:>10d}  (类型: int)   [OK]")
        print(f"    exercise_price    = {model.exercise_price:>10.2f}  (类型: float) [OK]")
        print(f"    market_price      = {model.market_price:>10.2f}  (类型: float) [OK]")
        print(f"    discount_rate     = {model.discount_rate:>10.2f}  (类型: float) [OK]")
        print(f"    waiting_period    = {model.waiting_period:>10.0f}  (类型: float) [OK]")
        print(f"    validity_period   = {model.validity_period:>10.0f}  (类型: float) [OK]")
    except Exception as e:
        print(f"  [FAIL] 校验失败: {e}")

    # 查错误日志
    error_ids = []
    with open("outputs/logs/validation_errors.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                error_ids.append(json.loads(line).get("doc_id"))
    print(f"\n  {DEMO_DOC_ID} {'不在' if DEMO_DOC_ID not in error_ids else '在'} validation_errors.jsonl 中")
    print(f"  200 条记录: 198 通过校验 | 2 条失败 (东软集团+中岩大地, 原因为附录文件)")
    wait()

    # ========================
    title(6, "最终 CSV 输出 (records_validated.csv)")

    show_file("outputs/results/records_validated.csv", "records_validated.csv", DEMO_DOC_ID)

    print(f"\n  这就是下游分析的输入数据")
    print(f"  11 列 = 身份信息(3列) + 提取字段(6列) + 衍生字段(2列)")
    wait()

    # ========================
    title(7, "关键字段提取逻辑深度解析")

    print(f"""
  ┌── market_price (交易均价) ── 三层优先级反推策略 ──────────────┐
  │                                                                │
  │  原文: "前1个交易日公司股票交易均价的 75%, 为每股 7.47 元"       │
  │                                                                │
  │  优先级1 [SKIP]: 找 "每股X元 的 Y%" 结构 → 原文不是这样写的     │
  │  优先级2 [HIT!]: 找 "交易均价 的 Y%, 为 Z元" → Z/Y*100=9.96     │
  │                 7.47 / 75% = 9.96 元 ← 这才是真正的市场价!      │
  │  优先级3 [SKIP]: 直接匹配 "为每股 X 元"                         │
  │                                                                │
  │  上下文过滤: 限定"前1个交易日", 排除第260行"前120个交易日"       │
  │  交叉验证: (1 - 8.22/9.96) * 100 = +17.47% -> 合理!            │
  │                                                                │
  │  错误案例: 直接取 7.47 -> discount_rate = -10.04% (逻辑错误!)   │
  └────────────────────────────────────────────────────────────────┘

  ┌── grant_amount (授予总量) ── 单位判断 ─────────────────────────┐
  │                                                                │
  │  原文: "拟授予激励对象的权益总计 776 万份"                       │
  │                                                                │
  │  15条正则规则按优先级依次匹配, 每条规则命中后:                    │
  │    检查匹配文本中是否包含 "万份" 或 "万股"                       │
  │    有 -> 直接使用 (如 776 万份 -> 776.0)                        │
  │    没有 -> /10000 (如 5,726,100 份 -> 572.61)                  │
  │                                                                │
  │  早期代码忽略此判断 -> 572万份被当成 5.7亿份 -> 已修正           │
  └────────────────────────────────────────────────────────────────┘
""")
    wait()

    # ========================
    print(f"\n{'='*70}")
    print(f"  [DONE] 完整 Demo 结束!")
    print(f"  数据 -> API -> MinerU -> Section -> Schema -> Workflow")
    print(f"  一条 PDF -> 6个环节 -> 11列结构化数据")
    print(f"  200份公告: 198通过(99%) | 2失败(附录文件)")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
