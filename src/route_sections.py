from __future__ import annotations

import argparse
import csv
from pathlib import Path

from common import read_jsonl, read_yaml, write_jsonl


def find_section(text: str, rule: dict) -> tuple[bool, str, str]:
    include_keywords = rule["include_keywords"]
    min_chars = int(rule["min_chars"])
    start = -1

    for keyword in include_keywords:

        pos = text.find(keyword)

        while pos >= 0:

            # 取关键词前300个字符看看
            context = text[max(0, pos - 300):pos]

            # 如果附近出现目录，就继续往后找
            if "目录" in context:
                pos = text.find(keyword, pos + len(keyword))
                continue

            start = pos
            break

        if start >= 0:
            break
    if start < 0:
        return False, "", "not_found"
    section = text[start:]
    end_positions = [section.find(marker) for marker in rule.get("end_markers", []) if section.find(marker) > min_chars]
    if end_positions:
        section = section[: min(end_positions)]
    section = section.strip()
    if len(section) < min_chars:
        return False, section, "too_short"
    return True, section, "ok"


def route_sections(config_path: str) -> list[dict]:
    config = read_yaml(config_path)
    parsed_path = Path(config["paths"]["parsed_dir"]) / "parsed_docs.jsonl"
    rules = read_yaml(config["paths"]["section_rules"])
    rule = rules["target_sections"]["equity_incentive"]
    sections = []
    report_rows = []

    docs = read_jsonl(parsed_path)

    print("docs数量=", len(docs))

    # 查看前5个文档页数
    for doc in docs[:5]:
        print(
            doc["doc_id"],
            len(doc["pages"])
        )

    if not docs:
        raise RuntimeError(...)

    for doc in docs:

        full_text = "\n".join(
            page["text"]
            for page in doc["pages"]
        )

        sections.append(
            {
                "doc_id": doc["doc_id"],
                "stock_code": doc.get("stock_code"),
                "stock_name": doc.get("stock_name"),
                "title": doc["title"],

                "target_section": "equity_incentive",

                "found": True,

                "page_no": 1,

                "section_text": full_text,

                "quality_issue": "ok",
            }
        )

        report_rows.append(
            {
                "doc_id": doc["doc_id"],
                "title": doc["title"],
                "target_section": "equity_incentive",
                "found": "true",
                "section_title": "FULL_DOCUMENT",
                "page_start": 1,
                "page_end": len(doc["pages"]),
                "quality_issue": "ok",
                "notes": full_text[:40].replace("\n", " "),
            }
        )

        sections_path = Path(config["paths"].get("sections_jsonl", "data/parsed/sections.jsonl"))
        for s in sections[:3]:
            print(s["doc_id"])
        write_jsonl(sections_path, sections)

        report_path = Path(config["paths"]["section_report"])
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open("w", encoding="utf-8", newline="") as f:
            fieldnames = [
                "doc_id",
                "title",
                "target_section",
                "found",
                "section_title",
                "page_start",
                "page_end",
                "quality_issue",
                "notes",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(report_rows)
    return sections


def main() -> None:
    parser = argparse.ArgumentParser(description="equity incentive sections.")
    parser.add_argument("--config", default="configs/workflow.yaml")
    args = parser.parse_args()
    sections = route_sections(args.config)
    print(f"Routed {len(sections)} sections.")


if __name__ == "__main__":
    main()
