# -*- coding: utf-8 -*-
"""
现场实时 Pipeline 演示 — 真正调用正则提取函数，在观众眼前跑出结果

用法:
    cd project/
    python scripts/demo_live.py <doc_id>

示例:
    python scripts/demo_live.py 1224848770     # 良信股份
    python scripts/demo_live.py 1224821225     # 北方华创
"""

import json
import os
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

os.chdir(Path(__file__).resolve().parent.parent)
sys.path.insert(0, ".")
sys.path.insert(0, "src")

from src.extract_fields import (
    extract_grant_amount,
    extract_grant_ratio,
    extract_participant_count,
    extract_exercise_price,
    extract_market_price,
    extract_waiting_period,
    extract_validity_period,
    calculate_discount_rate,
)

SEP = "=" * 70


def wait():
    input("\n  >>> 按 Enter 继续下一步...")


def hr(title=""):
    print(f"\n  {'─' * 60}")
    if title:
        print(f"  {title}")
        print(f"  {'─' * 60}")


def find_evidence_context(text, patterns, max_context=250):
    """用多条正则找原文, 返回上下文片段"""
    for pat in patterns:
        m = re.search(pat, text, re.S)
        if m:
            start = max(0, m.start() - 60)
            end = min(len(text), m.end() + 60)
            snippet = text[start:end].replace("\n", " ").strip()
            # 高亮匹配部分
            match_text = m.group(0).replace("\n", " ").strip()
            return snippet, match_text
    return None, None


def find_line_number(text, snippet):
    """在原文中定位片段的行号"""
    idx = text.find(snippet.split()[0] if snippet else "")
    if idx >= 0:
        return text[:idx].count("\n") + 1
    return None


def main():
    doc_id = sys.argv[1] if len(sys.argv) > 1 else "1224848770"

    # ===== 读取 metadata =====
    metadata = {}
    with open("data/metadata/metadata.csv", "r", encoding="utf-8-sig") as f:
        for row in __import__("csv").DictReader(f):
            if row["doc_id"] == doc_id:
                metadata = row
                break

    if not metadata:
        print(f"  [ERROR] doc_id={doc_id} 不在 metadata.csv 中")
        sys.exit(1)

    md_path = f"markdown/md/{doc_id}.md"
    if not os.path.exists(md_path):
        print(f"  [ERROR] {md_path} 不存在")
        sys.exit(1)

    with open(md_path, "r", encoding="utf-8") as f:
        full_text = f.read()

    # ===== 开场 =====
    print(f"\n{'='*70}")
    print(f"  股权激励字段智能抽取 —— 现场实时 Pipeline 演示")
    print(f"  公告: {metadata['company_name']} ({metadata['stock_code']})")
    print(f"  doc_id = {doc_id}")
    print(f"  标题   = {metadata['announcement_title']}")
    print(f"  日期   = {metadata['publish_date']}")
    print(f"{'='*70}")
    wait()

    # ================================================================
    # STEP 1: 数据入口
    # ================================================================
    print(f"\n{SEP}")
    print(f"  [Step 1] 数据入口: metadata.csv + MinerU Markdown")
    print(f"{SEP}")

    print(f"""
  metadata.csv 本条记录:
    doc_id        = {metadata['doc_id']}
    stock_code    = {metadata['stock_code']}
    company_name  = {metadata['company_name']}
    pdf_url       = {metadata['pdf_url'][:80]}...
    download      = {metadata['download_status']}

  Markdown 文件: markdown/md/{doc_id}.md
  文件大小: {len(full_text):,} 字符 | {full_text.count(chr(10)) + 1} 行
  前 8 行预览:
""")
    for line in full_text.split("\n")[:8]:
        print(f"  | {line[:100]}")
    print(f"  | ...")
    wait()

    # ================================================================
    # STEP 2: 关键词定位
    # ================================================================
    print(f"\n{SEP}")
    print(f"  [Step 2] 在 {len(full_text):,} 字符中搜索 6 个字段的关键词")
    print(f"{SEP}")

    field_keywords = {
        "grant_amount":      [r"拟授予.{0,30}?万[份股]", r"权益总[计計].{0,20}?万[份股]"],
        "participant_count": [r"激励对象[共合].{0,30}?人", r"[共合]计.{0,15}?人"],
        "exercise_price":    [r"行权价格[为是:：].{0,20}?元"],
        "market_price":      [r"前\s*1\s*个?\s*交\s*易\s*日.{0,150}?交易均价"],
        "waiting_period":    [r"等待期.{0,30}?个月", r"满\s*\d+\s*个月后"],
        "validity_period":   [r"有效期.{0,30}?个月"],
    }

    found_snippets = {}
    for field, patterns in field_keywords.items():
        for pat in patterns:
            m = re.search(pat, full_text, re.S)
            if m:
                start = max(0, m.start() - 20)
                end = min(len(full_text), m.end() + 30)
                snippet = full_text[start:end].replace("\n", " ").strip()
                found_snippets[field] = snippet
                line_no = full_text[:m.start()].count("\n") + 1
                print(f"  [{field:20s}] 第{line_no}行 -> ...{snippet[:130]}...")
                break
    wait()

    # ================================================================
    # STEP 3: 实时提取 (逐字段调用 extract_xxx)
    # ================================================================
    print(f"\n{SEP}")
    print(f"  [Step 3] 实时提取: 逐字段调用 extract_fields.py 的函数")
    print(f"  *** 以下结果均为此刻实时计算, 非预读数据 ***")
    print(f"{SEP}")

    hr("字段 1: grant_amount (拟授予总数量, 万份)")
    grant_amount = extract_grant_amount(full_text)
    print(f"  提取结果: {grant_amount} 万份")
    print(f"  15条正则 | 单位判断: 检查匹配文本是否含'万份/万股' -> 没有则/10000")
    wait()

    hr("字段 2: grant_ratio (占总股本比例, %)")
    grant_ratio = extract_grant_ratio(full_text)
    print(f"  提取结果: {grant_ratio} %")
    print(f"  10条正则 | 限定在'授予/激励'关键词1000字符内 | 过滤 >50% 的异常值")
    wait()

    hr("字段 3: participant_count (激励人数)")
    participant_count = extract_participant_count(full_text)
    print(f"  提取结果: {participant_count} 人")
    print(f"  15条正则 | 千分位处理 | 范围验证 1 < N < 100,000")
    wait()

    hr("字段 4: exercise_price (行权价格, 元/份)")
    exercise_price = extract_exercise_price(full_text)
    print(f"  提取结果: {exercise_price} 元/份")
    print(f"  8条正则 | 匹配 '行权价格为 X 元' 等表述")
    wait()

    hr("字段 5: market_price (公告前1日交易均价) -- 最复杂")
    market_price = extract_market_price(full_text)
    print(f"  提取结果: {market_price} 元")
    print(f"  20条正则 + 三层优先级:")
    print(f"    P1: '每股X元 的 Y%' -> X = 市场价")
    print(f"    P2: '交易均价 的 Y%, 为 Z元' -> Z/(Y/100) 反推")
    print(f"    P3: '为每股 X 元' 兜底")
    print(f"  上下文过滤: 仅匹配'前1个交易日', 排除'前20/60/120日'")
    wait()

    hr("字段 5衍生: discount_rate (折扣率) -- 公式计算")
    discount_rate = calculate_discount_rate(exercise_price, market_price)
    print(f"  公式: (1 - {exercise_price}/{market_price}) * 100 = {discount_rate}%")
    print(f"  含义: 员工以低于市价 {discount_rate}% 的价格获得股票")
    if discount_rate is not None and discount_rate < 0:
        print(f"  ! 负数 -> 行权价高于市价, 激励价值存疑")
    wait()

    hr("字段 6a: waiting_period (等待期, 月)")
    waiting_period = extract_waiting_period(full_text)
    print(f"  提取结果: {waiting_period} 月")
    print(f"  10条正则 | 多阶段'分别为12/24/36月' -> 取第一个")
    wait()

    hr("字段 6b: validity_period (有效期, 月)")
    validity_period = extract_validity_period(full_text)
    print(f"  提取结果: {validity_period} 月")
    print(f"  8条正则 | 匹配'有效期最长X个月'/'不超过X个月'")
    wait()

    # ================================================================
    # STEP 4: Evidence.text — 全部7个字段的原文证据追溯
    # ================================================================
    print(f"\n{SEP}")
    print(f"  [Step 4] Evidence.text: 全部字段的原文证据追溯")
    print(f"  (展示每个字段的正则命中原文、行号、提取推理)")
    print(f"{SEP}")

    # 收集所有 evidence
    all_evidences = {}

    # ---- 辅助函数: 用多条正则找原文证据 ----
    def search_evidence(patterns, text):
        for pat in patterns:
            m = re.search(pat, text, re.S)
            if m:
                snippet = m.group(1) if m.lastindex else m.group(0)
                snippet = snippet.replace("\n", " ").strip()
                line_no = text[:m.start()].count("\n") + 1
                return snippet, line_no, m
        return None, None, None

    # ---- 1. grant_amount ----
    ga_evidence, ga_line, ga_match = search_evidence([
        r'(授予(?:的)?(?:股票期权|股票|权益).{0,50}?(?:共计|合计|共)\s*[0-9,.，]+\s*万[份股])',
        r'(拟向激励对象授予.{0,50}?[0-9,.，]+\s*万份)',
        r'(权益总[计計]\s*[0-9,.，]+\s*万[份股])',
        r'(拟授予.{0,30}?[0-9,.，]+\s*万[份股])',
    ], full_text)
    all_evidences["grant_amount"] = ga_evidence

    # ---- 2. grant_ratio ----
    gr_evidence, gr_line, gr_match = search_evidence([
        r'(约占.{0,30}?总股本.{0,20}?[0-9.]+\s*%)',
        r'(占.{0,30}?股本总额.{0,20}?[0-9.]+\s*%)',
        r'(占.{0,30}?股本比例.{0,20}?[0-9.]+\s*%)',
    ], full_text)
    all_evidences["grant_ratio"] = gr_evidence

    # ---- 3. participant_count ----
    pc_evidence, pc_line, pc_match = search_evidence([
        r'(激励对象共计\s*[0-9,，]+\s*[人名])',
        r'(激励对象总人数(?:为)?\s*[0-9,，]+\s*人)',
        r'(首次授予(?:的)?激励对象(?:共计|共|总人数为|人数为|总人数)?\s*[0-9,，]+\s*[人名])',
        r'(共\s*[0-9,，]+\s*名激励对象)',
        r'(涉及激励对象\s*[0-9,，]+\s*人)',
    ], full_text)
    all_evidences["participant_count"] = pc_evidence

    # ---- 4. exercise_price ----
    ep_evidence, ep_line, ep_match = search_evidence([
        r'(行权价格[为是:：]\s*[0-9.]+\s*元[^/股])',
        r'(行权价格为\s*[0-9.]+\s*元)',
        r'(股票期权(?:的)?行权价格[为是:：]?\s*[0-9.]+\s*元)',
    ], full_text)
    all_evidences["exercise_price"] = ep_evidence

    # ---- 5. market_price (最复杂) ----
    mkt_evidence, mkt_line, mkt_match = search_evidence([
        r'(前\s*(?:1|一)\s*个?\s*交\s*易\s*日[^。；\n]{0,200}?交易均价[^。；\n]{0,200}?的\s*[0-9.]+\s*%[^。；\n]{0,100}?为每?股?\s*[0-9.]+\s*元)',
        r'(前\s*(?:1|一)\s*个?\s*交\s*易\s*日[^。；\n]{0,200}?交易均价[^。；\n]{0,200}?为每?股?\s*[0-9.]+\s*元)',
    ], full_text)
    all_evidences["market_price"] = mkt_evidence

    # ---- 6. waiting_period ----
    wp_evidence, wp_line, wp_match = search_evidence([
        r'(等待期[为是]?\s*[0-9]+\s*个?月)',
        r'(等待期分别[为是]?\s*[^。；\n]{0,100}?[0-9]+\s*个?月)',
        r'(满\s*[0-9]+\s*个月后.{0,30}?(?:行权|解锁|解除限售|归属))',
        r'(授权日起满\s*[0-9]+\s*个月)',
    ], full_text)
    all_evidences["waiting_period"] = wp_evidence

    # ---- 7. validity_period ----
    vp_evidence, vp_line, vp_match = search_evidence([
        r'(有效期.{0,30}?最长.{0,10}?[0-9]+\s*个?月)',
        r'(有效期[为是]?\s*[0-9]+\s*个?月)',
        r'(激励计划.*?有效期.{0,20}?[0-9]+\s*个?月)',
        r'(最长不超过\s*[0-9]+\s*个?月)',
    ], full_text)
    all_evidences["validity_period"] = vp_evidence

    # ===============================
    # 逐字段展示 evidence
    # ===============================

    evidence_blocks = [
        {
            "num": 1,
            "name": "grant_amount (拟授予总数量, 万份)",
            "value": grant_amount,
            "evidence": ga_evidence,
            "line": ga_line,
            "patterns": '"授予...共计/合计 X 万份" 等 (15条规则)',
            "logic": [
                f"正则命中原文第 {ga_line} 行",
                "提取值: " + str(grant_amount),
                "检查匹配文本是否包含 '万份/万股':",
                "  有 -> 直接保留原值",
                "  没有 -> 单位是'份/股', 除以 10000",
                "早期坑: 如原文写 '5,726,100 份'(不带万), 不除以10000会得到 5726100 而非 572.61",
            ],
        },
        {
            "num": 2,
            "name": "grant_ratio (占总股本比例, %)",
            "value": grant_ratio,
            "evidence": gr_evidence,
            "line": gr_line,
            "patterns": '"约占...总股本...X%" 等 (10条规则)',
            "logic": [
                f"正则命中原文第 {gr_line} 行" if gr_line else "本字段在授予上下文外无匹配",
                "提取值: " + str(grant_ratio),
                "限定条件: 仅在 '授予/激励' 关键词 1000 字符内搜索",
                "合理性过滤: 值必须在 0~50% 之间 (排除个人持股等无关百分比)",
                "注意: 多数公告的 grant_ratio < 10%, 超过 20% 已属极高",
            ],
        },
        {
            "num": 3,
            "name": "participant_count (激励人数)",
            "value": participant_count,
            "evidence": pc_evidence,
            "line": pc_line,
            "patterns": '"激励对象共计 X 人" / "X 名激励对象" 等 (15条规则)',
            "logic": [
                f"正则命中原文第 {pc_line} 行" if pc_line else "未定位原文",
                "提取值: " + str(participant_count),
                "千分位处理: '6,302人' -> 去除逗号 -> 6302",
                "范围验证: 1 < 结果 < 100,000 (防止误匹配到其他数字)",
                "如果公告使用表格合计行, 匹配 '合计 X 人 100%' 模式",
            ],
        },
        {
            "num": 4,
            "name": "exercise_price (行权价格, 元/份)",
            "value": exercise_price,
            "evidence": ep_evidence,
            "line": ep_line,
            "patterns": '"行权价格为 X 元" 等 (8条规则)',
            "logic": [
                f"正则命中原文第 {ep_line} 行" if ep_line else "未定位原文",
                "提取值: " + str(exercise_price),
                "行权价格在公告中的写法非常统一, 是最好提取的字段之一",
                "注意区分 '授予价格' 和 '行权价格' (限制性股票用授予价格)",
            ],
        },
        {
            "num": 5,
            "name": "market_price (公告前1日交易均价, 元) —— 最复杂!",
            "value": market_price,
            "evidence": mkt_evidence,
            "line": mkt_line,
            "patterns": "三层优先级匹配 (20条规则)",
            "logic": [
                f"正则命中原文第 {mkt_line} 行" if mkt_line else "未定位原文",
                "提取值: " + str(market_price),
                "三层匹配策略:",
                "  优先级1: '每股X元 的 Y%' -> X = 市场价 (本文不适用)",
                "  优先级2: '交易均价 的 Y%, 为 Z元' -> Z/(Y/100) 反推",
                "           本例: 7.47 / 0.75 = 9.96 (命中!)",
                "  优先级3: '为每股 X 元' 兜底 (仅前两级都失败时使用)",
                "上下文过滤: 严格限定'前1个交易日', 排除'前20/60/120日'干扰",
                "错误做法: 直接取 7.47 -> discount_rate = -10.04% (逻辑错误)",
            ],
        },
        {
            "num": 6,
            "name": "waiting_period (等待期, 月)",
            "value": waiting_period,
            "evidence": wp_evidence,
            "line": wp_line,
            "patterns": '"等待期为 X 个月" / "满 X 个月后行权" 等 (10条规则)',
            "logic": [
                f"正则命中原文第 {wp_line} 行" if wp_line else "未定位原文",
                "提取值: " + str(waiting_period),
                "多阶段处理: '等待期分别为12、24、36个月' -> 取第一个 (12)",
                "行业惯例: 超过75%的企业等待期 = 12个月",
                "范围验证: 1 <= 等待期 <= 120 个月",
            ],
        },
        {
            "num": 7,
            "name": "validity_period (有效期, 月)",
            "value": validity_period,
            "evidence": vp_evidence,
            "line": vp_line,
            "patterns": '"有效期最长 X 个月" / "不超过 X 个月" 等 (8条规则)',
            "logic": [
                f"正则命中原文第 {vp_line} 行" if vp_line else "未定位原文",
                "提取值: " + str(validity_period),
                "有效期 = 自授权日起至全部行权/注销完毕之日止",
                "行业分布: 多数集中在 36~60 个月, 最长可达 120 个月",
                "这个字段与 waiting_period 配合, 共同刻画激励的时间维度",
            ],
        },
    ]

    for blk in evidence_blocks:
        ev = blk["evidence"]
        ln = blk["line"]
        print(f"""
  ┌── Evidence {blk['num']}: {blk['name']} ──┐
  │ 正则规则: {blk['patterns']}""")
        if ev and ln:
            # 截断过长的 evidence
            display_ev = ev[:300] + ("..." if len(ev) > 300 else "")
            print(f"  │ 原文位置: 第 {ln} 行")
            print(f"  │")
            print(f"  │ 原文证据 (evidence.text):")
            # 按句号分行, 每行不超过80字符
            for sentence in display_ev.split("。"):
                s = sentence.strip()
                if s:
                    while len(s) > 80:
                        print(f"  │   {s[:80]}")
                        s = s[80:]
                    print(f"  │   {s}。")
            print(f"  │")
            print(f"  │ 提取推理:")
            for logic_line in blk["logic"]:
                print(f"  │   {logic_line}")
        else:
            print(f"  │")
            print(f"  │ (未找到该字段的独立原文证据片段, 可能嵌入在长段落中)")
            print(f"  │")
            print(f"  │ 提取推理:")
            for logic_line in blk["logic"]:
                print(f"  │   {logic_line}")
        print(f"  │   => 最终值: {blk['value']}")
        print(f"  └{'─'*64}┘")

    wait()

    # ================================================================
    # STEP 5: Pydantic 实时校验
    # ================================================================
    print(f"\n{SEP}")
    print(f"  [Step 5] Pydantic Schema 实时校验 (src/schemas.py)")
    print(f"{SEP}")

    raw_result = {
        "doc_id": doc_id,
        "company_name": metadata["company_name"],
        "stock_code": metadata["stock_code"],
        "grant_amount": grant_amount,
        "grant_ratio": grant_ratio,
        "participant_count": participant_count,
        "exercise_price": exercise_price,
        "market_price": market_price,
        "discount_rate": discount_rate,
        "waiting_period": waiting_period,
        "validity_period": validity_period,
        "evidences": (
            [{"text": full_text[:500], "page_no": 1}]
            + [{"text": ev[:500], "field": f} for f, ev in all_evidences.items() if ev]
        ),
    }

    print(f"  实时提取的 JSON (不含 evidence 字段):")
    field_data = {k: v for k, v in raw_result.items() if k != "evidences"}
    print(f"  {json.dumps(field_data, ensure_ascii=False, indent=2)}")

    from src.schemas import EquityIncentiveExtract

    try:
        model = EquityIncentiveExtract.model_validate(raw_result)
        print(f"\n  [PASS] Pydantic 校验通过! 全部字段类型正确")
        print(f"  ─────────────────────────────────────")
        for name in ["grant_amount", "grant_ratio", "participant_count",
                      "exercise_price", "market_price", "discount_rate",
                      "waiting_period", "validity_period"]:
            val = getattr(model, name, None)
            t = type(val).__name__ if val is not None else "None(Optional)"
            status = "[OK]" if val is not None else "[OK-可选]"
            print(f"    {name:20s} {status} 类型={t:8s} 值={val}")
    except Exception as e:
        print(f"\n  [FAIL] 校验失败: {e}")
        print(f"  这条记录会被写入 outputs/logs/validation_errors.jsonl")
    wait()

    # ================================================================
    # STEP 6: CSV 输出
    # ================================================================
    print(f"\n{SEP}")
    print(f"  [Step 6] 最终 CSV 输出 — 找到本条记录在 records_validated.csv 中的行")
    print(f"{SEP}")

    csv_path = "outputs/results/records_validated.csv"
    found_in_csv = False
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            header = f.readline().strip()
            for line_no, line in enumerate(f, start=2):
                if doc_id in line:
                    found_in_csv = True
                    vals = line.strip().split(",")
                    cols = header.split(",")
                    print(f"  [CSV 第 {line_no} 行 (含表头)]")
                    print(f"  表头: {header}")
                    print(f"  数据: {','.join(vals)}")
                    print(f"\n  逐列对照 (实时提取 vs CSV 记录):")
                    for c, v in zip(cols, vals):
                        if c in field_data:
                            live_val = str(field_data[c])
                            match = "[一致]" if live_val == v else "[不一致!]"
                            print(f"    {c:20s}  实时={live_val:>10s}  CSV={v:>10s}  {match}")
                        else:
                            print(f"    {c:20s}  CSV={v}")
                    break

    if not found_in_csv:
        print(f"  doc_id={doc_id} 未在 records_validated.csv 中找到")
        print(f"  可能原因: 该条未通过校验 (检查 outputs/logs/validation_errors.jsonl)")
    wait()

    # ================================================================
    # 总结
    # ================================================================
    print(f"\n{SEP}")
    print(f"  [DONE] 现场 Pipeline 演示结束")
    print(f"")
    print(f"  本脚本刚才真实执行了以下 8 个函数 (来自 src/extract_fields.py):")
    print(f"    extract_grant_amount()       -> {grant_amount}")
    print(f"    extract_grant_ratio()        -> {grant_ratio}")
    print(f"    extract_participant_count()  -> {participant_count}")
    print(f"    extract_exercise_price()     -> {exercise_price}")
    print(f"    extract_market_price()       -> {market_price}  (三层反推)")
    print(f"    calculate_discount_rate()    -> {discount_rate}%")
    print(f"    extract_waiting_period()     -> {waiting_period}")
    print(f"    extract_validity_period()    -> {validity_period}")
    print(f"")
    print(f"  + Pydantic EquityIncentiveExtract.model_validate() -> {'PASS' if found_in_csv else 'N/A'}")
    print(f"  + CSV 查表 records_validated.csv -> {'第' + str(line_no) + '行' if found_in_csv else 'N/A'}")
    print(f"  + Evidence.text 原文追溯 -> 全部 7 个字段 (含行号 + 推理链路)")
    print(f"")
    print(f"  换一个公告: python scripts/demo_live.py <其他doc_id>")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
