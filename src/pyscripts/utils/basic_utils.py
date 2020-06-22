import pandas as pd
import numpy as np
import os, pathlib, json, itertools
from sklearn.model_selection import StratifiedShuffleSplit

from os import listdir
from os.path import isfile, join

def get_files_with_name(filepath, name_flag):
    return [f for f in listdir(filepath) if isfile(join(filepath, f)) and name_flag in f]


def writeToTXT(file_name_with_path, _df):
    try:
        _df.to_csv(file_name_with_path, header=False, index=False, sep=' ')
    except FileNotFoundError:
        directory = os.path.dirname(file_name_with_path)
        pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
        print("Make folder ", directory)
        _df.to_csv(file_name_with_path, header=False, index=False, sep=' ')

def writeToCSV(file_name_with_path, _df):
    try:
        _df.to_csv(file_name_with_path, index=False)
    except FileNotFoundError:

        directory = os.path.dirname(file_name_with_path)
        pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
        print("Make folder ", directory)
        _df.to_csv(file_name_with_path, index=False)

def writeToJson(file_name_with_path, _data):
    directory = os.path.dirname(file_name_with_path)
    if not os.path.exists(directory):
        pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
        print("Make folder ", directory)
    with open(file_name_with_path, 'w') as fp:
        json.dump(_data, fp, indent=2)

def readFromJson(file_name_with_path, return_key=None):
    with open(file_name_with_path) as json_data:
        d = json.load(json_data)
    if return_key:
        return d[return_key]
    else:
        return d

def balance_split_train_test(_df, base_col, keep_cols, random_seed=0, test_ratio=0.3):
    X = _df[keep_cols]
    y = _df[base_col]

    sss = StratifiedShuffleSplit(n_splits=1, test_size=test_ratio, random_state=random_seed)

    for train_index, test_index in sss.split(X, y):
        X_train, X_test = X.loc[train_index, :], X.loc[test_index, :]
        y_train, y_test = y[train_index], y[test_index]
    return pd.concat([X_train, y_train], axis=1), pd.concat([X_test, y_test], axis=1)

def balance_split_train_test_inter(_df, base_col, keep_cols, random_seed=0, test_ratio=0.3):
    X = _df[keep_cols]
    y = _df[base_col]

    sss = StratifiedShuffleSplit(n_splits=1, test_size=test_ratio, random_state=random_seed)

    for train_index, test_index in sss.split(X, y):
        X_train, X_test = X.loc[train_index, :], X.loc[test_index, :]
        y_train, y_test = y[train_index], y[test_index]
    return pd.concat([X_train, y_train], axis=1), pd.concat([X_test, y_test], axis=1)


def select_balance_df(_df, _sort_col, return_ratio=0.7, quotas_on="GR", rand_input=0):
    sort_df = _df.sort_values(by=_sort_col, ascending=False).reset_index()
    group_list = list(sort_df[quotas_on].unique())
    return_df = pd.DataFrame()
    for gi in group_list:
        gi_df = sort_df[sort_df[quotas_on]==gi]
        gi_df = gi_df.sample(frac=return_ratio, random_state=rand_input).reset_index(drop=True)
        return_df = pd.concat([return_df, gi_df], axis=0)

    # if return_df.shape[0] != test_k:
    #     print("*** ", rand_input, return_df.shape[0])
    #     print("*** ", return_df[quotas_on].value_counts(normalize=True))

    return set(return_df["UID"])

def get_prediction_scores(file_path, run_timer, ranker):
    # return a dict in which key is the uuid and value is their prediction score
    # score is used to retrieve the relative order, not for other use!!!
    pred_latest_path = file_path + "/ranklib-experiments/" + ranker + "/"
    # retrieve the latest experiment folder
    sub_exp = [x for x in os.listdir(pred_latest_path) if "experiments_" in x]
    exp_suffix = max([os.path.join(pred_latest_path, d) for d in sub_exp], key=os.path.getmtime)[-15:]
    pred_latest_path = pred_latest_path + "experiments_" + exp_suffix + "/" + run_timer + "/predictions/prediction.txt"
    if os.path.exists(pred_latest_path):
        print("**** Reading pred at", pred_latest_path)
        with open(pred_latest_path, "r") as text_file:
            ranker_lines = text_file.read().splitlines()
        ranker_pred = {}
        for li in ranker_lines:
            li_res = li.split(" ")
            cur_id = li_res[2][0:li_res[2].find(";rel=")]
            ranker_pred[cur_id.replace("docid=", "")] = len(ranker_lines) - int(li_res[3]) # keep the ranking in the predictions
        return ranker_pred
    else:
        print("No prediction found for ", run_timer, " in ", pred_latest_path, "!\n")
        raise ValueError

def get_inter_size_dict(size_dict, inter_set):
    keys_level_1 = list(size_dict.keys())
    res_dict = {}
    for keys_level_2 in itertools.product(*[size_dict[k] for k in keys_level_1]):
        key_level_2 = ''.join(keys_level_2)
        res_dict[key_level_2] = np.prod([size_dict[key1][key2] for key1, key2 in zip(keys_level_1, key_level_2)])

        [res_dict.update(size_dict[key1]) for key1 in keys_level_1];
    # for intersectionality
    for key_level_2 in inter_set:
        delta = inter_set[key_level_2][0] * res_dict[key_level_2]
        res_dict[key_level_2] += delta
        res_dict[inter_set[key_level_2][1]] -= delta
    return res_dict

def get_quotas_count(_df):
    res_dict = {}
    for quotas_on in ["G", "R", "GR"]:
        res_dict.update(dict(_df[quotas_on].value_counts(normalize=True)))
    return res_dict

def get_quotas_df(_df, _sort_col, _eval_k, quotas_budget, quotas_on="GR"):
    res = _df.groupby(quotas_on).count()

    group_list = list(_df[quotas_on].unique())
    group_counts = _df[quotas_on].value_counts(sort=True)
    cur_g = group_counts.index[0]

    quotas_k = {x: int(_eval_k*quotas_budget[x]) for x in group_list}

    print1 = ("*****",sum(quotas_k.values()), _eval_k)
    if sum(quotas_k.values()) != _eval_k:
        if dict(group_counts)[cur_g] == quotas_k[cur_g]:
            for addi in range(_eval_k - sum(quotas_k.values())):
                cur_g = group_counts.index[-1-addi] # update to group have lowest count
                quotas_k[cur_g] = quotas_k[cur_g] + 1
        else:
             # group have highest count
             for addi in range(_eval_k - sum(quotas_k.values())):
                 cur_g = group_counts.index[addi]
                 quotas_k[cur_g] = quotas_k[cur_g] + 1

    print2 = ("***** after", sum(quotas_k.values()), _eval_k)
    if _eval_k == _df.shape[0]:
        sep_d = _df.groupby(quotas_on).apply(lambda x: x.sort_values(by=_sort_col, ascending=False)).reset_index(drop=True)
    else:
        sep_d = _df.groupby(quotas_on).apply(lambda x: x.sort_values(by=_sort_col, ascending=False).head(quotas_k[x[quotas_on].iloc[0]])).reset_index(drop=True)
    print3 = ("***** after group", sum(quotas_k.values()), _eval_k, sep_d.shape[0])

    if sep_d.shape[0] != _eval_k:
        print(_df.shape[0], _eval_k, _sort_col)
        print(print1)
        print(print2)
        print(print3)
        print(quotas_budget)
        print(quotas_k)
        print(res)
        exit()

    return sep_d


def get_sort_df(_sort_col, _df, _k, quotas_max=None):
    if "quotas" in _sort_col:
        sort_df = get_quotas_df(_df, _sort_col[0], _k, quotas_max, quotas_on=_sort_col.split("_")[-1])
    else:
        sort_df = _df.sort_values(by=_sort_col, ascending=False).head(_k)
    return sort_df
