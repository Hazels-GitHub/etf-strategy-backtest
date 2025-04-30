import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

class ResultReporter:
    def __init__(self, summary_df):
        self.df = summary_df.copy()

    def plot_avg_metrics_by_year(self):
        import seaborn as sns
        import matplotlib.pyplot as plt

        metrics = ["Annualized Return", "Annualized Volatility", "Sharpe Ratio", "Max Drawdown"]
        fig, axs = plt.subplots(2, 2, figsize=(12, 8))
        axs = axs.flatten()

        for i, metric in enumerate(metrics):
            sns.barplot(data=self.df, x="Mode", y=metric, hue="Years", ax=axs[i])
            axs[i].set_title(f"{metric} by Mode and Years")
            axs[i].grid(True)

        plt.tight_layout()
        plt.show()

    def plot_boxplot_by_year(self, metric):
        import seaborn as sns
        import matplotlib.pyplot as plt

        if metric not in self.df.columns:
            print(f"指標 {metric} 不存在")
            return

        plt.figure(figsize=(10, 6))
        sns.boxplot(data=self.df, x="Mode", y=metric, hue="Years")
        plt.title(f"{metric} by Strategy and Holding Years")
        plt.grid(True)
        plt.show()

    def plot_boxplot_by_label(self, metric):
        import seaborn as sns
        import matplotlib.pyplot as plt

        plt.figure(figsize=(10, 6))
        sns.boxplot(x="Label", y=metric, data=self.df)
        plt.title(f"{metric} by Mode + Years")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_trial_lines_by_year(self, metric="Annualized Return"):
        import matplotlib.pyplot as plt

        plt.figure(figsize=(10, 6))
        for (mode, year), group in self.df.groupby(["Mode", "Years"]):
            plt.plot(group["Trial"], group[metric], marker='o', label=f"{mode} ({year}Y)")

        plt.title(f"{metric} across Trials by Mode + Years")
        plt.xlabel("Trial")
        plt.ylabel(metric)
        plt.legend()
        plt.grid(True)
        plt.show()

    def export_all_outputs(self, output_dir="output"):
        import os

        os.makedirs(output_dir, exist_ok=True)

        # 1. 加上 Label 欄位（如未建立）
        if "Label" not in self.df.columns:
            self.df["Label"] = self.df["Mode"] + "_" + self.df["Years"].astype(str) + "Y"

        # 2. 匯出原始模擬資料
        self.df.to_csv(os.path.join(output_dir, "simulation_summary.csv"), index=False)

        # 3. 匯出平均績效表格
        grouped = self.df.groupby(["Mode", "Years"])[
            ["Annualized Return", "Annualized Volatility", "Sharpe Ratio", "Max Drawdown"]
        ].mean().round(4).reset_index()
        grouped.to_csv(os.path.join(output_dir, "summary_table.csv"), index=False)

        # 4. 儲存每個指標的 bar chart（Mode x Years）
        metrics = ["Annualized Return", "Annualized Volatility", "Sharpe Ratio", "Max Drawdown"]
        for metric in metrics:
            plt.figure(figsize=(8, 5))
            sns.barplot(data=self.df, x="Mode", y=metric, hue="Years")
            plt.title(f"{metric} by Strategy and Holding Years")
            plt.grid(True)
            plt.tight_layout()
            filename = f"{metric.lower().replace(' ', '_')}_barplot.png"
            plt.savefig(os.path.join(output_dir, filename))
            plt.close()

        # 5. 儲存 Sharpe Ratio boxplot（Label）
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=self.df, x="Label", y="Sharpe Ratio")
        plt.title("Sharpe Ratio by Strategy and Holding Period")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "sharpe_ratio_boxplot.png"))
        plt.close()

        print(f"✅ 所有圖表與表格已儲存至 {output_dir}/")
