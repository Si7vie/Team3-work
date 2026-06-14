import json
from pathlib import Path

import pandas as pd

# 读取 metadata

df = pd.read_csv("data/metadata/metadata.csv")

records = []

for _, row in df.iterrows():
    doc_id = str(row["doc_id"])

    md_path = Path(f"markdown/md/{doc_id}.md")

    if not md_path.exists():
        print(f"跳过: {doc_id}")
        continue

    markdown = md_path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    record = {
        "doc_id": doc_id,
        "stock_code": str(row["stock_code"]),
        "stock_name": row["company_name"],
        "title": row["announcement_title"],
        "markdown_path": str(md_path),
        "parser": "mineru",
        "pages": [
            {
                "page_no": 1,
                "text": markdown
            }
        ]
    }

    records.append(record)


# 创建输出目录

output_dir = Path("data/parsed")
output_dir.mkdir(parents=True, exist_ok=True)

# 输出 jsonl

output_file = output_dir / "parsed_docs.jsonl"

with open(output_file, "w", encoding="utf-8") as f:
    for record in records:
        f.write(
            json.dumps(
                record,
                ensure_ascii=False
            )
            + "\n"
        )

print("=" * 50)
print(f"生成完成: {output_file}")
print(f"文档数量: {len(records)}")
print("=" * 50)
