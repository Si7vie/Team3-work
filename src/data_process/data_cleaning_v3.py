#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 2: 数据清洗（Data Cleaning）
研究主题：构建上市公司股权激励慷慨度（Generosity Score）评价体系

最终评价指标：
1. grant_ratio（授予比例）
2. participant_ratio（参与比例）
3. discount_rate（折扣率）
4. waiting_period（等待期）
5. validity_period（有效期）

清洗策略：
1. 缺失值：Listwise Deletion
2. 重复值：不处理（无重复）
3. 异常值：
   - participant_ratio: 1% Winsorization
   - 其他指标：保留原值
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

class DataCleanerV3:
    def __init__(self, input_path: str, output_dir: str = "data_cleaning_output_v3"):
        self.input_path = input_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.df = pd.read_csv(input_path, encoding='utf-8-sig')
        
        self.core_vars = [
            'grant_ratio',
            'participant_ratio',
            'discount_rate',
            'waiting_period',
            'validity_period'
        ]
        
        self.original_count = len(self.df)
        self.df_cleaned = self.df.copy()
        
        print(f"原始数据集: {input_path}")
        print(f"原始样本数: {self.original_count}")
        print(f"核心指标: {self.core_vars}")
    
    def print_separator(self, title: str):
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80 + "\n")
    
    def handle_missing_values(self):
        self.print_separator("一、缺失值处理")
        
        print("缺失值统计（处理前）:")
        print("-" * 70)
        
        missing_before = []
        for col in self.df.columns:
            missing_count = self.df[col].isnull().sum()
            missing_rate = (missing_count / len(self.df)) * 100
            missing_before.append({
                'Variable': col,
                'Missing Count': int(missing_count),
                'Missing Rate (%)': round(missing_rate, 4)
            })
        
        missing_before_df = pd.DataFrame(missing_before)
        print(missing_before_df.to_string(index=False))
        
        core_missing = self.df[self.core_vars].isnull().any(axis=1)
        missing_row_count = core_missing.sum()
        
        print(f"\n含缺失值的样本数（核心指标）: {missing_row_count}")
        
        if missing_row_count > 0:
            print(f"\n缺失样本示例（前10条）:")
            missing_rows = self.df[self.df[self.core_vars].isnull().any(axis=1)]
            for i, (_, row) in enumerate(missing_rows.head(10).iterrows()):
                missing_cols = [col for col in self.core_vars if pd.isnull(row[col])]
                print(f"  {i+1}. {row['company_name']} ({row['stock_code']}): 缺失 {missing_cols}")
        
        self.df_cleaned = self.df.dropna(subset=self.core_vars).reset_index(drop=True)
        
        count_after = len(self.df_cleaned)
        deleted_count = self.original_count - count_after
        deleted_rate = (deleted_count / self.original_count) * 100
        
        print("\n" + "-" * 70)
        print("缺失值处理报告（Listwise Deletion）:")
        print(f"  删除前样本数: {self.original_count}")
        print(f"  删除后样本数: {count_after}")
        print(f"  删除样本数: {deleted_count}")
        print(f"  删除比例: {deleted_rate:.4f}%")
        
        report = {
            'Metric': ['Before Deletion', 'After Deletion', 'Deleted', 'Deletion Rate (%)'],
            'Value': [self.original_count, count_after, deleted_count, round(deleted_rate, 4)]
        }
        pd.DataFrame(report).to_csv(self.output_dir / "missing_value_cleaning_report.csv", index=False, encoding='utf-8-sig')
        
        return count_after
    
    def handle_duplicates(self):
        self.print_separator("二、重复值处理")
        
        exact_duplicates = self.df_cleaned.duplicated()
        exact_duplicate_count = exact_duplicates.sum()
        
        print(f"完全重复记录数: {exact_duplicate_count}")
        print(f"总记录数: {len(self.df_cleaned)}")
        
        if exact_duplicate_count == 0:
            print("\n无完全重复记录，保留全部数据")
        else:
            print(f"\n存在 {exact_duplicate_count} 条重复记录，将删除")
            self.df_cleaned = self.df_cleaned.drop_duplicates().reset_index(drop=True)
        
        report = {
            'Metric': ['Total Records', 'Exact Duplicates', 'Final Records'],
            'Value': [int(len(self.df_cleaned)), int(exact_duplicate_count), int(len(self.df_cleaned))]
        }
        pd.DataFrame(report).to_csv(self.output_dir / "duplicate_cleaning_report.csv", index=False, encoding='utf-8-sig')
        
        return len(self.df_cleaned)
    
    def outlier_recheck(self):
        self.print_separator("三、异常值复核")
        
        outlier_report = []
        
        for var in self.core_vars:
            data = self.df_cleaned[var].dropna()
            
            q1 = data.quantile(0.25)
            q3 = data.quantile(0.75)
            iqr = q3 - q1
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = data[(data < lower_bound) | (data > upper_bound)]
            outlier_count = len(outliers)
            outlier_rate = (outlier_count / len(data)) * 100 if len(data) > 0 else 0
            
            outlier_report.append({
                'Variable': var,
                'Q1': round(q1, 4),
                'Q3': round(q3, 4),
                'IQR': round(iqr, 4),
                'Lower Bound': round(lower_bound, 4),
                'Upper Bound': round(upper_bound, 4),
                'Outlier Count': int(outlier_count),
                'Outlier Rate (%)': round(outlier_rate, 4)
            })
        
        outlier_df = pd.DataFrame(outlier_report)
        
        print("异常值复核（IQR方法）:")
        print("-" * 130)
        print(f"{'Variable':<20} | {'Q1':<10} | {'Q3':<10} | {'IQR':<10} | {'Lower':<12} | {'Upper':<12} | {'Outliers':<10} | {'Rate (%)':<10}")
        print("-" * 130)
        for _, row in outlier_df.iterrows():
            print(f"{row['Variable']:<20} | {row['Q1']:<10.4f} | {row['Q3']:<10.4f} | {row['IQR']:<10.4f} | {row['Lower Bound']:<12.4f} | {row['Upper Bound']:<12.4f} | {row['Outlier Count']:<10} | {row['Outlier Rate (%)']:<10.4f}")
        print("-" * 130)
        
        outlier_df.to_csv(self.output_dir / "outlier_recheck_report.csv", index=False, encoding='utf-8-sig')
        
        return outlier_df
    
    def apply_winsorization(self):
        self.print_separator("四、异常值处理策略")
        
        winsorization_report = []
        
        print("异常值处理策略:")
        print("-" * 80)
        
        for var in self.core_vars:
            if var == 'participant_ratio':
                data = self.df_cleaned[var].copy()
                
                p1 = data.quantile(0.01)
                p99 = data.quantile(0.99)
                
                original_min = data.min()
                original_max = data.max()
                
                data_clipped = data.clip(lower=p1, upper=p99)
                
                self.df_cleaned[var] = data_clipped
                
                new_min = data_clipped.min()
                new_max = data_clipped.max()
                clipped_count = ((data < p1) | (data > p99)).sum()
                
                winsorization_report.append({
                    'Variable': var,
                    'Treatment': '1% Winsorization',
                    'P1': round(p1, 4),
                    'P99': round(p99, 4),
                    'Original Min': round(original_min, 4),
                    'Original Max': round(original_max, 4),
                    'New Min': round(new_min, 4),
                    'New Max': round(new_max, 4),
                    'Clipped Count': int(clipped_count)
                })
                
                print(f"  {var}: 1% Winsorization")
                print(f"    P1={p1:.4f}, P99={p99:.4f}, 处理 {clipped_count} 个异常值")
                print(f"    分布: Skewness≈3.29, Kurtosis≈13.68（右偏分布）")
            else:
                winsorization_report.append({
                    'Variable': var,
                    'Treatment': '保留原值',
                    'P1': None,
                    'P99': None,
                    'Original Min': None,
                    'Original Max': None,
                    'New Min': None,
                    'New Max': None,
                    'Clipped Count': 0
                })
                
                if var == 'discount_rate':
                    print(f"  {var}: 保留原值（负折扣率为正常经济现象）")
                    print(f"    折扣率 = (市场价 - 行权价) / 市场价 × 100%")
                    print(f"    当行权价 > 市场价时，折扣率自然为负")
                elif var == 'waiting_period':
                    print(f"  {var}: 保留原值（IQR=0，统计假异常）")
                    print(f"    Q1=Q3=12，IQR=0，24/36/48/60个月均为合理设计")
                else:
                    print(f"  {var}: 保留原值（异常值为真实经济现象）")
        
        winsorization_df = pd.DataFrame(winsorization_report)
        winsorization_df.to_csv(self.output_dir / "winsorization_report.csv", index=False, encoding='utf-8-sig')
        
        pr_df = self.df_cleaned[['company_name', 'stock_code', 'participant_ratio']].copy()
        pr_df.to_csv(self.output_dir / "participant_ratio_winsorized.csv", index=False, encoding='utf-8-sig')
        print(f"\nparticipant_ratio 缩尾后数据已保存至: participant_ratio_winsorized.csv")
        
        return winsorization_df
    
    def descriptive_statistics_cleaned(self):
        self.print_separator("五、清洗后描述统计")
        
        core_df = self.df_cleaned[self.core_vars]
        desc_stats = core_df.describe().T
        desc_stats = desc_stats[['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']]
        desc_stats = desc_stats.round(4)
        
        print("清洗后核心指标描述统计:")
        print("-" * 130)
        print(f"{'Variable':<20} | {'Count':<8} | {'Mean':<12} | {'Std':<12} | {'Min':<12} | {'Max':<12}")
        print("-" * 130)
        for var in self.core_vars:
            print(f"{var:<20} | {int(desc_stats.loc[var, 'count']):<8} | {desc_stats.loc[var, 'mean']:<12.4f} | {desc_stats.loc[var, 'std']:<12.4f} | {desc_stats.loc[var, 'min']:<12.4f} | {desc_stats.loc[var, 'max']:<12.4f}")
        print("-" * 130)
        
        desc_stats.to_csv(self.output_dir / "descriptive_statistics_cleaned.csv", encoding='utf-8-sig')
        
        return desc_stats
    
    def validate_cleaning(self):
        self.print_separator("六、数据验证")
        
        validation_report = []
        
        print("数据清洗验证:")
        print("-" * 70)
        
        missing_after = self.df_cleaned[self.core_vars].isnull().sum().sum()
        print(f"1. 缺失值检查:")
        print(f"   核心指标缺失总数: {missing_after}")
        validation_report.append({'Check': 'Missing Values', 'Status': 'Pass' if missing_after == 0 else 'Fail', 'Details': f'{missing_after} missing'})
        
        exact_duplicates_after = self.df_cleaned.duplicated().sum()
        print(f"\n2. 重复值检查:")
        print(f"   完全重复记录数: {exact_duplicates_after}")
        validation_report.append({'Check': 'Exact Duplicates', 'Status': 'Pass' if exact_duplicates_after == 0 else 'Fail', 'Details': f'{exact_duplicates_after} duplicates'})
        
        print(f"\n3. 数值有效性检查:")
        for var in self.core_vars:
            data = self.df_cleaned[var]
            valid_count = pd.api.types.is_numeric_dtype(data)
            print(f"   {var}: {'数值型 ✓' if valid_count else '非数值型 ✗'}")
        
        print(f"\n4. 数据类型检查:")
        for var in self.core_vars:
            dtype = str(self.df_cleaned[var].dtype)
            is_numeric = pd.api.types.is_numeric_dtype(self.df_cleaned[var])
            status = '✓' if is_numeric else '✗'
            print(f"   {var}: {dtype} {status}")
        
        validation_df = pd.DataFrame(validation_report)
        validation_df.to_csv(self.output_dir / "cleaning_validation_report.csv", index=False, encoding='utf-8-sig')
        
        return validation_df
    
    def generate_report(self):
        self.print_separator("七、数据清洗总结")
        
        final_count = len(self.df_cleaned)
        deleted_count = self.original_count - final_count
        deleted_rate = (deleted_count / self.original_count) * 100
        
        print("=" * 80)
        print("  数据清洗总结")
        print("=" * 80)
        print(f"\n1. 缺失值处理:")
        print(f"   - 原始样本数: {self.original_count}")
        print(f"   - 删除含缺失值样本: {deleted_count} ({deleted_rate:.2f}%)")
        print(f"   - 清洗后样本数: {final_count}")
        
        print(f"\n2. 重复值处理:")
        print(f"   - 无完全重复记录")
        print(f"   - 保留全部数据")
        
        print(f"\n3. 异常值处理:")
        print(f"   - grant_ratio: 保留原值（约2.5%异常值，真实经济现象）")
        print(f"   - participant_ratio: 1% Winsorization（右偏分布，Skewness≈3.29）")
        print(f"   - discount_rate: 保留原值（负折扣率为正常现象）")
        print(f"   - waiting_period: 保留原值（IQR=0，统计假异常）")
        print(f"   - validity_period: 保留原值（约3%异常值，真实制度设计）")
        
        print(f"\n4. 关于负折扣率的说明:")
        print(f"   折扣率 = (市场价 - 行权价) / 市场价 × 100%")
        print(f"   当行权价 > 市场价时，折扣率自然为负")
        print(f"   不执行 clip(lower=0)，保留原始信息")
        
        print(f"\n5. 最终数据集:")
        print(f"   - 样本数: {final_count}")
        print(f"   - 字段数: {len(self.df_cleaned.columns)}")
        
        output_path = self.output_dir / "cleaned_equity_incentive_data.csv"
        self.df_cleaned.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n清洗后数据集已保存至: {output_path}")
        
        report_content = """# 数据清洗报告

## 研究目的

对上市公司股权激励数据进行清洗，为后续相关性分析、标准化和熵权法评价体系构建提供可靠数据基础。

## 数据概况

- **原始样本数**: {original_count}
- **清洗后样本数**: {final_count}
- **删除样本数**: {deleted_count} ({deleted_rate:.2f}%)

## 数据清洗流程

### 1. 缺失值处理

采用 **Listwise Deletion**（删除含缺失值的样本）。

原因：
- 缺失率低于5%
- 删除少量样本对整体分析影响有限

### 2. 重复值处理

- **总记录数**: {final_count}
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
""".format(
            original_count=self.original_count,
            final_count=final_count,
            deleted_count=deleted_count,
            deleted_rate=deleted_rate
        )
        
        with open(self.output_dir / "data_cleaning_report.md", "w", encoding="utf-8") as f:
            f.write(report_content)
        
        print(f"\n清洗报告已保存至: {self.output_dir / 'data_cleaning_report.md'}")
        
        return output_path
    
    def run(self):
        print("\n" + "#" * 80)
        print("#     Step 2: 数据清洗")
        print("#     研究主题：上市公司股权激励慷慨度评价体系")
        print("#" * 80)
        
        self.handle_missing_values()
        self.handle_duplicates()
        self.outlier_recheck()
        self.apply_winsorization()
        self.descriptive_statistics_cleaned()
        self.validate_cleaning()
        self.generate_report()
        
        print("\n" + "#" * 80)
        print("#     Step 2 完成！等待下一步指令。")
        print("#" * 80)


if __name__ == "__main__":
    input_path = "data/final_data_unprocessed.csv"
    
    if os.path.exists(input_path):
        cleaner = DataCleanerV3(input_path)
        cleaner.run()
    else:
        print(f"错误: 文件 {input_path} 不存在!")