import numpy as np
import pandas as pd
from scipy.optimize import minimize

class PortfolioOptimizer:
    def __init__(self, price_data):
        """
        初始化：接收已整合好的價格資料 DataFrame（Date 為 index，欄位為 ETF）
        """
        self.price_data = price_data
        self.returns = self.compute_returns()


    def get_common_date_range(self, etf_list):
        """
        找出所有選定ETF共同擁有資料的起始日與結束日
        """
        selected_prices = self.price_df[etf_list]
        # 找出每一檔ETF的有效日期
        valid_dates = selected_prices.dropna().index
        # 交集區間
        start_date = valid_dates.min()
        end_date = valid_dates.max()
        return start_date, end_date

    def compute_returns(self):
        """
        計算日報酬率
        """
        return self.price_data.pct_change(fill_method=None).dropna()
        return returns

    def estimate_parameters(self, start_date, end_date, asset_list=None):
        """
        從 returns 中挑出指定區間、指定資產，計算年化期望報酬率與共變異數
        """
        if asset_list is not None:
            selected_returns = self.returns[asset_list].loc[start_date:end_date]
        else:
            selected_returns = self.returns.loc[start_date:end_date]

        mu = selected_returns.mean() * 252
        sigma = selected_returns.cov() * 252

        return mu, sigma


    def optimize_portfolio(self, mu, sigma, allow_short=False):
        """
        計算最適投資組合權重
        allow_short: 是否允許放空
        """
        n_assets = len(mu)

        if allow_short:
            # 允許放空：直接用公式 Σ^-1 * μ
            inv_sigma = np.linalg.inv(sigma)
            raw_weights = inv_sigma @ mu
            weights = raw_weights / np.sum(raw_weights)  # Normalize to sum to 1
        else:
            # 不允許放空：需要用最適化求解

            # 目標函數（最大化 (w' * mu) / sqrt(w' * sigma * w)）
            # 由於scipy minimize是最小化，所以加上負號
            def objective(w):
                portfolio_return = w @ mu
                portfolio_volatility = np.sqrt(w @ sigma @ w)
                # 最大化 Sharpe Ratio -> 最小化負的 Sharpe Ratio
                return - portfolio_return / portfolio_volatility

            # 條件：權重總和=1
            constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})

            # 每個權重範圍：0 ~ 1
            bounds = tuple((0, 1) for _ in range(n_assets))

            # 初始猜測值：等權重
            initial_guess = np.ones(n_assets) / n_assets

            # 最小化
            result = minimize(objective, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)

            if not result.success:
                raise BaseException('Optimization failed!')

            weights = result.x

        return weights

    def get_equal_weight_portfolio(self, asset_list):
        """
        給定資產列表，回傳等權重組合的權重
        """
        n_assets = len(asset_list)
        weights = np.ones(n_assets) / n_assets
        return weights



