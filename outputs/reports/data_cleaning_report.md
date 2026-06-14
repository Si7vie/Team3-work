# 数据清洗报告

## 研究目的

对上市公司股权激励数据进行清洗，为后续相关性分析、标准化和熵权法评价体系构建提供可靠数据基础。

## 数据概况

- **原始样本数**: 200
- **清洗后样本数**: 192
- **删除样本数**: 8 (4.00%)

## 数据清洗流程

### 1. 缺失值处理

采用 **Listwise Deletion**（删除含缺失值的样本）。

原因：
- 缺失率低于5%
- 删除少量样本对整体分析影响有限

### 2. 重复值处理

- **总记录数**: 192
- **完全重复记录数**: 0
- **处理方式**: 不删除任何记录

### 3. 异常值复核

| 指标 | Q1 | Q3 | IQR | 异常值数 | 异常值占比 |
|------|----|----|-----|---------|-----------|
| grant_ratio | - | - | - | - | ~2.5% |
| participant_ratio | - | - | - | - | ~11.9% |
| discount_rate | - | - | - | - | ~0.5% |
| waiting_period | 12 | 12 | 0 | - | ~24.7% |
| validity_period | - | - | - | - | ~3% |

### 4. 异常值处理策略

#### grant_ratio

- **异常值占比**: 约2.5%
- **处理方式**: 保留原值
- **原因**: 异常值反映部分公司采用高比例股权激励方案，属于真实经济现象

#### participant_ratio

- **异常值占比**: 约11.9%
- **分布特征**: Skewness ≈ 3.29, Kurtosis ≈ 13.68（明显右偏）
- **处理方式**: **1% Winsorization**
- **处理逻辑**:
  - 小于 P1 替换为 P1
  - 大于 P99 替换为 P99

#### discount_rate

- **异常值占比**: 约0.5%
- **处理方式**: 保留原值
- **特别说明**:
  - 负折扣率属于真实经济现象
  - 折扣率定义：
  - DiscountRate = (MarketPrice - ExercisePrice) / MarketPrice × 100%
  - 当 ExercisePrice > MarketPrice 时，折扣率自然为负
  - **不执行** `clip(lower=0)`
  - **不**将负值修改为0

#### waiting_period

- **异常值占比**: 约24.7%
- **处理方式**: 保留原值
- **原因**:
  - Q1 = Q3 = 12, IQR = 0
  - 属于统计方法导致的假异常
  - 24个月、36个月、48个月、60个月均属于合理激励设计

#### validity_period

- **异常值占比**: 约3%
- **处理方式**: 保留原值
- **原因**: 有效期较长属于真实制度设计

## 清洗后数据质量

- **无缺失值**：所有核心指标完整
- **无重复记录**：数据唯一性已验证
- **数值有效**：所有指标为数值型
- **异常值处理**：participant_ratio 已 Winsorization

## 输出文件

- `cleaned_equity_incentive_data.csv`：清洗后数据集
- `descriptive_statistics_cleaned.csv`：清洗后描述统计
- `missing_value_cleaning_report.csv`：缺失值处理报告
- `duplicate_cleaning_report.csv`：重复值处理报告
- `outlier_recheck_report.csv`：异常值复核报告
- `winsorization_report.csv`：Winsorization报告
- `participant_ratio_winsorized.csv`：participant_ratio缩尾数据
- `cleaning_validation_report.csv`：清洗验证报告

## 下一步建议

完成 Step 2 数据清洗后，可以进入：
- Step 3：相关性分析
- Step 4：指标方向统一与标准化
- Step 5：熵权法赋权
- Step 6：Generosity Score 计算与排名
