# 熵权法赋权报告

## 研究目的

基于信息熵原理，客观计算股权激励慷慨度评价体系中各指标的权重，为后续 Generosity Score 综合评价提供科学依据。

## 熵权法原理

### 基本思想

信息熵是衡量系统不确定性的指标：
- 信息熵越小 → 指标值差异越大 → 信息量越多 → 权重越高
- 信息熵越大 → 指标值越一致 → 信息量越少 → 权重越低

### 核心公式

1. 构建标准化评价矩阵 Z
   - 已完成 Min-Max 标准化，范围 [0, 1]

2. 计算指标占比矩阵 P
   - P_ij = Z_ij / Σ(Z_ij)
   - Σ(P_ij) = 1 (按列求和)

3. 计算信息熵 e
   - k = 1 / ln(n)
   - e_j = -k * Σ(P_ij * ln(P_ij))
   - 若 P_ij = 0，则 P_ij * ln(P_ij) = 0

4. 计算差异系数 d
   - d_j = 1 - e_j

5. 计算熵权 w
   - w_j = d_j / Σ(d_j)
   - Σ(w_j) = 1

## 数据概况

- 样本数 (n): 192
- 指标数 (m): 5
- 指标: grant_ratio, participant_ratio, discount_rate, waiting_period_adj, validity_period

## 信息熵结果

详见 `entropy_values.csv`

信息熵解释:
- e_j ≈ 1: 指标值趋于一致，信息量少
- e_j ≈ 0: 指标值差异大，信息量多

## 差异系数结果

详见 `diversity_coefficient.csv`

差异系数 d_j = 1 - e_j:
- d_j 越大 → 指标区分度越强 → 权重越高

## 最终权重结果

详见 `entropy_weights.csv`

### 权重排序

- **participant_ratio**: 0.5275 (52.75%)
- **grant_ratio**: 0.4070 (40.70%)
- **validity_period**: 0.0352 (3.52%)
- **waiting_period_adj**: 0.0155 (1.55%)
- **discount_rate**: 0.0148 (1.48%)

### 关键发现

1. **权重最高指标**: participant_ratio
   - 权重: 0.5275 (52.75%)
   - 说明: 样本差异性最大，对 Generosity Score 贡献最大

2. **权重最低指标**: discount_rate
   - 权重: 0.0148 (1.48%)
   - 说明: 样本差异性较小，信息量相对较低

## 权重经济解释

### grant_ratio

反映股权激励的相对规模。
如果权重较高，说明不同公司的授予比例差异较大。

### participant_ratio

反映股权激励的覆盖广度。
如果权重较高，说明不同公司的激励覆盖策略差异较大。

### discount_rate

反映股权激励的定价优惠程度。
如果权重较高，说明不同公司的定价策略差异较大。

### waiting_period_adj

反映股权激励的时间约束（已正向化）。
如果权重较高，说明不同公司的锁定期设计差异较大。

### validity_period

反映股权激励的时间跨度。
如果权重较高，说明不同公司的计划期限差异较大。

## 权重合理性评估

### 1. 权重结构是否合理？

✓ 熵权法是客观赋权方法，完全基于数据特征
✓ 权重反映了各指标在样本中的区分能力
✓ 避免了主观赋权的偏差

### 2. 是否符合经济直觉？

需要结合股权激励理论分析。
权重高的指标说明该维度在样本公司中差异较大，
是区分公司激励慷慨度的关键维度。

### 3. 是否体现客观赋权思想？

✓ 完全基于数据的信息熵计算
✓ 无主观判断介入
✓ 权重随样本分布自动调整

### 4. 是否建议直接用于 Generosity Score 构建？

✓ 建议直接使用
✓ 权重经过严格数学推导
✓ 各指标区分度已充分体现

## 输出文件

1. `entropy_input_validation.csv` - 输入数据验证
2. `proportion_matrix.csv` - 指标占比矩阵
3. `entropy_values.csv` - 信息熵结果
4. `diversity_coefficient.csv` - 差异系数结果
5. `entropy_weights.csv` - 最终熵权结果
6. `entropy_weight_report.md` - 本报告

## 下一步

完成 Step 5 后，可以进入：
- Step 6: Generosity Score 计算与排名
