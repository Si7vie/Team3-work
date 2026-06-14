# 相关性分析报告

## 研究目的

检验上市公司股权激励慷慨度评价指标之间是否存在明显信息重叠、潜在多重共线性风险，以及是否能够从不同维度共同衡量股权激励慷慨度。

## 分析方法

### 1. Pearson 相关性分析
- 衡量变量之间的线性相关程度
- 假设变量服从正态分布
- 适合线性关系检验

### 2. Spearman 秩相关分析
- 衡量变量之间的单调相关程度
- 不要求正态分布
- 对异常值更稳健
- 适合偏态分布数据（如 participant_ratio、discount_rate）

## 数据概况

- **样本数**: 192
- **评价指标数**: 5
- **评价指标**: grant_ratio, participant_ratio, discount_rate, waiting_period, validity_period

## Pearson 相关性分析结果

### 相关性矩阵

详见 `correlation_matrix.csv`

### 相关性分类

- **高度相关（|r| > 0.7）**: 0 对
- **中等相关（0.3 < |r| < 0.7）**: 0 对
- **弱相关（|r| < 0.3）**: 10 对

## Spearman 相关性分析结果

详见 `spearman_correlation_matrix.csv`

## 多重共线性判断

参考标准:
| 相关系数 | 解释 |
|---------|------|
| |r| < 0.3 | Weak（弱相关） |
| 0.3 < |r| < 0.7 | Moderate（中等相关） |
| |r| > 0.7 | Strong（高度相关） |

### 诊断结果

**无高度相关变量（|r| > 0.7）**

✓ 潜在多重共线性风险较低
✓ 各指标能够提供相对独立的信息

## 关键指标对分析

### 1. grant_ratio 与 participant_ratio

- **经济含义**: 授予比例 vs 参与比例
- **分析目的**: 是否存在规模效应

如果二者正相关，说明覆盖面越广的方案通常授予比例越高（规模效应）。
如果二者负相关，说明覆盖面越广的方案通常授予比例越低（替代关系）。

### 2. grant_ratio 与 discount_rate

- **经济含义**: 授予比例 vs 折扣率
- **分析目的**: 是否同时反映激励强度

如果二者正相关，说明授予比例高的方案同时折扣率也高（双重慷慨）。
如果相关性较弱，说明二者从不同维度反映激励强度。

### 3. participant_ratio 与 discount_rate

- **经济含义**: 参与比例 vs 折扣率
- **分析目的**: 是否具有独立信息价值

participant_ratio 代表覆盖广度，discount_rate 代表定价深度。
如果相关性较弱，说明二者具有独立信息价值。

### 4. waiting_period 与 validity_period

- **经济含义**: 等待期 vs 有效期
- **分析目的**: 是否共同反映长期激励特征

如果二者正相关，说明等待期越长的方案有效期也越长（长期激励特征）。

### 5. discount_rate 与 waiting_period

- **经济含义**: 折扣率 vs 等待期
- **分析目的**: 是否存在替代关系

如果二者负相关，说明公司可能在价格激励和时间约束之间进行权衡。

## 评价体系合理性评估

### 1. 指标维度分析

| 指标 | 维度 | 经济含义 |
|------|------|---------|
| grant_ratio | 规模维度 | 股权激励的相对规模 |
| participant_ratio | 覆盖维度 | 股权激励的覆盖广度 |
| discount_rate | 定价维度 | 股权激励的定价优惠程度 |
| waiting_period | 时间约束 | 员工获得激励的时间成本 |
| validity_period | 时间跨度 | 激励计划的持续时长 |

### 2. 重复测量问题

无高度相关变量，不存在严重重复测量问题。

### 3. 指标保留建议

**✓ 建议全部保留进入熵权法评价体系**

理由:
1. 各指标提供相对独立的信息
2. 不存在严重的多重共线性问题
3. 能够从不同维度衡量股权激励慷慨度

## 输出文件

1. `descriptive_statistics_final.csv` - 最终描述统计
2. `correlation_matrix.csv` - Pearson 相关性矩阵
3. `spearman_correlation_matrix.csv` - Spearman 相关性矩阵
4. `pearson_heatmap.png` - Pearson 相关性热力图
5. `spearman_heatmap.png` - Spearman 相关性热力图

## 下一步

完成相关性分析后，可以进入:
- Step 4: 指标方向统一与标准化
- Step 5: 熵权法赋权
- Step 6: Generosity Score 计算与排名
