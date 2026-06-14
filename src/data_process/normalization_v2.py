#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 4: 指标方向统一与标准化（Indicator Direction Adjustment & Normalization）
研究主题：构建上市公司股权激励慷慨度（Generosity Score）评价体系

最终评价指标：
1. grant_ratio（授予比例）- 正向
2. participant_ratio（参与比例）- 正向
3. discount_rate（折扣率）- 正向
4. waiting_period（等待期）- 逆向
5. validity_period（有效期）- 正向

处理流程：
1. 逆向指标正向化：waiting_period_adj = X_max - X
2. Min-Max 标准化：将所有指标映射到 [0,1]
3. 生成熵权法输入数据
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

class NormalizationProcessor:
    def __init__(self, input_path: str, output_dir: str = "normalization_output_v2"):
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
        
        self.positive_vars = ['grant_ratio', 'participant_ratio', 'discount_rate', 'validity_period']
        self.negative_vars = ['waiting_period']
        
        print(f"输入文件: {input_path}")
        print(f"输出目录: {output_dir}")
        print(f"样本数: {len(self.df)}")
        print(f"正向指标: {self.positive_vars}")
        print(f"逆向指标: {self.negative_vars}")
    
    def print_separator(self, title: str):
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80 + "\n")
    
    def indicator_direction_report(self):
        self.print_separator("一、指标方向识别")
        
        direction_data = [
            {
                'Indicator': 'grant_ratio',
                'Direction': 'Positive',
                'Economic Meaning': '授予比例越高，说明给予员工的股权激励力度越大'
            },
            {
                'Indicator': 'participant_ratio',
                'Direction': 'Positive',
                'Economic Meaning': '参与比例越高，说明更多员工能够分享股权激励'
            },
            {
                'Indicator': 'discount_rate',
                'Direction': 'Positive',
                'Economic Meaning': '折扣率越高，说明员工获得的价格优惠越大'
            },
            {
                'Indicator': 'validity_period',
                'Direction': 'Positive',
                'Economic Meaning': '有效期越长，说明长期激励价值越强'
            },
            {
                'Indicator': 'waiting_period',
                'Direction': 'Negative',
                'Economic Meaning': '等待期越长，员工实现收益所需等待时间越长'
            }
        ]
        
        direction_df = pd.DataFrame(direction_data)
        
        print("指标方向判断:")
        print("-" * 120)
        print(f"{'Indicator':<20} | {'Direction':<15} | {'Economic Meaning':<50}")
        print("-" * 120)
        for _, row in direction_df.iterrows():
            print(f"{row['Indicator']:<20} | {row['Direction']:<15} | {row['Economic Meaning']:<50}")
        print("-" * 120)
        
        direction_df.to_csv(self.output_dir / "indicator_direction_report.csv", index=False, encoding='utf-8-sig')
        print(f"\n指标方向报告已保存至: {self.output_dir / 'indicator_direction_report.csv'}")
        
        return direction_df
    
    def direction_adjustment(self):
        self.print_separator("二、指标方向统一")
        
        self.df_adjusted = self.df.copy()
        
        for var in self.negative_vars:
            data = self.df[var]
            max_val = data.max()
            min_val = data.min()
            
            self.df_adjusted[f'{var}_adj'] = max_val - data
            
            print(f"逆向指标正向化: {var}")
            print(f"  原值范围: [{min_val:.4f}, {max_val:.4f}]")
            print(f"  转换公式: {var}_adj = X_max - X = {max_val:.4f} - X")
            
            print(f"  转换示例（前10条）:")
            for i, (idx, row) in enumerate(self.df_adjusted.head(10).iterrows()):
                orig = row[var]
                adj = row[f'{var}_adj']
                print(f"    {i+1}. 原值={orig:.4f} → 正向化后={adj:.4f}")
        
        self.df_adjusted.to_csv(self.output_dir / "direction_adjusted_data.csv", index=False, encoding='utf-8-sig')
        print(f"\n方向统一后数据已保存至: {self.output_dir / 'direction_adjusted_data.csv'}")
        
        return self.df_adjusted
    
    def min_max_normalization(self):
        self.print_separator("三、Min-Max标准化")
        
        self.df_normalized = pd.DataFrame()
        
        self.normalization_params = {}
        
        norm_vars = [
            'grant_ratio',
            'participant_ratio',
            'discount_rate',
            'waiting_period_adj',
            'validity_period'
        ]
        
        print("标准化处理:")
        print("-" * 100)
        print(f"{'Variable':<20} | {'Min':<12} | {'Max':<12} | {'Range':<12}")
        print("-" * 100)
        
        for var in norm_vars:
            data = self.df_adjusted[var]
            min_val = data.min()
            max_val = data.max()
            range_val = max_val - min_val
            
            self.normalization_params[var] = {'min': min_val, 'max': max_val}
            
            self.df_normalized[var] = (data - min_val) / range_val
            
            print(f"{var:<20} | {min_val:<12.4f} | {max_val:<12.4f} | {range_val:<12.4f}")
        
        print("-" * 100)
        
        print("\n标准化公式:")
        print("  Z_ij = (X_ij - X_min) / (X_max - X_min)")
        print("  标准化后范围: [0, 1]")
        
        return self.df_normalized
    
    def normalization_validation(self):
        self.print_separator("四、标准化结果检查")
        
        norm_vars = self.df_normalized.columns.tolist()
        
        validation_report = []
        
        print("标准化结果验证:")
        print("-" * 100)
        print(f"{'Variable':<20} | {'Neg. Values':<12} | {'> 1 Values':<12} | {'Missing':<10} | {'Min':<10} | {'Max':<10}")
        print("-" * 100)
        
        for var in norm_vars:
            data = self.df_normalized[var]
            
            neg_count = (data < 0).sum()
            gt1_count = (data > 1).sum()
            missing_count = data.isnull().sum()
            actual_min = data.min()
            actual_max = data.max()
            
            min_ok = abs(actual_min) < 1e-10
            max_ok = abs(actual_max - 1) < 1e-10
            
            validation_report.append({
                'Variable': var,
                'Negative Values': int(neg_count),
                'Values > 1': int(gt1_count),
                'Missing Values': int(missing_count),
                'Actual Min': round(actual_min, 6),
                'Actual Max': round(actual_max, 6),
                'Min = 0': min_ok,
                'Max = 1': max_ok
            })
            
            min_mark = '✓' if min_ok else '✗'
            max_mark = '✓' if max_ok else '✗'
            print(f"{var:<20} | {neg_count:<12} | {gt1_count:<12} | {missing_count:<10} | {actual_min:<10.6f} {min_mark} | {actual_max:<10.6f} {max_mark}")
        
        print("-" * 100)
        
        validation_df = pd.DataFrame(validation_report)
        validation_df.to_csv(self.output_dir / "normalization_validation_report.csv", index=False, encoding='utf-8-sig')
        print(f"\n标准化验证报告已保存至: {self.output_dir / 'normalization_validation_report.csv'}")
        
        all_pass = (
            (validation_df['Negative Values'] == 0).all() and
            (validation_df['Values > 1'] == 0).all() and
            (validation_df['Missing Values'] == 0).all()
        )
        
        if all_pass:
            print("\n✓ 所有指标标准化验证通过！")
            print("✓ 无负值、无大于1的值、无缺失值")
        else:
            print("\n⚠️ 部分指标存在问题，请检查！")
        
        return validation_df
    
    def normalized_statistics(self):
        self.print_separator("五、标准化后描述统计")
        
        norm_vars = self.df_normalized.columns.tolist()
        
        stats_data = []
        for var in norm_vars:
            data = self.df_normalized[var]
            stats_data.append({
                'Variable': var,
                'Mean': round(data.mean(), 4),
                'Median': round(data.median(), 4),
                'Std': round(data.std(), 4),
                'Min': round(data.min(), 4),
                'Max': round(data.max(), 4)
            })
        
        stats_df = pd.DataFrame(stats_data)
        
        print("标准化后描述统计:")
        print("-" * 100)
        print(f"{'Variable':<20} | {'Mean':<12} | {'Median':<12} | {'Std':<12} | {'Min':<10} | {'Max':<10}")
        print("-" * 100)
        for _, row in stats_df.iterrows():
            print(f"{row['Variable']:<20} | {row['Mean']:<12.4f} | {row['Median']:<12.4f} | {row['Std']:<12.4f} | {row['Min']:<10.4f} | {row['Max']:<10.4f}")
        print("-" * 100)
        
        stats_df.to_csv(self.output_dir / "normalized_statistics.csv", index=False, encoding='utf-8-sig')
        print(f"\n标准化统计已保存至: {self.output_dir / 'normalized_statistics.csv'}")
        
        return stats_df
    
    def normalization_visualization(self):
        self.print_separator("六、标准化结果可视化")
        
        fig_dir = self.output_dir / "figures"
        fig_dir.mkdir(exist_ok=True)
        
        print("生成标准化前后对比图...")
        
        norm_vars = [
            'grant_ratio',
            'participant_ratio',
            'discount_rate',
            'waiting_period',
            'validity_period'
        ]
        
        fig, axes = plt.subplots(2, 5, figsize=(18, 8))
        
        for i, var in enumerate(norm_vars):
            data_before = self.df_adjusted[var]
            
            if var == 'waiting_period':
                data_after = self.df_normalized['waiting_period_adj']
            else:
                data_after = self.df_normalized[var]
            
            axes[0, i].hist(data_before, bins=20, color='#4C72B0', edgecolor='white', alpha=0.8)
            axes[0, i].set_title(f'{var}\n(Before)', fontsize=10)
            axes[0, i].set_xlabel('')
            
            axes[1, i].hist(data_after, bins=20, color='#DD8452', edgecolor='white', alpha=0.8)
            axes[1, i].set_title(f'{var}\n(After)', fontsize=10)
            axes[1, i].set_xlabel('')
        
        plt.suptitle('Normalization Comparison: Before vs After', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(fig_dir / "normalization_comparison.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ 已生成: normalization_comparison.png")
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()
        
        for i, var in enumerate(norm_vars):
            if var == 'waiting_period':
                data_after = self.df_normalized['waiting_period_adj']
            else:
                data_after = self.df_normalized[var]
            
            sns.histplot(data_after, ax=axes[i], bins=20, kde=True, color='#55A868', edgecolor='white')
            axes[i].set_title(f'{var} (After Normalization)', fontsize=11)
            axes[i].set_xlabel('Standardized Value')
        
        axes[-1].axis('off')
        plt.suptitle('Distribution After Normalization', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(fig_dir / "after_normalization_histograms.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ 已生成: after_normalization_histograms.png")
        
        print(f"\n可视化图片已保存至: {fig_dir}")
    
    def generate_entropy_input(self):
        self.print_separator("七、输出最终熵权法输入数据")
        
        entropy_vars = [
            'grant_ratio',
            'participant_ratio',
            'discount_rate',
            'waiting_period_adj',
            'validity_period'
        ]
        
        entropy_input = self.df_normalized[entropy_vars].copy()
        
        print("熵权法输入数据字段:")
        for var in entropy_vars:
            data = entropy_input[var]
            print(f"  {var}: 范围 [{data.min():.4f}, {data.max():.4f}]")
        
        print(f"\n样本数: {len(entropy_input)}")
        print(f"字段数: {len(entropy_input.columns)}")
        
        entropy_input.to_csv(self.output_dir / "entropy_input_data.csv", index=False, encoding='utf-8-sig')
        print(f"\n熵权法输入数据已保存至: {self.output_dir / 'entropy_input_data.csv'}")
        
        print("\n该文件将作为 Step 5 熵权法赋权的唯一输入文件。")
        
        return entropy_input
    
    def generate_report(self):
        self.print_separator("八、研究报告输出")
        
        report_content = """# 指标方向统一与标准化报告

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
"""
        
        with open(self.output_dir / "normalization_report.md", "w", encoding="utf-8") as f:
            f.write(report_content)
        
        print(f"标准化报告已保存至: {self.output_dir / 'normalization_report.md'}")
    
    def run(self):
        print("\n" + "#" * 80)
        print("#     Step 4: 指标方向统一与标准化")
        print("#     研究主题：上市公司股权激励慷慨度评价体系")
        print("#" * 80)
        
        self.indicator_direction_report()
        self.direction_adjustment()
        self.min_max_normalization()
        self.normalization_validation()
        self.normalized_statistics()
        self.normalization_visualization()
        self.generate_entropy_input()
        self.generate_report()
        
        print("\n" + "#" * 80)
        print("#     Step 4 完成！等待下一步指令。")
        print("#" * 80)


if __name__ == "__main__":
    input_path = "data_cleaning_output_v3/cleaned_equity_incentive_data.csv"
    
    if os.path.exists(input_path):
        processor = NormalizationProcessor(input_path)
        processor.run()
    else:
        print(f"错误: 文件 {input_path} 不存在!")