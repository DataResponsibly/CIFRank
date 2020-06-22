import pandas as pd
import os, argparse
from utils.eval_utils import compute_k_recall, compute_ap, compute_score_util, compute_rKL, compute_igf_ratio
from utils.basic_utils import writeToCSV, get_quotas_count, get_files_with_name, get_sort_df

def eval_counter_results(args):
    res_df = pd.DataFrame(columns=["run", "rank", "k", "group", args.measure])
    counter_path = os.path.join(args.repo_dir, "counterfactual_data") + "/" + args.data_flag + "/" + args.model_flag + "/"

    all_files = get_files_with_name(counter_path, args.file_n)

    for ri, fi in enumerate(all_files):
        # cur_run = int(fi.replace("_LTR", "").replace("R", "").replace(".csv",""))
        count_df = pd.read_csv(counter_path + fi)
        k_list = [int(x) for x in args.eval_ks.split(",")]

        seti_quotas = get_quotas_count(count_df)

        for rank_all in args.rankings.split(","):
            if "__" in rank_all:
                train_ranki = rank_all.split("__")[0]
            else:
                train_ranki = rank_all[0]
            orig_df = count_df.sort_values(by=train_ranki, ascending=False)
            # shift score to positive
            orig_df[train_ranki] = orig_df[train_ranki] + abs(orig_df[train_ranki].min())

            for ki in k_list:
                opt_u = sum(orig_df.head(ki)[train_ranki])
                res_row = [ri+1, rank_all, ki]
                all_row = res_row+["all"]

                if args.measure == "select_rate" :
                    all_row.append(1)

                sort_df = get_sort_df(rank_all, count_df, ki, quotas_max=seti_quotas)

                if args.measure == "score_utility":
                    all_row.append(compute_score_util(list(sort_df["UID"]), orig_df, train_ranki, opt_u))


                sort_df["rank"] = list(range(1, ki + 1))

                # compute jacard index and kendall-tau distance at top-k ranking
                top_orig = orig_df.head(ki)

                if args.measure == "sensitivity":
                    all_row.append(compute_k_recall(list(top_orig["UID"]), list(sort_df["UID"]), ki))

                if args.measure == "ap":
                    all_row.append(compute_ap(list(top_orig["UID"]), list(sort_df["UID"]), ki))

                if args.measure == "igf":
                    all_row.append(compute_igf_ratio(list(sort_df["UID"]), orig_df, train_ranki))

                if args.measure == "rKL":
                    if args.data_flag == "cm": # random permutate for COMPAS to avoid bias due to sorting with ties
                        all_row.append(compute_rKL(sort_df, orig_df, sort_col=rank_all, group_col=args.group_col))
                    else:
                        all_row.append(compute_rKL(sort_df, orig_df, group_col=args.group_col))

                res_df.loc[res_df.shape[0]] = all_row


                # group-level evaluation
                cur_quotas = dict(sort_df['GR'].value_counts(normalize=True))
                for gi in list(orig_df[args.group_col].unique()):
                    gi_row = res_row + [gi]
                    if args.measure == "select_rate":
                        # selection rate to rank inside top-k
                        if gi in cur_quotas:
                            gi_row.append(cur_quotas[gi] / seti_quotas[gi])
                        else:
                            gi_row.append(0)

                    gi_df = sort_df[sort_df["GR"] == gi]
                    gi_orig = orig_df[orig_df["GR"] == gi]

                    if args.measure == "score_utility":
                        gi_row.append(compute_score_util(list(gi_df["UID"]), gi_orig, train_ranki))


                    gi_orig_k = top_orig[top_orig["GR"] == gi]

                    if args.measure == "sensitivity":
                        gi_row.append(compute_k_recall(list(gi_orig_k["UID"]), list(gi_df["UID"]), len(gi_orig_k["UID"])))
                    if args.measure == "ap":
                        gi_row.append(compute_ap(list(gi_orig_k["UID"]), list(gi_df["UID"]), ki))

                    if args.measure == "igf":
                        if not gi_df.shape[0]:
                            gi_row.append(-1)
                        else:
                            gi_row.append(compute_igf_ratio(list(gi_df["UID"]), gi_orig, train_ranki))
                    if args.measure == "rKL": # not application to group
                        gi_row.append(-1)
                    res_df.loc[res_df.shape[0]] = gi_row
        if args.verbose:
            print("--- Done eval ", args.measure, " for ", args.data_flag, args.model_flag, ri+1, " --- \n")
    if "select" in args.measure: # selection rate for counterfactual and LTR
        output_f = os.path.join(args.repo_dir, "evaluation_res") + "/"+args.data_flag + "/"+ args.model_flag + "/Eval_R" + str(ri+1) + "_" + args.measure + args.file_n + ".csv"
    else:
        output_f = os.path.join(args.repo_dir, "evaluation_res") + "/"+args.data_flag + "/"+ args.model_flag + "/Eval_R" + str(ri+1) + "_" + args.measure + ".csv"
    writeToCSV(output_f, res_df)
    if args.verbose:
        print("--- Save eval file in ", output_f, " --- \n")

if __name__ == "__main__":
    repo_dir = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(description="Run Evaluation")

    parser.add_argument("--data_flag", type=str)
    parser.add_argument("--model_flag", type=str, help="name of the causal model to locate estimation results")

    parser.add_argument("--eval_ks", type=str, help="the top-k rankings to evaluate", default="50,100,200")
    parser.add_argument("--rankings", type=str, help="the rankings to be evaluated. default is the predictions of LTR, otherwise the specified rankings", default="Y__Y__full,Y_count__Y__full,Y_count__Y_count__full,Y_count_resolve__Y__full,Y_count_resolve__Y_count_resolve__full")

    parser.add_argument("--measure", type=str, help="the measure that is used in the evaluation", default="select_rate")

    parser.add_argument("--file_n", type=str, help="the file suffix that is used to identify the data for evaluation", default="_LTR")

    parser.add_argument("--group_col", type=str, help="the column that defines the groups to be evaluated", default="GR")
    parser.add_argument("--verbose", type=bool, default=True)

    args = parser.parse_args()
    args.repo_dir = repo_dir[0:repo_dir.find(os.getenv("PY_SRC_DIR"))] + "out/"

    eval_counter_results(args)