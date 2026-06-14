# 候选方向 1：股权激励方案"可比化"分析
## 公告类型：
2021年1月-2025年12月半导体、电子、计算机、医药、高端制造行业股票期权激励计划
## 关键词：
股票期权激励计划
股权激励计划
## 金融问题：
基于巨潮资讯股票期权激励计划草案，通过文本智能抽取构建股权激励慷慨度评价体系，解决同行业股权激励方案无法量化对标、激励合理性难以批量判别的金融实务问题。
## 巨潮咨询数据来源：
### Data Source
本研究的数据来源于中国上市公司信息披露平台——巨潮资讯网（CNINFO）。
项目将通过巨潮资讯公开公告检索接口获取公告元数据（Metadata），并下载对应的股权激励计划PDF文件作为原始数据来源。
### Data Collection Pipeline
项目采用如下数据获取流程：
CNINFO公告检索
        ↓
metadata.csv
        ↓
PDF下载
        ↓
PDF文本抽取
        ↓
结构化数据集

## 示例公告：
| 公司 | 代码 | 标题 | 日期 | URL |
|------|------|----------|----------|----------|
| 士兰微 | 600460 | 杭州士兰微电子股份有限公司2021年股票期权激励计划（草案） | 2021-11-30 | https://www.cninfo.com.cn/new/disclosure/detail?stockCode=600460&announcementId=1211721855&orgId=gssh0600460&announcementTime=2021-11-30
| 华天科技 | 002185 | 2023年股票期权激励计划（草案） | 2023-11-29 | https://www.cninfo.com.cn/new/disclosure/detail?stockCode=002185&announcementId=1218467450&orgId=9900003862&announcementTime=2023-11-29
| 澜起科技 | 688008 | 2023年股票期权激励计划（草案） | 2023-06-09 | https://www.cninfo.com.cn/new/disclosure/detail?stockCode=688008&announcementId=1217022438&orgId=9900039002&announcementTime=2023-06-09
| 北方华创 | 002371 | 2025年股票期权激励计划（草案） | 2025-11-22 | https://www.cninfo.com.cn/new/disclosure/detail?stockCode=002371&announcementId=1224821225&orgId=9900006137&announcementTime=2025-11-22
| 兆易创新 | 603986 | 兆易创新科技集团股份有限公司2024年股票期权激励计划（草案） | 2024-4-20 | https://www.cninfo.com.cn/new/disclosure/detail?stockCode=603986&announcementId=1219696536&orgId=9900026561&announcementTime=2024-04-20
| 中微公司 | 688012 | 中微公司2025年限制性股票激励计划（草案） | 2025-4-18 | https://www.cninfo.com.cn/new/disclosure/detail?stockCode=688012&announcementId=1223127203&orgId=9900038991&announcementTime=2025-04-18

## 目标字段

### 一、激励规模
| 字段 | 类型 | 是否必填 | 金融含义 | 证据来源 |
|------|------|----------|----------|----------|
| 拟授予总数量（万份） | 数值 | 是 | 激励总量 | 公告正文"授予数量"章节 |
| 占公告日总股本比例（%） | 数值 | 是 | 激励稀释程度 | 公告正文"授予数量"章节 |

### 二、激励覆盖范围
| 字段 | 类型 | 是否必填 | 金融含义 | 证据来源 |
|------|------|----------|----------|----------|
| 首次授予总人数 | 数值 | 是 | 覆盖人数 | 公告正文"激励对象"章节 |

### 三、定价指标
| 字段 | 类型 | 是否必填 | 金融含义 | 证据来源 |
|------|------|----------|----------|----------|
| 行权价格（元/份） | 数值 | 是 | 激励成本基准 | 公告正文"行权价格"章节 |
| 定价折扣率（%） | 数值 | 是 | 激励优惠力度 | 公告正文"行权价格"章节 |


### 四、解锁速度
| 字段 | 类型 | 是否必填 | 金融含义 | 证据来源 |
|------|------|----------|----------|----------|
| 激励计划最长有效期（月） | 数值 | 是 | 激励持续时间 | 公告正文"有效期与等待期"章节 |
| 等待期（月） | 数值 | 否 | 首次可行权等待时间 | 公告正文"有效期与等待期"章节 |

## 构建股权激励慷慨度评价体系：
Generosity Score=0.25×Scale+0.25×Coverage+0.25×Pricing+0.25×Time

##  项目最终成果：
| Deliverable（交付成果）              | 文件                                   | 含义说明                                                        |
| ------------------------------ | ------------------------------------ | ----------------------------------------------------------- |
| Metadata Database              | data/metadata.csv                    | 公告元数据库，记录所有股权激励公告的基本信息、来源链接、PDF地址及下载状态，是后续数据处理的基础数据表。       |
| PDF Repository                 | data/pdfs/                           | 下载保存的股权激励计划PDF文件库，用于后续信息抽取与人工核验。                            |
| Structured Dataset             | outputs/equity_incentive_dataset.csv | 从PDF中抽取并整理后的结构化数据集，包含拟授予总量、授予比例、激励人数、行权价格、折扣率、等待期、有效期等核心字段。 |
| Generosity Ranking             | outputs/generosity_ranking.csv       | 根据构建的Generosity Score（股权激励慷慨度评分）生成的公司排名结果。                  |
| Industry Summary               | outputs/industry_summary.csv         | 各行业股权激励特征统计结果，包括平均授予比例、平均折扣率、平均激励人数、平均等待期等指标。               |
| Visualization Package          | outputs/figures/                     | 项目生成的可视化图表，包括慷慨度分布图、行业比较图、时间趋势图及Top20排行榜等。                  |
| Final Report                   | final_report.pdf                     | 项目最终研究报告，介绍研究背景、数据获取流程、字段抽取方法、评分体系设计及实证分析结果。                |
| Presentation Slides            | final_slides.pdf                     | 项目答辩展示PPT。                                                  |
| Reproducible GitHub Repository | GitHub Repo                          | 可复现项目仓库，包含代码、配置文件、样例数据、运行说明及项目文档。                           |

### Metadata Database Schema（元数据库设计）
| 字段名               | 含义说明                      |
| ----------------- | ------------------------- |
| doc_id            | 公告唯一标识符，用于关联后续所有数据        |
| stock_code        | 上市公司股票代码                  |
| company_name      | 公司名称                      |
| industry          | 行业分类（半导体、电子、计算机、医药、高端制造）  |
| announcement_date | 公告发布日期                    |
| title             | 公告标题                      |
| url               | 公告网页地址                    |
| pdf_url           | PDF下载地址                   |
| local_pdf_path    | 本地PDF存储路径                 |
| download_status   | PDF下载状态（success / failed） |
| error_message     | 下载失败时的错误信息                |

###  Structured Dataset Schema（结构化数据集设计）
| 字段名               | 含义说明            |
| ----------------- | --------------- |
| stock_code        | 上市公司股票代码        |
| company_name      | 公司名称            |
| grant_amount      | 拟授予股票期权总量       |
| grant_ratio       | 拟授予数量占总股本比例     |
| participant_count | 激励对象总人数         |
| exercise_price    | 股票期权行权价格        |
| discount_rate     | 行权价格相对于市场价格的折扣率 |
| waiting_period    | 首次可行权等待期（月）     |
| validity_period   | 激励计划有效期（月）      |
| generosity_score  | 股权激励慷慨度综合评分     |

## 难度评估：
1.0分
理由：目标字段均为标准化披露信息，量纲统一，可比性强，适合自动抽取与批量分析；研究问题明确，能够在课程项目周期内完成从数据获取、结构化抽取到量化评价的完整链路。

## 主要风险：
1、PDF格式差异导致字段抽取准确率下降；
2、行权价格披露格式存在差异；
3、部分公告缺少标准化表格结构；
4、样本行业分类需要额外清洗。


## 候选方向 2：重大合同/中标公告信息抽取
## 下一步计划
1. 完善候选方向的详细内容
2. 选择最终研究方向
3. 制定项目执行计划
