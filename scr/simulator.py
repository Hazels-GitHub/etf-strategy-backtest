import numpy as np
import pandas as pd
from scr.performance import PerformanceEvaluator



class Simulator:
    def __init__(self, optimizer, backtester, asset_list, n_trials=5):
        self.optimizer = optimizer
        self.backtester = backtester
        self.asset_list = asset_list
        self.n_trials = n_trials
        self.returns = self.optimizer.returns[asset_list]
        self.start_dates = None  # 初始化為 None，稍後會由 get_valid_start_dates() 填入
        self.trading_days = 252 # 給全域使用的 252 個交易日

    def get_valid_start_dates(self, holding_years=3, lookback_years=5):
        """
        找出所有合法的模擬起始日（必須：可回測 holding_years + 可回顧 lookback_years）
        """
        # 1. 所有 ETF 的交集日（returns 內部就是有 dropna 過的報酬率交集）
        full_dates = self.returns.index

        # 2. 抓出：最早日 + 至少要留有過去 5 年資料空間 + 未來持有 N 年空間
        start_limit = full_dates[0] + pd.DateOffset(years=lookback_years)
        end_limit = full_dates[-1] - pd.DateOffset(years=holding_years)

        # 3. 篩選合法起始日
        valid_dates = full_dates[(full_dates >= start_limit) & (full_dates <= end_limit)]

        if len(valid_dates) < self.n_trials:
            raise ValueError("符合條件的起始日太少，請檢查資料是否完整")

        # 4. 隨機選擇 N 筆
        selected_start_dates = np.random.choice(valid_dates, size=self.n_trials, replace=False)
        selected_start_dates = pd.to_datetime(sorted(selected_start_dates))

        self.start_dates = selected_start_dates
        return selected_start_dates

    def run_simulation(self, mode="optimal", holding_years=3):
        """
        mode: "optimal" | "equal" | "historical"
        holding_years: 3 or 5
        return: list of dicts, 每筆模擬的績效摘要
        """
        if self.start_dates is None:
            self.get_valid_start_dates(holding_years=holding_years, lookback_years=5)

        results = []
        for start_date in self.start_dates:
            start_date = pd.to_datetime(start_date)
            end_date = start_date + pd.DateOffset(years=holding_years)

            # 模式③：historical ➜ 從過去推績效
            if mode == "historical":
                hist_start = start_date - pd.DateOffset(years=holding_years)
                past_returns = self.returns.loc[hist_start:start_date]

                combined_returns = past_returns.mean(axis=1)  # ✅ 確保是一維
                expected_days = holding_years * self.trading_days
                if len(combined_returns) < expected_days * 0.9:
                    print(f"{start_date.date()} 的過去資料太短（{len(combined_returns)} 天），略過")
                    continue

                evaluator = PerformanceEvaluator(combined_returns)
                results.append(evaluator.summary())

            # 模式① or ②：run_backtest
            else:
                allow_short = False
                equal_weight = (mode == "equal")
                port_returns = self.backtester.run_backtest(
                    start_date, end_date, allow_short=allow_short, equal_weight=equal_weight
                )

                if len(port_returns) == 0:
                    print(f"{start_date.date()} 無資料回測失敗，略過")
                    continue

                evaluator = PerformanceEvaluator(port_returns)
                results.append(evaluator.summary())

        return results

    def run_and_summarize(self, mode="optimal", holding_years=3):
        raw_results = self.run_simulation(mode=mode, holding_years=holding_years)
        df = pd.DataFrame(raw_results)
        df["Mode"] = mode
        df["Years"] = holding_years
        df["Trial"] = range(1, len(df) + 1)  # ✅ 新增 Trial 編號
        return df


