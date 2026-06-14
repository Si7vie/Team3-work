# 指标方向统一与标准化报告

## 研究目的

对股权激励慷慨度评价指标进行方向统一与标准化处理，为后续熵权法客观赋权和 Generosity Score 计算构建标准化评价矩阵。

## 指标方向判断依据

### 正向指标（数值越大越慷慨）

| 指标 | 经济含义 |
|------|---------|
| grant_ratio | 授予比例越高，给予员工的股权激励力度越大 |
| participant_ratio | 参与比例越高，更多员工能够分享股权激励 |
| discount_rate | 折扣率越高，员工获得的价格优惠越大 |
| validity_period | 有效期越长，长期激励价值越强 |

### 逆向指标（数值越大越不慷慨）

| 指标 | 经济含义 |
|------|---------|
| waiting_period | 等待期越长，员工实现收益所需等待时间越长 |

## 指标方向统一方法

### 逆向指标正向化

对 waiting_period 采用极差转换法：

waiting_period_adj = X_max - X

转换后：
- 原等待期最短的公司 → 正向化后值最大（最慷慨）
- 原等待期最长的公司 → 正向化后值最小（最不慷慨）

## Min-Max标准化方法

对方向统一后的所有指标进行 Min-Max 标准化：

Z_ij = (X_ij - X_min) / (X_max - X_min)

标准化后：
- 所有指标取值范围: [0, 1]
- 0 表示该指标在样本中最差
- 1 表示该指标在样本中最好

## 标准化结果检验

标准化后数据应满足：
1. 无负值
2. 无大于1的数值
3. 无缺失值
4. 各指标最小值 = 0
5. 各指标最大值 = 1

## 熵权法输入数据

最终生成的 `entropy_input_data.csv` 包含：
- grant_ratio（已标准化）
- participant_ratio（已标准化）
- discount_rate（已标准化）
- waiting_period_adj（已正向化并标准化）
- validity_period（已标准化）

所有指标均为方向统一后的数据，且取值范围为 [0, 1]，可直接用于熵权法赋权。

## 后续步骤

完成 Step 4 后，可以进入：
- Step 5: 熵权法赋权
- Step 6: Generosity Score 计算与排名

## 输出文件清单

1. `indicator_direction_report.csv` - 指标方向报告
2. `direction_adjusted_data.csv` - 方向统一后数据
3. `entropy_input_data.csv` - 熵权法输入数据
4. `normalized_statistics.csv` - 标准化后统计
5. `normalization_validation_report.csv` - 标准化验证报告
6. `normalization_report.md` - 本报告

可视化图片:
- `figures/normalization_comparison.png`
- `figures/after_normalization_histograms.png`
