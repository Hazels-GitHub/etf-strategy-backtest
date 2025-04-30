import pandas as pd
import numpy as np

class Backtester:
    def __init__(self, optimizer, asset_list, rebalance_freq='6M'):
        self.optimizer = optimizer
        self.asset_list = asset_list
        self.rebalance_freq = rebalance_freq
        self.returns = optimizer.returns[asset_list]

    def run_backtest(self, start_date, end_date, allow_short=False, equal_weight=False):
        """
        回測主流程
        每個 rebalance 週期重新計算權重
        """
        # 初始化
        current_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        all_returns = []

        # 只取有資料的部分
        returns_df = self.returns.loc[start_date:end_date]

        while current_date < end_date:
            # 決定下一次rebalance的時間
            next_rebalance_date = current_date + pd.DateOffset(months=6)

            if next_rebalance_date > end_date:
                next_rebalance_date = end_date

            # 抓這一段期間內的資料
            period_returns = returns_df.loc[current_date:next_rebalance_date]

            if len(period_returns) == 0:
                break

            # 在current_date這天，重新估參數
            estimation_end_date = current_date - pd.Timedelta(days=1)
            estimation_start_date = estimation_end_date - pd.DateOffset(years=5)

            try:
                mu, sigma = self.optimizer.estimate_parameters(estimation_start_date, estimation_end_date,
                                                               self.asset_list)
            except:
                print(f"估計失敗，跳過 {current_date}")
                break

            # 根據設定決定權重
            if equal_weight:
                weights = self.optimizer.get_equal_weight_portfolio(self.asset_list)
            else:
                weights = self.optimizer.optimize_portfolio(mu, sigma, allow_short=allow_short)

            # 計算這段期間的投資組合報酬
            portfolio_returns = self.calculate_portfolio_return(weights, period_returns)

            # 存起來
            all_returns.append(portfolio_returns)

            # 移動到下一次rebalance
            current_date = next_rebalance_date

        # 把所有段落串起來成一條完整序列
        if all_returns:
            full_returns = pd.concat(all_returns)
            full_returns = full_returns.loc[start_date:end_date]  # 確保沒超過
            return full_returns
        else:
            return pd.Series(dtype=float)

    def calculate_portfolio_return(self, weights, returns_df):
        """
        給定權重與報酬率資料，計算組合的日報酬率序列
        """
        # weights shape: (n_assets,)
        # returns_df shape: (n_days, n_assets)

        # (n_days, n_assets) dot (n_assets,) -> (n_days,)
        portfolio_returns = returns_df @ weights

        return portfolio_returns

    def evaluate_performance(self, portfolio_returns):
        """
        給定投資組合日報酬率，計算各種績效指標
        """
        n_days = len(portfolio_returns)
        cumulative_return = (1 + portfolio_returns).prod() - 1
        annualized_return = (1 + cumulative_return) ** (252 / n_days) - 1

        annualized_volatility = portfolio_returns.std() * np.sqrt(252)

        if annualized_volatility != 0:
            sharpe_ratio = annualized_return / annualized_volatility
        else:
            sharpe_ratio = np.nan

        cumulative_nav = (1 + portfolio_returns).cumprod()
        historical_max = cumulative_nav.cummax()
        drawdowns = (cumulative_nav - historical_max) / historical_max
        max_drawdown = drawdowns.min()

        return {
            'Annualized Return': annualized_return,
            'Annualized Volatility': annualized_volatility,
            'Sharpe Ratio': sharpe_ratio,
            'Max Drawdown': max_drawdown
        }

