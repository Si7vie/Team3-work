from __future__ import annotations

import argparse
import json
import os
import re

import requests
from dotenv import load_dotenv

from common import read_jsonl, read_yaml, write_jsonl


# ============================================================================
# Regex extraction helpers
# ============================================================================

def _first_number(s: str) -> float | None:
    """Return the first float from a cleaned string, or None."""
    s = s.replace(",", "").replace("，", "").strip()
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)", s)
    return float(m.group(1)) if m else None


def _safe_float(s: str) -> float:
    return float(s.replace(",", "").replace("，", "").strip())


# ============================================================================
# grant_amount
# ============================================================================

def extract_grant_amount(text: str) -> float | None:
    patterns = [
        # "授予...共计/合计/共 X 万份"
        r"授予(?:的)?(?:股票期权|股票|权益).*?(?:共计|合计|共)\s*([0-9,.，]+)\s*万[份股]",
        # "拟向激励对象授予...X万份"
        r"拟向激励对象授予.*?([0-9,.，]+)\s*万份",
        r"拟授予.*?(?:股票期权)?.*?([0-9,.，]+)\s*万份",
        r"授予(?:的)?股票期权(?:总量|数量).*?([0-9,.，]+)\s*万份",
        r"拟授出(?:的)?(?:权益|股票期权).*?([0-9,.，]+)\s*万份",
        r"权益总[计計]\s*([0-9,.，]+)\s*万[份股]",
        r"授予权益总[计計]\s*([0-9,.，]+)\s*万[份股]",
        r"股票期权(?:总量|数量)\s*(?:为|共计|共)?\s*([0-9,.，]+)\s*万份",
        # 不超过
        r"不超过\s*([0-9,.，]+)\s*万份",
        # "可授予的...期权上限为 X 份" (不带万)
        r"(?:可授予|授予)(?:的)?.*?期权上限为\s*([0-9,.，]+)\s*[份股]",
        # 不带"万"的(需要除以10000)
        r"拟向激励对象授予.*?([0-9,.，]+)\s*[份股](?:股票|激励|，|。)",
        r"授予(?:的)?股票期权总量.*?([0-9,.，]+)\s*[份股]",
        r"拟授予.*?([0-9,.，]+)\s*[份股](?:股票|，|。)",
        r"权益总[计計]\s*([0-9,.，]+)\s*[份股]",
        # 激励计划涉及的股票期权
        r"(?:本|本次?)(?:激励)?计划.*?拟授予.*?([0-9,.，]+)\s*万[份股]",
        # 拟授出的权益情况章节的表格
        r"拟授出的权益.*?([0-9,.，]+)\s*万[份股]",
    ]

    for p in patterns:
        m = re.search(p, text, re.S)
        if m:
            value = _safe_float(m.group(1))
            matched = m.group(0)
            # 如果匹配文本中不包含"万份"或"万股"，说明单位是"份"，需要除以10000
            if "万份" not in matched and "万股" not in matched:
                value = value / 10000
            return round(value, 4)

    # 兜底：尝试找 "股票期权数量为 X 万份"
    m = re.search(r"股票期权数量[为计]\s*([0-9,.，]+)\s*万", text)
    if m:
        return round(_safe_float(m.group(1)), 4)

    return None


# ============================================================================
# grant_ratio
# ============================================================================

def extract_grant_ratio(text: str) -> float | None:
    patterns = [
        r"约占.*?总股本.*?([0-9.]+)\s*%",
        r"约占.*?股本总额.*?([0-9.]+)\s*%",
        r"约占.*?股份总数.*?([0-9.]+)\s*%",
        r"约占.*?股本总数.*?([0-9.]+)\s*%",
        r"占.*?总股本.*?([0-9.]+)\s*%",
        r"占.*?股本总额.*?([0-9.]+)\s*%",
        r"占.*?股本比例.*?([0-9.]+)\s*%",
        r"占.*?公司股本总额.*?([0-9.]+)\s*%",
        r"占.*?目前总股本.*?([0-9.]+)\s*%",
        r"占.*?股份总数.*?([0-9.]+)\s*%",
    ]

    # 优先找"拟授予"或"授予"附近的
    for p in patterns:
        grant_contexts = [m.start() for m in re.finditer(r"授[予与]|激励", text)]
        best_val = None
        for m in re.finditer(p, text, re.S):
            val = float(m.group(1))
            pos = m.start()
            # 检查是否在授予相关上下文附近
            near_grant = any(abs(pos - gc) < 1000 for gc in grant_contexts)
            if near_grant:
                # 过滤掉明显不对的值(如个人占比)
                if val <= 50:
                    return val
            if best_val is None:
                best_val = val
        if best_val is not None and best_val <= 50:
            return best_val

    # 如果以上都没找到，在全文中直接找
    for p in patterns:
        m = re.search(p, text, re.S)
        if m:
            val = float(m.group(1))
            if val <= 50:
                return val

    return None


# ============================================================================
# participant_count
# ============================================================================

def extract_participant_count(text: str) -> int | None:
    patterns = [
        # 最精确的模式优先
        r"首次授予(?:的)?激励对象(?:共计|共|总人数为|人数为|总人数)?\s*([0-9,，]+)\s*[人名]",
        r"激励对象总人数(?:为)?\s*([0-9,，]+)\s*人",
        r"激励对象人数(?:为)?\s*([0-9,，]+)\s*人",
        r"激励对象共计\s*([0-9,，]+)\s*[人名]",
        r"激励对象(?:共计|共)?\s*([0-9,，]+)\s*[人名]",
        r"(?:本|本次?)(?:激励)?计划.*?激励对象.*?共计\s*([0-9,，]+)\s*人",
        r"(?:本|本次?)(?:激励)?计划.*?激励对象.*?([0-9,，]+)\s*[人名]",
        r"涉及激励对象\s*([0-9,，]+)\s*人",
        r"涉及\s*([0-9,，]+)\s*名激励对象",
        r"共\s*([0-9,，]+)\s*名激励对象",
        r"激励对象\s*([0-9,，]+)\s*人",
        r"激励对象.*?不超过\s*([0-9,，]+)\s*人",
        r"首次授予.*?共计\s*([0-9,，]+)\s*人",
        r"首次授予.*?共\s*([0-9,，]+)\s*人",
        # 表格合计行
        r"合[计計]\s*([0-9,，]+)\s*[人名]",
        r"总[计計]\s*([0-9,，]+)\s*[人名]",
        r"合[计計]\s*([0-9,，]+)\s*(?:100|100\.00)\s*%",
    ]

    for p in patterns:
        m = re.search(p, text, re.S)
        if m:
            try:
                val = int(m.group(1).replace(",", "").replace("，", ""))
                if 0 < val < 100000:  # sane range
                    return val
            except ValueError:
                continue

    return None


# ============================================================================
# exercise_price
# ============================================================================

def extract_exercise_price(text: str) -> float | None:
    patterns = [
        r"行权价格[为是:：]\s*([0-9.]+)\s*元",
        r"行权价格为\s*([0-9.]+)\s*元",
        r"股票期权(?:的)?行权价格[为是:：]?\s*([0-9.]+)\s*元",
        r"授予价格[为是:：]\s*([0-9.]+)\s*元",
        r"行权价格[^。；\n]{0,50}?([0-9.]+)\s*元",
        r"行权价[为是]\s*([0-9.]+)\s*元",
        # 比较宽泛的模式
        r"股票期权的行权价格.*?([0-9.]+)\s*元",
        r"首次授予.*?行权价格.*?([0-9.]+)\s*元",
    ]

    for p in patterns:
        m = re.search(p, text, re.S)
        if m:
            return float(m.group(1))

    return None


# ============================================================================
# market_price (完全重写)
# ============================================================================

def extract_market_price(text: str) -> float | None:
    """
    从公告文本中提取 "草案公告前1个交易日公司股票交易均价"。

    按优先级三步匹配:
      1. "每股X元 / X元/股 的 Y%"      →  X 就是交易均价
      2. "交易均价(的) Y%，为/即 Z元"   →  Z / (Y/100) 反推交易均价
      3. 直接价格声明                     →  直接提取
    """

    # ---- 第一步: 找到所有"前1个交易日"+"交易均价"的上下文 ----
    # 策略: 找到所有"前1(一)个交易日"的位置, 提取其后的文本直到句号/分号/换行,
    #        只要该段落在"交易均价"之前没有出现"前20/60/120"

    segments = []

    # 找到所有 "前1个交易日" / "前一个交易日" 的位置
    anchor_pattern = re.compile(
        r'(?:前|本|本次?|股权|该)?(?:激励计划|股票期权|计划|草案|本计划)?'
        r'(?:草案)?(?:公布|公告|披露)?'
        r'前\s*(?:1|一)\s*个?\s*交\s*易\s*日',
        re.S
    )

    for anchor in anchor_pattern.finditer(text):
        anchor_start = anchor.start()
        # 提取从anchor开始到下一个分段标记的文本(~400 chars)
        end_markers = r'[。；\n]'
        rest = text[anchor_start:anchor_start + 600]
        # 找到第一个句号/分号/换行的位置
        end_match = re.search(end_markers, rest)
        if end_match:
            window_end = anchor_start + end_match.start()
        else:
            window_end = min(len(text), anchor_start + 600)

        window = text[anchor_start:window_end]

        # 只在window包含"交易均价"时才处理
        if '交易均价' not in window:
            continue

        # 检查: 在"前1个交易日"和"交易均价"之间是否有"前20/60/120"
        tjj_pos = window.find('交易均价')
        prefix = window[:tjj_pos]
        if re.search(r'前\s*(?:20|60|120)\s*个\s*交\s*易\s*日', prefix):
            # 这个window混合了1日和20/60/120日, 需要更精确提取
            # 只保留到"交易均价"之前不含20/60/120的部分
            continue  # skip ambiguous windows

        # 获取更完整的上下文（包含前的引导语）
        full_start = max(0, anchor_start - 80)
        full_end = min(len(text), window_end + 200)
        full_window = text[full_start:full_end]
        segments.append(full_window)

    # 去重
    seen = set()
    unique_segments = []
    for s in segments:
        if s not in seen:
            seen.add(s)
            unique_segments.append(s)

    # ---- 第二步: 在每个segment中按优先级提取价格 ----
    for segment in unique_segments:

        # ==== 优先级1: "X元/股 的 Y%" 或 "每股X元 的 Y%" ====
        # 如: "14.10元/股的50%，为每股7.05元" → X=14.10
        # 如: "每股90.49元的50%，为每股45.25元" → X=90.49
        m1 = re.search(
            r'(?:每股\s*([0-9.]+)\s*元|([0-9.]+)\s*元\s*/\s*股)'
            r'[^。；\n]{0,60}?的\s*([0-9.]+)\s*%',
            segment, re.S
        )
        if m1:
            price = float(m1.group(1) or m1.group(2))
            pct_val = float(m1.group(3))
            # 验证后面跟着的折扣价是否合理
            verify = re.search(
                r'(?:为每股|即每股|为\s*每股|即为每股|为每份|即每份|为|即)\s*([0-9.]+)\s*元',
                segment[m1.end():], re.S
            )
            if verify:
                expected = round(price * pct_val / 100, 2)
                got = float(verify.group(1))
                if abs(expected - got) <= max(0.15, expected * 0.05):
                    return price
            # 验证不通过也返回（模式足够明确）
            return price

        # ==== 优先级2: "交易均价(的) Y%，为/即 Z元" (反推) ====
        m2 = re.search(
            r'交易均价[^。；\n]{0,60}?的\s*([0-9.]+)\s*%'
            r'[^。；\n]{0,80}?'
            r'(?:为每股|即每股|为\s*每股|即为每股|为每份|即每份|为|即|即为)\s*([0-9.]+)\s*元',
            segment, re.S
        )
        if m2:
            pct = float(m2.group(1)) / 100
            discounted_price = float(m2.group(2))
            if pct > 0:
                market_price = round(discounted_price / pct, 2)
                if 0.01 < market_price < 10000:
                    return market_price

        # ==== 优先级3: 直接价格声明 ====

        # 3a: "为每股 X 元"
        m3a = re.search(r'为每股\s*([0-9.]+)\s*元', segment)
        if m3a:
            return float(m3a.group(1))

        # 3b: "为每份 X 元" 或 "即每份 X 元"
        m3b = re.search(r'(?:为每份|即每份)\s*([0-9.]+)\s*元', segment)
        if m3b:
            return float(m3b.group(1))

        # 3c: "为 X 元/股" 或 "即 X 元/股"
        m3c = re.search(r'(?:为|即)\s*([0-9.]+)\s*元\s*/\s*股', segment)
        if m3c:
            return float(m3c.group(1))

        # 3d: "为 X 元" (在交易均价上下文中)
        m3d = re.search(r'为\s*([0-9.]+)\s*元[^/\w]', segment)
        if m3d:
            candidate = float(m3d.group(1))
            if 0.5 < candidate < 10000:
                return candidate

        # 3e: "即人民币 X 元"
        m3e = re.search(r'即人民币\s*([0-9.]+)\s*元', segment)
        if m3e:
            return float(m3e.group(1))

        # 3f: "即每股 X 元"
        m3f = re.search(r'即每股\s*([0-9.]+)\s*元', segment)
        if m3f:
            return float(m3f.group(1))

        # 3g: "交易均价" 后紧跟 "X 元" (无"为"/"即")
        m3g = re.search(r'交易均价[^。；\n]{0,100}?[^0-9]([0-9.]+)\s*元[^/股]', segment)
        if m3g:
            candidate = float(m3g.group(1))
            if 0.5 < candidate < 10000:
                return candidate

        # 3h: "交易均价" 后紧跟 "X 元/股" (无"为"/"即")
        m3h = re.search(r'交易均价[^。；\n]{0,100}?[^0-9]([0-9.]+)\s*元\s*/\s*股', segment)
        if m3h:
            return float(m3h.group(1))

    # ==== Fallback: 全文中找任何"前1个交易日"相关的行 ====
    fallback_pattern = re.compile(
        r'(?:前\s*(?:1|一)\s*个?\s*交\s*易\s*日)'
        r'[^。；\n]{0,500}'
        r'(?:交易均价|股票交易均价)',
        re.S
    )
    for m in fallback_pattern.finditer(text):
        line_start = max(0, m.start() - 30)
        line_end = min(len(text), m.end() + 100)
        line = text[line_start:line_end]
        # 如果在"交易均价"前有"前20/60/120"，跳过
        tjj_idx = line.find('交易均价')
        before_tjj = line[:tjj_idx] if tjj_idx > 0 else line
        if re.search(r'前\s*(?:20|60|120)\s*个\s*交\s*易\s*日', before_tjj):
            continue

        # 尝试提取价格
        for pat in [
            r'(?:为每股|即每股|为每份|即每份|为|即)\s*([0-9.]+)\s*元',
            r'([0-9.]+)\s*元\s*/\s*股',
            r'人民币\s*([0-9.]+)\s*元',
        ]:
            pm = re.search(pat, line)
            if pm:
                val = float(pm.group(1))
                if 0.01 < val < 10000:
                    return val

    return None


# ============================================================================
# discount_rate
# ============================================================================

def calculate_discount_rate(
    exercise_price: float | None,
    market_price: float | None,
) -> float | None:
    if exercise_price is None or market_price is None or market_price <= 0:
        return None
    discount_rate = round((1 - exercise_price / market_price) * 100, 2)
    # 异常值过滤
    if discount_rate < -100 or discount_rate > 100:
        return None
    return discount_rate


# ============================================================================
# waiting_period
# ============================================================================

def extract_waiting_period(text: str) -> float | None:
    patterns = [
        # "等待期分别为 X个月、Y个月、Z个月" → 取第一个
        r"等待期分别[为是]?\s*[^。；\n]{0,100}?([0-9]+)\s*个?月[、，和及]",
        # "等待期为 X 个月"
        r"等待期[为是]?\s*([0-9]+)\s*个月",
        r"等待期为\s*([0-9]+)\s*个月",
        r"等待期\s*([0-9]+)\s*个?月",
        # "授权日起满 X 个月...行权"
        r"授权日起满\s*([0-9]+)\s*个月.*?行权",
        r"首次.*?等待.*?([0-9]+)\s*个月",
        # "自授予登记完成之日起X个月"
        r"自[^。；\n]{0,60}?(?:授予|登记|授权)[^。；\n]{0,30}?(?:之日|日)?起[^。；\n]{0,60}?([0-9]+)\s*个?月",
        # "满 X 个月后...行权/解锁/解除限售/归属"
        r"满\s*([0-9]+)\s*个月后.*?(?:行权|解锁|解除限售|归属)",
    ]

    for p in patterns:
        m = re.search(p, text, re.S)
        if m:
            val = float(m.group(1))
            if 1 <= val <= 120:  # reasonable range
                return val
    return None


# ============================================================================
# validity_period
# ============================================================================

def extract_validity_period(text: str) -> float | None:
    patterns = [
        r"有效期.*?最长.*?([0-9]+)\s*个月",
        r"有效期最长.*?([0-9]+)\s*个月",
        r"有效期.*?不超过\s*([0-9]+)\s*个月",
        r"本激励计划有效期.*?([0-9]+)\s*个月",
        r"有效期[为是]?\s*([0-9]+)\s*个月",
        r"有效期(?:为)?\s*([0-9]+)\s*个?月",
        r"激励计划.*?有效期.*?([0-9]+)\s*个月",
        r"最长不超过\s*([0-9]+)\s*个月",
    ]

    for p in patterns:
        m = re.search(p, text, re.S)
        if m:
            return float(m.group(1))
    return None


# ============================================================================
# Rule-based extraction orchestrator
# ============================================================================

def extract_one_rule(section: dict, config: dict) -> dict | None:
    text = section["section_text"]

    exercise_price = extract_exercise_price(text)
    market_price = extract_market_price(text)

    if market_price is None:
        print("MISS market_price:", section["doc_id"])

    discount_rate = calculate_discount_rate(exercise_price, market_price)

    result = {
        "doc_id": section["doc_id"],
        "company_name": section.get("stock_name"),
        "stock_code": section.get("stock_code"),

        "grant_amount": extract_grant_amount(text),
        "grant_ratio": extract_grant_ratio(text),
        "participant_count": extract_participant_count(text),
        "exercise_price": exercise_price,
        "market_price": market_price,
        "discount_rate": discount_rate,
        "waiting_period": extract_waiting_period(text),
        "validity_period": extract_validity_period(text),

        "evidences": [
            {
                "text": text[:500],
                "page_no": section.get("page_no"),
            }
        ],
    }

    return result


# ============================================================================
# LLM helpers (备用)
# ============================================================================

def strip_json_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text, flags=re.I).strip()
        text = re.sub(r"```$", "", text).strip()
    return text


def call_llm(messages: list[dict], config: dict) -> str:
    load_dotenv()
    llm = config.get("llm", {})
    base_url = os.getenv(llm.get("base_url_env", "LLM_BASE_URL"), "").rstrip("/")
    api_key = os.getenv(llm.get("api_key_env", "LLM_API_KEY"), "")
    model = os.getenv(llm.get("model_env", "LLM_MODEL"), "")

    if not base_url:
        raise RuntimeError("Missing LLM_BASE_URL. For SiliconFlow use https://api.siliconflow.cn/v1")
    if not api_key or api_key == "your_key_here":
        raise RuntimeError("Missing real LLM_API_KEY.")
    if not model or model == "your_model_here":
        raise RuntimeError("Missing real LLM_MODEL.")

    print("BASE_URL =", base_url)
    print("MODEL =", model)

    response = requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": messages,
            "temperature": float(llm.get("temperature", 0)),
            "max_tokens": int(llm.get("max_tokens", 2048)),
        },
        timeout=int(llm.get("timeout_seconds", 60)),
    )
    print(response.status_code)
    print(response.text)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def extract_market_price_llm(text: str, config: dict) -> float | None:
    prompt = f"""
你是上市公司股权激励方案信息抽取助手。

任务:
抽取公告日前1个交易日股票交易均价(market_price)。

定义:
market_price =
股权激励草案公告前1个交易日公司股票交易均价。

规则:

1. 只输出JSON。
2. 找不到返回null。
3. 如果出现:

"公司股票交易均价为每股16.14元"

则:

{{
  "market_price": 16.14
}}

4. 如果出现:

"公司股票交易均价的75%，为每股7.47元"

则反推:

7.47 ÷ 0.75 = 9.96

输出:

{{
  "market_price": 9.96
}}

5. 如果出现:

"公司股票交易均价每股90.49元的50%，为每股45.25元"

则第一个价格(90.49)就是交易均价:

{{
  "market_price": 90.49
}}

6. 如果出现多个价格:

优先选择交易均价,
不要选择授予价格、
行权价格、
限制性股票授予价格。

7. 只输出合法JSON。

文本:

{text[:12000]}
"""

    content = call_llm(
        [
            {
                "role": "system",
                "content": "你只输出合法JSON。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        config
    )

    try:
        result = json.loads(strip_json_fence(content))
        value = result.get("market_price")
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


# ============================================================================
# Main pipeline
# ============================================================================

def extract_fields(config_path: str, method: str | None = None) -> list[dict]:
    config = read_yaml(config_path)
    sections_path = config["paths"].get("sections_jsonl", "data/parsed/sections.jsonl")
    output_path = config["paths"]["extract_results"]
    method = method or config.get("extract", {}).get("provider", "rule")
    results = []

    for section in read_jsonl(sections_path):
        if section["found"]:
            if method == "rule":
                record = extract_one_rule(section, config)
                if record is not None:
                    results.append(record)
            elif method == "llm":
                results.append(
                    extract_one_llm(section, config)
                )

    if not results:
        raise RuntimeError("No extraction results were produced.")
    write_jsonl(output_path, results)
    return results


def extract_one_llm(section: dict, config: dict) -> dict:
    """LLM-based extraction (备用方案)."""
    text = section["section_text"]

    prompt = f"""
你是上市公司股权激励方案信息抽取助手。
从以下公告文本中提取关键字段，返回严格JSON。

字段说明:
- grant_amount: 拟授予总数量(万份)，数字
- grant_ratio: 占公告日总股本比例(%)，数字
- participant_count: 首次授予总人数，整数
- exercise_price: 行权价格(元/份)，数字
- market_price: 公告前1个交易日股票交易均价(元)，数字
- waiting_period: 等待期(月)，数字
- validity_period: 激励计划最长有效期(月)，数字

找不到填null。

只输出合法JSON，格式如下:
{{
  "grant_amount": ...,
  "grant_ratio": ...,
  "participant_count": ...,
  "exercise_price": ...,
  "market_price": ...,
  "waiting_period": ...,
  "validity_period": ...
}}

文本:
{text[:12000]}
"""

    content = call_llm(
        [
            {"role": "system", "content": "你只输出合法JSON。"},
            {"role": "user", "content": prompt}
        ],
        config
    )

    try:
        data = json.loads(strip_json_fence(content))
    except Exception:
        data = {}

    exercise_price = data.get("exercise_price")
    market_price = data.get("market_price")
    discount_rate = calculate_discount_rate(exercise_price, market_price)

    return {
        "doc_id": section["doc_id"],
        "company_name": section.get("stock_name"),
        "stock_code": section.get("stock_code"),
        "grant_amount": data.get("grant_amount"),
        "grant_ratio": data.get("grant_ratio"),
        "participant_count": data.get("participant_count"),
        "exercise_price": exercise_price,
        "market_price": market_price,
        "discount_rate": discount_rate,
        "waiting_period": data.get("waiting_period"),
        "validity_period": data.get("validity_period"),
        "evidences": [{"text": text[:500], "page_no": section.get("page_no")}],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract equity incentive fields.")
    parser.add_argument("--config", default="configs/workflow.yaml")
    parser.add_argument("--method", choices=["rule", "llm"], default=None)
    args = parser.parse_args()
    results = extract_fields(args.config, args.method)
    print(f"Extracted {len(results)} records.")


if __name__ == "__main__":
    main()
