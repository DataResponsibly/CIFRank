import pandas as pd
import math

def compute_k_recall(true_list, pred_list, batch_size = 10):
    if len(true_list):
        if batch_size == len(true_list):
            return len(set(true_list).intersection(pred_list)) / len(true_list)
        else:
            res = 0
            for i in range(batch_size, len(true_list)+1, batch_size):
                res += len(set(true_list[0:i]).intersection(pred_list[0:i])) / i
            return round(res / len(true_list), 3)
    else:
        return 0

def compute_ap(true_list, pred_list, k, batch_size=1):
    # if len(pred_list) != k:
    #     print("AP input wrong, not equal ", k)
    #     exit()
    if len(pred_list) > 0:
        res_ap = 0
        for i in range(batch_size, len(pred_list) + 1, batch_size):
            if pred_list[i - 1] in true_list:
                res_ap += (len(set(true_list[0:i]).intersection(pred_list[0:i])) / i)
        return round(res_ap / k, 3)
    else:
        if len(true_list) > 0:
            return 0
        else:
            return -1

def compute_score_util(top_k_IDS, _orig_df, _orig_sort_col, opt_u=None):
    if not opt_u:
        if len(top_k_IDS) > 0:
            opt_u = sum(_orig_df.head(len(top_k_IDS))[_orig_sort_col])
    if len(top_k_IDS) > 0:
        cur_u = sum([_orig_df[_orig_df["UID"] == x][_orig_sort_col].values[0] for x in top_k_IDS])
        return round(1-(cur_u/opt_u), 3)
    else:
        return -1

def KL_divergence(p_list, q_list, log_base=2):
    res = 0
    for pi, qi in zip(p_list, q_list):
        res += pi*math.log(pi/qi,log_base)
    return res


def compute_rKL(_top_df, _orig_df, sort_col=None, group_col="GR", cut_off=10, log_base=2):
    if sort_col: # random permutation within ties in _top_df
        print("!!!Ties in the ranking!!!")
        rand_top_df = pd.DataFrame(columns=list(_top_df.columns))
        for yi in _top_df[sort_col].unique():
            yi_df = _top_df[_top_df[sort_col]==yi].copy().sample(frac=1).reset_index(drop=True)
            rand_top_df = pd.concat([rand_top_df, yi_df])
    else:
        rand_top_df = _top_df.copy()
    base_quotas = dict(_orig_df[group_col].value_counts(normalize=True))
    res = 0
    for ci in range(cut_off, rand_top_df.shape[0], cut_off):
        ci_quotas = dict(rand_top_df.head(ci)[group_col].value_counts(normalize=True))
        ci_p_list = []
        ci_q_list = []
        for gi, gi_v in base_quotas.items():
            if gi in ci_quotas:
                ci_p_list.append(ci_quotas[gi])
            else:
                ci_p_list.append(0.001) # to compute the KL-diverfence for value 0
            if gi_v == 0:
                ci_q_list.append(0.001)
            else:
                ci_q_list.append(base_quotas[gi])
        res += KL_divergence(ci_p_list, ci_q_list, log_base=log_base) / math.log(ci + 1, log_base)
    return res



def compute_igf_ratio(top_k_IDS, _orig_df, _orig_sort_col):
    # assume _orig_df is sorted according to the _orig_sort_col
    cur_res = min(_orig_df[_orig_df["UID"].isin(top_k_IDS)][_orig_sort_col]) / max(_orig_df[~_orig_df["UID"].isin(top_k_IDS)][_orig_sort_col])
    if cur_res > 1:
        return 1
    else:
        return cur_res