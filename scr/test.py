from prepare_data import ETFDataLoader
from portfolio_optimizer import PortfolioOptimizer
from backtester import Backtester
from performance import PerformanceEvaluator

# 資料路徑
etf_files = {
    'VTSMX': 'VTSMX.csv',
    'VGSIX': 'VGSIX.csv',
    'VEIEX': 'VEIEX.csv',
    'VBMFX': 'VBMFX.csv',
    'VIPSX': 'VIPSX.csv',
    'NAESX': 'NAESX.csv'
}
data_folder = "../data"

# 1. 資料整合
loader = ETFDataLoader(etf_files, data_dir=data_folder)
price_df = loader.price_df

# 2. 建 optimizer
optimizer = PortfolioOptimizer(price_df)
asset_list = list(etf_files.keys())

# 3. 建 backtester
backtester = Backtester(optimizer, asset_list)

# 4. 跑回測（你可以改起始日和年限）
portfolio_returns_opt = backtester.run_backtest("2010-01-01", "2015-01-01", allow_short=False, equal_weight=False)
portfolio_returns_eq = backtester.run_backtest("2010-01-01", "2015-01-01", allow_short=False, equal_weight=True)

# 5. 評估績效
evaluator_opt = PerformanceEvaluator(portfolio_returns_opt)
evaluator_eq = PerformanceEvaluator(portfolio_returns_eq)

# 6. 顯示
print("最適權重績效：")
print(evaluator_opt.summary())

print("等權重績效：")
print(evaluator_eq.summary())
