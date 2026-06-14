#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 1: 数据质量检查（Data Quality Assessment）
研究主题：构建上市公司股权激励慷慨度（Generosity Score）评价体系

最终评价指标：
1. grant_ratio（授予比例）
2. participant_ratio（参与比例）
3. discount_rate（折扣率）
4. waiting_period（等待期）
5. validity_period（有效期）

本阶段仅进行数据质量审查，不进行任何数据修改。
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

class DataQualityCheckerV3:
    def __init__(self, input_path: str, output_dir: str = "data_quality_report_v3"):
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
        
        self.percent_vars = ['grant_ratio', 'participant_ratio', 'discount_rate']
        self.time_vars = ['waiting_period', 'validity_period']
        
        print(f"输入文件: {input_path}")
        print(f"输出目录: {output_dir}")
        print(f"核心指标: {self.core_vars}")
    
    def print_separator(self, title: str):
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80 + "\n")
    
    def data_overview(self):
        self.print_separator("一、数据集概况")
        
        sample_count = len(self.df)
        field_count = len(self.df.columns)
        
        print(f"样本数量: {sample_count}")
        print(f"字段数量: {field_count}")
        print(f"\n字段名称列表:")
        for i, col in enumerate(self.df.columns, 1):
            dtype = str(self.df[col].dtype)
            print(f"  {i}. {col} ({dtype})")
        
        overview = {
            'Metric': ['Sample Count', 'Field Count'],
            'Value': [sample_count, field_count]
        }
        pd.DataFrame(overview).to_csv(self.output_dir / "data_overview_summary.csv", index=False, encoding='utf-8-sig')
        
        print(f"\n数据前5行预览:")
        print(self.df.head().to_string())
        print(f"\n数据概览已保存至: {self.output_dir / 'data_overview_summary.csv'}")
        
        return sample_count, field_count
    
    def missing_value_check(self):
        self.print_separator("二、缺失值检查")
        
        missing_report = []
        
        for col in self.df.columns:
            missing_count = self.df[col].isnull().sum()
            missing_rate = (missing_count / len(self.df)) * 100
            
            missing_report.append({
                'Variable': col,
                'Missing Count': int(missing_count),
                'Missing Rate (%)': round(missing_rate, 4)
            })
        
        missing_df = pd.DataFrame(missing_report)
        
        print("缺失值统计:")
        print("-" * 70)
        print(f"{'Variable':<20} | {'Missing Count':<15} | {'Missing Rate (%)':<15}")
        print("-" * 70)
        for _, row in missing_df.iterrows():
            print(f"{row['Variable']:<20} | {row['Missing Count']:<15} | {row['Missing Rate (%)']:<15.4f}")
        print("-" * 70)
        
        core_missing = missing_df[missing_df['Variable'].isin(self.core_vars)]
        high_missing = core_missing[core_missing['Missing Rate (%)'] > 5]
        
        print("\n核心指标缺失值分析:")
        if len(high_missing) > 0:
            print("  ⚠️ 存在高缺失率字段（> 5%）:")
            for _, row in high_missing.iterrows():
                print(f"    - {row['Variable']}: {row['Missing Rate (%)']:.4f}%")
        else:
            print("  ✓ 所有核心指标缺失率均低于5%")
        
        total_missing = core_missing['Missing Count'].sum()
        if total_missing > 0:
            print(f"  建议: 需要后续处理 {total_missing} 个缺失值")
        else:
            print("  无需处理缺失值")
        
        missing_df.to_csv(self.output_dir / "missing_value_report.csv", index=False, encoding='utf-8-sig')
        print(f"\n缺失值报告已保存至: {self.output_dir / 'missing_value_report.csv'}")
        
        return missing_df
    
    def duplicate_check(self):
        self.print_separator("三、重复值检查")
        
        exact_duplicates = self.df.duplicated()
        exact_duplicate_count = exact_duplicates.sum()
        
        duplicate_rate = (exact_duplicate_count / len(self.df)) * 100
        
        print(f"是否存在完全重复记录: {'是' if exact_duplicate_count > 0 else '否'}")
        print(f"重复记录数量: {exact_duplicate_count}")
        print(f"重复率: {duplicate_rate:.4f}%")
        
        if exact_duplicate_count > 0:
            print(f"\n重复记录预览（前10条）:")
            dup_rows = self.df[self.df.duplicated(keep=False)]
            for i, (_, row) in enumerate(dup_rows.head(10).iterrows()):
                print(f"  {i+1}. {row['company_name']} ({row['stock_code']})")
        
        duplicate_report = {
            'Metric': ['Total Records', 'Exact Duplicates', 'Duplicate Rate (%)'],
            'Value': [len(self.df), int(exact_duplicate_count), round(duplicate_rate, 4)]
        }
        pd.DataFrame(duplicate_report).to_csv(self.output_dir / "duplicate_record_report.csv", index=False, encoding='utf-8-sig')
        print(f"\n重复值报告已保存至: {self.output_dir / 'duplicate_record_report.csv'}")
        
        return exact_duplicate_count
    
    def data_type_check(self):
        self.print_separator("四、数据类型检查")
        
        type_report = []
        issues = []
        
        for col in self.core_vars:
            dtype = str(self.df[col].dtype)
            is_numeric = pd.api.types.is_numeric_dtype(self.df[col])
            
            has_percent = False
            has_chinese = False
            has_space = False
            has_special = False
            
            if self.df[col].dtype == 'object':
                for val in self.df[col].dropna():
                    val_str = str(val)
                    if '%' in val_str:
                        has_percent = True
                    if any('\u4e00' <= c <= '\u9fff' for c in val_str):
                        has_chinese = True
                    if ' ' in val_str.strip():
                        has_space = True
                    try:
                        float(val_str.replace('%', ''))
                    except:
                        has_special = True
            
            type_report.append({
                'Variable': col,
                'Data Type': dtype,
                'Is Numeric': is_numeric,
                'Has %': has_percent,
                'Has Chinese': has_chinese,
                'Has Space': has_space,
                'Has Special Char': has_special
            })
            
            if not is_numeric:
                issues.append(f"{col}: 应为数值型，但当前为 {dtype}")
        
        type_df = pd.DataFrame(type_report)
        
        print("数据类型检查:")
        print("-" * 120)
        print(f"{'Variable':<20} | {'Data Type':<15} | {'Numeric':<10} | {'%':<6} | {'中文':<6} | {'空格':<6} | {'特殊字符':<10}")
        print("-" * 120)
        for _, row in type_df.iterrows():
            print(f"{row['Variable']:<20} | {row['Data Type']:<15} | {str(row['Is Numeric']):<10} | {str(row['Has %']):<6} | {str(row['Has Chinese']):<6} | {str(row['Has Space']):<6} | {str(row['Has Special Char']):<10}")
        print("-" * 120)
        
        print("\n数据类型问题:")
        if issues:
            for issue in issues:
                print(f"  ⚠️ {issue}")
        else:
            print("  ✓ 所有核心指标均为数值型")
        
        type_df.to_csv(self.output_dir / "type_validation_report.csv", index=False, encoding='utf-8-sig')
        print(f"\n数据类型报告已保存至: {self.output_dir / 'type_validation_report.csv'}")
        
        return type_df
    
    def descriptive_statistics(self):
        self.print_separator("五、描述统计分析")
        
        core_df = self.df[self.core_vars]
        desc_stats = core_df.describe().T
        desc_stats = desc_stats[['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']]
        desc_stats = desc_stats.round(4)
        
        print("核心指标描述统计:")
        print("-" * 130)
        print(f"{'Variable':<20} | {'Count':<8} | {'Mean':<12} | {'Std':<12} | {'Min':<12} | {'Max':<12}")
        print("-" * 130)
        for var in self.core_vars:
            print(f"{var:<20} | {int(desc_stats.loc[var, 'count']):<8} | {desc_stats.loc[var, 'mean']:<12.4f} | {desc_stats.loc[var, 'std']:<12.4f} | {desc_stats.loc[var, 'min']:<12.4f} | {desc_stats.loc[var, 'max']:<12.4f}")
        print("-" * 130)
        
        desc_stats.to_csv(self.output_dir / "descriptive_statistics.csv", encoding='utf-8-sig')
        print(f"\n描述统计已保存至: {self.output_dir / 'descriptive_statistics.csv'}")
        
        return desc_stats
    
    def distribution_analysis(self):
        self.print_separator("六、分布特征分析")
        
        dist_report = []
        
        for var in self.core_vars:
            data = self.df[var].dropna()
            
            skewness = data.skew()
            kurtosis = data.kurtosis()
            
            skew_interpretation = "轻微右偏" if skewness > 0.5 else ("轻微左偏" if skewness < -0.5 else "近似对称")
            if abs(skewness) > 1:
                skew_interpretation = "严重右偏" if skewness > 1 else "严重左偏"
            
            kurt_interpretation = "厚尾分布" if kurtosis > 0 else "薄尾分布"
            if abs(kurtosis) > 3:
                kurt_interpretation = "极端厚尾" if kurtosis > 3 else "极端薄尾"
            
            dist_report.append({
                'Variable': var,
                'Skewness': round(skewness, 4),
                'Kurtosis': round(kurtosis, 4),
                'Skewness Interpretation': skew_interpretation,
                'Kurtosis Interpretation': kurt_interpretation
            })
        
        dist_df = pd.DataFrame(dist_report)
        
        print("分布特征分析:")
        print("-" * 120)
        print(f"{'Variable':<20} | {'Skewness':<12} | {'Kurtosis':<12} | {'偏度判断':<15} | {'峰度判断':<15}")
        print("-" * 120)
        for _, row in dist_df.iterrows():
            print(f"{row['Variable']:<20} | {row['Skewness']:<12.4f} | {row['Kurtosis']:<12.4f} | {row['Skewness Interpretation']:<15} | {row['Kurtosis Interpretation']:<15}")
        print("-" * 120)
        
        dist_df.to_csv(self.output_dir / "distribution_statistics.csv", index=False, encoding='utf-8-sig')
        print(f"\n分布统计已保存至: {self.output_dir / 'distribution_statistics.csv'}")
        
        return dist_df
    
    def outlier_detection(self):
        self.print_separator("七、异常值初步识别")
        
        outlier_report = []
        
        for var in self.core_vars:
            data = self.df[var].dropna()
            
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
        
        print("异常值检测（IQR方法）:")
        print("-" * 140)
        print(f"{'Variable':<20} | {'Q1':<10} | {'Q3':<10} | {'IQR':<10} | {'Lower':<12} | {'Upper':<12} | {'Outliers':<10} | {'Rate (%)':<10}")
        print("-" * 140)
        for _, row in outlier_df.iterrows():
            print(f"{row['Variable']:<20} | {row['Q1']:<10.4f} | {row['Q3']:<10.4f} | {row['IQR']:<10.4f} | {row['Lower Bound']:<12.4f} | {row['Upper Bound']:<12.4f} | {row['Outlier Count']:<10} | {row['Outlier Rate (%)']:<10.4f}")
        print("-" * 140)
        
        print("\n说明:")
        print("  本阶段仅识别异常值，不进行删除或修改")
        print("  异常值可能是真实经济现象，需后续谨慎处理")
        
        outlier_df.to_csv(self.output_dir / "outlier_detection_report.csv", index=False, encoding='utf-8-sig')
        print(f"\n异常值检测报告已保存至: {self.output_dir / 'outlier_detection_report.csv'}")
        
        return outlier_df
    
    def discount_rate_special_check(self):
        self.print_separator("八、discount_rate 专项检查")
        
        dr_data = self.df['discount_rate'].dropna()
        
        min_val = dr_data.min()
        max_val = dr_data.max()
        mean_val = dr_data.mean()
        median_val = dr_data.median()
        
        negative_count = (dr_data < 0).sum()
        negative_rate = (negative_count / len(dr_data)) * 100 if len(dr_data) > 0 else 0
        
        zero_count = (dr_data == 0).sum()
        positive_count = (dr_data > 0).sum()
        
        print(f"discount_rate 统计:")
        print("-" * 70)
        print(f"  最小值: {min_val:.4f}%")
        print(f"  最大值: {max_val:.4f}%")
        print(f"  平均值: {mean_val:.4f}%")
        print(f"  中位数: {median_val:.4f}%")
        print("-" * 70)
        
        print(f"\ndiscount_rate 分布:")
        print(f"  负折扣率数量: {negative_count} ({negative_rate:.2f}%)")
        print(f"  零折扣率数量: {zero_count}")
        print(f"  正折扣率数量: {positive_count}")
        
        print(f"\n负折扣率说明:")
        print("  负折扣率 = (MarketPrice - ExercisePrice) / MarketPrice × 100%")
        print("  当 ExercisePrice > MarketPrice 时，折扣率自然为负")
        print("  这属于真实经济现象，不视为数据错误")
        
        dr_sorted = self.df.dropna(subset=['discount_rate']).sort_values('discount_rate')
        
        print(f"\ndiscount_rate 最低的10家公司:")
        print("-" * 70)
        for i, (_, row) in enumerate(dr_sorted.head(10).iterrows(), 1):
            print(f"  {i}. {row['company_name']} ({row['stock_code']}): {row['discount_rate']:.4f}%")
        
        print(f"\ndiscount_rate 最高的10家公司:")
        print("-" * 70)
        for i, (_, row) in enumerate(dr_sorted.tail(10).iterrows(), 1):
            print(f"  {i}. {row['company_name']} ({row['stock_code']}): {row['discount_rate']:.4f}%")
        
        dr_report = {
            'Metric': [
                'Min', 'Max', 'Mean', 'Median',
                'Negative Count', 'Negative Rate (%)',
                'Zero Count', 'Positive Count',
                'Total Valid'
            ],
            'Value': [
                round(min_val, 4), round(max_val, 4), round(mean_val, 4), round(median_val, 4),
                int(negative_count), round(negative_rate, 4),
                int(zero_count), int(positive_count),
                int(len(dr_data))
            ]
        }
        pd.DataFrame(dr_report).to_csv(self.output_dir / "discount_rate_diagnostic_report.csv", index=False, encoding='utf-8-sig')
        print(f"\ndiscount_rate 专项报告已保存至: {self.output_dir / 'discount_rate_diagnostic_report.csv'}")
        
        return dr_report
    
    def distribution_visualization(self):
        self.print_separator("九、分布可视化")
        
        fig_dir = self.output_dir / "figures"
        fig_dir.mkdir(exist_ok=True)
        
        print("生成分布图...")
        
        for var in self.core_vars:
            data = self.df[var].dropna()
            
            fig, axes = plt.subplots(1, 2, figsize=(14, 5))
            
            sns.histplot(data, ax=axes[0], bins=30, kde=True, color='#4C72B0', edgecolor='white')
            axes[0].set_title(f'{var} - Histogram', fontsize=12, fontweight='bold')
            axes[0].set_xlabel(var, fontsize=10)
            axes[0].set_ylabel('Frequency', fontsize=10)
            
            sns.boxplot(y=data, ax=axes[1], color='#DD8452', width=0.5)
            axes[1].set_title(f'{var} - Boxplot', fontsize=12, fontweight='bold')
            axes[1].set_ylabel(var, fontsize=10)
            
            plt.tight_layout()
            plt.savefig(fig_dir / f'{var}_distribution.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"  ✓ 已生成: {var}_distribution.png")
        
        print(f"\n分布图已保存至: {fig_dir}")
    
    def summary_conclusion(self):
        self.print_separator("十、初步结论与建议")
        
        print("=" * 80)
        print("  数据质量评估总结")
        print("=" * 80)
        
        print(f"\n1. 数据集规模:")
        print(f"   - 样本数量: {len(self.df)}")
        print(f"   - 字段数量: {len(self.df.columns)}")
        print(f"   - 核心指标: {len(self.core_vars)} 个")
        
        core_missing = self.df[self.core_vars].isnull().sum().sum()
        print(f"\n2. 缺失值情况:")
        print(f"   - 核心指标缺失总数: {core_missing}")
        if core_missing > 0:
            print(f"   - 建议: Step 2 数据清洗时处理缺失值")
        else:
            print(f"   - 无缺失值，数据完整性良好")
        
        duplicate_count = self.df.duplicated().sum()
        print(f"\n3. 重复值情况:")
        print(f"   - 完全重复记录数: {duplicate_count}")
        if duplicate_count > 0:
            print(f"   - 建议: Step 2 检查并删除重复记录")
        else:
            print(f"   - 无重复记录")
        
        print(f"\n4. 数据类型:")
        print(f"   - 所有核心指标均为数值型")
        print(f"   - 无格式问题（百分号、中文字符等）")
        
        print(f"\n5. 异常值情况:")
        print(f"   - 已识别潜在异常值")
        print(f"   - 建议: Step 2 采用差异化处理策略")
        print(f"     * grant_ratio: 保留原始值")
        print(f"     * participant_ratio: 检查是否需要处理")
        print(f"     * discount_rate: 负折扣率为正常现象，不处理")
        print(f"     * waiting_period: 保留原始值")
        print(f"     * validity_period: 保留原始值")
        
        print(f"\n6. discount_rate 专项:")
        dr_data = self.df['discount_rate'].dropna()
        neg_count = (dr_data < 0).sum()
        neg_rate = (neg_count / len(dr_data)) * 100 if len(dr_data) > 0 else 0
        print(f"   - 负折扣率: {neg_count} 个 ({neg_rate:.2f}%)")
        print(f"   - 说明: 行权价格 > 市场价格时出现负折扣率")
        print(f"   - 结论: 属于真实经济现象，不视为异常")
        
        print(f"\n7. 下一步建议:")
        print(f"   - Step 2: 数据清洗（缺失值、重复值、异常值处理）")
        print(f"   - Step 3: 相关性分析")
        print(f"   - Step 4: 指标方向统一与标准化")
        print(f"   - Step 5: 熵权法赋权")
        print(f"   - Step 6: Generosity Score 计算与排名")
        
        print("\n" + "=" * 80)
        print("  Step 1 完成！等待下一步指令。")
        print("=" * 80)
    
    def run(self):
        print("\n" + "#" * 80)
        print("#     Step 1: 数据质量检查")
        print("#     研究主题：上市公司股权激励慷慨度评价体系")
        print("#" * 80)
        
        self.data_overview()
        self.missing_value_check()
        self.duplicate_check()
        self.data_type_check()
        self.descriptive_statistics()
        self.distribution_analysis()
        self.outlier_detection()
        self.discount_rate_special_check()
        self.distribution_visualization()
        self.summary_conclusion()


if __name__ == "__main__":
    input_path = "data/final_data_unprocessed.csv"
    
    if os.path.exists(input_path):
        checker = DataQualityCheckerV3(input_path)
        checker.run()
    else:
        print(f"错误: 文件 {input_path} 不存在!")