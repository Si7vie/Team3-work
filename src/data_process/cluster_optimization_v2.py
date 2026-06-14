#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 7.1：聚类模型优化（Cluster Analysis Revision）
研究主题：构建上市公司股权激励慷慨度评价体系

优化内容：
- 不再使用 Generosity Score 作为聚类输入
- 仅使用5个原始指标进行聚类
- 使用 StandardScaler 标准化
- Elbow Method + Silhouette Score 选择最佳K
- 根据数据特征自动命名Cluster
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'STHeiti', 'WenQuanYi Micro Hei']
plt.rcParams['axes.unicode_minus'] = False

class ClusterOptimizer:
    def __init__(self, output_dir: str = "cluster_optimization_output_v2"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.entropy_path = "normalization_output_v2/entropy_input_data.csv"
        self.cleaned_path = "data_cleaning_output_v3/cleaned_equity_incentive_data.csv"
        self.ranking_path = "ranking_final_output_v2/generosity_ranking_final.csv"
        
        print(f"输出目录: {output_dir}")
        self.load_data()
    
    def load_data(self):
        print("加载数据文件...")
        
        if Path(self.entropy_path).exists():
            self.df_entropy = pd.read_csv(self.entropy_path, encoding='utf-8-sig')
            print(f"✓ entropy_input_data.csv: {len(self.df_entropy)} 条")
        else:
            raise FileNotFoundError(f"文件不存在: {self.entropy_path}")
        
        if Path(self.cleaned_path).exists():
            self.df_cleaned = pd.read_csv(self.cleaned_path, encoding='utf-8-sig')
            print(f"✓ cleaned_equity_incentive_data.csv: {len(self.df_cleaned)} 条")
        else:
            raise FileNotFoundError(f"文件不存在: {self.cleaned_path}")
        
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
        
        print(f"\n聚类输入变量: {self.core_vars}")
        print("  (注意: Generosity Score 不参与聚类，仅用于结果对比)")
    
    def print_separator(self, title: str):
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80 + "\n")
    
    def step1_select_variables(self):
        self.print_separator("一、重新选择聚类输入变量")
        
        print("聚类输入变量（仅5个原始指标）:")
        print("-" * 60)
        
        X_raw = self.df_entropy[self.core_vars].copy()
        
        print("\n各指标统计:")
        print("-" * 80)
        print(f"{'指标':<20} | {'均值':<12} | {'标准差':<12} | {'最小值':<12} | {'最大值':<12}")
        print("-" * 80)
        
        for var in self.core_vars:
            print(f"{var:<20} | {X_raw[var].mean():<12.4f} | {X_raw[var].std():<12.4f} | {X_raw[var].min():<12.4f} | {X_raw[var].max():<12.4f}")
        
        print("-" * 80)
        
        print("\n✓ 已选择5个原始指标作为聚类输入")
        print("  不包含 Generosity Score，避免信息重复")
        
        self.X_raw = X_raw
        
        return X_raw
    
    def step2_standardization(self):
        self.print_separator("二、数据标准化")
        
        print("使用 StandardScaler 进行标准化...")
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(self.X_raw)
        
        df_scaled = pd.DataFrame(X_scaled, columns=self.core_vars)
        
        print("\n标准化后统计:")
        print("-" * 80)
        print(f"{'指标':<20} | {'均值':<12} | {'标准差':<12} | {'最小值':<12} | {'最大值':<12}")
        print("-" * 80)
        
        for var in self.core_vars:
            print(f"{var:<20} | {df_scaled[var].mean():<12.4f} | {df_scaled[var].std():<12.4f} | {df_scaled[var].min():<12.4f} | {df_scaled[var].max():<12.4f}")
        
        print("-" * 80)
        print("\n✓ 标准化完成 (均值≈0, 标准差≈1)")
        
        df_standardized = pd.concat([
            self.df_cleaned[['company_name', 'stock_code']],
            df_scaled
        ], axis=1)
        
        df_standardized.to_csv(self.output_dir / "cluster_standardized_data.csv", index=False, encoding='utf-8-sig')
        print(f"✓ 已保存: {self.output_dir / 'cluster_standardized_data.csv'}")
        
        self.X_scaled = X_scaled
        self.df_scaled = df_scaled
        
        return df_standardized
    
    def step3_evaluate_k(self):
        self.print_separator("三、K-Means聚类 - 最佳K选择")
        
        print("尝试 K = 2, 3, 4, 5...")
        print("-" * 60)
        
        k_values = [2, 3, 4, 5]
        sse_values = []
        silhouette_values = []
        
        for k in k_values:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(self.X_scaled)
            
            sse = kmeans.inertia_
            sse_values.append(sse)
            
            if k > 1:
                sil = silhouette_score(self.X_scaled, labels)
            else:
                sil = 0
            silhouette_values.append(sil)
            
            print(f"  K={k}: SSE={sse:.2f}, Silhouette={sil:.4f}")
        
        print("-" * 60)
        
        sse_diffs = np.diff(sse_values)
        sse_diffs2 = np.diff(sse_diffs)
        
        if len(sse_diffs2) > 0:
            elbow_idx = np.argmax(sse_diffs2)
        else:
            elbow_idx = 1
        
        sil_idx = np.argmax(silhouette_values)
        
        print("\nElbow Method 分析:")
        print(f"  SSE 下降幅度最大在 K={k_values[elbow_idx + 1]}")
        
        print("\nSilhouette Score 分析:")
        print(f"  Silhouette Score 最高在 K={k_values[sil_idx]}")
        
        if sil_idx == elbow_idx:
            best_k = k_values[sil_idx]
            print(f"\n✓ 两种方法一致，选择 K={best_k}")
        else:
            if silhouette_values[sil_idx] - silhouette_values[elbow_idx] > 0.05:
                best_k = k_values[sil_idx]
                print(f"\n✓ Silhouette Score 差异较大，选择 K={best_k}")
            else:
                best_k = k_values[elbow_idx]
                print(f"\n✓ 综合考虑，选择 K={best_k}")
        
        df_evaluation = pd.DataFrame({
            'K': k_values,
            'SSE': sse_values,
            'Silhouette Score': silhouette_values
        })
        
        df_evaluation.to_csv(self.output_dir / "cluster_evaluation.csv", index=False, encoding='utf-8-sig')
        print(f"✓ 已保存: {self.output_dir / 'cluster_evaluation.csv'}")
        
        self.best_k = best_k
        self.k_values = k_values
        self.sse_values = sse_values
        self.silhouette_values = silhouette_values
        
        self._plot_k_evaluation()
        
        return df_evaluation, best_k
    
    def _plot_k_evaluation(self):
        fig_dir = self.output_dir / "figures"
        fig_dir.mkdir(exist_ok=True)
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        ax1 = axes[0]
        ax1.plot(self.k_values, self.sse_values, 'o-', linewidth=2, markersize=8, color='#4C72B0')
        ax1.set_xlabel('K (Number of Clusters)', fontsize=11)
        ax1.set_ylabel('SSE (Within-Cluster Sum of Squares)', fontsize=11)
        ax1.set_title('Elbow Method - SSE vs K', fontsize=13, fontweight='bold')
        ax1.set_xticks(self.k_values)
        ax1.grid(alpha=0.3)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        
        ax2 = axes[1]
        ax2.plot(self.k_values, self.silhouette_values, 'o-', linewidth=2, markersize=8, color='#DD8452')
        ax2.set_xlabel('K (Number of Clusters)', fontsize=11)
        ax2.set_ylabel('Silhouette Score', fontsize=11)
        ax2.set_title('Silhouette Score vs K', fontsize=13, fontweight='bold')
        ax2.set_xticks(self.k_values)
        ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax2.grid(alpha=0.3)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(fig_dir / "k_evaluation.png", dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"  - 已生成: k_evaluation.png")
    
    def step4_generate_clusters(self):
        self.print_separator("四、重新生成聚类结果")
        
        print(f"使用 K={self.best_k} 进行K-Means聚类...")
        
        kmeans = KMeans(n_clusters=self.best_k, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(self.X_scaled)
        
        df_cluster = pd.concat([
            self.df_cleaned[['company_name', 'stock_code']],
            pd.DataFrame({'Cluster': cluster_labels})
        ], axis=1)
        
        print("\n聚类结果统计:")
        print("-" * 50)
        
        cluster_counts = df_cluster['Cluster'].value_counts().sort_index()
        for cluster_id, count in cluster_counts.items():
            print(f"  Cluster {int(cluster_id)}: {count} 家公司")
        
        print("-" * 50)
        
        df_cluster.to_csv(self.output_dir / "cluster_result_v2.csv", index=False, encoding='utf-8-sig')
        print(f"\n✓ 已保存: {self.output_dir / 'cluster_result_v2.csv'}")
        
        self.df_cluster = df_cluster
        self.cluster_labels = cluster_labels
        
        return df_cluster
    
    def step5_calculate_profiles(self):
        self.print_separator("五、计算每个Cluster画像")
        
        print("合并数据进行画像分析...")
        
        df_merged = pd.concat([
            self.df_cleaned[['company_name', 'stock_code']],
            self.df_entropy[self.core_vars],
            pd.DataFrame({'Cluster': self.cluster_labels}),
            self.df_ranking[['Generosity Score']]
        ], axis=1)
        
        print("\n计算各Cluster指标均值...")
        print("-" * 120)
        print(f"{'Cluster':<10} | {'Count':<8} | {'grant_ratio':<12} | {'participant_ratio':<18} | {'discount_rate':<12} | {'waiting_period_adj':<18} | {'validity_period':<14} | {'Generosity Score':<16}")
        print("-" * 120)
        
        cluster_profiles = []
        
        for cluster_id in sorted(df_merged['Cluster'].unique()):
            df_c = df_merged[df_merged['Cluster'] == cluster_id]
            
            profile = {
                'Cluster': int(cluster_id),
                'Count': len(df_c),
                'grant_ratio_mean': df_c['grant_ratio'].mean(),
                'participant_ratio_mean': df_c['participant_ratio'].mean(),
                'discount_rate_mean': df_c['discount_rate'].mean(),
                'waiting_period_adj_mean': df_c['waiting_period_adj'].mean(),
                'validity_period_mean': df_c['validity_period'].mean(),
                'generosity_score_mean': df_c['Generosity Score'].mean()
            }
            cluster_profiles.append(profile)
            
            gr_mean = profile['grant_ratio_mean']
            pr_mean = profile['participant_ratio_mean']
            dr_mean = profile['discount_rate_mean']
            wp_mean = profile['waiting_period_adj_mean']
            vp_mean = profile['validity_period_mean']
            gs_mean = profile['generosity_score_mean']
            
            print(f"Cluster {int(cluster_id):<4} | {len(df_c):<8} | {gr_mean:<12.4f} | {pr_mean:<18.4f} | {dr_mean:<12.4f} | {wp_mean:<18.4f} | {vp_mean:<14.4f} | {gs_mean:<16.4f}")
        
        print("-" * 120)
        
        df_profile = pd.DataFrame(cluster_profiles)
        df_profile.to_csv(self.output_dir / "cluster_profile_v2.csv", index=False, encoding='utf-8-sig')
        print(f"\n✓ 已保存: {self.output_dir / 'cluster_profile_v2.csv'}")
        
        self.df_profile = df_profile
        self.df_merged = df_merged
        
        return df_profile
    
    def step6_auto_naming(self):
        self.print_separator("六、自动命名Cluster")
        
        print("根据数据特征自动命名Cluster...")
        print("-" * 80)
        
        overall_means = {
            'grant_ratio': self.df_merged['grant_ratio'].mean(),
            'participant_ratio': self.df_merged['participant_ratio'].mean(),
            'discount_rate': self.df_merged['discount_rate'].mean(),
            'waiting_period_adj': self.df_merged['waiting_period_adj'].mean(),
            'validity_period': self.df_merged['validity_period'].mean()
        }
        
        print(f"\n全样本均值 (标准化后):")
        for key, val in overall_means.items():
            print(f"  {key}: {val:.4f}")
        
        cluster_names = {}
        cluster_descriptions = {}
        
        for idx, profile in self.df_profile.iterrows():
            cid = int(profile['Cluster'])
            gr = profile['grant_ratio_mean']
            pr = profile['participant_ratio_mean']
            dr = profile['discount_rate_mean']
            wp = profile['waiting_period_adj_mean']
            vp = profile['validity_period_mean']
            gs = profile['generosity_score_mean']
            
            gr_high = gr > overall_means['grant_ratio'] * 1.3
            gr_low = gr < overall_means['grant_ratio'] * 0.7
            
            pr_high = pr > overall_means['participant_ratio'] * 1.3
            pr_low = pr < overall_means['participant_ratio'] * 0.7
            
            dr_high = dr > overall_means['discount_rate'] * 1.3
            dr_low = dr < overall_means['discount_rate'] * 0.7
            
            wp_high = wp > overall_means['waiting_period_adj'] * 1.2
            wp_low = wp < overall_means['waiting_period_adj'] * 0.8
            
            vp_high = vp > overall_means['validity_period'] * 1.2
            vp_low = vp < overall_means['validity_period'] * 0.8
            
            name = ""
            desc = ""
            
            if pr_high and gr_high:
                if vp_high:
                    name = "全面高慷慨度型"
                    desc = "高授予比例、高覆盖广度、长期有效期，全面体现慷慨度"
                elif wp_high:
                    name = "高覆盖即时激励型"
                    desc = "高授予比例、高覆盖广度、等待期短，激励即时性强"
                else:
                    name = "高覆盖核心激励型"
                    desc = "高授予比例、高覆盖广度，但时间约束一般"
            elif pr_high:
                if vp_high:
                    name = "高覆盖长期型"
                    desc = "覆盖广度高，有效期长，适合长期激励"
                elif dr_high:
                    name = "高覆盖高折扣型"
                    desc = "覆盖广度高，折扣力度大，员工参与度高"
                else:
                    name = "高覆盖广度型"
                    desc = "让更多员工参与股权激励，但其他维度一般"
            elif gr_high:
                if dr_high:
                    name = "高规模高折扣型"
                    desc = "授予比例高，折扣力度大，对核心员工激励强"
                elif vp_high:
                    name = "高规模长期型"
                    desc = "授予比例高，有效期长，针对核心群体的长期激励"
                else:
                    name = "高授予规模型"
                    desc = "授予比例高，但覆盖广度有限"
            elif dr_high:
                if wp_high:
                    name = "高折扣即时型"
                    desc = "折扣力度大，等待期短，激励效果立竿见影"
                else:
                    name = "价格优惠型"
                    desc = "折扣力度大，员工获得实惠多"
            elif vp_high:
                if wp_high:
                    name = "长期友好型"
                    desc = "有效期长，等待期短，时间维度非常友好"
                else:
                    name = "长期激励型"
                    desc = "有效期长，但等待期也可能较长"
            elif wp_high:
                name = "即时激励型"
                desc = "等待期短，员工能较快获得收益"
            else:
                if pr_low and gr_low and dr_low:
                    name = "保守激励型"
                    desc = "各维度均低于平均，激励策略偏保守"
                else:
                    name = "均衡型"
                    desc = "各维度均衡，无特别突出的特征"
            
            cluster_names[cid] = name
            cluster_descriptions[cid] = desc
            
            print(f"\nCluster {cid} ({int(profile['Count'])} 家公司):")
            print(f"  Generosity Score: {gs:.4f}")
            print(f"  名称: {name}")
            print(f"  描述: {desc}")
            
            features = []
            if gr_high: features.append(f"grant_ratio高 (+{(gr/overall_means['grant_ratio']-1)*100:.1f}%)")
            if gr_low: features.append(f"grant_ratio低 ({(1-gr/overall_means['grant_ratio'])*100:.1f}%)")
            if pr_high: features.append(f"participant_ratio高 (+{(pr/overall_means['participant_ratio']-1)*100:.1f}%)")
            if pr_low: features.append(f"participant_ratio低 ({(1-pr/overall_means['participant_ratio'])*100:.1f}%)")
            if dr_high: features.append(f"discount_rate高 (+{(dr/overall_means['discount_rate']-1)*100:.1f}%)")
            if dr_low: features.append(f"discount_rate低 ({(1-dr/overall_means['discount_rate'])*100:.1f}%)")
            if wp_high: features.append(f"waiting_period_adj高 (+{(wp/overall_means['waiting_period_adj']-1)*100:.1f}%)")
            if wp_low: features.append(f"waiting_period_adj低 ({(1-wp/overall_means['waiting_period_adj'])*100:.1f}%)")
            if vp_high: features.append(f"validity_period高 (+{(vp/overall_means['validity_period']-1)*100:.1f}%)")
            if vp_low: features.append(f"validity_period低 ({(1-vp/overall_means['validity_period'])*100:.1f}%)")
            
            print(f"  特征: {', '.join(features)}")
        
        print("-" * 80)
        
        self.df_profile['Cluster_Name'] = self.df_profile['Cluster'].map(cluster_names)
        self.df_profile['Cluster_Description'] = self.df_profile['Cluster'].map(cluster_descriptions)
        
        self.df_profile.to_csv(self.output_dir / "cluster_profile_v2.csv", index=False, encoding='utf-8-sig')
        print(f"\n✓ 已更新: {self.output_dir / 'cluster_profile_v2.csv'}")
        
        self.cluster_names = cluster_names
        self.cluster_descriptions = cluster_descriptions
        
        return self.df_profile
    
    def step7_visualization(self):
        self.print_separator("七、可视化")
        
        fig_dir = self.output_dir / "figures"
        fig_dir.mkdir(exist_ok=True)
        
        print("生成可视化图片...")
        
        self._plot_pca_clusters(fig_dir)
        self._plot_cluster_radar(fig_dir)
        self._plot_cluster_profile_bar(fig_dir)
        self._plot_generosity_comparison(fig_dir)
        
        print(f"\n✓ 所有可视化图片已保存至: {fig_dir}")
    
    def _plot_pca_clusters(self, fig_dir):
        print("  - 生成: cluster_pca_visualization.png")
        
        pca = PCA(n_components=2, random_state=42)
        X_pca = pca.fit_transform(self.X_scaled)
        
        df_plot = pd.DataFrame({
            'PC1': X_pca[:, 0],
            'PC2': X_pca[:, 1],
            'Cluster': self.cluster_labels.astype(int),
            'company_name': self.df_cleaned['company_name'],
            'Generosity Score': self.df_ranking['Generosity Score']
        })
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 7))
        
        colors = plt.cm.tab10(np.linspace(0, 1, self.best_k))
        
        ax1 = axes[0]
        for cluster_id in sorted(df_plot['Cluster'].unique()):
            cluster_data = df_plot[df_plot['Cluster'] == cluster_id]
            name = self.cluster_names.get(cluster_id, f'Cluster {cluster_id}')
            ax1.scatter(cluster_data['PC1'], cluster_data['PC2'], 
                       color=colors[cluster_id], alpha=0.7, s=80, label=name, edgecolors='white', linewidth=0.5)
        
        ax1.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)', fontsize=11)
        ax1.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)', fontsize=11)
        ax1.set_title(f'K-Means聚类（K={self.best_k}）：PCA降维可视化', fontsize=13, fontweight='bold')
        ax1.legend(fontsize=9, bbox_to_anchor=(1.02, 1), loc='upper left')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        
        ax2 = axes[1]
        scatter = ax2.scatter(df_plot['PC1'], df_plot['PC2'], 
                            c=df_plot['Generosity Score'], cmap='RdYlGn', 
                            alpha=0.7, s=80, edgecolors='white', linewidth=0.5)
        
        cbar = plt.colorbar(scatter, ax=ax2)
        cbar.set_label('Generosity Score', fontsize=11)
        
        ax2.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)', fontsize=11)
        ax2.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)', fontsize=11)
        ax2.set_title('Generosity Score 分布', fontsize=13, fontweight='bold')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(fig_dir / "cluster_pca_visualization.png", dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
    
    def _plot_cluster_radar(self, fig_dir):
        print("  - 生成: cluster_radar_chart.png")
        
        metrics = ['grant_ratio', 'participant_ratio', 'discount_rate', 'waiting_period_adj', 'validity_period']
        metric_labels = ['授予比例', '参与比例', '折扣率', '等待期(正向化)', '有效期']
        
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        angles += angles[:1]
        
        n_clusters = len(self.df_profile)
        cols = 2
        rows = (n_clusters + 1) // 2
        
        fig, axes = plt.subplots(rows, cols, figsize=(14, 6 * rows), subplot_kw=dict(projection='polar'))
        if n_clusters == 1:
            axes = np.array([axes])
        axes = axes.flatten()
        
        colors = plt.cm.tab10(np.linspace(0, 1, self.best_k))
        
        for idx, (_, profile) in enumerate(self.df_profile.iterrows()):
            cid = int(profile['Cluster'])
            name = self.cluster_names.get(cid, f'Cluster {cid}')
            count = int(profile['Count'])
            gs = profile['generosity_score_mean']
            
            values = [
                profile['grant_ratio_mean'],
                profile['participant_ratio_mean'],
                profile['discount_rate_mean'],
                profile['waiting_period_adj_mean'],
                profile['validity_period_mean']
            ]
            values += values[:1]
            
            ax = axes[idx]
            ax.plot(angles, values, 'o-', linewidth=2, markersize=8, color=colors[idx])
            ax.fill(angles, values, alpha=0.25, color=colors[idx])
            
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(metric_labels, fontsize=9)
            ax.set_ylim(0, 1)
            ax.set_yticks([0.25, 0.5, 0.75])
            ax.set_yticklabels(['', '', ''])
            ax.set_title(f'{name}\n({count}家公司, Score: {gs:.4f})', fontsize=11, pad=10)
        
        for j in range(n_clusters, len(axes)):
            axes[j].axis('off')
        
        plt.suptitle(f'各Cluster指标雷达图（K={self.best_k}）', fontsize=15, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig(fig_dir / "cluster_radar_chart.png", dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
    
    def _plot_cluster_profile_bar(self, fig_dir):
        print("  - 生成: cluster_profile_comparison.png")
        
        metrics = ['grant_ratio_mean', 'participant_ratio_mean', 'discount_rate_mean', 
                  'waiting_period_adj_mean', 'validity_period_mean']
        metric_labels = ['授予比例', '参与比例', '折扣率', '等待期(正向化)', '有效期']
        
        n_clusters = len(self.df_profile)
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        bar_width = 0.15
        x = np.arange(len(metrics))
        
        colors = plt.cm.tab10(np.linspace(0, 1, n_clusters))
        
        for idx, (_, profile) in enumerate(self.df_profile.iterrows()):
            cid = int(profile['Cluster'])
            name = self.cluster_names.get(cid, f'Cluster {cid}')
            values = [profile[m] for m in metrics]
            
            bars = ax.bar(x + idx * bar_width, values, bar_width, 
                         label=name, color=colors[idx], alpha=0.8, edgecolor='white')
        
        ax.set_xlabel('指标', fontsize=11)
        ax.set_ylabel('标准化后均值', fontsize=11)
        ax.set_title(f'各Cluster指标对比（K={self.best_k}）', fontsize=13, fontweight='bold')
        ax.set_xticks(x + bar_width * (n_clusters - 1) / 2)
        ax.set_xticklabels(metric_labels, fontsize=10)
        ax.legend(fontsize=9, bbox_to_anchor=(1.02, 1), loc='upper left')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(fig_dir / "cluster_profile_comparison.png", dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
    
    def _plot_generosity_comparison(self, fig_dir):
        print("  - 生成: cluster_generosity_comparison.png")
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        cluster_labels_list = []
        score_values = []
        
        for idx, (_, profile) in enumerate(self.df_profile.iterrows()):
            cid = int(profile['Cluster'])
            name = self.cluster_names.get(cid, f'Cluster {cid}')
            cluster_labels_list.append(f'{name}\n({int(profile["Count"])}家)')
            score_values.append(profile['generosity_score_mean'])
        
        colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(score_values)))
        sorted_indices = np.argsort(score_values)
        
        bars = ax.barh(range(len(score_values)), 
                      [score_values[i] for i in sorted_indices],
                      color=[colors[i] for i in sorted_indices],
                      edgecolor='white', linewidth=1)
        
        ax.set_yticks(range(len(score_values)))
        ax.set_yticklabels([cluster_labels_list[i] for i in sorted_indices], fontsize=10)
        
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + 0.005, bar.get_y() + bar.get_height()/2,
                   f'{[score_values[j] for j in sorted_indices][i]:.4f}',
                   va='center', fontsize=10, fontweight='bold')
        
        ax.set_xlabel('平均 Generosity Score', fontsize=11)
        ax.set_title(f'各Cluster平均 Generosity Score 对比（K={self.best_k}）', fontsize=13, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(fig_dir / "cluster_generosity_comparison.png", dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
    
    def step8_generate_report(self):
        self.print_separator("八、输出分析报告")
        
        print("生成 cluster_analysis_v2.md...")
        
        overall_means = {
            'grant_ratio': self.df_merged['grant_ratio'].mean(),
            'participant_ratio': self.df_merged['participant_ratio'].mean(),
            'discount_rate': self.df_merged['discount_rate'].mean(),
            'waiting_period_adj': self.df_merged['waiting_period_adj'].mean(),
            'validity_period': self.df_merged['validity_period'].mean()
        }
        
        report_content = """# 聚类模型优化分析报告

## 优化背景

原聚类模型中不同Cluster的Generosity Score差异过小，原因可能是Generosity Score作为综合评价结果参与了聚类，导致信息重复。

## 优化方案

### 改进措施

1. **移除Generosity Score**：不再作为聚类输入变量
2. **仅使用5个原始指标**：
   - grant_ratio（授予比例）
   - participant_ratio（参与比例）
   - discount_rate（折扣率）
   - waiting_period_adj（等待期，已正向化）
   - validity_period（有效期）

3. **重新标准化**：使用StandardScaler
4. **综合选择最佳K**：Elbow Method + Silhouette Score

## 一、最佳K选择理由

### 聚类评估结果

| K | SSE | Silhouette Score |
|---|-----|------------------|
"""
        
        for k, sse, sil in zip(self.k_values, self.sse_values, self.silhouette_values):
            report_content += f"| {k} | {sse:.2f} | {sil:.4f} |\n"
        
        report_content += f"""
### 选择依据

1. **Elbow Method**: 观察SSE下降幅度
2. **Silhouette Score**: 评估聚类紧密度

**最终选择**: K = **{self.best_k}**

## 二、各Cluster特点

"""
        
        sorted_profile = self.df_profile.sort_values('generosity_score_mean', ascending=False)
        
        for _, profile in sorted_profile.iterrows():
            cid = int(profile['Cluster'])
            name = self.cluster_names.get(cid, f'Cluster {cid}')
            desc = self.cluster_descriptions.get(cid, '')
            count = int(profile['Count'])
            gs = profile['generosity_score_mean']
            
            report_content += f"""
### {name}

- **Cluster ID**: {cid}
- **公司数量**: {count} 家
- **平均Generosity Score**: {gs:.4f}
- **描述**: {desc}

| 指标 | Cluster均值 | 全样本均值 | 对比 |
|------|------------|-----------|------|
| grant_ratio | {profile['grant_ratio_mean']:.4f} | {overall_means['grant_ratio']:.4f} | {'+' if profile['grant_ratio_mean'] > overall_means['grant_ratio'] else ''}{(profile['grant_ratio_mean']/overall_means['grant_ratio']-1)*100:.1f}% |
| participant_ratio | {profile['participant_ratio_mean']:.4f} | {overall_means['participant_ratio']:.4f} | {'+' if profile['participant_ratio_mean'] > overall_means['participant_ratio'] else ''}{(profile['participant_ratio_mean']/overall_means['participant_ratio']-1)*100:.1f}% |
| discount_rate | {profile['discount_rate_mean']:.4f} | {overall_means['discount_rate']:.4f} | {'+' if profile['discount_rate_mean'] > overall_means['discount_rate'] else ''}{(profile['discount_rate_mean']/overall_means['discount_rate']-1)*100:.1f}% |
| waiting_period_adj | {profile['waiting_period_adj_mean']:.4f} | {overall_means['waiting_period_adj']:.4f} | {'+' if profile['waiting_period_adj_mean'] > overall_means['waiting_period_adj'] else ''}{(profile['waiting_period_adj_mean']/overall_means['waiting_period_adj']-1)*100:.1f}% |
| validity_period | {profile['validity_period_mean']:.4f} | {overall_means['validity_period']:.4f} | {'+' if profile['validity_period_mean'] > overall_means['validity_period'] else ''}{(profile['validity_period_mean']/overall_means['validity_period']-1)*100:.1f}% |

"""
        
        report_content += """
## 三、各Cluster Generosity Score比较

"""
        
        gs_sorted = sorted(zip(self.df_profile['Cluster'], self.df_profile['generosity_score_mean'], self.df_profile['Count']),
                          key=lambda x: x[1], reverse=True)
        
        for cid, gs, count in gs_sorted:
            name = self.cluster_names.get(int(cid), f'Cluster {cid}')
            report_content += f"1. **{name}**: {gs:.4f} ({int(count)} 家公司)\n"
        
        report_content += """
## 四、经济含义解释

### 为什么不同Cluster有不同的Generosity Score？

1. **高慷慨度Cluster**的特点：
   - 通常在**participant_ratio**（覆盖广度）和**grant_ratio**（授予规模）上表现突出
   - 这两个指标在熵权法中的权重最高（合计超过90%）
   - 因此这些维度的优势直接转化为高Generosity Score

2. **低慷慨度Cluster**的特点：
   - 往往在覆盖广度和授予规模上低于平均
   - 即使在其他维度（如折扣率、时间维度）有优势，但权重较低
   - 难以弥补核心维度的不足

3. **聚类的意义**：
   - 基于原始指标的聚类能够识别出真正的激励策略差异
   - Generosity Score是这些差异的综合量化结果
   - 两者相互印证，验证了评价体系的合理性

## 五、可视化说明

已生成以下可视化图片：

1. **k_evaluation.png**: K值选择评估（Elbow Method + Silhouette Score）
2. **cluster_pca_visualization.png**: 聚类PCA降维可视化
3. **cluster_radar_chart.png**: 各Cluster指标雷达图
4. **cluster_profile_comparison.png**: 各Cluster指标对比柱状图
5. **cluster_generosity_comparison.png**: 各Cluster平均Generosity Score对比

## 输出文件

1. `cluster_standardized_data.csv` - 标准化后的聚类输入数据
2. `cluster_evaluation.csv` - K值评估结果
3. `cluster_result_v2.csv` - 聚类结果
4. `cluster_profile_v2.csv` - 各Cluster画像（含自动命名）
5. `cluster_analysis_v2.md` - 本报告

---

**完成日期**: 2026年
"""
        
        with open(self.output_dir / "cluster_analysis_v2.md", "w", encoding="utf-8") as f:
            f.write(report_content)
        
        print(f"✓ 已保存: {self.output_dir / 'cluster_analysis_v2.md'}")
    
    def run(self):
        print("\n" + "#" * 80)
        print("#     Step 7.1: 聚类模型优化（Cluster Analysis Revision）")
        print("#     研究主题：上市公司股权激励慷慨度评价体系")
        print("#" * 80)
        
        self.step1_select_variables()
        self.step2_standardization()
        self.step3_evaluate_k()
        self.step4_generate_clusters()
        self.step5_calculate_profiles()
        self.step6_auto_naming()
        self.step7_visualization()
        self.step8_generate_report()
        
        print("\n" + "#" * 80)
        print("#     Step 7.1 完成！")
        print("#" * 80)
        
        print(f"\n输出目录: {self.output_dir}")


if __name__ == "__main__":
    optimizer = ClusterOptimizer()
    optimizer.run()