from arctic import Arctic, CHUNK_STORE


class ArcticDataFeed:
    def __init__(self, db_name='etf_quotes'):
        self.code_dfs = {}
        a = Arctic('localhost')
        a.initialize_library(db_name, lib_type=CHUNK_STORE)
        self.lib = a[db_name]

    def get_df(self, code, cols=None):
        if code in self.code_dfs.keys():
            return self.code_dfs[code]
        df = self.lib.read(code)
        self.code_dfs[code] = df
        return df


if __name__ == '__main__':
    df = ArcticDataFeed().get_df('562310.SH')
    print(df)
