import numpy as np
import pandas as pd


class PerformanceEvaluator:
    def __init__(self, returns_series):
        self.returns = returns_series.dropna()
        self.n_days = len(self.returns)

    def compute_annualized_return(self):
        cumulative_return = (1 + self.returns).prod() - 1
        annualized_return = (1 + cumulative_return) ** (252 / self.n_days) - 1
        return annualized_return

    def compute_annualized_volatility(self):
        annualized_volatility = self.returns.std() * np.sqrt(252)
        return annualized_volatility

    def compute_sharpe_ratio(self, risk_free_rate=0):
        ann_return = self.compute_annualized_return()
        ann_vol = self.compute_annualized_volatility()

        # 安全轉換為純 float 數字
        if isinstance(ann_vol, pd.Series):
            if len(ann_vol) == 1:
                ann_vol = ann_vol.iloc[0]
            else:
                raise ValueError(f"ann_vol 為多個值的 Series，長度 = {len(ann_vol)}，應該是一個單一值")

        if ann_vol != 0:
            sharpe_ratio = (ann_return - risk_free_rate) / ann_vol
        else:
            sharpe_ratio = np.nan

        return sharpe_ratio

    def compute_max_drawdown(self):
        cumulative_nav = (1 + self.returns).cumprod()
        historical_max = cumulative_nav.cummax()
        drawdowns = (cumulative_nav - historical_max) / historical_max
        max_drawdown = drawdowns.min()
        return max_drawdown

    def summary(self):
        """
        一次輸出完整的績效指標
        """
        return {
            'Annualized Return': self.compute_annualized_return(),
            'Annualized Volatility': self.compute_annualized_volatility(),
            'Sharpe Ratio': self.compute_sharpe_ratio(),
            'Max Drawdown': self.compute_max_drawdown()
        }



if __name__ == "__main__":
    import pandas as pd
    test_returns = pd.Series([0.01, -0.005, 0.007, 0.002, -0.003])
    evaluator = PerformanceEvaluator(test_returns)
    print("績效摘要：")
    print(evaluator.compute_annualized_return())
    print(evaluator.compute_annualized_volatility())
    print(evaluator.compute_sharpe_ratio())
    print(evaluator.compute_max_drawdown())
    print(evaluator.summary())

