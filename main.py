import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scr.prepare_data import ETFDataLoader
from scr.portfolio_optimizer import PortfolioOptimizer
from scr.backtester import Backtester
from scr.simulator import Simulator
from scr.result_reporter import ResultReporter

def main():
    # 1. 資料準備
    data_dir = "data"
    etf_files = {
        'VTSMX': 'VTSMX.csv',
        'VGSIX': 'VGSIX.csv',
        'VTMGX': 'VTMGX.csv',
        'VEIEX': 'VEIEX.csv',
        'NAESX': 'NAESX.csv',
        'VIVAX': 'VIVAX.csv',
        'VISVX': 'VISVX.csv',
        'VIPSX': 'VIPSX.csv',
        'VBMFX': 'VBMFX.csv',
        'VFISX': 'VFISX.csv'
    }

    full_paths = {k: os.path.join(data_dir, v) for k, v in etf_files.items()}
    loader = ETFDataLoader(full_paths)
    price_df = loader.price_df
    # 2. 初始化模組
    asset_list = list(etf_files.keys())
    optimizer = PortfolioOptimizer(price_df)
    backtester = Backtester(optimizer, asset_list)
    simulator = Simulator(optimizer, backtester, asset_list, n_trials=5)

    # 執行三種模式 × 3年
    df_opt_3y = simulator.run_and_summarize(mode="optimal", holding_years=3)
    df_eq_3y = simulator.run_and_summarize(mode="equal", holding_years=3)
    df_hist_3y = simulator.run_and_summarize(mode="historical", holding_years=3)

    #  執行三種模式 × 5 年
    df_opt_5y = simulator.run_and_summarize(mode="optimal", holding_years=5)
    df_eq_5y = simulator.run_and_summarize(mode="equal", holding_years=5)
    df_hist_5y = simulator.run_and_summarize(mode="historical", holding_years=5)

    # 合併所有資料（含 3年與 5年）
    summary_df = pd.concat([
        df_opt_3y, df_eq_3y, df_hist_3y,
        df_opt_5y, df_eq_5y, df_hist_5y
    ], ignore_index=True)
    summary_df["Label"] = summary_df["Mode"] + "_" + summary_df["Years"].astype(str) + "Y"
    sns.boxplot(x="Label", y="Sharpe Ratio", data=summary_df)

    # 5. 成果報告
    reporter = ResultReporter(summary_df)
    reporter.plot_avg_metrics_by_year() # 分年期比較平均績效
    reporter.plot_boxplot_by_year("Sharpe Ratio") # 分年期 Sharpe Ratio 分布
    reporter.plot_trial_lines_by_year("Annualized Return")   # Trial-wise 報酬線（3年 vs 5年）
    reporter.plot_boxplot_by_label("Sharpe Ratio")
    reporter = ResultReporter(summary_df)
    reporter.export_all_outputs()


if __name__ == "__main__":
    main()
