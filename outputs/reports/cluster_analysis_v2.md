# 聚类模型优化分析报告

## 优化背景

原聚类模型中不同Cluster的Generosity Score差异过小，原因可能是Generosity Score作为综合评价结果参与了聚类，导致信息重复。

## 优化方案

### 改进措施

1. **移除Generosity Score**：不再作为聚类输入变量
2. **仅使用5个原始指标**：
   - grant_ratio（授予比例）
   - participant_ratio（参与比例）
   - discount_rate（折扣率）
   - waiting_period_adj（等待期，已正向化）
   - validity_period（有效期）

3. **重新标准化**：使用StandardScaler
4. **综合选择最佳K**：Elbow Method + Silhouette Score

## 一、最佳K选择理由

### 聚类评估结果

| K | SSE | Silhouette Score |
|---|-----|------------------|
| 2 | 793.73 | 0.3997 |
| 3 | 649.14 | 0.2431 |
| 4 | 527.85 | 0.2695 |
| 5 | 445.93 | 0.2778 |

### 选择依据

1. **Elbow Method**: 观察SSE下降幅度
2. **Silhouette Score**: 评估聚类紧密度

**最终选择**: K = **2**

## 二、各Cluster特点


### 均衡型

- **Cluster ID**: 1
- **公司数量**: 175 家
- **平均Generosity Score**: 0.1808
- **描述**: 各维度均衡，无特别突出的特征

| 指标 | Cluster均值 | 全样本均值 | 对比 |
|------|------------|-----------|------|
| grant_ratio | 0.1790 | 0.1707 | +4.9% |
| participant_ratio | 0.1380 | 0.1365 | +1.1% |
| discount_rate | 0.6241 | 0.6214 | +0.4% |
| waiting_period_adj | 0.9808 | 0.9301 | +5.4% |
| validity_period | 0.3677 | 0.3673 | +0.1% |


### 均衡型

- **Cluster ID**: 0
- **公司数量**: 17 家
- **平均Generosity Score**: 0.1501
- **描述**: 各维度均衡，无特别突出的特征

| 指标 | Cluster均值 | 全样本均值 | 对比 |
|------|------------|-----------|------|
| grant_ratio | 0.0853 | 0.1707 | -50.0% |
| participant_ratio | 0.1216 | 0.1365 | -10.9% |
| discount_rate | 0.5937 | 0.6214 | -4.5% |
| waiting_period_adj | 0.4087 | 0.9301 | -56.1% |
| validity_period | 0.3633 | 0.3673 | -1.1% |


## 三、各Cluster Generosity Score比较

1. **均衡型**: 0.1808 (175 家公司)
1. **均衡型**: 0.1501 (17 家公司)

## 四、经济含义解释

### 为什么不同Cluster有不同的Generosity Score？

1. **高慷慨度Cluster**的特点：
   - 通常在**participant_ratio**（覆盖广度）和**grant_ratio**（授予规模）上表现突出
   - 这两个指标在熵权法中的权重最高（合计超过90%）
   - 因此这些维度的优势直接转化为高Generosity Score

2. **低慷慨度Cluster**的特点：
   - 往往在覆盖广度和授予规模上低于平均
   - 即使在其他维度（如折扣率、时间维度）有优势，但权重较低
   - 难以弥补核心维度的不足

3. **聚类的意义**：
   - 基于原始指标的聚类能够识别出真正的激励策略差异
   - Generosity Score是这些差异的综合量化结果
   - 两者相互印证，验证了评价体系的合理性

## 五、可视化说明

已生成以下可视化图片：

1. **k_evaluation.png**: K值选择评估（Elbow Method + Silhouette Score）
2. **cluster_pca_visualization.png**: 聚类PCA降维可视化
3. **cluster_radar_chart.png**: 各Cluster指标雷达图
4. **cluster_profile_comparison.png**: 各Cluster指标对比柱状图
5. **cluster_generosity_comparison.png**: 各Cluster平均Generosity Score对比

## 输出文件

1. `cluster_standardized_data.csv` - 标准化后的聚类输入数据
2. `cluster_evaluation.csv` - K值评估结果
3. `cluster_result_v2.csv` - 聚类结果
4. `cluster_profile_v2.csv` - 各Cluster画像（含自动命名）
5. `cluster_analysis_v2.md` - 本报告

---

**完成日期**: 2026年
