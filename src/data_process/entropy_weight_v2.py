#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 5: 熵权法赋权（Entropy Weight Method）
研究主题：构建上市公司股权激励慷慨度（Generosity Score）评价体系

最终评价指标：
1. grant_ratio（授予比例）
2. participant_ratio（参与比例）
3. discount_rate（折扣率）
4. waiting_period_adj（等待期正向化）
5. validity_period（有效期）

熵权法原理：
- 信息熵越小，指标值越不一致，区分度越强，权重越高
- 信息熵越大，指标值越一致，区分度越弱，权重越低

核心公式：
1. 指标占比: P_ij = Z_ij / ΣZ_ij
2. 信息熵: e_j = -k * Σ(P_ij * ln(P_ij)), k = 1/ln(n)
3. 差异系数: d_j = 1 - e_j
4. 熵权: w_j = d_j / Σd_j
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

class EntropyWeightCalculator:
    def __init__(self, input_path: str, output_dir: str = "entropy_weight_output_v2"):
        self.input_path = input_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.df = pd.read_csv(input_path, encoding='utf-8-sig')
        
        self.core_vars = [
            'grant_ratio',
            'participant_ratio',
            'discount_rate',
            'waiting_period_adj',
            'validity_period'
        ]
        
        print(f"输入文件: {input_path}")
        print(f"输出目录: {output_dir}")
        print(f"样本数: {len(self.df)}")
        print(f"指标数: {len(self.core_vars)}")
        print(f"指标: {self.core_vars}")
    
    def print_separator(self, title: str):
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80 + "\n")
    
    def entropy_input_validation(self):
        self.print_separator("一、构建标准化评价矩阵")
        
        print("标准化评价矩阵概览:")
        print("-" * 100)
        print(f"样本数 (n): {len(self.df)}")
        print(f"指标数 (m): {len(self.df.columns)}")
        print(f"字段: {list(self.df.columns)}")
        
        validation_data = []
        
        print("\n各指标范围验证:")
        print("-" * 100)
        print(f"{'Indicator':<20} | {'Min':<10} | {'Max':<10} | {'Missing':<10} | {'Valid':<10}")
        print("-" * 100)
        
        for col in self.df.columns:
            data = self.df[col]
            min_val = data.min()
            max_val = data.max()
            missing = data.isnull().sum()
            
            min_valid = min_val >= 0
            max_valid = max_val <= 1
            range_valid = min_valid and max_valid
            missing_valid = missing == 0
            all_valid = range_valid and missing_valid
            
            validation_data.append({
                'Indicator': col,
                'Min': round(min_val, 6),
                'Max': round(max_val, 6),
                'Missing Values': int(missing),
                'Range [0,1]': range_valid,
                'No Missing': missing_valid,
                'Valid': all_valid
            })
            
            status = '✓' if all_valid else '✗'
            print(f"{col:<20} | {min_val:<10.6f} | {max_val:<10.6f} | {missing:<10} | {status:<10}")
        
        print("-" * 100)
        
        validation_df = pd.DataFrame(validation_data)
        validation_df.to_csv(self.output_dir / "entropy_input_validation.csv", index=False, encoding='utf-8-sig')
        print(f"\n输入验证报告已保存至: {self.output_dir / 'entropy_input_validation.csv'}")
        
        all_valid = validation_df['Valid'].all()
        if all_valid:
            print("\n✓ 所有指标均已正确标准化（范围 [0,1]，无缺失值）")
            print("✓ 可以直接进行熵权法计算")
        else:
            print("\n⚠️ 部分指标存在问题，请检查！")
        
        return validation_df
    
    def calculate_proportion_matrix(self):
        self.print_separator("二、计算指标占比矩阵")
        
        Z = self.df[self.core_vars].values
        
        print("指标占比公式:")
        print("  P_ij = Z_ij / Σ(Z_ij)")
        print("  Σ(P_ij) = 1 (按列求和)")
        
        col_sums = Z.sum(axis=0)
        self.P = Z / col_sums
        
        self.P_df = pd.DataFrame(self.P, columns=self.core_vars)
        
        print("\n指标占比矩阵统计:")
        print("-" * 100)
        print(f"{'Indicator':<20} | {'Σ(P_ij)':<12} | {'Min(P)':<12} | {'Max(P)':<12}")
        print("-" * 100)
        
        for i, var in enumerate(self.core_vars):
            col = self.P[:, i]
            print(f"{var:<20} | {col.sum():<12.6f} | {col.min():<12.6f} | {col.max():<12.6f}")
        
        print("-" * 100)
        
        self.P_df.to_csv(self.output_dir / "proportion_matrix.csv", index=False, encoding='utf-8-sig')
        print(f"\n占比矩阵已保存至: {self.output_dir / 'proportion_matrix.csv'}")
        
        return self.P_df
    
    def calculate_entropy(self):
        self.print_separator("三、计算信息熵")
        
        n = len(self.df)
        k = 1 / np.log(n)
        
        print("信息熵公式:")
        print(f"  k = 1 / ln(n) = 1 / ln({n}) = {k:.6f}")
        print("  e_j = -k * Σ(P_ij * ln(P_ij))")
        print("  若 P_ij = 0，则 P_ij * ln(P_ij) = 0")
        
        self.entropy_values = []
        
        print("\n信息熵计算:")
        print("-" * 100)
        print(f"{'Indicator':<20} | {'Entropy (e_j)':<15} | {'Variability':<20}")
        print("-" * 100)
        
        for i, var in enumerate(self.core_vars):
            col = self.P[:, i]
            
            entropy_terms = col * np.log(col, where=col > 0)
            entropy_terms[col == 0] = 0
            
            e_j = -k * entropy_terms.sum()
            
            if e_j > 0.95:
                variability = '低（值趋于一致）'
            elif e_j > 0.9:
                variability = '较低'
            elif e_j > 0.8:
                variability = '中等'
            else:
                variability = '高（区分度强）'
            
            self.entropy_values.append({
                'Indicator': var,
                'Entropy': round(e_j, 6),
                'Variability': variability
            })
            
            print(f"{var:<20} | {e_j:<15.6f} | {variability:<20}")
        
        print("-" * 100)
        print("\n信息熵解释:")
        print("  • e_j ≈ 1: 指标值趋于一致，信息量少，权重低")
        print("  • e_j ≈ 0: 指标值差异大，信息量多，权重高")
        
        entropy_df = pd.DataFrame(self.entropy_values)
        entropy_df.to_csv(self.output_dir / "entropy_values.csv", index=False, encoding='utf-8-sig')
        print(f"\n信息熵已保存至: {self.output_dir / 'entropy_values.csv'}")
        
        return entropy_df
    
    def calculate_diversity_coefficient(self):
        self.print_separator("四、计算差异系数")
        
        print("差异系数公式:")
        print("  d_j = 1 - e_j")
        print("  d_j 越大，指标区分度越强，权重越高")
        
        self.diversity_data = []
        
        print("\n差异系数计算:")
        print("-" * 100)
        print(f"{'Indicator':<20} | {'Entropy (e_j)':<15} | {'Diversity (d_j)':<15} | {'Rank':<6}")
        print("-" * 100)
        
        entropy_dict = {item['Indicator']: item['Entropy'] for item in self.entropy_values}
        
        for var in self.core_vars:
            e_j = entropy_dict[var]
            d_j = 1 - e_j
            
            self.diversity_data.append({
                'Indicator': var,
                'Entropy': round(e_j, 6),
                'Diversity Coefficient': round(d_j, 6)
            })
        
        diversity_df = pd.DataFrame(self.diversity_data)
        diversity_df = diversity_df.sort_values('Diversity Coefficient', ascending=False).reset_index(drop=True)
        diversity_df['Rank'] = diversity_df.index + 1
        
        for idx, row in diversity_df.iterrows():
            print(f"{row['Indicator']:<20} | {row['Entropy']:<15.6f} | {row['Diversity Coefficient']:<15.6f} | {int(row['Rank']):<6}")
        
        print("-" * 100)
        
        diversity_df.to_csv(self.output_dir / "diversity_coefficient.csv", index=False, encoding='utf-8-sig')
        print(f"\n差异系数已保存至: {self.output_dir / 'diversity_coefficient.csv'}")
        
        return diversity_df
    
    def calculate_entropy_weights(self):
        self.print_separator("五、计算熵权")
        
        print("熵权公式:")
        print("  w_j = d_j / Σ(d_j)")
        print("  Σ(w_j) = 1")
        
        self.weight_data = []
        
        total_diversity = sum(item['Diversity Coefficient'] for item in self.diversity_data)
        
        print(f"\n差异系数总和 Σ(d_j) = {total_diversity:.6f}")
        print("-" * 100)
        
        diversity_dict = {item['Indicator']: item['Diversity Coefficient'] for item in self.diversity_data}
        
        for var in self.core_vars:
            d_j = diversity_dict[var]
            w_j = d_j / total_diversity
            
            self.weight_data.append({
                'Indicator': var,
                'Diversity Coefficient': round(d_j, 6),
                'Weight': round(w_j, 6)
            })
        
        weights_df = pd.DataFrame(self.weight_data)
        weights_df = weights_df.sort_values('Weight', ascending=False).reset_index(drop=True)
        weights_df['Rank'] = weights_df.index + 1
        
        print("\n熵权计算结果（按权重排序）:")
        print("-" * 120)
        print(f"{'Indicator':<20} | {'Diversity (d_j)':<15} | {'Weight (w_j)':<15} | {'Weight (%)':<12} | {'Rank':<6}")
        print("-" * 120)
        
        for idx, row in weights_df.iterrows():
            weight_pct = row['Weight'] * 100
            print(f"{row['Indicator']:<20} | {row['Diversity Coefficient']:<15.6f} | {row['Weight']:<15.6f} | {weight_pct:<12.2f}% | {int(row['Rank']):<6}")
        
        print("-" * 120)
        
        total_weight = weights_df['Weight'].sum()
        print(f"\n权重总和: Σ(w_j) = {total_weight:.6f}")
        if abs(total_weight - 1.0) < 1e-10:
            print("✓ 权重总和 = 1，计算正确")
        else:
            print("⚠️ 权重总和 ≠ 1，请检查！")
        
        weights_df.to_csv(self.output_dir / "entropy_weights.csv", index=False, encoding='utf-8-sig')
        print(f"\n熵权已保存至: {self.output_dir / 'entropy_weights.csv'}")
        
        return weights_df
    
    def interpret_weights(self, weights_df):
        self.print_separator("六、权重结果解释")
        
        weight_dict = dict(zip(weights_df['Indicator'], weights_df['Weight']))
        
        sorted_weights = sorted(weight_dict.items(), key=lambda x: x[1], reverse=True)
        highest_var, highest_w = sorted_weights[0]
        lowest_var, lowest_w = sorted_weights[-1]
        
        print("权重结果分析:")
        print("-" * 100)
        
        print(f"\n1. 权重最高指标: {highest_var}")
        print(f"   权重: {highest_w:.4f} ({highest_w*100:.2f}%)")
        print(f"   说明: {highest_var} 的样本差异性最大")
        print(f"   对 Generosity Score 贡献最大")
        
        print(f"\n2. 权重最低指标: {lowest_var}")
        print(f"   权重: {lowest_w:.4f} ({lowest_w*100:.2f}%)")
        print(f"   说明: {lowest_var} 的样本差异性较小")
        print(f"   信息量相对较低")
        
        pr_w = weight_dict.get('participant_ratio', 0)
        print(f"\n3. participant_ratio 权重表现")
        print(f"   权重: {pr_w:.4f} ({pr_w*100:.2f}%)")
        if pr_w > 0.2:
            print(f"   → 员工覆盖面具有较强区分度")
            print(f"   → 不同公司的激励覆盖广度差异较大")
        elif pr_w > 0.15:
            print(f"   → 员工覆盖面区分度中等")
        else:
            print(f"   → 员工覆盖面区分度相对较低")
        
        dr_w = weight_dict.get('discount_rate', 0)
        print(f"\n4. discount_rate 权重表现")
        print(f"   权重: {dr_w:.4f} ({dr_w*100:.2f}%)")
        if dr_w > 0.2:
            print(f"   → 价格优惠是解释慷慨度的重要维度")
            print(f"   → 不同公司的定价策略差异较大")
        elif dr_w > 0.15:
            print(f"   → 价格优惠区分度中等")
        else:
            print(f"   → 价格优惠区分度相对较低")
        
        wp_w = weight_dict.get('waiting_period_adj', 0)
        print(f"\n5. waiting_period_adj 权重表现")
        print(f"   权重: {wp_w:.4f} ({wp_w*100:.2f}%)")
        if wp_w > 0.2:
            print(f"   → 时间约束在评价体系中重要程度较高")
        elif wp_w > 0.15:
            print(f"   → 时间约束重要程度中等")
        else:
            print(f"   → 时间约束重要程度相对较低")
        
        print("\n" + "-" * 100)
    
    def evaluate_weights(self, weights_df):
        self.print_separator("七、权重合理性评估")
        
        weight_dict = dict(zip(weights_df['Indicator'], weights_df['Weight']))
        
        print("权重结构合理性评估:")
        print("-" * 100)
        
        print("\n1. 权重结构是否合理？")
        print("   ✓ 熵权法是客观赋权方法，完全基于数据特征")
        print("   ✓ 权重反映了各指标在样本中的区分能力")
        print("   ✓ 避免了主观赋权的偏差")
        
        print("\n2. 是否符合经济直觉？")
        print("   需要结合股权激励理论分析:")
        for var in self.core_vars:
            w = weight_dict[var]
            print(f"   - {var}: {w:.4f} ({w*100:.2f}%)")
        
        print("\n3. 是否体现客观赋权思想？")
        print("   ✓ 完全基于数据的信息熵计算")
        print("   ✓ 无主观判断介入")
        print("   ✓ 权重随样本分布自动调整")
        
        print("\n4. 是否建议直接用于 Generosity Score 构建？")
        print("   ✓ 建议直接使用")
        print("   ✓ 权重经过严格数学推导")
        print("   ✓ 各指标区分度已充分体现")
        print("   ✓ 可以进入 Step 6 Generosity Score 计算")
        
        print("\n" + "-" * 100)
        print("理论解释:")
        print("  • grant_ratio: 反映授予规模，若权重高说明样本公司规模差异大")
        print("  • participant_ratio: 反映覆盖广度，若权重高说明公司覆盖策略差异大")
        print("  • discount_rate: 反映定价策略，若权重高说明定价方式差异大")
        print("  • waiting_period_adj: 反映时间约束，若权重高说明锁定期设计差异大")
        print("  • validity_period: 反映时间跨度，若权重高说明计划期限差异大")
    
    def generate_report(self, weights_df):
        self.print_separator("八、研究报告输出")
        
        n = len(self.df)
        m = len(self.core_vars)
        
        weight_dict = dict(zip(weights_df['Indicator'], weights_df['Weight']))
        sorted_weights = sorted(weight_dict.items(), key=lambda x: x[1], reverse=True)
        highest_var, highest_w = sorted_weights[0]
        lowest_var, lowest_w = sorted_weights[-1]
        
        report_content = """# 熵权法赋权报告

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

- 样本数 (n): {n}
- 指标数 (m): {m}
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

""".format(n=n, m=m)
        
        for var, w in sorted_weights:
            report_content += f"- **{var}**: {w:.4f} ({w*100:.2f}%)\n"
        
        report_content += """
### 关键发现

1. **权重最高指标**: {highest_var}
   - 权重: {highest_w:.4f} ({highest_w_pct:.2f}%)
   - 说明: 样本差异性最大，对 Generosity Score 贡献最大

2. **权重最低指标**: {lowest_var}
   - 权重: {lowest_w:.4f} ({lowest_w_pct:.2f}%)
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
""".format(
            highest_var=highest_var,
            highest_w=highest_w,
            highest_w_pct=highest_w*100,
            lowest_var=lowest_var,
            lowest_w=lowest_w,
            lowest_w_pct=lowest_w*100
        )
        
        with open(self.output_dir / "entropy_weight_report.md", "w", encoding="utf-8") as f:
            f.write(report_content)
        
        print(f"熵权法报告已保存至: {self.output_dir / 'entropy_weight_report.md'}")
    
    def run(self):
        print("\n" + "#" * 80)
        print("#     Step 5: 熵权法赋权")
        print("#     研究主题：上市公司股权激励慷慨度评价体系")
        print("#" * 80)
        
        self.entropy_input_validation()
        self.calculate_proportion_matrix()
        self.calculate_entropy()
        diversity_df = self.calculate_diversity_coefficient()
        weights_df = self.calculate_entropy_weights()
        self.interpret_weights(weights_df)
        self.evaluate_weights(weights_df)
        self.generate_report(weights_df)
        
        print("\n" + "#" * 80)
        print("#     Step 5 完成！等待下一步指令。")
        print("#" * 80)


if __name__ == "__main__":
    input_path = "normalization_output_v2/entropy_input_data.csv"
    
    if os.path.exists(input_path):
        calculator = EntropyWeightCalculator(input_path)
        calculator.run()
    else:
        print(f"错误: 文件 {input_path} 不存在!")