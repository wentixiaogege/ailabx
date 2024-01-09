import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime
from engine.ml.expr.expr_mgr import ExprMgr



def make_dataset(df, time_lags=5):
    expr = ExprMgr()
    expr.init()

    fields = []
    names = []

    fields += ["Corr($close/Ref($close,1), Log($volume/Ref($volume, 1)+1), 30)"]
    names += ["CORR30"]
    fields += ["Corr($close/Ref($close,1), Log($volume/Ref($volume, 1)+1), 60)"]
    names += ["CORR60"]

    fields += ["Std($close, 30)/$close"]
    names += ["STD30"]
    fields += ["Corr($close, Log($volume+1), 5)"]
    names += ["CORR5"]

    # fields += ["Resi($close, 10)/$close"]
    # names += ["RESI10"]
    # fields += ["Resi($close, 5)/$close"]
    # names += ["RESI5"]

    fields += ["Std($close, 5)/$close"]
    names += ["STD5"]
    fields += ["Std($close, 20)/$close"]
    names += ["STD20"]
    fields += ["Std($close, 60)/$close"]
    names += ["STD60"]

    fields += ["Ref($low, 0)/$close"]
    names += ["LOW0"]

    fields += [
        "Std(Abs($close/Ref($close, 1)-1)*$volume, 30)/(Mean(Abs($close/Ref($close, 1)-1)*$volume, 30)+1e-12)"
    ]
    names += ['WVMA30']

    fields += ["Ref($close, 5)/$close"]
    names += ["ROC5"]

    fields += ["(2*$close-$high-$low)/$open"]
    names += ['KSFT']

    fields += ["($close-Min($low, 5))/(Max($high, 5)-Min($low, 5)+1e-12)"]
    names += ["RSV5"]

    fields += ["($high-$low)/$open"]
    names += ['KLEN']

    for name, field in zip(names, fields):
        exp = expr.get_expression(field)
        se = exp.load(code)
        df[name] = se
    df['label'] = np.sign(df['close'].shift(-1).pct_change())
    #df_lag["volume_Direction"] = np.sign(df_lag["volume_Lag%s_Change" % str(time_lags)])
    print(names)
    return df.dropna(how='any')


def get_date_by_percent(start_date, end_date, percent):
    days = (end_date - start_date).days
    target_days = np.trunc(days * percent)
    target_date = start_date + dt.timedelta(days=target_days)
    # print days, target_days,target_date
    return target_date


def split_dataset(df, input_column_array, output_column, spllit_ratio):
    split_date = get_date_by_percent(df.index[0], df.index[df.shape[0] - 1], spllit_ratio)

    input_data = df[input_column_array]
    output_data = df[output_column]

    # Create training and test sets
    X_train = input_data[input_data.index < split_date]
    X_test = input_data[input_data.index >= split_date]
    Y_train = output_data[output_data.index < split_date]
    Y_test = output_data[output_data.index >= split_date]

    return X_train, X_test, Y_train, Y_test


if __name__ == '__main__':
    from engine.datafeed.datafeed_csv import CSVDatafeed
    from engine.config import DATA_DIR_CSV
    from engine.data_utils import to_backtrader_dataframe

    feed = CSVDatafeed()
    codes = ['000300.SH', 'SPX']
    for code in codes:
        feed.add_data(code, DATA_DIR_CSV.joinpath('{}.csv'.format(code)))

    code = 'SPX'
    time_lags = 5
    df = feed.get_df(code)
    df.index = pd.to_datetime(df.index)
    df_dataset = make_dataset(df, time_lags=time_lags)
    X_train, X_test, Y_train, Y_test = split_dataset(df_dataset,
                                                     ['CORR30', 'CORR60', 'STD30', 'CORR5', 'STD5', 'STD20', 'STD60', 'LOW0', 'WVMA30', 'ROC5', 'KSFT', 'RSV5', 'KLEN'],
                                                     "label", 0.85)
    print(X_train)
    print(X_test)

    from engine.ml.models import do_svm, do_random_forest, do_logistic_regression, test_predictor

    lr_classifier = do_logistic_regression(X_train, Y_train)
    lr_hit_ratio, lr_score = test_predictor(lr_classifier, X_test, Y_test)

    rf_classifier = do_random_forest(X_train, Y_train)
    rf_hit_ratio, rf_score = test_predictor(rf_classifier, X_test, Y_test)

    svm_classifier = do_svm(X_train, Y_train)
    svm_hit_ratio, svm_score = test_predictor(rf_classifier, X_test, Y_test)

    print("%s : Hit Ratio - Logistic Regreesion=%0.2f, RandomForest=%0.2f, SVM=%0.2f" % (
    'name', lr_hit_ratio, rf_hit_ratio, svm_hit_ratio))
