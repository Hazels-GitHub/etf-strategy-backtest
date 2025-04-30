import pandas as pd
import os

class ETFDataLoader:
    def __init__(self, file_path_dict, data_dir=""):
        """
        file_path_dict: dict, {ETF代碼: 檔案檔名（不含路徑）}
        data_dir: 字串，所有csv檔所在資料夾的路徑
        """
        self.file_path_dict = file_path_dict
        self.data_dir = data_dir
        self.price_df = self.load_data()

    def load_data(self):
        """
        整合所有ETF的Adj Close收盤價，合併成一張表
        """
        price_data = []

        for etf_code, filename in self.file_path_dict.items():
            full_path = os.path.join(self.data_dir, filename)  # <<<<< 這裡重要，組合完整路徑！

            if not os.path.exists(full_path):
                raise FileNotFoundError(f"找不到檔案：{full_path}")

            df = pd.read_csv(full_path)
            df = df[['Date', 'Adj Close']].copy()
            df.rename(columns={'Adj Close': etf_code}, inplace=True)
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            price_data.append(df)

        # 以Date為key進行outer join合併
        merged_price_df = pd.concat(price_data, axis=1, join='outer')
        merged_price_df.sort_index(inplace=True)
        return merged_price_df

if __name__ == "__main__":
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

    data_folder = "../data"  # 資料夾路徑

    # 建立資料載入器
    loader = ETFDataLoader(etf_files, data_dir=data_folder)

    # 抓出合併後的價格表
    price_df = loader.price_df

    # 查看一下前五筆資料
    print(price_df.head())
