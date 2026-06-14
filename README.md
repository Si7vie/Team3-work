# 上市公司股权激励慷慨度评价项目

## 项目简介

本项目基于中国A股上市公司股权激励方案数据，构建股权激励慷慨度（Generosity Score）评价体系。

项目采用熵权法（Entropy Weight Method）对多个激励设计维度进行客观赋权，并计算上市公司的股权激励慷慨度得分及排名。

在此基础上，进一步开展：

- 数据质量检查
- 数据清洗
- 相关性分析
- 熵权法赋权
- 慷慨度评分与排名
- 稳健性检验
- 聚类分析与验证

最终形成可复现的数据挖掘与机器学习项目流程。

***

## 研究问题

如何从多个维度客观评价上市公司股权激励方案的慷慨程度？

***

## 评价指标体系

最终保留5个核心评价指标：

| 指标                 | 含义     | 属性 |
| :----------------- | :----- | :- |
| grant\_ratio       | 授予比例   | 正向 |
| participant\_ratio | 激励覆盖比例 | 正向 |
| discount\_rate     | 定价折扣率  | 正向 |
| waiting\_period    | 等待期    | 负向 |
| validity\_period   | 有效期    | 正向 |

***

## 项目目录结构

```text
equity_incentive_generosity_project/

├── configs/
│   ├── workflow.yaml
│   └── indicator_rules.yaml
│
├── data/
│   ├── raw/
│   ├── cleaned/
│   └── processed/
│
├── outputs/
│   ├── data_quality/
│   ├── data_cleaning/
│   ├── correlation/
│   ├── entropy/
│   ├── ranking/
│   ├── robustness/
│   └── cluster/
│
├── figures/
│
├── reports/
│
├── src/
│
├── presentation/
│
├── README.md
└── requirements.txt
```

