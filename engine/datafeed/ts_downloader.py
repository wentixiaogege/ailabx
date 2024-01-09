# encoding:utf8
# 导入tushare
import pandas as pd
import tushare as ts

# 初始化pro接口
pro = ts.pro_api('854634d420c0b6aea2907030279da881519909692cf56e6f35c4718c')


def get_etf(code):
    # 拉取数据
    df = pro.fund_daily(**{
        "trade_date": "",
        "start_date": "",
        "end_date": "",
        "ts_code": code,
        "limit": "",
        "offset": ""
    }, fields=[
        "ts_code",
        "trade_date",
        "open",
        "high",
        "low",
        "close",
        "vol"
    ])

    df.rename(columns={'trade_date': 'date', 'ts_code': 'code', 'vol': 'volume'}, inplace=True)
    df.index = df['date']
    # 拉取数据
    df_adj = pro.fund_adj(**{
        "ts_code": code,
        "trade_date": "",
        "start_date": "",
        "end_date": "",
        "offset": "",
        "limit": ""
    }, fields=[
        "trade_date",
        "adj_factor"
    ])
    df_adj.rename(columns={'trade_date':'date'}, inplace=True)
    df_adj.index = df_adj['date']
    df =pd.concat([df,df_adj], axis=1)
    df.dropna(inplace=True)
    for col in ['open', 'high', 'low', 'close']:
        df[col] *= df['adj_factor']
    return df


if __name__ == '__main__':
    from engine.config import DATA_DIR_CSV

    for code in ['159928.SZ', '510050.SH', '512010.SH', '513100.SH', '518880.SH', '511220.SH', '511010.SH',
                 '161716.SZ']:
        df = get_etf(code)
        print(df)
        df.to_csv(DATA_DIR_CSV.joinpath(code + '.csv'), index=False)
