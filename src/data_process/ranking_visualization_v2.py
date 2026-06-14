#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 6 可视化：为 ranking_final_output_v2 生成6种可视化图片
研究主题：上市公司股权激励慷慨度评价体系

生成的可视化图片：
1. Top 20 公司柱状图
2. Bottom 20 公司柱状图
3. Generosity Score 分布图
4. 箱线图
5. Top 10 公司各指标雷达图
6. Top vs Bottom 对比图
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import matplotlib.font_manager as fm

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'STHeiti', 'WenQuanYi Micro Hei']
plt.rcParams['axes.unicode_minus'] = False

class RankingVisualizer:
    def __init__(self, input_dir: str = "ranking_final_output_v2", output_dir: str = "ranking_final_output_v2/figures"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"输入目录: {input_dir}")
        print(f"输出目录: {output_dir}")
        
        self.load_data()
    
    def load_data(self):
        ranking_file = self.input_dir / "generosity_ranking_final.csv"
        cleaned_file = "data_cleaning_output_v3/cleaned_equity_incentive_data.csv"
        
        if ranking_file.exists():
            self.df_ranking = pd.read_csv(ranking_file, encoding='utf-8-sig')
            print(f"✓ 已加载: {ranking_file}")
        else:
            print(f"✗ 文件不存在: {ranking_file}")
            raise FileNotFoundError(f"文件不存在: {ranking_file}")
        
        if Path(cleaned_file).exists():
            self.df_cleaned = pd.read_csv(cleaned_file, encoding='utf-8-sig')
            print(f"✓ 已加载: {cleaned_file}")
        else:
            print(f"✗ 文件不存在: {cleaned_file}")
            self.df_cleaned = None
        
        print(f"排名数据样本数: {len(self.df_ranking)}")
    
    def print_separator(self, title: str):
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80 + "\n")
    
    def plot_top20_bar(self):
        self.print_separator("1. Top 20 公司柱状图")
        
        df_top20 = self.df_ranking.head(20)
        
        fig, ax = plt.subplots(figsize=(14, 10))
        
        colors = plt.cm.RdYlGn_r(np.linspace(0.3, 0.9, 20))
        bars = ax.barh(range(len(df_top20)), df_top20['Generosity Score'], color=colors, edgecolor='white', linewidth=0.8)
        
        ax.set_yticks(range(len(df_top20)))
        ax.set_yticklabels(df_top20['company_name'], fontsize=10)
        ax.invert_yaxis()
        
        ax.set_title('Top 20 股权激励慷慨度最高的公司', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Generosity Score', fontsize=12)
        ax.set_ylabel('')
        
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + 0.005, bar.get_y() + bar.get_height()/2,
                   f'{df_top20.iloc[i]["Generosity Score"]:.4f}',
                   va='center', fontsize=10, fontweight='bold')
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        output_path = self.output_dir / "top20_generosity_companies.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✓ 已生成: {output_path}")
        print(f"  Top 1 公司: {df_top20.iloc[0]['company_name']} ({df_top20.iloc[0]['Generosity Score']:.4f})")
    
    def plot_bottom20_bar(self):
        self.print_separator("2. Bottom 20 公司柱状图")
        
        df_bottom20 = self.df_ranking.tail(20)
        df_bottom20 = df_bottom20.sort_values('Generosity Score', ascending=True).reset_index(drop=True)
        
        fig, ax = plt.subplots(figsize=(14, 10))
        
        colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, 20))
        bars = ax.barh(range(len(df_bottom20)), df_bottom20['Generosity Score'], color=colors, edgecolor='white', linewidth=0.8)
        
        ax.set_yticks(range(len(df_bottom20)))
        ax.set_yticklabels(df_bottom20['company_name'], fontsize=10)
        ax.invert_yaxis()
        
        ax.set_title('Bottom 20 股权激励慷慨度最低的公司', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Generosity Score', fontsize=12)
        ax.set_ylabel('')
        
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + 0.005, bar.get_y() + bar.get_height()/2,
                   f'{df_bottom20.iloc[i]["Generosity Score"]:.4f}',
                   va='center', fontsize=10, fontweight='bold')
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        output_path = self.output_dir / "bottom20_generosity_companies.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✓ 已生成: {output_path}")
        print(f"  最低公司: {df_bottom20.iloc[0]['company_name']} ({df_bottom20.iloc[0]['Generosity Score']:.4f})")
    
    def plot_score_distribution(self):
        self.print_separator("3. Generosity Score 分布图")
        
        scores = self.df_ranking['Generosity Score']
        
        fig, axes = plt.subplots(2, 1, figsize=(12, 10))
        
        ax1 = axes[0]
        sns.histplot(scores, bins=25, kde=True, color='#4C72B0', edgecolor='white', linewidth=1, ax=ax1)
        
        ax1.axvline(scores.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean = {scores.mean():.4f}')
        ax1.axvline(scores.median(), color='orange', linestyle='-.', linewidth=2, label=f'Median = {scores.median():.4f}')
        
        ax1.set_title('Generosity Score 分布直方图', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Generosity Score', fontsize=11)
        ax1.set_ylabel('频数', fontsize=11)
        ax1.legend(fontsize=10)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        
        ax2 = axes[1]
        sns.kdeplot(scores, fill=True, color='#4C72B0', alpha=0.3, linewidth=2, ax=ax2)
        
        ax2.axvline(scores.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean = {scores.mean():.4f}')
        ax2.axvline(scores.median(), color='orange', linestyle='-.', linewidth=2, label=f'Median = {scores.median():.4f}')
        
        ax2.set_title('Generosity Score 核密度图', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Generosity Score', fontsize=11)
        ax2.set_ylabel('密度', fontsize=11)
        ax2.legend(fontsize=10)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        
        plt.tight_layout()
        output_path = self.output_dir / "generosity_score_distribution.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✓ 已生成: {output_path}")
        print(f"  均值: {scores.mean():.4f}")
        print(f"  中位数: {scores.median():.4f}")
        print(f"  标准差: {scores.std():.4f}")
    
    def plot_boxplot(self):
        self.print_separator("4. 箱线图")
        
        scores = self.df_ranking['Generosity Score']
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        boxprops = dict(facecolor='#4C72B0', alpha=0.7)
        medianprops = dict(color='red', linewidth=2)
        flierprops = dict(marker='o', markerfacecolor='red', markersize=8, markeredgecolor='white')
        
        bp = ax.boxplot([scores], vert=False, patch_artist=True,
                       boxprops=boxprops, medianprops=medianprops,
                       flierprops=flierprops, showmeans=True,
                       meanprops=dict(marker='D', markeredgecolor='black', markerfacecolor='orange'))
        
        q1 = scores.quantile(0.25)
        q3 = scores.quantile(0.75)
        iqr = q3 - q1
        lower_whisker = max(scores.min(), q1 - 1.5 * iqr)
        upper_whisker = min(scores.max(), q3 + 1.5 * iqr)
        
        outliers = scores[(scores < lower_whisker) | (scores > upper_whisker)]
        
        ax.set_title('Generosity Score 箱线图', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Generosity Score', fontsize=11)
        ax.set_yticklabels([''])
        
        stats_text = f'''统计信息:
最小值: {scores.min():.4f}
Q1 (25%): {q1:.4f}
中位数: {scores.median():.4f}
Q3 (75%): {q3:.4f}
最大值: {scores.max():.4f}
IQR: {iqr:.4f}
异常值数量: {len(outliers)}'''
        
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=props)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        output_path = self.output_dir / "generosity_score_boxplot.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✓ 已生成: {output_path}")
        print(f"  Q1: {q1:.4f}")
        print(f"  Q3: {q3:.4f}")
        print(f"  IQR: {iqr:.4f}")
        print(f"  异常值数量: {len(outliers)}")
    
    def plot_radar_chart(self):
        self.print_separator("5. Top 10 公司各指标雷达图")
        
        if self.df_cleaned is None:
            print("✗ 缺少 cleaned_equity_incentive_data.csv，无法生成雷达图")
            return
        
        df_top10 = self.df_ranking.head(10)
        
        metrics = ['grant_ratio', 'participant_ratio', 'discount_rate', 'validity_period']
        metric_labels = ['授予比例', '参与比例', '折扣率', '有效期']
        
        fig, axes = plt.subplots(2, 5, figsize=(18, 10), subplot_kw=dict(projection='polar'))
        axes = axes.flatten()
        
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        angles += angles[:1]
        
        for i, (idx, row) in enumerate(df_top10.iterrows()):
            company_name = row['company_name']
            score = row['Generosity Score']
            stock_code = row['stock_code']
            
            metric_values = []
            for metric in metrics:
                if metric in self.df_cleaned.columns:
                    metric_max = self.df_cleaned[metric].max()
                    metric_min = self.df_cleaned[metric].min()
                    
                    if stock_code in self.df_cleaned['stock_code'].astype(str).values:
                        company_data = self.df_cleaned[self.df_cleaned['stock_code'].astype(str) == str(stock_code)]
                        if len(company_data) > 0:
                            raw_value = company_data[metric].values[0]
                            if metric_max != metric_min:
                                normalized = (raw_value - metric_min) / (metric_max - metric_min)
                            else:
                                normalized = 0.5
                            metric_values.append(normalized)
                        else:
                            metric_values.append(0.5)
                    else:
                        metric_values.append(0.5)
                else:
                    metric_values.append(0.5)
            
            metric_values += metric_values[:1]
            
            ax = axes[i]
            ax.plot(angles, metric_values, 'o-', linewidth=2, markersize=6, color='#4C72B0')
            ax.fill(angles, metric_values, alpha=0.25, color='#4C72B0')
            
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(metric_labels, fontsize=9)
            ax.set_ylim(0, 1)
            ax.set_yticks([0.25, 0.5, 0.75])
            ax.set_yticklabels(['', '', ''], fontsize=8)
            
            ax.set_title(f'{company_name}\nScore: {score:.4f}', fontsize=10, pad=10, fontweight='bold')
        
        for j in range(len(df_top10), len(axes)):
            axes[j].axis('off')
        
        plt.suptitle('Top 10 公司各指标雷达图（标准化后）', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        output_path = self.output_dir / "top10_radar_chart.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✓ 已生成: {output_path}")
        print(f"  Top 1: {df_top10.iloc[0]['company_name']}")
    
    def plot_top_vs_bottom_comparison(self):
        self.print_separator("6. Top vs Bottom 对比图")
        
        if self.df_cleaned is None:
            print("✗ 缺少 cleaned_equity_incentive_data.csv，无法生成对比图")
            return
        
        df_top10 = self.df_ranking.head(10)
        df_bottom10 = self.df_ranking.tail(10)
        
        top_stock_codes = df_top10['stock_code'].astype(str).tolist()
        bottom_stock_codes = df_bottom10['stock_code'].astype(str).tolist()
        
        metrics = ['grant_ratio', 'participant_ratio', 'discount_rate', 'validity_period']
        metric_labels = ['授予比例', '参与比例', '折扣率', '有效期']
        
        top_means = []
        bottom_means = []
        sample_means = []
        
        for metric in metrics:
            if metric in self.df_cleaned.columns:
                top_values = []
                bottom_values = []
                
                for code in top_stock_codes:
                    match = self.df_cleaned[self.df_cleaned['stock_code'].astype(str) == code]
                    if len(match) > 0:
                        top_values.append(match[metric].values[0])
                
                for code in bottom_stock_codes:
                    match = self.df_cleaned[self.df_cleaned['stock_code'].astype(str) == code]
                    if len(match) > 0:
                        bottom_values.append(match[metric].values[0])
                
                top_mean = np.mean(top_values) if top_values else 0
                bottom_mean = np.mean(bottom_values) if bottom_values else 0
                sample_mean = self.df_cleaned[metric].mean()
                
                top_means.append(top_mean)
                bottom_means.append(bottom_mean)
                sample_means.append(sample_mean)
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        axes = axes.flatten()
        
        colors = {
            'Top 10': '#55A868',
            'Bottom 10': '#C44E52',
            'Sample Mean': '#4C72B0'
        }
        
        for i, (metric, label, top, bottom, sample) in enumerate(zip(metrics, metric_labels, top_means, bottom_means, sample_means)):
            ax = axes[i]
            
            x = np.arange(3)
            width = 0.6
            
            bars = ax.bar(x, [top, bottom, sample], width, 
                         color=[colors['Top 10'], colors['Bottom 10'], colors['Sample Mean']],
                         edgecolor='white', linewidth=1)
            
            ax.set_xticks(x)
            ax.set_xticklabels(['Top 10', 'Bottom 10', '全样本'], fontsize=11)
            ax.set_ylabel('均值', fontsize=11)
            ax.set_title(f'{label}对比', fontsize=13, fontweight='bold')
            
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.2f}',
                       ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
        
        plt.suptitle('Top 10 vs Bottom 10 各指标对比', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        output_path = self.output_dir / "top_vs_bottom_comparison.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✓ 已生成: {output_path}")
        print("  对比维度: 授予比例、参与比例、折扣率、有效期")
    
    def run(self):
        print("\n" + "#" * 80)
        print("#     排名分析可视化")
        print("#     研究主题：上市公司股权激励慷慨度评价体系")
        print("#" * 80)
        
        self.plot_top20_bar()
        self.plot_bottom20_bar()
        self.plot_score_distribution()
        self.plot_boxplot()
        self.plot_radar_chart()
        self.plot_top_vs_bottom_comparison()
        
        print("\n" + "#" * 80)
        print("#     所有可视化图片已生成完成！")
        print("#" * 80)
        
        print(f"\n输出目录: {self.output_dir}")
        print("生成的图片:")
        print("  1. top20_generosity_companies.png")
        print("  2. bottom20_generosity_companies.png")
        print("  3. generosity_score_distribution.png")
        print("  4. generosity_score_boxplot.png")
        print("  5. top10_radar_chart.png")
        print("  6. top_vs_bottom_comparison.png")


if __name__ == "__main__":
    visualizer = RankingVisualizer()
    visualizer.run()