#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 6 修正版：恢复公司信息并重新生成排名结果
研究主题：构建上市公司股权激励慷慨度（Generosity Score）评价体系

目标：
1. 从 cleaned_equity_incentive_data.csv 提取 company_name 和 stock_code
2. 与 generosity_scores.csv 按原样本顺序合并
3. 重新生成带真实公司名称和股票代码的排名结果

注意：
- 不重新计算标准化
- 不重新计算熵权法
- 不重新计算权重
- 仅恢复公司身份信息并重新输出排名结果
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

class RankingRegenerator:
    def __init__(self, output_dir: str = "ranking_final_output_v2"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.cleaned_data_path = "data_cleaning_output_v3/cleaned_equity_incentive_data.csv"
        self.scores_path = "generosity_score_output_v2/generosity_scores.csv"
        self.ranking_path = "generosity_score_output_v2/generosity_ranking.csv"
        
        print(f"输出目录: {output_dir}")
    
    def print_separator(self, title: str):
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80 + "\n")
    
    def load_and_merge_data(self):
        self.print_separator("一、恢复公司识别信息")
        
        print("读取原始数据文件...")
        
        df_cleaned = pd.read_csv(self.cleaned_data_path, encoding='utf-8-sig')
        df_scores = pd.read_csv(self.scores_path, encoding='utf-8-sig')
        
        print(f"cleaned_equity_incentive_data.csv: {len(df_cleaned)} 条记录")
        print(f"generosity_scores.csv: {len(df_scores)} 条记录")
        
        print("\n提取公司识别字段...")
        df_company_info = df_cleaned[['company_name', 'stock_code', 'grant_ratio', 'participant_ratio', 'discount_rate', 'waiting_period', 'validity_period']].copy()
        df_company_info['idx'] = df_company_info.index
        
        print(f"\n公司信息字段: {list(df_company_info.columns)}")
        print("前5条记录:")
        for idx, row in df_company_info.head().iterrows():
            print(f"  {idx+1}. {row['company_name']} ({row['stock_code']})")
        
        print("\n合并公司信息与Generosity Score...")
        
        df_merged = pd.concat([df_company_info, df_scores], axis=1)
        
        print(f"合并后字段: {list(df_merged.columns)}")
        print(f"合并后记录数: {len(df_merged)}")
        
        if len(df_merged) == len(df_cleaned) == len(df_scores):
            print("✓ 样本数一致，合并成功！")
        else:
            print("⚠️ 样本数不一致，请注意！")
        
        self.df_merged = df_merged
        
        return df_merged
    
    def generate_final_scores(self):
        self.print_separator("二、重新生成评分结果")
        
        df_scores_final = self.df_merged[['company_name', 'stock_code', 'generosity_score']].copy()
        df_scores_final.columns = ['company_name', 'stock_code', 'Generosity Score']
        
        print("generosity_scores_final.csv 格式:")
        print("-" * 80)
        print(f"{'company_name':<20} | {'stock_code':<12} | {'Generosity Score':<15}")
        print("-" * 80)
        
        for idx, row in df_scores_final.head(10).iterrows():
            print(f"{row['company_name']:<20} | {row['stock_code']:<12} | {row['Generosity Score']:<15.6f}")
        
        print("-" * 80)
        
        df_scores_final.to_csv(self.output_dir / "generosity_scores_final.csv", index=False, encoding='utf-8-sig')
        print(f"\n已保存至: {self.output_dir / 'generosity_scores_final.csv'}")
        
        return df_scores_final
    
    def generate_final_ranking(self):
        self.print_separator("三、重新生成完整排名")
        
        df_ranking_final = self.df_merged.sort_values('generosity_score', ascending=False).reset_index(drop=True)
        df_ranking_final['Rank'] = df_ranking_final.index + 1
        
        df_ranking_export = df_ranking_final[['Rank', 'stock_code', 'company_name', 'generosity_score']].copy()
        df_ranking_export.columns = ['Rank', 'stock_code', 'company_name', 'Generosity Score']
        
        print("完整排名预览（Top 20）:")
        print("-" * 100)
        print(f"{'Rank':<6} | {'stock_code':<12} | {'company_name':<20} | {'Generosity Score':<15}")
        print("-" * 100)
        
        for idx, row in df_ranking_final.head(20).iterrows():
            print(f"{int(row['Rank']):<6} | {str(row['stock_code']):<12} | {row['company_name']:<20} | {row['generosity_score']:<15.6f}")
        
        print("-" * 100)
        
        df_ranking_export.to_csv(self.output_dir / "generosity_ranking_final.csv", index=False, encoding='utf-8-sig')
        print(f"\n已保存至: {self.output_dir / 'generosity_ranking_final.csv'}")
        
        self.df_ranking = df_ranking_final
        
        return df_ranking_export
    
    def generate_top10(self):
        self.print_separator("四、重新生成Top10")
        
        df_top10 = self.df_ranking.head(10).copy()
        
        df_top10_export = df_top10[['Rank', 'stock_code', 'company_name', 'generosity_score']].copy()
        df_top10_export.columns = ['Rank', 'stock_code', 'company_name', 'Generosity Score']
        
        print("Top 10 Generosity Companies:")
        print("-" * 100)
        print(f"{'Rank':<6} | {'stock_code':<12} | {'company_name':<20} | {'Generosity Score':<15}")
        print("-" * 100)
        
        for idx, row in df_top10.iterrows():
            print(f"{int(row['Rank']):<6} | {str(row['stock_code']):<12} | {row['company_name']:<20} | {row['generosity_score']:<15.6f}")
        
        print("-" * 100)
        
        df_top10_export.to_csv(self.output_dir / "top10_generosity_companies_final.csv", index=False, encoding='utf-8-sig')
        print(f"\n已保存至: {self.output_dir / 'top10_generosity_companies_final.csv'}")
        
        self.df_top10 = df_top10
        
        return df_top10_export
    
    def generate_bottom10(self):
        self.print_separator("五、重新生成Bottom10")
        
        df_bottom10 = self.df_ranking.tail(10).copy()
        df_bottom10 = df_bottom10.sort_values('generosity_score', ascending=True).reset_index(drop=True)
        df_bottom10['Rank'] = range(len(self.df_ranking) - 9, len(self.df_ranking) + 1)
        
        df_bottom10_export = df_bottom10[['Rank', 'stock_code', 'company_name', 'generosity_score']].copy()
        df_bottom10_export.columns = ['Rank', 'stock_code', 'company_name', 'Generosity Score']
        
        print("Bottom 10 Generosity Companies:")
        print("-" * 100)
        print(f"{'Rank':<6} | {'stock_code':<12} | {'company_name':<20} | {'Generosity Score':<15}")
        print("-" * 100)
        
        for idx, row in df_bottom10.iterrows():
            print(f"{int(row['Rank']):<6} | {str(row['stock_code']):<12} | {row['company_name']:<20} | {row['generosity_score']:<15.6f}")
        
        print("-" * 100)
        
        df_bottom10_export.to_csv(self.output_dir / "bottom10_generosity_companies_final.csv", index=False, encoding='utf-8-sig')
        print(f"\n已保存至: {self.output_dir / 'bottom10_generosity_companies_final.csv'}")
        
        self.df_bottom10 = df_bottom10
        
        return df_bottom10_export
    
    def analyze_top10_features(self):
        self.print_separator("六、Top10公司分析")
        
        print("Top10公司各指标均值与全样本对比:")
        print("-" * 120)
        print(f"{'指标':<15} | {'全样本均值':<15} | {'Top10均值':<15} | {'倍数':<10} | {'结论':<20}")
        print("-" * 120)
        
        metrics = ['grant_ratio', 'participant_ratio', 'discount_rate', 'validity_period']
        
        analysis_data = []
        
        for metric in metrics:
            sample_mean = self.df_merged[metric].mean()
            top10_mean = self.df_top10[metric].mean()
            ratio = top10_mean / sample_mean if sample_mean != 0 else 0
            
            if ratio > 1.5:
                conclusion = "显著高于"
            elif ratio > 1.2:
                conclusion = "高于"
            elif ratio > 0.8:
                conclusion = "接近"
            else:
                conclusion = "低于"
            
            analysis_data.append({
                '指标': metric,
                '全样本均值': round(sample_mean, 4),
                'Top10均值': round(top10_mean, 4),
                '倍数': round(ratio, 2),
                '结论': conclusion
            })
            
            print(f"{metric:<15} | {sample_mean:<15.4f} | {top10_mean:<15.4f} | {ratio:<10.2f}x | {conclusion:<20}")
        
        print("-" * 120)
        
        print("\nTop10公司排名靠前的原因分析:")
        
        high_gr = analysis_data[0]['倍数'] > 1.2
        high_pr = analysis_data[1]['倍数'] > 1.2
        high_dr = analysis_data[2]['倍数'] > 1.2
        high_vp = analysis_data[3]['倍数'] > 1.2
        
        if high_pr and high_gr:
            print("  ✓ participant_ratio 和 grant_ratio 均显著高于样本均值")
            print("    → 高慷慨度公司在**覆盖广度**和**授予规模**两个核心维度均表现突出")
            print("    → 既让更多员工参与，又给予较高的授予比例")
        elif high_pr:
            print("  ✓ participant_ratio 显著高于样本均值")
            print("    → 高慷慨度主要体现在**覆盖广度**上")
            print("    → 公司倾向于让更多员工分享股权激励")
        elif high_gr:
            print("  ✓ grant_ratio 显著高于样本均值")
            print("    → 高慷慨度主要体现在**授予规模**上")
            print("    → 公司倾向于给予较高的授予比例")
        else:
            print("  → 主要优势体现在其他维度（如时间维度）")
        
        if high_dr:
            print("  ✓ discount_rate 也高于样本均值")
            print("    → 定价优惠也是高慷慨度的重要表现")
        
        return analysis_data
    
    def analyze_bottom10_features(self):
        self.print_separator("七、Bottom10公司分析")
        
        print("Bottom10公司各指标均值与全样本对比:")
        print("-" * 120)
        print(f"{'指标':<15} | {'全样本均值':<15} | {'Bottom10均值':<15} | {'倍数':<10} | {'结论':<20}")
        print("-" * 120)
        
        metrics = ['grant_ratio', 'participant_ratio', 'discount_rate', 'validity_period']
        
        analysis_data = []
        
        for metric in metrics:
            sample_mean = self.df_merged[metric].mean()
            bottom10_mean = self.df_bottom10[metric].mean()
            ratio = bottom10_mean / sample_mean if sample_mean != 0 else 0
            
            if ratio < 0.5:
                conclusion = "显著低于"
            elif ratio < 0.8:
                conclusion = "低于"
            elif ratio > 1.2:
                conclusion = "高于"
            else:
                conclusion = "接近"
            
            analysis_data.append({
                '指标': metric,
                '全样本均值': round(sample_mean, 4),
                'Bottom10均值': round(bottom10_mean, 4),
                '倍数': round(ratio, 2),
                '结论': conclusion
            })
            
            print(f"{metric:<15} | {sample_mean:<15.4f} | {bottom10_mean:<15.4f} | {ratio:<10.2f}x | {conclusion:<20}")
        
        print("-" * 120)
        
        print("\nBottom10公司排名靠后的原因分析:")
        
        low_gr = analysis_data[0]['倍数'] < 0.8
        low_pr = analysis_data[1]['倍数'] < 0.8
        
        if low_pr and low_gr:
            print("  ✗ participant_ratio 和 grant_ratio 均显著低于样本均值")
            print("    → 低慷慨度公司在**覆盖广度**和**授予规模**两个核心维度均表现不足")
            print("    → 参与员工少，授予比例也低")
        elif low_pr:
            print("  ✗ participant_ratio 显著低于样本均值")
            print("    → 低慷慨度主要源于**覆盖广度偏窄**")
            print("    → 只有少数员工能参与股权激励")
        elif low_gr:
            print("  ✗ grant_ratio 显著低于样本均值")
            print("    → 低慷慨度主要源于**授予比例偏低**")
            print("    → 股权激励的相对规模较小")
        else:
            print("  → 主要不足体现在其他维度")
        
        return analysis_data
    
    def generate_report(self):
        self.print_separator("八、输出研究结果")
        
        n = len(self.df_merged)
        mean_score = self.df_merged['generosity_score'].mean()
        std_score = self.df_merged['generosity_score'].std()
        min_score = self.df_merged['generosity_score'].min()
        max_score = self.df_merged['generosity_score'].max()
        
        report_content = """# 股权激励慷慨度排名分析报告

## 研究背景

基于熵权法客观赋权，构建上市公司股权激励慷慨度评价体系，从5个维度综合衡量上市公司股权激励方案的慷慨程度。

## 评价指标

| 指标 | 方向 | 权重 | 说明 |
|------|------|------|------|
| participant_ratio | 正向 | 52.75% | 参与比例（覆盖广度） |
| grant_ratio | 正向 | 40.70% | 授予比例（相对规模） |
| validity_period | 正向 | 3.52% | 有效期（时间跨度） |
| waiting_period_adj | 正向 | 1.55% | 等待期（时间约束，已正向化） |
| discount_rate | 正向 | 1.48% | 折扣率（定价优惠） |

## Generosity Score 统计

| 统计量 | 值 |
|--------|-----|
| 样本数 | {n} |
| 均值 | {mean_score:.6f} |
| 标准差 | {std_score:.6f} |
| 最小值 | {min_score:.6f} |
| 最大值 | {max_score:.6f} |
| 范围 | [{min_score:.6f}, {max_score:.6f}] |

## Top 10 慷慨度公司

""".format(n=n, mean_score=mean_score, std_score=std_score, min_score=min_score, max_score=max_score)
        
        for idx, row in self.df_top10.iterrows():
            report_content += f"{int(row['Rank'])}. **{row['company_name']}** ({row['stock_code']}): {row['generosity_score']:.6f}\n"
        
        report_content += """
## Bottom 10 慷慨度公司

"""
        
        for idx, row in self.df_bottom10.iterrows():
            report_content += f"{int(row['Rank'])}. **{row['company_name']}** ({row['stock_code']}): {row['generosity_score']:.6f}\n"
        
        report_content += """
## 高慷慨度公司特征

### 核心优势维度

高慷慨度公司主要在以下维度表现突出：

1. **参与比例 (participant_ratio)**
   - 覆盖更多员工，让更多人分享股权激励
   - 体现公司的包容性和激励范围

2. **授予比例 (grant_ratio)**
   - 给予更高的授予比例
   - 体现激励的相对规模

3. **折扣率 (discount_rate)**
   - 给予更多的价格优惠
   - 体现定价慷慨度

### 经济解释

- 高慷慨度公司通常在多个维度上同时表现出色
- 不仅覆盖广，而且授予规模大
- 体现了公司对员工激励的高度重视

## 低慷慨度公司特征

### 主要不足维度

低慷慨度公司主要在以下维度表现不足：

1. **参与比例 (participant_ratio)**
   - 只有少数员工能参与股权激励
   - 覆盖范围有限

2. **授予比例 (grant_ratio)**
   - 授予比例相对较低
   - 激励规模偏小

### 经济解释

- 低慷慨度公司可能更保守，只对核心员工进行激励
- 或者公司本身规模较小，股权激励的空间有限
- 需要关注这些公司是否存在激励不足的问题

## Generosity Score 经济解释

### 评分维度

Generosity Score 综合反映了上市公司股权激励在以下维度的慷慨程度：

| 维度 | 指标 | 高值含义 |
|------|------|---------|
| 覆盖广度 | participant_ratio | 更多员工参与 |
| 授予规模 | grant_ratio | 更高的授予比例 |
| 定价优惠 | discount_rate | 更大的折扣 |
| 时间约束 | waiting_period_adj | 等待期更短 |
| 时间跨度 | validity_period | 有效期更长 |

### 实际应用

Generosity Score 可用于：

1. **公司治理评价**
   - 评估上市公司股权激励的慷慨程度
   - 识别激励充分的公司和激励不足的公司

2. **投资参考**
   - 慷慨的股权激励可能预示更好的员工激励
   - 但需综合考虑公司基本面

3. **监管参考**
   - 监控股权激励的公平性
   - 识别过度激励或激励不足的异常情况

## 输出文件

1. `generosity_scores_final.csv` - 所有公司评分（含公司名称、股票代码）
2. `generosity_ranking_final.csv` - 完整排名结果
3. `top10_generosity_companies_final.csv` - Top 10 公司
4. `bottom10_generosity_companies_final.csv` - Bottom 10 公司
5. `ranking_analysis_report.md` - 本报告
"""
        
        with open(self.output_dir / "ranking_analysis_report.md", "w", encoding="utf-8") as f:
            f.write(report_content)
        
        print(f"排名分析报告已保存至: {self.output_dir / 'ranking_analysis_report.md'}")
    
    def run(self):
        print("\n" + "#" * 80)
        print("#     Step 6 修正版：恢复公司信息并重新生成排名结果")
        print("#     研究主题：上市公司股权激励慷慨度评价体系")
        print("#" * 80)
        
        self.load_and_merge_data()
        self.generate_final_scores()
        self.generate_final_ranking()
        self.generate_top10()
        self.generate_bottom10()
        self.analyze_top10_features()
        self.analyze_bottom10_features()
        self.generate_report()
        
        print("\n" + "#" * 80)
        print("#     Step 6 修正版完成！")
        print("#" * 80)


if __name__ == "__main__":
    regenerator = RankingRegenerator()
    regenerator.run()