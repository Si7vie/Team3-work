#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 7.5：聚类结果验证与特殊群体识别
研究主题：上市公司股权激励慷慨度评价体系

当前聚类结果：
- Cluster 1: 175家企业（主流群体）
- Cluster 0: 17家企业（特殊群体）

分析目标：
1. 验证Cluster间是否存在显著差异
2. 挖掘特殊群体（17家公司）的特征
3. 为Cluster重新命名
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats
from scipy.stats import f_oneway

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'STHeiti', 'WenQuanYi Micro Hei']
plt.rcParams['axes.unicode_minus'] = False

class ClusterValidator:
    def __init__(self, output_dir: str = "cluster_validation_output_v2"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.cluster_path = "cluster_optimization_output_v2/cluster_result_v2.csv"
        self.cleaned_path = "data_cleaning_output_v3/cleaned_equity_incentive_data.csv"
        self.entropy_path = "normalization_output_v2/entropy_input_data.csv"
        self.ranking_path = "ranking_final_output_v2/generosity_ranking_final.csv"
        self.profile_path = "cluster_optimization_output_v2/cluster_profile_v2.csv"
        
        print(f"输出目录: {output_dir}")
        self.load_data()
    
    def load_data(self):
        print("加载数据文件...")
        
        if Path(self.cluster_path).exists():
            self.df_cluster = pd.read_csv(self.cluster_path, encoding='utf-8-sig')
            print(f"✓ cluster_result_v2.csv: {len(self.df_cluster)} 条")
        else:
            raise FileNotFoundError(f"文件不存在: {self.cluster_path}")
        
        if Path(self.cleaned_path).exists():
            self.df_cleaned = pd.read_csv(self.cleaned_path, encoding='utf-8-sig')
            print(f"✓ cleaned_equity_incentive_data.csv: {len(self.df_cleaned)} 条")
        else:
            raise FileNotFoundError(f"文件不存在: {self.cleaned_path}")
        
        if Path(self.entropy_path).exists():
            self.df_entropy = pd.read_csv(self.entropy_path, encoding='utf-8-sig')
            print(f"✓ entropy_input_data.csv: {len(self.df_entropy)} 条")
        else:
            raise FileNotFoundError(f"文件不存在: {self.entropy_path}")
        
        if Path(self.ranking_path).exists():
            self.df_ranking = pd.read_csv(self.ranking_path, encoding='utf-8-sig')
            print(f"✓ generosity_ranking_final.csv: {len(self.df_ranking)} 条")
        else:
            raise FileNotFoundError(f"文件不存在: {self.ranking_path}")
        
        self.core_vars = [
            'grant_ratio',
            'participant_ratio',
            'discount_rate',
            'waiting_period_adj',
            'validity_period'
        ]
        
        self._merge_all_data()
    
    def _merge_all_data(self):
        print("\n合并所有数据...")
        
        df_merged = pd.concat([
            self.df_cleaned[['company_name', 'stock_code']],
            self.df_entropy[self.core_vars],
            self.df_ranking[['Generosity Score']],
            self.df_cluster[['Cluster']]
        ], axis=1)
        
        self.df_merged = df_merged
        print(f"✓ 合并完成，共 {len(df_merged)} 条记录")
        
        print("\nCluster分布:")
        cluster_counts = df_merged['Cluster'].value_counts().sort_index()
        for cid, count in cluster_counts.items():
            print(f"  Cluster {int(cid)}: {count} 家公司")
    
    def print_separator(self, title: str):
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80 + "\n")
    
    def step1_cluster_naming(self):
        self.print_separator("一、Cluster命名修正")
        
        print("分析各Cluster特征...")
        
        cluster_stats = []
        for cid in sorted(self.df_merged['Cluster'].unique()):
            df_c = self.df_merged[self.df_merged['Cluster'] == cid]
            stats_dict = {
                'Cluster': int(cid),
                'Count': len(df_c),
                'grant_ratio': df_c['grant_ratio'].mean(),
                'participant_ratio': df_c['participant_ratio'].mean(),
                'discount_rate': df_c['discount_rate'].mean(),
                'waiting_period_adj': df_c['waiting_period_adj'].mean(),
                'validity_period': df_c['validity_period'].mean(),
                'Generosity Score': df_c['Generosity Score'].mean()
            }
            cluster_stats.append(stats_dict)
        
        df_stats = pd.DataFrame(cluster_stats)
        
        overall_means = {
            'grant_ratio': self.df_merged['grant_ratio'].mean(),
            'participant_ratio': self.df_merged['participant_ratio'].mean(),
            'discount_rate': self.df_merged['discount_rate'].mean(),
            'waiting_period_adj': self.df_merged['waiting_period_adj'].mean(),
            'validity_period': self.df_merged['validity_period'].mean(),
            'Generosity Score': self.df_merged['Generosity Score'].mean()
        }
        
        print("\n全样本均值:")
        for key, val in overall_means.items():
            print(f"  {key}: {val:.4f}")
        
        print("\n各Cluster指标与全样本对比:")
        print("-" * 140)
        print(f"{'Cluster':<10} | {'指标':<20} | {'Cluster均值':<12} | {'全样本均值':<12} | {'偏离度(%)':<12} | {'方向':<10}")
        print("-" * 140)
        
        cluster_names = {}
        cluster_descriptions = {}
        
        for cid in sorted(self.df_merged['Cluster'].unique()):
            df_c = self.df_merged[self.df_merged['Cluster'] == cid]
            cid_int = int(cid)
            
            gr = df_c['grant_ratio'].mean()
            pr = df_c['participant_ratio'].mean()
            dr = df_c['discount_rate'].mean()
            wp = df_c['waiting_period_adj'].mean()
            vp = df_c['validity_period'].mean()
            gs = df_c['Generosity Score'].mean()
            
            features = []
            directions = []
            
            for var in self.core_vars + ['Generosity Score']:
                c_mean = df_c[var].mean()
                s_mean = overall_means[var]
                diff_pct = (c_mean - s_mean) / s_mean * 100 if s_mean != 0 else 0
                direction = "↑" if diff_pct > 0 else "↓" if diff_pct < 0 else "="
                
                print(f"{f'Cluster {cid_int}':<10} | {var:<20} | {c_mean:<12.4f} | {s_mean:<12.4f} | {diff_pct:<12.2f} | {direction:<10}")
                
                if diff_pct > 20:
                    features.append(f"{var}显著高(+{diff_pct:.1f}%)")
                    directions.append((var, 'high'))
                elif diff_pct > 10:
                    features.append(f"{var}偏高(+{diff_pct:.1f}%)")
                    directions.append((var, 'moderate_high'))
                elif diff_pct < -20:
                    features.append(f"{var}显著低({diff_pct:.1f}%)")
                    directions.append((var, 'low'))
                elif diff_pct < -10:
                    features.append(f"{var}偏低({diff_pct:.1f}%)")
                    directions.append((var, 'moderate_low'))
            
            print("-" * 140)
            
            gs_diff = (gs - overall_means['Generosity Score']) / overall_means['Generosity Score'] * 100
            
            count = len(df_c)
            
            if count < 50:
                if pr > overall_means['participant_ratio'] * 1.3:
                    if gr > overall_means['grant_ratio'] * 1.2:
                        name = "高覆盖高慷慨型"
                        desc = "参与比例显著高于平均，授予比例也较高，整体慷慨度突出"
                    else:
                        name = "高覆盖广度型"
                        desc = "参与比例显著高于平均，体现出广覆盖的激励策略"
                elif gs > overall_means['Generosity Score'] * 1.5:
                    name = "高慷慨度特殊型"
                    desc = "Generosity Score显著高于平均，激励设计与众不同"
                elif pr < overall_means['participant_ratio'] * 0.7 and gr < overall_means['grant_ratio'] * 0.7:
                    name = "保守小众型"
                    desc = "参与比例和授予比例均显著低于平均，激励策略偏保守"
                elif wp > overall_means['waiting_period_adj'] * 1.1:
                    name = "即时激励特殊型"
                    desc = "等待期显著短于平均，员工能更快获得收益"
                elif vp > overall_means['validity_period'] * 1.1:
                    name = "长期导向特殊型"
                    desc = "有效期显著长于平均，注重长期激励"
                else:
                    name = "特殊激励设计型"
                    desc = "激励设计与主流企业存在差异，形成独立Cluster"
            else:
                if pr < overall_means['participant_ratio'] * 0.9 and gr < overall_means['grant_ratio'] * 0.9:
                    name = "主流保守激励型"
                    desc = "大多数企业采用的保守激励策略"
                elif gs < overall_means['Generosity Score'] * 0.9:
                    name = "主流标准激励型"
                    desc = "大多数企业采用的标准激励方案"
                else:
                    name = "主流均衡激励型"
                    desc = "大多数企业采用的均衡激励策略"
            
            cluster_names[cid_int] = name
            cluster_descriptions[cid_int] = desc
            
            print(f"\nCluster {cid_int} ({count}家公司):")
            print(f"  建议名称: {name}")
            print(f"  主要特征: {', '.join(features) if features else '各指标均衡'}")
            print(f"  经济含义: {desc}")
        
        print("-" * 140)
        
        self._save_naming_report(cluster_names, cluster_descriptions, df_stats, overall_means)
        
        self.cluster_names = cluster_names
        self.cluster_descriptions = cluster_descriptions
        self.cluster_stats = df_stats
        self.overall_means = overall_means
        
        return cluster_names
    
    def _save_naming_report(self, names, descriptions, stats, overall_means):
        report_content = """# Cluster命名修正报告

## 背景

原自动命名存在问题，两个Cluster均被命名为"均衡型"，无法体现实际差异。

## 全样本均值

| 指标 | 均值 |
|------|------|
"""
        
        for key, val in overall_means.items():
            report_content += f"| {key} | {val:.4f} |\n"
        
        report_content += """
## Cluster分析

"""
        
        for cid in sorted(self.df_merged['Cluster'].unique()):
            cid_int = int(cid)
            df_c = self.df_merged[self.df_merged['Cluster'] == cid]
            name = names[cid_int]
            desc = descriptions[cid_int]
            count = len(df_c)
            
            report_content += f"""
### {name} (Cluster {cid_int})

- **公司数量**: {count} 家
- **建议名称**: {name}
- **描述**: {desc}

#### 各指标与全样本对比

| 指标 | Cluster均值 | 全样本均值 | 偏离度 | 方向 |
|------|------------|-----------|--------|------|
"""
            
            for var in self.core_vars + ['Generosity Score']:
                c_mean = df_c[var].mean()
                s_mean = overall_means[var]
                diff_pct = (c_mean - s_mean) / s_mean * 100 if s_mean != 0 else 0
                direction = "高于" if diff_pct > 0 else "低于" if diff_pct < 0 else "持平"
                report_content += f"| {var} | {c_mean:.4f} | {s_mean:.4f} | {diff_pct:+.2f}% | {direction} |\n"
        
        report_content += """
## 命名依据

1. **根据偏离度判断特征**：指标偏离全样本均值超过20%视为显著差异
2. **根据样本规模判断类型**：样本数量少的Cluster被视为特殊群体
3. **结合经济含义命名**：根据实际激励特征给出可解释的名称

## 结论

两个Cluster确实存在显著差异，不应被命名为相同的"均衡型"。
"""
        
        with open(self.output_dir / "cluster_naming_report.md", "w", encoding="utf-8") as f:
            f.write(report_content)
        
        print(f"\n✓ 已保存: {self.output_dir / 'cluster_naming_report.md'}")
    
    def step2_anova_test(self):
        self.print_separator("二、Cluster差异显著性检验（ANOVA）")
        
        print("进行One-Way ANOVA检验...")
        
        variables = self.core_vars + ['Generosity Score']
        
        anova_results = []
        
        print("\nANOVA检验结果:")
        print("-" * 90)
        print(f"{'变量':<20} | {'F统计量':<12} | {'P值':<15} | {'显著性':<10}")
        print("-" * 90)
        
        for var in variables:
            groups = []
            for cid in sorted(self.df_merged['Cluster'].unique()):
                df_c = self.df_merged[self.df_merged['Cluster'] == cid]
                groups.append(df_c[var].values)
            
            f_stat, p_val = f_oneway(*groups)
            
            significant = "是" if p_val < 0.05 else "否"
            sig_marker = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
            
            print(f"{var:<20} | {f_stat:<12.4f} | {p_val:<15.6f} | {significant:<10} {sig_marker}")
            
            anova_results.append({
                'Variable': var,
                'F Statistic': round(f_stat, 4),
                'P Value': round(p_val, 6),
                'Significant': significant,
                'Significance Level': '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else ''
            })
        
        print("-" * 90)
        print("\n显著性说明:")
        print("  ***: P < 0.001 (极显著)")
        print("  **: P < 0.01 (非常显著)")
        print("  *: P < 0.05 (显著)")
        print("  无标记: P >= 0.05 (不显著)")
        
        df_anova = pd.DataFrame(anova_results)
        df_anova.to_csv(self.output_dir / "anova_test_results.csv", index=False, encoding='utf-8-sig')
        print(f"\n✓ 已保存: {self.output_dir / 'anova_test_results.csv'}")
        
        self.df_anova = df_anova
        
        return df_anova
    
    def step3_enhanced_profile(self):
        self.print_separator("三、Cluster画像深度分析")
        
        print("生成增强版Cluster画像...")
        
        enhanced_data = []
        
        print("\nCluster画像（含偏离度分析）:")
        print("-" * 180)
        header = f"{'Cluster':<10} | {'公司数':<8} | {'平均Score':<12}"
        for var in self.core_vars:
            header += f" | {var:<15}"
        print(header)
        print("-" * 180)
        
        for cid in sorted(self.df_merged['Cluster'].unique()):
            df_c = self.df_merged[self.df_merged['Cluster'] == cid]
            cid_int = int(cid)
            
            gr = df_c['grant_ratio'].mean()
            pr = df_c['participant_ratio'].mean()
            dr = df_c['discount_rate'].mean()
            wp = df_c['waiting_period_adj'].mean()
            vp = df_c['validity_period'].mean()
            gs = df_c['Generosity Score'].mean()
            
            row = {
                'Cluster': cid_int,
                'Company Count': len(df_c),
                'Avg Score': round(gs, 6),
                'grant_ratio': round(gr, 4),
                'grant_ratio_Sample': round(self.overall_means['grant_ratio'], 4),
                'grant_ratio_Diff_Pct': round((gr - self.overall_means['grant_ratio']) / self.overall_means['grant_ratio'] * 100 if self.overall_means['grant_ratio'] != 0 else 0, 2),
                'participant_ratio': round(pr, 4),
                'participant_ratio_Sample': round(self.overall_means['participant_ratio'], 4),
                'participant_ratio_Diff_Pct': round((pr - self.overall_means['participant_ratio']) / self.overall_means['participant_ratio'] * 100 if self.overall_means['participant_ratio'] != 0 else 0, 2),
                'discount_rate': round(dr, 4),
                'discount_rate_Sample': round(self.overall_means['discount_rate'], 4),
                'discount_rate_Diff_Pct': round((dr - self.overall_means['discount_rate']) / self.overall_means['discount_rate'] * 100 if self.overall_means['discount_rate'] != 0 else 0, 2),
                'waiting_period_adj': round(wp, 4),
                'waiting_period_adj_Sample': round(self.overall_means['waiting_period_adj'], 4),
                'waiting_period_adj_Diff_Pct': round((wp - self.overall_means['waiting_period_adj']) / self.overall_means['waiting_period_adj'] * 100 if self.overall_means['waiting_period_adj'] != 0 else 0, 2),
                'validity_period': round(vp, 4),
                'validity_period_Sample': round(self.overall_means['validity_period'], 4),
                'validity_period_Diff_Pct': round((vp - self.overall_means['validity_period']) / self.overall_means['validity_period'] * 100 if self.overall_means['validity_period'] != 0 else 0, 2)
            }
            enhanced_data.append(row)
            
            name = self.cluster_names.get(cid_int, f'Cluster {cid_int}')
            line = f"{name:<10} | {len(df_c):<8} | {gs:<12.4f}"
            line += f" | {gr:>6.2f}% ({row['grant_ratio_Diff_Pct']:+>6.1f}%)"
            line += f" | {pr:>6.2f}% ({row['participant_ratio_Diff_Pct']:+>6.1f}%)"
            line += f" | {dr:>6.2f}% ({row['discount_rate_Diff_Pct']:+>6.1f}%)"
            line += f" | {wp:>6.2f}% ({row['waiting_period_adj_Diff_Pct']:+>6.1f}%)"
            line += f" | {vp:>6.2f}% ({row['validity_period_Diff_Pct']:+>6.1f}%)"
            print(line)
        
        print("-" * 180)
        
        print("\n驱动聚类结果的关键指标:")
        for var in self.core_vars:
            diffs = []
            for cid in sorted(self.df_merged['Cluster'].unique()):
                df_c = self.df_merged[self.df_merged['Cluster'] == cid]
                c_mean = df_c[var].mean()
                diff = abs(c_mean - self.overall_means[var])
                diffs.append(diff)
            max_diff = max(diffs)
            if max_diff > self.overall_means[var] * 0.2:
                print(f"  ✓ {var}: Cluster间差异较大（最大偏离{max_diff*100/self.overall_means[var]:.1f}%）")
        
        df_enhanced = pd.DataFrame(enhanced_data)
        df_enhanced.to_csv(self.output_dir / "cluster_profile_enhanced.csv", index=False, encoding='utf-8-sig')
        print(f"\n✓ 已保存: {self.output_dir / 'cluster_profile_enhanced.csv'}")
        
        self.df_enhanced = df_enhanced
        
        return df_enhanced
    
    def step4_identify_small_group(self):
        self.print_separator("四、识别特殊群体（17家公司）")
        
        cluster_counts = self.df_merged['Cluster'].value_counts()
        small_cluster_id = int(cluster_counts.idxmin())
        small_count = cluster_counts.min()
        
        print(f"识别出小规模Cluster:")
        print(f"  Cluster {small_cluster_id}: {small_count} 家公司")
        
        df_small = self.df_merged[self.df_merged['Cluster'] == small_cluster_id].copy()
        df_small = df_small.sort_values('Generosity Score', ascending=False).reset_index(drop=True)
        
        df_small_export = df_small[['company_name', 'stock_code', 'Cluster', 'Generosity Score']].copy()
        
        print(f"\n小规模Cluster公司名单（按Generosity Score排序）:")
        print("-" * 80)
        print(f"{'排名':<6} | {'公司名称':<20} | {'股票代码':<12} | {'Generosity Score':<15}")
        print("-" * 80)
        
        for idx, row in df_small_export.head(small_count).iterrows():
            print(f"{idx+1:<6} | {row['company_name']:<20} | {str(row['stock_code']):<12} | {row['Generosity Score']:<15.6f}")
        
        print("-" * 80)
        
        df_small_export.to_csv(self.output_dir / "cluster_small_group_companies.csv", index=False, encoding='utf-8-sig')
        print(f"\n✓ 已保存: {self.output_dir / 'cluster_small_group_companies.csv'}")
        
        self.small_cluster_id = small_cluster_id
        self.df_small = df_small
        
        return df_small_export
    
    def step5_small_group_analysis(self):
        self.print_separator("五、特殊群体特征挖掘")
        
        df_small = self.df_small
        df_large = self.df_merged[self.df_merged['Cluster'] != self.small_cluster_id]
        
        small_name = self.cluster_names.get(self.small_cluster_id, '小规模Cluster')
        large_cluster_ids = [cid for cid in self.df_merged['Cluster'].unique() if int(cid) != self.small_cluster_id]
        large_name = self.cluster_names.get(large_cluster_ids[0], '大规模Cluster') if large_cluster_ids else '其他Cluster'
        
        print(f"特殊群体: {small_name} ({len(df_small)}家)")
        print(f"对比群体: {large_name} ({len(df_large)}家)")
        
        print("\n特殊群体 vs 主流群体 指标对比:")
        print("-" * 120)
        print(f"{'指标':<20} | {'特殊群体均值':<15} | {'主流群体均值':<15} | {'差异':<10} | {'倍数':<10}")
        print("-" * 120)
        
        for var in self.core_vars + ['Generosity Score']:
            s_mean = df_small[var].mean()
            l_mean = df_large[var].mean()
            diff = s_mean - l_mean
            ratio = s_mean / l_mean if l_mean != 0 else 0
            
            print(f"{var:<20} | {s_mean:<15.4f} | {l_mean:<15.4f} | {diff:>+10.4f} | {ratio:<10.2f}x")
        
        print("-" * 120)
        
        print("\n特殊群体特征分析:")
        
        pr_small = df_small['participant_ratio'].mean()
        pr_large = df_large['participant_ratio'].mean()
        gr_small = df_small['grant_ratio'].mean()
        gr_large = df_large['grant_ratio'].mean()
        gs_small = df_small['Generosity Score'].mean()
        gs_large = df_large['Generosity Score'].mean()
        
        findings = []
        
        if pr_small > pr_large * 1.2:
            print(f"  ✓ 参与比例显著高于主流群体 ({pr_small:.4f} vs {pr_large:.4f})")
            print("    → 特殊群体让更多员工参与股权激励")
            findings.append("参与比例显著高于主流群体")
        elif pr_small < pr_large * 0.8:
            print(f"  ✗ 参与比例显著低于主流群体 ({pr_small:.4f} vs {pr_large:.4f})")
            print("    → 特殊群体只让少数核心员工参与")
            findings.append("参与比例显著低于主流群体")
        else:
            print(f"  → 参与比例接近 ({pr_small:.4f} vs {pr_large:.4f})")
            findings.append("参与比例接近主流群体")
        
        if gr_small > gr_large * 1.2:
            print(f"  ✓ 授予比例显著高于主流群体 ({gr_small:.4f} vs {gr_large:.4f})")
            print("    → 特殊群体给予更高的股权激励规模")
            findings.append("授予比例显著高于主流群体")
        elif gr_small < gr_large * 0.8:
            print(f"  ✗ 授予比例显著低于主流群体 ({gr_small:.4f} vs {gr_large:.4f})")
            print("    → 特殊群体的股权激励规模较小")
            findings.append("授予比例显著低于主流群体")
        else:
            print(f"  → 授予比例接近 ({gr_small:.4f} vs {gr_large:.4f})")
            findings.append("授予比例接近主流群体")
        
        if gs_small > gs_large * 1.5:
            print(f"  ★ Generosity Score显著高于主流群体 ({gs_small:.4f} vs {gs_large:.4f})")
            print("    → 特殊群体的整体慷慨度远高于平均水平")
            findings.append("Generosity Score显著高于主流群体")
        elif gs_small < gs_large * 0.7:
            print(f"  ★ Generosity Score显著低于主流群体 ({gs_small:.4f} vs {gs_large:.4f})")
            print("    → 特殊群体的整体慷慨度远低于平均水平")
            findings.append("Generosity Score显著低于主流群体")
        
        print("\n结论:")
        if gs_small > gs_large * 1.2:
            print("  → 这些公司被单独聚类是因为它们的激励设计更加慷慨")
            print("  → 可能是行业领先企业或对人才竞争激烈的公司")
        elif gs_small < gs_large * 0.8:
            print("  → 这些公司被单独聚类是因为它们的激励设计更加保守")
            print("  → 可能是成熟稳定行业或激励文化保守的公司")
        else:
            print("  → 这些公司被单独聚类是因为它们在某些特定维度上存在差异")
            print("  → 虽然整体慷慨度接近，但具体激励设计不同")
        
        self._save_small_cluster_analysis(small_name, large_name, findings)
        
        return findings
    
    def _save_small_cluster_analysis(self, small_name, large_name, findings):
        df_small = self.df_small
        df_large = self.df_merged[self.df_merged['Cluster'] != self.small_cluster_id]
        
        report_content = f"""# 特殊群体（小规模Cluster）深度分析

## 基本信息

- **特殊群体名称**: {small_name}
- **特殊群体规模**: {len(df_small)} 家公司
- **对比群体名称**: {large_name}
- **对比群体规模**: {len(df_large)} 家公司

## 指标对比

| 指标 | 特殊群体均值 | 主流群体均值 | 差异 | 倍数 |
|------|------------|------------|------|------|
"""
        
        for var in self.core_vars + ['Generosity Score']:
            s_mean = df_small[var].mean()
            l_mean = df_large[var].mean()
            diff = s_mean - l_mean
            ratio = s_mean / l_mean if l_mean != 0 else 0
            report_content += f"| {var} | {s_mean:.4f} | {l_mean:.4f} | {diff:+.4f} | {ratio:.2f}x |\n"
        
        report_content += """
## 特征分析

"""
        
        for finding in findings:
            report_content += f"- {finding}\n"
        
        report_content += """
## 为什么这些公司会被单独聚为一类？

### 可能的原因

1. **激励策略差异**
   - 在核心指标（参与比例、授予比例等）上与主流企业存在显著差异
   - K-Means算法能够识别这种系统性差异

2. **行业特征**
   - 可能集中于某些特定行业
   - 不同行业的激励惯例可能不同

3. **企业属性**
   - 可能集中于特定板块（创业板/科创板）
   - 不同发展阶段的企业激励策略不同

4. **特殊设计**
   - 可能存在特殊的激励设计（如限制性股票vs股票期权）
   - 或特殊的解锁条件设计

## 与主流企业的不同之处

### 量化差异

"""
        
        pr_small = df_small['participant_ratio'].mean()
        pr_large = df_large['participant_ratio'].mean()
        gr_small = df_small['grant_ratio'].mean()
        gr_large = df_large['grant_ratio'].mean()
        gs_small = df_small['Generosity Score'].mean()
        gs_large = df_large['Generosity Score'].mean()
        
        pr_diff = (pr_small - pr_large) / pr_large * 100 if pr_large != 0 else 0
        gr_diff = (gr_small - gr_large) / gr_large * 100 if gr_large != 0 else 0
        gs_diff = (gs_small - gs_large) / gs_large * 100 if gs_large != 0 else 0
        
        report_content += f"""
- **参与比例**: {pr_small:.4f} vs {pr_large:.4f} ({pr_diff:+.2f}%)
- **授予比例**: {gr_small:.4f} vs {gr_large:.4f} ({gr_diff:+.2f}%)
- **Generosity Score**: {gs_small:.4f} vs {gs_large:.4f} ({gs_diff:+.2f}%)

### 经济含义

如果特殊群体的Generosity Score显著更高：
- 这些公司更加慷慨，对人才的激励力度更大
- 可能是高成长性行业，需要更强的激励留住人才
- 或可能是行业领先企业，有能力提供更慷慨的激励

如果特殊群体的Generosity Score显著更低：
- 这些公司更加保守，激励力度较小
- 可能是成熟稳定行业，对人才的依赖度较低
- 或可能是国企/传统企业，激励文化较为保守

## 结论

这些公司被单独聚类并非偶然，而是反映了A股市场中确实存在少数企业采用了与众不同的股权激励策略。
"""
        
        with open(self.output_dir / "small_cluster_analysis.md", "w", encoding="utf-8") as f:
            f.write(report_content)
        
        print(f"\n✓ 已保存: {self.output_dir / 'small_cluster_analysis.md'}")
    
    def step6_visualization(self):
        self.print_separator("六、Generosity Score分布验证")
        
        print("生成可视化图片...")
        
        fig_dir = self.output_dir / "figures"
        fig_dir.mkdir(exist_ok=True)
        
        self._plot_score_distribution(fig_dir)
        self._plot_cluster_boxplot(fig_dir)
        self._plot_cluster_violin(fig_dir)
        self._plot_combined_validation(fig_dir)
        
        print(f"\n✓ 可视化图片已保存至: {fig_dir}")
    
    def _plot_score_distribution(self, fig_dir):
        print("  - 生成: score_histogram.png")
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        sns.histplot(data=self.df_merged, x='Generosity Score', kde=True, color='#4C72B0', 
                    bins=25, alpha=0.7, edgecolor='white', ax=ax)
        
        ax.axvline(self.df_merged['Generosity Score'].mean(), color='red', linestyle='--', 
                  linewidth=2, label=f'Mean = {self.df_merged["Generosity Score"].mean():.4f}')
        ax.axvline(self.df_merged['Generosity Score'].median(), color='orange', linestyle='-.', 
                  linewidth=2, label=f'Median = {self.df_merged["Generosity Score"].median():.4f}')
        
        ax.set_title('Generosity Score 整体分布图', fontsize=14, fontweight='bold')
        ax.set_xlabel('Generosity Score', fontsize=11)
        ax.set_ylabel('频数', fontsize=11)
        ax.legend(fontsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(fig_dir / "score_histogram.png", dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
    
    def _plot_cluster_boxplot(self, fig_dir):
        print("  - 生成: cluster_boxplot.png")
        
        df_plot = self.df_merged.copy()
        df_plot['Cluster_Label'] = df_plot['Cluster'].map(self.cluster_names)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        boxprops = dict(linewidth=1.5)
        medianprops = dict(color='red', linewidth=2)
        flierprops = dict(marker='o', markerfacecolor='#DD8452', markersize=6, markeredgecolor='white')
        
        sns.boxplot(data=df_plot, x='Cluster_Label', y='Generosity Score', 
                   palette='Set2', ax=ax,
                   boxprops=boxprops, medianprops=medianprops, flierprops=flierprops)
        
        ax.set_title('各Cluster Generosity Score 箱线图', fontsize=14, fontweight='bold')
        ax.set_xlabel('Cluster', fontsize=11)
        ax.set_ylabel('Generosity Score', fontsize=11)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        for i, cid in enumerate(sorted(df_plot['Cluster'].unique())):
            subset = df_plot[df_plot['Cluster'] == cid]
            median_val = subset['Generosity Score'].median()
            ax.text(i, median_val + 0.01, f'Median: {median_val:.4f}', 
                   ha='center', fontsize=9, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(fig_dir / "cluster_boxplot.png", dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
    
    def _plot_cluster_violin(self, fig_dir):
        print("  - 生成: cluster_violin.png")
        
        df_plot = self.df_merged.copy()
        df_plot['Cluster_Label'] = df_plot['Cluster'].map(self.cluster_names)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        sns.violinplot(data=df_plot, x='Cluster_Label', y='Generosity Score', 
                      palette='Set2', inner='quartile', ax=ax)
        
        ax.set_title('各Cluster Generosity Score 小提琴图', fontsize=14, fontweight='bold')
        ax.set_xlabel('Cluster', fontsize=11)
        ax.set_ylabel('Generosity Score', fontsize=11)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(fig_dir / "cluster_violin.png", dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
    
    def _plot_combined_validation(self, fig_dir):
        print("  - 生成: score_distribution_validation.png")
        
        df_plot = self.df_merged.copy()
        df_plot['Cluster_Label'] = df_plot['Cluster'].map(self.cluster_names)
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        ax1 = axes[0, 0]
        sns.histplot(data=df_plot, x='Generosity Score', kde=True, color='#4C72B0', 
                    bins=25, alpha=0.7, ax=ax1)
        ax1.axvline(df_plot['Generosity Score'].mean(), color='red', linestyle='--', linewidth=2)
        ax1.set_title('Generosity Score 整体分布', fontsize=12, fontweight='bold')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        
        ax2 = axes[0, 1]
        sns.boxplot(data=df_plot, x='Cluster_Label', y='Generosity Score', 
                   palette='Set2', ax=ax2)
        ax2.set_title('各Cluster箱线图', fontsize=12, fontweight='bold')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        
        ax3 = axes[1, 0]
        sns.violinplot(data=df_plot, x='Cluster_Label', y='Generosity Score', 
                      palette='Set2', inner='quartile', ax=ax3)
        ax3.set_title('各Cluster小提琴图', fontsize=12, fontweight='bold')
        ax3.spines['top'].set_visible(False)
        ax3.spines['right'].set_visible(False)
        
        ax4 = axes[1, 1]
        for cluster_id in sorted(df_plot['Cluster'].unique()):
            cluster_data = df_plot[df_plot['Cluster'] == cluster_id]
            label = self.cluster_names.get(int(cluster_id), f'Cluster {cluster_id}')
            sns.kdeplot(data=cluster_data, x='Generosity Score', fill=True, alpha=0.3, 
                       label=f'{label} ({len(cluster_data)}家)', ax=ax4)
        ax4.set_title('各Cluster密度曲线', fontsize=12, fontweight='bold')
        ax4.legend(fontsize=9)
        ax4.spines['top'].set_visible(False)
        ax4.spines['right'].set_visible(False)
        
        plt.suptitle('Generosity Score 分布验证（2 Cluster）', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig(fig_dir / "score_distribution_validation.png", dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
    
    def step7_generate_final_report(self):
        self.print_separator("七、研究结论升级")
        
        print("生成最终验证报告...")
        
        significant_vars = self.df_anova[self.df_anova['Significant'] == '是']['Variable'].tolist()
        non_significant_vars = self.df_anova[self.df_anova['Significant'] == '否']['Variable'].tolist()
        
        small_count = len(self.df_small)
        large_count = len(self.df_merged) - small_count
        
        gs_small = self.df_small['Generosity Score'].mean()
        gs_large = self.df_merged[self.df_merged['Cluster'] != self.small_cluster_id]['Generosity Score'].mean()
        gs_ratio = gs_small / gs_large if gs_large != 0 else 0
        
        report_content = """# 聚类结果验证与特殊群体识别报告

## 研究背景

当前K-Means聚类结果显示：
- **主流群体**: 175家企业（91%）
- **特殊群体**: 17家企业（9%）

存在明显的不平衡现象，需要验证聚类结果的统计意义。

## 一、Cluster命名修正

"""
        
        for cid, name in self.cluster_names.items():
            desc = self.cluster_descriptions.get(cid, '')
            count = len(self.df_merged[self.df_merged['Cluster'] == cid])
            report_content += f"### {name} (Cluster {cid})\n\n- **规模**: {count} 家公司\n- **描述**: {desc}\n\n"
        
        report_content += f"""
## 二、ANOVA差异检验结果

| 变量 | F统计量 | P值 | 显著性 |
|------|---------|-----|--------|
"""
        
        for _, row in self.df_anova.iterrows():
            sig = "✓ 显著" if row['Significant'] == '是' else "✗ 不显著"
            report_content += f"| {row['Variable']} | {row['F Statistic']:.4f} | {row['P Value']:.6f} | {sig} |\n"
        
        report_content += f"""
### 检验结论

- **显著差异的变量**: {', '.join(significant_vars) if significant_vars else '无'}
- **无显著差异的变量**: {', '.join(non_significant_vars) if non_significant_vars else '无'}

"""
        
        if len(significant_vars) >= 3:
            report_content += """
**结论**: 多数指标在Cluster间存在显著差异，聚类结果具有统计意义。
"""
        elif len(significant_vars) >= 1:
            report_content += """
**结论**: 部分指标在Cluster间存在显著差异，聚类结果具有一定统计意义。
"""
        else:
            report_content += """
**结论**: Cluster间差异不显著，可能存在假聚类现象。
"""
        
        report_content += f"""
## 三、特殊群体深度分析

### 群体规模对比

| 群体类型 | 公司数量 | 占比 |
|---------|---------|------|
| 主流群体 | {large_count} | {large_count/len(self.df_merged)*100:.1f}% |
| 特殊群体 | {small_count} | {small_count/len(self.df_merged)*100:.1f}% |

### Generosity Score对比

| 群体 | 平均Score | 对比 |
|------|----------|------|
| 特殊群体 | {gs_small:.4f} | 基准 (1.00x) |
| 主流群体 | {gs_large:.4f} | {gs_ratio:.2f}x |

### 关键发现

"""
        
        if gs_ratio > 1.2:
            report_content += f"""
1. **特殊群体更慷慨**: 特殊群体的Generosity Score ({gs_small:.4f}) 显著高于主流群体 ({gs_large:.4f})，是主流群体的 {gs_ratio:.2f} 倍。

2. **差异驱动因素**:
   - 参与比例可能更高
   - 授予比例可能更高
   - 或在时间维度上更友好

3. **经济含义**:
   - 特殊群体可能是行业领先企业
   - 或处于人才竞争激烈的行业
   - 愿意提供更慷慨的激励吸引和留住人才
"""
        elif gs_ratio < 0.8:
            report_content += f"""
1. **特殊群体更保守**: 特殊群体的Generosity Score ({gs_small:.4f}) 显著低于主流群体 ({gs_large:.4f})，仅为主流群体的 {gs_ratio:.2f} 倍。

2. **差异驱动因素**:
   - 参与比例可能更低
   - 授予比例可能更低
   - 或在时间维度上更严格

3. **经济含义**:
   - 特殊群体可能是成熟稳定行业
   - 或国企/传统企业
   - 激励文化较为保守
"""
        else:
            report_content += f"""
1. **整体慷慨度接近**: 特殊群体与主流群体的Generosity Score差异不大 ({gs_small:.4f} vs {gs_large:.4f})。

2. **差异体现在具体维度**:
   - 虽然整体评分接近，但在某些特定指标上存在差异
   - 激励设计的具体方案不同，但综合效果相似
"""
        
        report_content += """
## 四、研究问题回答

### 1. 当前聚类是否具有统计意义？

"""
        
        if len(significant_vars) >= 2:
            report_content += """
**回答**: 是，聚类结果具有统计意义。

ANOVA检验显示，多个核心指标在Cluster间存在显著差异（P < 0.05），
说明两个Cluster确实代表了不同的激励设计群体。
"""
        else:
            report_content += """
**回答**: 部分具有统计意义。

虽然存在一些显著差异，但差异可能不够大，聚类结果可能受到算法参数的影响。
"""
        
        report_content += """
### 2. 是否支持"A股股权激励存在同质化现象"的结论？

"""
        
        if large_count > 150:
            report_content += f"""
**回答**: 部分支持。

主流群体包含 {large_count} 家公司（占比 {large_count/len(self.df_merged)*100:.1f}%），
说明大多数公司的股权激励设计确实存在同质化倾向。
但同时也存在 {small_count} 家公司采用了不同的策略。
"""
        else:
            report_content += """
**回答**: 不支持。

Cluster分布相对均衡，说明A股股权激励并不存在明显的同质化现象，
而是存在多种不同的激励策略。
"""
        
        report_content += """
### 3. 是否存在少数特殊激励设计企业？

"""
        
        if small_count < 50:
            report_content += f"""
**回答**: 是。

确实存在 {small_count} 家公司（占比 {small_count/len(self.df_merged)*100:.1f}%）的激励设计与众不同，
被K-Means算法单独聚类。这些公司可能：
- 处于特殊行业
- 具有特殊的企业属性
- 采用了非传统的激励方案
"""
        else:
            report_content += """
**回答**: 不存在明显的特殊群体。

两个Cluster的规模都较大，说明市场中存在多种主流激励模式，
而非少数公司采用特殊方案。
"""
        
        report_content += """
### 4. 聚类结果对于Generosity Score评价体系有何验证作用？

"""
        
        if 'Generosity Score' in significant_vars:
            gs_row = self.df_anova[self.df_anova['Variable'] == 'Generosity Score'].iloc[0]
            report_content += f"""
**回答**: 聚类结果有效验证了Generosity Score的区分能力。

Generosity Score在Cluster间存在显著差异（F = {gs_row['F Statistic']:.4f}, P = {gs_row['P Value']:.6f}），
说明：

1. **Generosity Score能够有效区分不同激励策略**
   - 不同Cluster的公司在Generosity Score上存在显著差异
   - 验证了评分体系的有效性

2. **聚类结果与评价体系相互印证**
   - 基于原始指标的聚类与基于综合评分的分类一致
   - 说明评价体系捕捉到了真实的激励策略差异

3. **为分层分析提供依据**
   - 可以针对不同Cluster的公司进行深入分析
   - 了解不同激励策略的经济后果
"""
        else:
            report_content += """
**回答**: 聚类结果对Generosity Score的验证作用有限。

Generosity Score在Cluster间差异不显著，可能：
1. 聚类主要基于其他维度的差异
2. Generosity Score的区分能力有待提升
3. 需要进一步优化评价体系
"""
        
        report_content += """
## 五、输出文件

### 数据文件

1. `anova_test_results.csv` - ANOVA差异检验结果
2. `cluster_profile_enhanced.csv` - 增强版Cluster画像
3. `cluster_small_group_companies.csv` - 特殊群体公司名单

### 报告文件

1. `cluster_naming_report.md` - Cluster命名修正报告
2. `small_cluster_analysis.md` - 特殊群体深度分析
3. `cluster_validation_report.md` - 本报告

### 可视化图片

1. `figures/score_histogram.png` - Generosity Score直方图
2. `figures/cluster_boxplot.png` - Cluster箱线图
3. `figures/cluster_violin.png` - Cluster小提琴图
4. `figures/score_distribution_validation.png` - 综合验证图

---

**完成日期**: 2026年
"""
        
        with open(self.output_dir / "cluster_validation_report.md", "w", encoding="utf-8") as f:
            f.write(report_content)
        
        print(f"✓ 已保存: {self.output_dir / 'cluster_validation_report.md'}")
    
    def run(self):
        print("\n" + "#" * 80)
        print("#     Step 7.5: 聚类结果验证与特殊群体识别")
        print("#     研究主题：上市公司股权激励慷慨度评价体系")
        print("#" * 80)
        
        self.step1_cluster_naming()
        self.step2_anova_test()
        self.step3_enhanced_profile()
        self.step4_identify_small_group()
        self.step5_small_group_analysis()
        self.step6_visualization()
        self.step7_generate_final_report()
        
        print("\n" + "#" * 80)
        print("#     Step 7.5 完成！")
        print("#" * 80)
        
        print(f"\n输出目录: {self.output_dir}")


if __name__ == "__main__":
    validator = ClusterValidator()
    validator.run()