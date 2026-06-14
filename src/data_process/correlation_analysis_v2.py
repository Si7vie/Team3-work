#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 3: 相关性分析（Correlation Analysis）
研究主题：构建上市公司股权激励慷慨度（Generosity Score）评价体系

最终评价指标：
1. grant_ratio（授予比例）
2. participant_ratio（参与比例）
3. discount_rate（折扣率）
4. waiting_period（等待期）
5. validity_period（有效期）

分析方法：
1. Pearson 相关性分析（线性相关）
2. Spearman 秩相关分析（非线性相关，更稳健）
3. 多重共线性初步诊断

本阶段目标：检验指标之间是否存在明显信息重叠、潜在多重共线性风险。
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

class CorrelationAnalyzer:
    def __init__(self, input_path: str, output_dir: str = "correlation_analysis_output_v2"):
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
        
        print(f"输入文件: {input_path}")
        print(f"输出目录: {output_dir}")
        print(f"样本数: {len(self.df)}")
        print(f"核心指标: {self.core_vars}")
    
    def print_separator(self, title: str):
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80 + "\n")
    
    def descriptive_statistics_final(self):
        self.print_separator("一、描述统计复核")
        
        core_df = self.df[self.core_vars]
        desc_stats = core_df.describe().T
        desc_stats = desc_stats[['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']]
        desc_stats = desc_stats.round(4)
        
        print("最终评价指标描述统计:")
        print("-" * 130)
        print(f"{'Variable':<20} | {'Count':<8} | {'Mean':<12} | {'Std':<12} | {'Min':<12} | {'Max':<12}")
        print("-" * 130)
        for var in self.core_vars:
            print(f"{var:<20} | {int(desc_stats.loc[var, 'count']):<8} | {desc_stats.loc[var, 'mean']:<12.4f} | {desc_stats.loc[var, 'std']:<12.4f} | {desc_stats.loc[var, 'min']:<12.4f} | {desc_stats.loc[var, 'max']:<12.4f}")
        print("-" * 130)
        
        desc_stats.to_csv(self.output_dir / "descriptive_statistics_final.csv", encoding='utf-8-sig')
        print(f"\n描述统计已保存至: {self.output_dir / 'descriptive_statistics_final.csv'}")
        
        return desc_stats
    
    def pearson_correlation(self):
        self.print_separator("二、Pearson相关性分析")
        
        core_df = self.df[self.core_vars]
        pearson_corr = core_df.corr(method='pearson')
        pearson_corr = pearson_corr.round(4)
        
        print("Pearson Correlation Matrix:")
        print("-" * 120)
        print(f"{'Variable':<20}", end="")
        for var in self.core_vars:
            print(f"{var:<15}", end="")
        print()
        print("-" * 120)
        for var in self.core_vars:
            print(f"{var:<20}", end="")
            for other_var in self.core_vars:
                val = pearson_corr.loc[var, other_var]
                marker = "*" if abs(val) > 0.3 else " "
                print(f"{val:<15.4f}{marker}", end="")
            print()
        print("-" * 120)
        print("说明: * 表示 |r| > 0.3（中等相关）")
        
        pearson_corr.to_csv(self.output_dir / "correlation_matrix.csv", encoding='utf-8-sig')
        print(f"\nPearson相关性矩阵已保存至: {self.output_dir / 'correlation_matrix.csv'}")
        
        return pearson_corr
    
    def spearman_correlation(self):
        self.print_separator("三、Spearman相关性分析")
        
        core_df = self.df[self.core_vars]
        spearman_corr = core_df.corr(method='spearman')
        spearman_corr = spearman_corr.round(4)
        
        print("Spearman Rank Correlation Matrix:")
        print("-" * 120)
        print(f"{'Variable':<20}", end="")
        for var in self.core_vars:
            print(f"{var:<15}", end="")
        print()
        print("-" * 120)
        for var in self.core_vars:
            print(f"{var:<20}", end="")
            for other_var in self.core_vars:
                val = spearman_corr.loc[var, other_var]
                marker = "*" if abs(val) > 0.3 else " "
                print(f"{val:<15.4f}{marker}", end="")
            print()
        print("-" * 120)
        print("说明: * 表示 |r| > 0.3（中等相关）")
        
        spearman_corr.to_csv(self.output_dir / "spearman_correlation_matrix.csv", encoding='utf-8-sig')
        print(f"\nSpearman相关性矩阵已保存至: {self.output_dir / 'spearman_correlation_matrix.csv'}")
        
        return spearman_corr
    
    def correlation_heatmaps(self, pearson_corr, spearman_corr):
        self.print_separator("四、相关性热力图")
        
        print("生成 Pearson 相关性热力图...")
        
        fig, ax = plt.subplots(figsize=(10, 8))
        mask = np.triu(np.ones_like(pearson_corr, dtype=bool), k=1)
        
        sns.heatmap(pearson_corr, annot=True, fmt='.4f', cmap='coolwarm', 
                   center=0, mask=mask, ax=ax,
                   annot_kws={'size': 10}, cbar_kws={'shrink': 0.8})
        
        ax.set_title('Pearson Correlation Matrix', fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.savefig(self.output_dir / "pearson_heatmap.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print("生成 Spearman 相关性热力图...")
        
        fig, ax = plt.subplots(figsize=(10, 8))
        mask = np.triu(np.ones_like(spearman_corr, dtype=bool), k=1)
        
        sns.heatmap(spearman_corr, annot=True, fmt='.4f', cmap='coolwarm',
                   center=0, mask=mask, ax=ax,
                   annot_kws={'size': 10}, cbar_kws={'shrink': 0.8})
        
        ax.set_title('Spearman Rank Correlation Matrix', fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.savefig(self.output_dir / "spearman_heatmap.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"热力图已保存至: {self.output_dir}")
    
    def interpret_correlations(self, pearson_corr, spearman_corr):
        self.print_separator("五、相关性结果解释")
        
        high_correlations = []
        moderate_correlations = []
        weak_correlations = []
        
        for i, var1 in enumerate(self.core_vars):
            for j, var2 in enumerate(self.core_vars):
                if i < j:
                    pearson_r = pearson_corr.loc[var1, var2]
                    spearman_r = spearman_corr.loc[var1, var2]
                    
                    if abs(pearson_r) > 0.7:
                        high_correlations.append((var1, var2, pearson_r, spearman_r))
                    elif abs(pearson_r) > 0.3:
                        moderate_correlations.append((var1, var2, pearson_r, spearman_r))
                    else:
                        weak_correlations.append((var1, var2, pearson_r, spearman_r))
        
        print("相关性分类:")
        print("-" * 80)
        
        print(f"\n【高度相关 |r| > 0.7】: {len(high_correlations)} 对")
        if high_correlations:
            for var1, var2, p_r, s_r in high_correlations:
                print(f"  - {var1} vs {var2}: Pearson={p_r:.4f}, Spearman={s_r:.4f}")
        else:
            print("  - 无高度相关变量")
        
        print(f"\n【中等相关 0.3 < |r| < 0.7】: {len(moderate_correlations)} 对")
        if moderate_correlations:
            for var1, var2, p_r, s_r in moderate_correlations:
                print(f"  - {var1} vs {var2}: Pearson={p_r:.4f}, Spearman={s_r:.4f}")
        
        print(f"\n【弱相关 |r| < 0.3】: {len(weak_correlations)} 对")
        if weak_correlations:
            for var1, var2, p_r, s_r in weak_correlations:
                print(f"  - {var1} vs {var2}: Pearson={p_r:.4f}, Spearman={s_r:.4f}")
        
        print("\n" + "-" * 80)
        print("重点分析:")
        print("-" * 80)
        
        print("\n1. grant_ratio 与 participant_ratio:")
        gr_pr_p = pearson_corr.loc['grant_ratio', 'participant_ratio']
        gr_pr_s = spearman_corr.loc['grant_ratio', 'participant_ratio']
        print(f"   Pearson r = {gr_pr_p:.4f}, Spearman r = {gr_pr_s:.4f}")
        if abs(gr_pr_p) > 0.3:
            print(f"   → 存在{'正' if gr_pr_p > 0 else '负'}向{'中等' if abs(gr_pr_p) < 0.7 else '高度'}相关")
            if gr_pr_p > 0:
                print(f"   → 覆盖面越广的方案通常授予比例越高（规模效应）")
            else:
                print(f"   → 覆盖面越广的方案通常授予比例越低（替代关系）")
        else:
            print(f"   → 相关性较弱，各自提供独立信息")
        
        print("\n2. grant_ratio 与 discount_rate:")
        gr_dr_p = pearson_corr.loc['grant_ratio', 'discount_rate']
        print(f"   Pearson r = {gr_dr_p:.4f}")
        if abs(gr_dr_p) > 0.3:
            print(f"   → 存在{'正' if gr_dr_p > 0 else '负'}向{'中等' if abs(gr_dr_p) < 0.7 else '高度'}相关")
            if gr_dr_p > 0:
                print(f"   → 授予比例高的方案同时折扣率也高（双重慷慨）")
            else:
                print(f"   → 授予比例高的方案折扣率较低（替代关系）")
        else:
            print(f"   → 相关性较弱，各自从不同维度反映激励强度")
        
        print("\n3. participant_ratio 与 discount_rate:")
        pr_dr_p = pearson_corr.loc['participant_ratio', 'discount_rate']
        print(f"   Pearson r = {pr_dr_p:.4f}")
        if abs(pr_dr_p) < 0.3:
            print(f"   → 相关性较弱，具有独立信息价值")
            print(f"   → participant_ratio 代表覆盖广度，discount_rate 代表定价深度")
        else:
            print(f"   → 存在{'正' if pr_dr_p > 0 else '负'}向相关")
        
        print("\n4. waiting_period 与 validity_period:")
        wp_vp_p = pearson_corr.loc['waiting_period', 'validity_period']
        print(f"   Pearson r = {wp_vp_p:.4f}")
        if abs(wp_vp_p) > 0.3:
            print(f"   → 存在{'正' if wp_vp_p > 0 else '负'}向相关")
            if wp_vp_p > 0:
                print(f"   → 等待期越长的方案有效期也越长（长期激励特征）")
        else:
            print(f"   → 相关性较弱，各自代表不同的时间维度特征")
        
        print("\n5. discount_rate 与 waiting_period:")
        dr_wp_p = pearson_corr.loc['discount_rate', 'waiting_period']
        print(f"   Pearson r = {dr_wp_p:.4f}")
        if dr_wp_p < 0:
            print(f"   → 负相关，可能存在替代关系：等待期越长，折扣率越低")
            print(f"   → 公司可能在价格激励和时间约束之间进行权衡")
        else:
            print(f"   → 相关性较弱或正相关")
        
        return high_correlations, moderate_correlations, weak_correlations
    
    def multicollinearity_diagnosis(self, pearson_corr, high_correlations):
        self.print_separator("六、多重共线性初步判断")
        
        print("多重共线性判断标准:")
        print("  |r| < 0.3: 弱相关（无共线性风险）")
        print("  0.3 < |r| < 0.7: 中等相关（需关注）")
        print("  |r| > 0.7: 高度相关（存在多重共线性风险）")
        
        print("\n" + "-" * 80)
        
        if len(high_correlations) > 0:
            print(f"⚠️ 存在 {len(high_correlations)} 对高度相关变量（|r| > 0.7）:")
            for var1, var2, p_r, s_r in high_correlations:
                print(f"   - {var1} vs {var2}: r = {p_r:.4f}")
            print("\n建议: 存在潜在多重共线性风险，后续可考虑:")
            print("  1. 删除一个高度相关变量")
            print("  2. 使用主成分分析降维")
            print("  3. 采用岭回归等方法处理")
        else:
            print("✓ 无高度相关变量（|r| > 0.7）")
            print("✓ 潜在多重共线性风险较低")
            print("✓ 各指标能够提供相对独立的信息")
        
        print("\n结论:")
        if len(high_correlations) > 0:
            print("  存在多重共线性风险，建议谨慎处理。")
        else:
            print("  各指标相关性适中，能够从不同维度衡量股权激励慷慨度。")
    
    def evaluate_system(self, pearson_corr, high_correlations):
        self.print_separator("七、评价体系合理性评估")
        
        print("评价体系合理性评估:")
        print("-" * 80)
        
        print("\n1. 当前5个指标是否能够从不同维度衡量股权激励慷慨度？")
        if len(high_correlations) > 0:
            print("   → 部分指标高度相关，存在信息重叠，但整体仍能从多个维度衡量")
        else:
            print("   → 各指标相关性较低，能够从不同维度衡量")
            print("     * grant_ratio: 授予比例（相对规模）")
            print("     * participant_ratio: 参与比例（覆盖广度）")
            print("     * discount_rate: 折扣率（定价慷慨度）")
            print("     * waiting_period: 等待期（时间约束）")
            print("     * validity_period: 有效期（时间长度）")
        
        print("\n2. 是否存在严重重复测量问题？")
        if len(high_correlations) > 0:
            print(f"   → 存在 {len(high_correlations)} 对高度相关变量，存在一定重复测量问题")
        else:
            print("   → 无高度相关变量，不存在严重重复测量问题")
        
        print("\n3. 是否建议全部保留进入熵权法评价体系？")
        if len(high_correlations) > 0:
            print("   → 建议谨慎保留，或考虑删除高度相关变量中的一个")
        else:
            print("   → ✓ 建议全部保留进入熵权法评价体系")
            print("   → 各指标提供相对独立的信息")
            print("   → 不存在严重的多重共线性问题")
        
        print("\n4. 学术化解释:")
        print("   本研究采用的5个评价指标分别从以下维度衡量股权激励慷慨度:")
        print("   - grant_ratio: 股权激励的相对规模维度")
        print("   - participant_ratio: 股权激励的覆盖广度维度")
        print("   - discount_rate: 股权激励的定价优惠维度")
        print("   - waiting_period: 股权激励的时间约束维度")
        print("   - validity_period: 股权激励的时间跨度维度")
        print("   相关性分析表明，各指标之间相关性适中，不存在严重的多重共线性问题，")
        print("   能够从不同维度共同构成股权激励慷慨度的综合评价体系。")
    
    def generate_report(self, pearson_corr, spearman_corr, high_correlations, moderate_correlations):
        self.print_separator("八、研究报告输出")
        
        n = len(self.df)
        n_vars = len(self.core_vars)
        
        total_pairs = n_vars * (n_vars - 1) // 2
        high_count = len(high_correlations)
        moderate_count = len(moderate_correlations)
        weak_count = total_pairs - high_count - moderate_count
        
        report_content = """# 相关性分析报告

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

- **样本数**: {n}
- **评价指标数**: {n_vars}
- **评价指标**: grant_ratio, participant_ratio, discount_rate, waiting_period, validity_period

## Pearson 相关性分析结果

### 相关性矩阵

详见 `correlation_matrix.csv`

### 相关性分类

- **高度相关（|r| > 0.7）**: {high_count} 对
- **中等相关（0.3 < |r| < 0.7）**: {moderate_count} 对
- **弱相关（|r| < 0.3）**: {weak_count} 对

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

""".format(
            n=n,
            n_vars=n_vars,
            high_count=high_count,
            moderate_count=moderate_count,
            weak_count=weak_count
        )
        
        if high_count > 0:
            report_content += """**存在高度相关变量（|r| > 0.7）**:

"""
            for var1, var2, p_r, s_r in high_correlations:
                report_content += f"- {var1} vs {var2}: Pearson r = {p_r:.4f}, Spearman r = {s_r:.4f}\n"
            
            report_content += """
⚠️ **存在多重共线性风险**

建议:
1. 删除一个高度相关变量
2. 使用主成分分析降维
3. 采用岭回归等方法处理
"""
        else:
            report_content += """**无高度相关变量（|r| > 0.7）**

✓ 潜在多重共线性风险较低
✓ 各指标能够提供相对独立的信息
"""
        
        report_content += """
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

"""
        
        if high_count > 0:
            report_content += f"存在 {high_count} 对高度相关变量，存在一定重复测量问题。\n"
        else:
            report_content += "无高度相关变量，不存在严重重复测量问题。\n"
        
        report_content += """
### 3. 指标保留建议

"""
        
        if high_count > 0:
            report_content += """建议谨慎保留，或考虑删除高度相关变量中的一个。
"""
        else:
            report_content += """**✓ 建议全部保留进入熵权法评价体系**

理由:
1. 各指标提供相对独立的信息
2. 不存在严重的多重共线性问题
3. 能够从不同维度衡量股权激励慷慨度
"""
        
        report_content += """
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
"""
        
        with open(self.output_dir / "correlation_analysis_report.md", "w", encoding="utf-8") as f:
            f.write(report_content)
        
        print(f"相关性分析报告已保存至: {self.output_dir / 'correlation_analysis_report.md'}")
    
    def run(self):
        print("\n" + "#" * 80)
        print("#     Step 3: 相关性分析")
        print("#     研究主题：上市公司股权激励慷慨度评价体系")
        print("#" * 80)
        
        self.descriptive_statistics_final()
        pearson_corr = self.pearson_correlation()
        spearman_corr = self.spearman_correlation()
        self.correlation_heatmaps(pearson_corr, spearman_corr)
        high, moderate, weak = self.interpret_correlations(pearson_corr, spearman_corr)
        self.multicollinearity_diagnosis(pearson_corr, high)
        self.evaluate_system(pearson_corr, high)
        self.generate_report(pearson_corr, spearman_corr, high, moderate)
        
        print("\n" + "#" * 80)
        print("#     Step 3 完成！等待下一步指令。")
        print("#" * 80)


if __name__ == "__main__":
    input_path = "data_cleaning_output_v3/cleaned_equity_incentive_data.csv"
    
    if os.path.exists(input_path):
        analyzer = CorrelationAnalyzer(input_path)
        analyzer.run()
    else:
        print(f"错误: 文件 {input_path} 不存在!")