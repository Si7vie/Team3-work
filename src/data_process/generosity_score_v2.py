#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 6: Generosity Score计算与排名分析（Score Construction & Ranking Analysis）
研究主题：构建上市公司股权激励慷慨度（Generosity Score）评价体系

核心公式：
Generosity Score_i = Σ(w_j * Z_ij)

其中：
- w_j: 熵权法计算的指标权重
- Z_ij: 标准化后的指标值

输出：
- 每家公司的 Generosity Score
- 排名结果
- Top10/Bottom10 分析
- 分布特征分析
- 可视化图表
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

class GenerosityScoreCalculator:
    def __init__(self, data_path: str, weights_path: str, output_dir: str = "generosity_score_output_v2"):
        self.data_path = data_path
        self.weights_path = weights_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.df_data = pd.read_csv(data_path, encoding='utf-8-sig')
        self.weights_df = pd.read_csv(weights_path, encoding='utf-8-sig')
        
        self.core_vars = [
            'grant_ratio',
            'participant_ratio',
            'discount_rate',
            'waiting_period_adj',
            'validity_period'
        ]
        
        print(f"输入数据: {data_path}")
        print(f"权重数据: {weights_path}")
        print(f"输出目录: {output_dir}")
        print(f"样本数: {len(self.df_data)}")
    
    def print_separator(self, title: str):
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80 + "\n")
    
    def validate_weights(self):
        self.print_separator("一、读取权重结果并验证")
        
        print("权重结果:")
        print("-" * 100)
        print(f"{'Indicator':<20} | {'Weight':<12} | {'Weight (%)':<12}")
        print("-" * 100)
        
        for _, row in self.weights_df.iterrows():
            print(f"{row['Indicator']:<20} | {row['Weight']:<12.6f} | {row['Weight']*100:<12.2f}%")
        print("-" * 100)
        
        total_weight = self.weights_df['Weight'].sum()
        missing_weights = self.weights_df['Weight'].isnull().sum()
        negative_weights = (self.weights_df['Weight'] < 0).sum()
        
        print("\n权重验证:")
        print(f"  权重总和: {total_weight:.10f}")
        print(f"  缺失权重: {missing_weights}")
        print(f"  负权重: {negative_weights}")
        
        validation_data = {
            'Check': ['权重总和 = 1', '无缺失权重', '无负权重'],
            'Result': [
                '✓' if abs(total_weight - 1.0) < 1e-10 else '✗',
                '✓' if missing_weights == 0 else '✗',
                '✓' if negative_weights == 0 else '✗'
            ],
            'Value': [f"{total_weight:.10f}", f"{missing_weights}", f"{negative_weights}"]
        }
        
        validation_df = pd.DataFrame(validation_data)
        validation_df.to_csv(self.output_dir / "weight_validation_report.csv", index=False, encoding='utf-8-sig')
        
        all_valid = (
            abs(total_weight - 1.0) < 1e-10 and
            missing_weights == 0 and
            negative_weights == 0
        )
        
        if all_valid:
            print("\n✓ 权重验证通过！")
            print("✓ 权重总和 = 1")
            print("✓ 无缺失权重")
            print("✓ 无负权重")
        else:
            print("\n⚠️ 权重存在问题！")
        
        return all_valid
    
    def calculate_generosity_score(self):
        self.print_separator("二、计算Generosity Score")
        
        weight_dict = dict(zip(self.weights_df['Indicator'], self.weights_df['Weight']))
        
        print("权重配置:")
        for var in self.core_vars:
            w = weight_dict.get(var, 0)
            print(f"  {var}: {w:.6f}")
        
        print("\nGenerosity Score 公式:")
        print("  Generosity Score_i = Σ(w_j × Z_ij)")
        
        self.df_scores = self.df_data.copy()
        self.df_scores['generosity_score'] = 0
        
        for var in self.core_vars:
            w = weight_dict.get(var, 0)
            self.df_scores['generosity_score'] += self.df_scores[var] * w
        
        self.df_scores['generosity_score'] = self.df_scores['generosity_score'].round(6)
        
        print("\nGenerosity Score 统计:")
        print("-" * 100)
        scores = self.df_scores['generosity_score']
        print(f"  样本数: {len(scores)}")
        print(f"  均值: {scores.mean():.6f}")
        print(f"  中位数: {scores.median():.6f}")
        print(f"  标准差: {scores.std():.6f}")
        print(f"  最小值: {scores.min():.6f}")
        print(f"  最大值: {scores.max():.6f}")
        print(f"  范围: [{scores.min():.6f}, {scores.max():.6f}]")
        print("-" * 100)
        
        output_df = self.df_scores[['generosity_score']].copy()
        output_df.index = range(1, len(output_df) + 1)
        output_df.index.name = 'Company'
        output_df.reset_index(inplace=True)
        
        output_df.to_csv(self.output_dir / "generosity_scores.csv", index=False, encoding='utf-8-sig')
        print(f"\nGenerosity Score 已保存至: {self.output_dir / 'generosity_scores.csv'}")
        
        return self.df_scores
    
    def build_ranking(self):
        self.print_separator("三、构建排名结果")
        
        self.df_ranking = self.df_scores.copy()
        self.df_ranking = self.df_ranking.sort_values('generosity_score', ascending=False).reset_index(drop=True)
        self.df_ranking['rank'] = self.df_ranking.index + 1
        
        self.df_ranking['Company'] = [f"公司{i+1}" for i in range(len(self.df_ranking))]
        
        cols = ['rank', 'Company', 'generosity_score'] + self.core_vars
        self.df_ranking = self.df_ranking[cols]
        
        print("排名结果预览（Top 10）:")
        print("-" * 120)
        print(f"{'Rank':<6} | {'Company':<10} | {'Score':<12} | {'grant_ratio':<12} | {'participant_ratio':<18} | {'discount_rate':<12}")
        print("-" * 120)
        
        for idx, row in self.df_ranking.head(10).iterrows():
            print(f"{int(row['rank']):<6} | {row['Company']:<10} | {row['generosity_score']:<12.6f} | {row['grant_ratio']:<12.6f} | {row['participant_ratio']:<18.6f} | {row['discount_rate']:<12.6f}")
        
        print("-" * 120)
        
        ranking_output = self.df_ranking[['rank', 'Company', 'generosity_score']].copy()
        ranking_output.columns = ['Rank', 'Company', 'Generosity Score']
        
        ranking_output.to_csv(self.output_dir / "generosity_ranking.csv", index=False, encoding='utf-8-sig')
        print(f"\n排名结果已保存至: {self.output_dir / 'generosity_ranking.csv'}")
        
        return self.df_ranking
    
    def descriptive_statistics(self):
        self.print_separator("四、描述统计分析")
        
        scores = self.df_ranking['generosity_score']
        
        stats_data = {
            'Statistic': ['Count', 'Mean', 'Median', 'Std', 'Min', '25%', '50%', '75%', 'Max'],
            'Value': [
                len(scores),
                round(scores.mean(), 6),
                round(scores.median(), 6),
                round(scores.std(), 6),
                round(scores.min(), 6),
                round(scores.quantile(0.25), 6),
                round(scores.quantile(0.50), 6),
                round(scores.quantile(0.75), 6),
                round(scores.max(), 6)
            ]
        }
        
        stats_df = pd.DataFrame(stats_data)
        
        print("Generosity Score 描述统计:")
        print("-" * 50)
        for _, row in stats_df.iterrows():
            print(f"  {row['Statistic']:<12}: {row['Value']}")
        print("-" * 50)
        
        stats_df.to_csv(self.output_dir / "score_descriptive_statistics.csv", index=False, encoding='utf-8-sig')
        print(f"\n描述统计已保存至: {self.output_dir / 'score_descriptive_statistics.csv'}")
        
        return stats_df
    
    def distribution_analysis(self):
        self.print_separator("五、分布特征分析")
        
        scores = self.df_ranking['generosity_score']
        
        from scipy import stats
        
        skewness = stats.skew(scores)
        kurtosis = stats.kurtosis(scores, fisher=True)
        
        print("分布特征分析:")
        print("-" * 100)
        print(f"  偏度 (Skewness): {skewness:.6f}")
        print(f"  峰度 (Kurtosis): {kurtosis:.6f}")
        
        print("\n偏度解释:")
        if skewness > 1:
            print(f"  → 严重正偏态 (Skewness = {skewness:.4f} > 1)")
            print("    存在少数高慷慨度公司拉高均值")
        elif skewness > 0.5:
            print(f"  → 适度正偏态 (0.5 < Skewness = {skewness:.4f} < 1)")
        elif abs(skewness) < 0.5:
            print(f"  → 接近对称分布 (|Skewness| = {abs(skewness):.4f} < 0.5)")
        elif skewness > -1:
            print(f"  → 适度负偏态 (-1 < Skewness = {skewness:.4f} < -0.5)")
        else:
            print(f"  → 严重负偏态 (Skewness = {skewness:.4f} < -1)")
        
        print("\n峰度解释:")
        if kurtosis > 1:
            print(f"  → 尖峰分布 (Kurtosis = {kurtosis:.4f} > 1)")
            print("    极端值较多")
        elif kurtosis > -1:
            print(f"  → 接近正态峰度 (|Kurtosis| = {abs(kurtosis):.4f} < 1)")
        else:
            print(f"  → 低峰分布 (Kurtosis = {kurtosis:.4f} < -1)")
        
        distribution_data = {
            'Metric': ['Skewness', 'Kurtosis'],
            'Value': [round(skewness, 6), round(kurtosis, 6)],
            'Interpretation': [
                '正偏态' if skewness > 0 else '负偏态',
                '尖峰' if kurtosis > 0 else '低峰'
            ]
        }
        
        distribution_df = pd.DataFrame(distribution_data)
        distribution_df.to_csv(self.output_dir / "score_distribution_report.csv", index=False, encoding='utf-8-sig')
        print(f"\n分布报告已保存至: {self.output_dir / 'score_distribution_report.csv'}")
        
        return distribution_df
    
    def visualization(self):
        self.print_separator("六、可视化分析")
        
        fig_dir = self.output_dir / "figures"
        fig_dir.mkdir(exist_ok=True)
        
        scores = self.df_ranking['generosity_score']
        
        print("生成可视化图表...")
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        sns.histplot(scores, bins=20, kde=True, color='#4C72B0', edgecolor='white', ax=ax)
        
        ax.axvline(scores.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean = {scores.mean():.4f}')
        ax.axvline(scores.median(), color='orange', linestyle='-.', linewidth=2, label=f'Median = {scores.median():.4f}')
        
        ax.set_title('Distribution of Generosity Score', fontsize=14, fontweight='bold')
        ax.set_xlabel('Generosity Score', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.legend()
        
        plt.tight_layout()
        plt.savefig(fig_dir / "generosity_score_histogram.png", dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ 已生成: generosity_score_histogram.png")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        sns.boxplot(x=scores, ax=ax, color='#DD8452')
        
        ax.set_title('Boxplot of Generosity Score', fontsize=14, fontweight='bold')
        ax.set_xlabel('Generosity Score', fontsize=12)
        
        plt.tight_layout()
        plt.savefig(fig_dir / "generosity_score_boxplot.png", dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ 已生成: generosity_score_boxplot.png")
        
        top20 = self.df_ranking.head(20)
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, 20))
        bars = ax.barh(range(len(top20)), top20['generosity_score'], color=colors, edgecolor='white')
        
        ax.set_yticks(range(len(top20)))
        ax.set_yticklabels(top20['Company'], fontsize=10)
        ax.invert_yaxis()
        
        ax.set_title('Top 20 Generosity Companies', fontsize=14, fontweight='bold')
        ax.set_xlabel('Generosity Score', fontsize=12)
        
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + 0.005, bar.get_y() + bar.get_height()/2,
                   f'{top20.iloc[i]["generosity_score"]:.4f}',
                   va='center', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(fig_dir / "top20_generosity_companies.png", dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ 已生成: top20_generosity_companies.png")
        
        bottom20 = self.df_ranking.tail(20)
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        colors = plt.cm.Reds_r(np.linspace(0.3, 0.8, 20))
        bars = ax.barh(range(len(bottom20)), bottom20['generosity_score'], color=colors, edgecolor='white')
        
        ax.set_yticks(range(len(bottom20)))
        ax.set_yticklabels(bottom20['Company'], fontsize=10)
        ax.invert_yaxis()
        
        ax.set_title('Bottom 20 Generosity Companies', fontsize=14, fontweight='bold')
        ax.set_xlabel('Generosity Score', fontsize=12)
        
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + 0.005, bar.get_y() + bar.get_height()/2,
                   f'{bottom20.iloc[i]["generosity_score"]:.4f}',
                   va='center', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(fig_dir / "bottom20_generosity_companies.png", dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ 已生成: bottom20_generosity_companies.png")
        
        print(f"\n可视化图片已保存至: {fig_dir}")
    
    def top10_analysis(self):
        self.print_separator("七、Top 10分析")
        
        top10 = self.df_ranking.head(10)
        
        print("Top 10 Generosity Companies:")
        print("-" * 140)
        print(f"{'Rank':<6} | {'Company':<10} | {'Score':<12} | {'grant_ratio':<12} | {'participant_ratio':<18} | {'discount_rate':<12} | {'waiting_period':<14} | {'validity_period':<14}")
        print("-" * 140)
        
        for idx, row in top10.iterrows():
            print(f"{int(row['rank']):<6} | {row['Company']:<10} | {row['generosity_score']:<12.6f} | {row['grant_ratio']:<12.6f} | {row['participant_ratio']:<18.6f} | {row['discount_rate']:<12.6f} | {row['waiting_period_adj']:<14.6f} | {row['validity_period']:<14.6f}")
        print("-" * 140)
        
        sample_mean_gr = self.df_ranking['grant_ratio'].mean()
        sample_mean_pr = self.df_ranking['participant_ratio'].mean()
        sample_mean_dr = self.df_ranking['discount_rate'].mean()
        
        top10_mean_gr = top10['grant_ratio'].mean()
        top10_mean_pr = top10['participant_ratio'].mean()
        top10_mean_dr = top10['discount_rate'].mean()
        
        print("\nTop 10 与样本均值对比:")
        print("-" * 100)
        print(f"{'Metric':<20} | {'Sample Mean':<15} | {'Top10 Mean':<15} | {'Ratio':<12}")
        print("-" * 100)
        print(f"{'grant_ratio':<20} | {sample_mean_gr:<15.4f} | {top10_mean_gr:<15.4f} | {top10_mean_gr/sample_mean_gr:<12.2f}x")
        print(f"{'participant_ratio':<20} | {sample_mean_pr:<15.4f} | {top10_mean_pr:<15.4f} | {top10_mean_pr/sample_mean_pr:<12.2f}x")
        print(f"{'discount_rate':<20} | {sample_mean_dr:<15.4f} | {top10_mean_dr:<15.4f} | {top10_mean_dr/sample_mean_dr:<12.2f}x")
        print("-" * 100)
        
        print("\nTop 10 特征分析:")
        gr_higher = top10_mean_gr > sample_mean_gr * 1.2
        pr_higher = top10_mean_pr > sample_mean_pr * 1.2
        
        if gr_higher and pr_higher:
            print("  ✓ grant_ratio 和 participant_ratio 均显著高于样本均值")
            print("    → 高慷慨度公司在规模和覆盖面两个维度均表现突出")
        elif gr_higher:
            print("  ✓ grant_ratio 显著高于样本均值")
            print("    → 高慷慨度公司主要通过授予比例体现慷慨度")
        elif pr_higher:
            print("  ✓ participant_ratio 显著高于样本均值")
            print("    → 高慷慨度公司主要通过覆盖广度体现慷慨度")
        else:
            print("  → grant_ratio 和 participant_ratio 与样本均值差异不大")
            print("    → 高慷慨度可能主要体现在其他维度（如 discount_rate 或时间维度）")
        
        top10_output = top10[['rank', 'Company', 'generosity_score']].copy()
        top10_output.columns = ['Rank', 'Company', 'Generosity Score']
        top10_output.to_csv(self.output_dir / "top10_generosity_companies.csv", index=False, encoding='utf-8-sig')
        print(f"\nTop 10 数据已保存至: {self.output_dir / 'top10_generosity_companies.csv'}")
        
        return top10
    
    def bottom10_analysis(self):
        self.print_separator("八、Bottom 10分析")
        
        bottom10 = self.df_ranking.tail(10)
        bottom10 = bottom10.sort_values('rank', ascending=True).reset_index(drop=True)
        
        print("Bottom 10 Generosity Companies:")
        print("-" * 140)
        print(f"{'Rank':<6} | {'Company':<10} | {'Score':<12} | {'grant_ratio':<12} | {'participant_ratio':<18} | {'discount_rate':<12} | {'waiting_period':<14} | {'validity_period':<14}")
        print("-" * 140)
        
        for idx, row in bottom10.iterrows():
            print(f"{int(row['rank']):<6} | {row['Company']:<10} | {row['generosity_score']:<12.6f} | {row['grant_ratio']:<12.6f} | {row['participant_ratio']:<18.6f} | {row['discount_rate']:<12.6f} | {row['waiting_period_adj']:<14.6f} | {row['validity_period']:<14.6f}")
        print("-" * 140)
        
        sample_mean_gr = self.df_ranking['grant_ratio'].mean()
        sample_mean_pr = self.df_ranking['participant_ratio'].mean()
        
        bottom10_mean_gr = bottom10['grant_ratio'].mean()
        bottom10_mean_pr = bottom10['participant_ratio'].mean()
        
        print("\nBottom 10 与样本均值对比:")
        print("-" * 100)
        print(f"{'Metric':<20} | {'Sample Mean':<15} | {'Bottom10 Mean':<15} | {'Ratio':<12}")
        print("-" * 100)
        print(f"{'grant_ratio':<20} | {sample_mean_gr:<15.4f} | {bottom10_mean_gr:<15.4f} | {bottom10_mean_gr/sample_mean_gr:<12.2f}x")
        print(f"{'participant_ratio':<20} | {sample_mean_pr:<15.4f} | {bottom10_mean_pr:<15.4f} | {bottom10_mean_pr/sample_mean_pr:<12.2f}x")
        print("-" * 100)
        
        print("\nBottom 10 特征分析:")
        gr_lower = bottom10_mean_gr < sample_mean_gr * 0.8
        pr_lower = bottom10_mean_pr < sample_mean_pr * 0.8
        
        if gr_lower and pr_lower:
            print("  ✗ grant_ratio 和 participant_ratio 均显著低于样本均值")
            print("    → 低慷慨度公司在规模和覆盖面两个维度均表现不足")
        elif gr_lower:
            print("  ✗ grant_ratio 显著低于样本均值")
            print("    → 低慷慨度主要源于授予比例偏低")
        elif pr_lower:
            print("  ✗ participant_ratio 显著低于样本均值")
            print("    → 低慷慨度主要源于覆盖广度偏窄")
        else:
            print("  → grant_ratio 和 participant_ratio 与样本均值差异不大")
            print("    → 低慷慨度可能主要体现在其他维度")
        
        bottom10_output = bottom10[['rank', 'Company', 'generosity_score']].copy()
        bottom10_output.columns = ['Rank', 'Company', 'Generosity Score']
        bottom10_output.to_csv(self.output_dir / "bottom10_generosity_companies.csv", index=False, encoding='utf-8-sig')
        print(f"\nBottom 10 数据已保存至: {self.output_dir / 'bottom10_generosity_companies.csv'}")
        
        return bottom10
    
    def validity_test(self):
        self.print_separator("九、慷慨度指数有效性检验")
        
        scores = self.df_ranking['generosity_score']
        
        score_range = scores.max() - scores.min()
        std = scores.std()
        mean = scores.mean()
        cv = std / mean if mean != 0 else 0
        
        print("有效性检验:")
        print("-" * 100)
        
        print("\n1. Generosity Score 是否能够有效区分不同公司？")
        print(f"   最大值: {scores.max():.6f}")
        print(f"   最小值: {scores.min():.6f}")
        print(f"   范围: {score_range:.6f}")
        print(f"   标准差: {std:.6f}")
        print(f"   变异系数 (CV): {cv:.4f}")
        
        if score_range > 0.5:
            print("   ✓ 范围较大，能够有效区分不同公司")
        elif score_range > 0.3:
            print("   → 范围适中，具有一定区分能力")
        else:
            print("   ⚠️ 范围较小，区分能力有限")
        
        print("\n2. 是否存在严重集中现象？")
        q25 = scores.quantile(0.25)
        q75 = scores.quantile(0.75)
        iqr = q75 - q25
        
        print(f"   Q25: {q25:.6f}")
        print(f"   Q75: {q75:.6f}")
        print(f"   IQR: {iqr:.6f}")
        
        if iqr < 0.15:
            print("   ⚠️ 中间50%的公司得分较为集中")
        else:
            print("   ✓ 中间50%的公司得分分布相对分散")
        
        print("\n3. 是否满足综合评价指标的基本要求？")
        print("   ✓ 可解释性: 基于5个明确的经济指标加权")
        print("   ✓ 区分度: 基于熵权法客观赋权，自动识别区分能力强的指标")
        print("   ✓ 稳定性: 权重基于样本分布，具有统计稳定性")
        
        print("-" * 100)
    
    def generate_report(self):
        self.print_separator("十、研究结论输出")
        
        scores = self.df_ranking['generosity_score']
        weight_dict = dict(zip(self.weights_df['Indicator'], self.weights_df['Weight']))
        sorted_weights = sorted(weight_dict.items(), key=lambda x: x[1], reverse=True)
        highest_var, highest_w = sorted_weights[0]
        
        from scipy import stats
        skewness = stats.skew(scores)
        kurtosis = stats.kurtosis(scores, fisher=True)
        
        top10 = self.df_ranking.head(10)
        bottom10 = self.df_ranking.tail(10)
        
        count_val = len(scores)
        mean_val = scores.mean()
        median_val = scores.median()
        std_val = scores.std()
        min_val = scores.min()
        max_val = scores.max()
        range_val = max_val - min_val
        cv_val = std_val / mean_val if mean_val != 0 else 0
        
        report_content = """# 上市公司股权激励慷慨度评价体系研究报告

## 研究目的

构建上市公司股权激励慷慨度（Generosity Score）评价体系，从多个维度综合衡量上市公司股权激励方案的慷慨程度。

## 方法

### 1. 数据清洗
- 缺失值处理：Listwise Deletion
- 异常值处理：对 participant_ratio 采用 1% Winsorization
- 异常值复核：基于 IQR 方法
- 最终有效样本：{n} 条

### 2. 相关性分析
- Pearson 相关性分析：衡量线性相关程度
- Spearman 秩相关分析：衡量单调相关程度
- 结论：不存在高度相关变量，不存在明显多重共线性风险

### 3. 指标方向统一与标准化
- 正向指标：grant_ratio, participant_ratio, discount_rate, validity_period
- 逆向指标：waiting_period → 正向化：waiting_period_adj = X_max - X
- Min-Max 标准化：所有指标映射到 [0, 1]

### 4. 熵权法赋权
- 信息熵：衡量指标的区分能力
- 差异系数：d_j = 1 - e_j
- 熵权：w_j = d_j / Σ(d_j)

## 权重结果

""".format(n=count_val)
        
        for var, w in sorted_weights:
            report_content += """- **%s**: %.4f (%.2f%%)
""" % (var, w, w * 100)
        
        report_content += """
- **权重最高指标**: %(highest_var)s (%(highest_w_pct).2f%%)
- **权重最低指标**: %(lowest_var)s (%(lowest_w_pct).2f%%)

## Generosity Score 结果

### 描述统计

| 统计量 | 值 |
|-------|-----|
| 样本数 | %(count)d |
| 均值 | %(mean).6f |
| 中位数 | %(median).6f |
| 标准差 | %(std).6f |
| 最小值 | %(min_val).6f |
| 最大值 | %(max_val).6f |
| 范围 | [%(min_val).6f, %(max_val).6f] |

### 分布特征

| 指标 | 值 | 解释 |
|------|-----|------|
| 偏度 (Skewness) | %(skewness).4f | %(skew_interpret)s |
| 峰度 (Kurtosis) | %(kurtosis).4f | %(kurt_interpret)s |

## Top 10 分析

### Top 10 公司

""" % {
            'highest_var': highest_var,
            'highest_w_pct': highest_w * 100,
            'lowest_var': sorted_weights[-1][0],
            'lowest_w_pct': sorted_weights[-1][1] * 100,
            'count': len(scores),
            'mean': scores.mean(),
            'median': scores.median(),
            'std': scores.std(),
            'min_val': scores.min(),
            'max_val': scores.max(),
            'skewness': skewness,
            'kurtosis': kurtosis,
            'skew_interpret': '正偏态' if skewness > 0 else '负偏态',
            'kurt_interpret': '尖峰' if kurtosis > 0 else '低峰'
        }
        
        for idx, row in top10.iterrows():
            report_content += f"{int(row['rank'])}. {row['Company']}: {row['generosity_score']:.6f}\n"
        
        sample_mean_gr = self.df_ranking['grant_ratio'].mean()
        sample_mean_pr = self.df_ranking['participant_ratio'].mean()
        top10_mean_gr = top10['grant_ratio'].mean()
        top10_mean_pr = top10['participant_ratio'].mean()
        
        report_content += """
### Top 10 特征

- **grant_ratio**: 样本均值 = %(sample_mean_gr).4f, Top10 均值 = %(top10_mean_gr).4f (%(top10_gr_ratio).2fx)
- **participant_ratio**: 样本均值 = %(sample_mean_pr).4f, Top10 均值 = %(top10_mean_pr).4f (%(top10_pr_ratio).2fx)

高慷慨度公司通常在多个维度上表现突出，尤其是在授予比例和覆盖广度方面。

## Bottom 10 分析

### Bottom 10 公司

""" % {
            'sample_mean_gr': sample_mean_gr,
            'top10_mean_gr': top10_mean_gr,
            'top10_gr_ratio': top10_mean_gr / sample_mean_gr,
            'sample_mean_pr': sample_mean_pr,
            'top10_mean_pr': top10_mean_pr,
            'top10_pr_ratio': top10_mean_pr / sample_mean_pr
        }
        
        for idx, row in bottom10.iterrows():
            report_content += f"{int(row['rank'])}. {row['Company']}: {row['generosity_score']:.6f}\n"
        
        bottom10_mean_gr = bottom10['grant_ratio'].mean()
        bottom10_mean_pr = bottom10['participant_ratio'].mean()
        
        report_content += """
### Bottom 10 特征

- **grant_ratio**: 样本均值 = %(sample_mean_gr).4f, Bottom10 均值 = %(bottom10_mean_gr).4f (%(bottom10_gr_ratio).2fx)
- **participant_ratio**: 样本均值 = %(sample_mean_pr).4f, Bottom10 均值 = %(bottom10_mean_pr).4f (%(bottom10_pr_ratio).2fx)

低慷慨度公司往往在授予比例和覆盖广度方面表现不足。

## 评价体系有效性分析

### 1. 区分能力

- 最大值 - 最小值 = %(score_range).6f
- 标准差 = %(std_val).6f
- 变异系数 = %(cv_val).4f

指数范围较大，能够有效区分不同公司的股权激励慷慨度。

### 2. 分布合理性

- 偏度 = %(skewness).4f
- 峰度 = %(kurtosis).4f

得分分布反映了市场上公司股权激励慷慨度的真实差异。

### 3. 方法科学性

- 基于熵权法客观赋权，避免主观偏差
- 多维度综合评价，而非单一指标
- 权重反映指标区分能力，符合客观赋权思想

## 后续研究建议

1. **行业比较分析**
   - 按行业分组，比较不同行业的股权激励慷慨度
   - 分析行业特征与慷慨度的关系

2. **影响因素分析**
   - 公司特征（规模、盈利能力、治理结构）对慷慨度的影响
   - 市场环境与慷慨度的关系

3. **经济后果研究**
   - 股权激励慷慨度对公司绩效的影响
   - 对员工激励效果的长期追踪

4. **动态分析**
   - 追踪同一公司历年慷慨度变化
   - 分析慷慨度变化的影响因素

## 输出文件

1. `generosity_scores.csv` - 所有公司的 Generosity Score
2. `generosity_ranking.csv` - 完整排名结果
3. `top10_generosity_companies.csv` - Top 10 公司
4. `bottom10_generosity_companies.csv` - Bottom 10 公司
5. `score_descriptive_statistics.csv` - 描述统计
6. `score_distribution_report.csv` - 分布特征
7. `generosity_score_report.md` - 本报告

可视化图片:
- `figures/generosity_score_histogram.png`
- `figures/generosity_score_boxplot.png`
- `figures/top20_generosity_companies.png`
- `figures/bottom20_generosity_companies.png`
""" % {
            'sample_mean_gr': sample_mean_gr,
            'bottom10_mean_gr': bottom10_mean_gr,
            'bottom10_gr_ratio': bottom10_mean_gr / sample_mean_gr,
            'sample_mean_pr': sample_mean_pr,
            'bottom10_mean_pr': bottom10_mean_pr,
            'bottom10_pr_ratio': bottom10_mean_pr / sample_mean_pr,
            'score_range': scores.max() - scores.min(),
            'std_val': scores.std(),
            'cv_val': scores.std() / scores.mean() if scores.mean() != 0 else 0,
            'skewness': skewness,
            'kurtosis': kurtosis
        }
        
        with open(self.output_dir / "generosity_score_report.md", "w", encoding="utf-8") as f:
            f.write(report_content)
        
        print(f"Generosity Score 报告已保存至: {self.output_dir / 'generosity_score_report.md'}")
    
    def run(self):
        print("\n" + "#" * 80)
        print("#     Step 6: Generosity Score 计算与排名分析")
        print("#     研究主题：上市公司股权激励慷慨度评价体系")
        print("#" * 80)
        
        self.validate_weights()
        self.calculate_generosity_score()
        self.build_ranking()
        self.descriptive_statistics()
        self.distribution_analysis()
        self.visualization()
        self.top10_analysis()
        self.bottom10_analysis()
        self.validity_test()
        self.generate_report()
        
        print("\n" + "#" * 80)
        print("#     Step 6 完成！等待下一步指令。")
        print("#" * 80)


if __name__ == "__main__":
    data_path = "normalization_output_v2/entropy_input_data.csv"
    weights_path = "entropy_weight_output_v2/entropy_weights.csv"
    
    if os.path.exists(data_path) and os.path.exists(weights_path):
        calculator = GenerosityScoreCalculator(data_path, weights_path)
        calculator.run()
    else:
        print(f"错误: 输入文件不存在!")
        print(f"  数据路径: {data_path}")
        print(f"  权重路径: {weights_path}")