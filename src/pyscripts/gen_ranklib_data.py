import pandas as pd
import os, argparse
from utils.basic_utils import writeToTXT, select_balance_df
M2_LTR_COLS = {"Full": {"fair_count": ["G", "R", "X_count", "Y_count"],
                          "bias": ["G", "R", "X", "Y"],
                          "fair_res": ["G", "R", "X", "Y_count_resolve"]},

                 "Unaware": {"fair_count": ["X_count", "Y_count"],
                          "bias": ["X", "Y"],
                          "fair_res": ["X", "Y_count_resolve"]}}

M1_LTR_COLS = {"Full": {"fair_count": ["G", "R", "Y_count"],
                         "bias": ["G", "R", "Y"]}}

# special set for meps with a moderator age encoded as X
MEPS_LTR_COLS = {"Full": {"fair_count": ["G", "R", "X", "Y_count"],
                         "bias": ["G", "R", "X", "Y"]}}

GROUP_VALUE_MAP = {"Female": 1, "Male": 0, "F": 1, "M": 0,
                    "Black": 1, "White": 0, "B": 1, "W": 0,
                    "small": 1, "large": 0, "S": 1, "L": 0,
                    "NE": 0, "W": 0, "SE": 1, "N": 0}

def generate_ranklib_txt_multiple(args):

    name_map = {0: "train", 1: "test"}
    for ri in range(args.test_run):
        for modeli in args.settings.split(","):
            folder_name = [args.train_input, args.test_input]

            for qi, ti in enumerate([args.train_start, args.test_start]):
                df = pd.read_csv(os.path.join(args.repo_dir, "counterfactual_data") + "/" + args.data_flag + "/" + args.model_flag + "/R" + str(ri + ti) + str(args.file_n) + ".csv")

                if args.model_flag == "m2":
                    col_map = M2_LTR_COLS[modeli]
                else:
                    col_map = M1_LTR_COLS[modeli]

                if qi:
                    df = df.sort_values(by=col_map[args.test_input][-1], ascending=False).reset_index()
                    cols = col_map[args.test_input]
                else:
                    df = df.sort_values(by=col_map[args.train_input][-1], ascending=False).reset_index()
                    cols = col_map[args.train_input]

                if args.rel_col: # user-specified relevance data that is stored as a dict of UID to its relevance label
                    rel_df = pd.read_csv(args.src_data)
                    rel_maps = dict(zip(rel_df['UID'], rel_df[args.rel_col]))
                    df["judgment"] = df["UID"].apply(lambda x: rel_maps[x])
                    df.loc[df.index < args.opt_k, "judgment"] = 0  # filtered out top-k relevance label to optimize k

                else: # automatically assign the top-k items in target have the relevance as its reversed ranks.
                    df["judgment"] = list(range(args.opt_k, 0, -1)) + [0 for _ in range(args.total_n - args.opt_k)]

                df["query_id"] = "qid:" + str(qi + 1)

                if qi:  # for test data
                    df["UID"] = df[["UID", "judgment", "G", "R"]].astype(str).apply(
                        lambda x: "#docid={};rel={};g={};r={};".format(x.iloc[0], x.iloc[1], x.iloc[2], x.iloc[3]),
                        axis=1)
                else:  # for train data
                    df["UID"] = df["UID"].apply(lambda x: "#docid=" + str(x))

                df["G"] = df["G"].apply(lambda x: GROUP_VALUE_MAP[x])
                df["R"] = df["R"].apply(lambda x: GROUP_VALUE_MAP[x])

                for idx, ci in enumerate(cols):
                    df[ci] = df[ci].apply(lambda x: str(idx + 1) + ":" + str(x))

                # shuffle df
                df = df.sample(frac=1).reset_index(drop=True)
                df = df[["judgment", "query_id"] + cols + ["UID"]]

                output_f = os.path.join(args.repo_dir, "ranklib_data") + "/" + args.data_flag + "/" + args.model_flag + "/" + modeli + "/" + "__".join(folder_name) + "/R" + str(ri + 1) + "_" + name_map[qi] + "_ranklib.txt"
                writeToTXT(output_f, df)
                if args.verbose:
                    print("--- Save ranklib data in", output_f, " --- \n")



def generate_ranklib_txt_single(args):

    cur_df = pd.read_csv(os.path.join(args.repo_dir, "counterfactual_data") + "/" + args.data_flag + "/" + args.model_flag + "/R1" + args.file_n+".csv")
    k_list = [int(x) for x in args.opt_k_list.split(',')]
    for ri in range(1, args.test_run+1):
        # based on original Y to do balance split, all setting share the same set of UIDS in train and test
        train_ids = select_balance_df(cur_df, "Y", rand_input=ri)
        test_ids = set(cur_df["UID"]).difference(train_ids)
        all_df = [cur_df[cur_df["UID"].isin(train_ids)], cur_df[cur_df["UID"].isin(test_ids)]]

        for modeli in args.settings.split(","):
            for qi, ti in enumerate(["train", "test"]):
                if args.model_flag == "m2":
                    col_map = M2_LTR_COLS[modeli]
                else:
                    if args.data_flag == "mp":
                        col_map = MEPS_LTR_COLS[modeli]
                    else:
                        col_map = M1_LTR_COLS[modeli]

                df = all_df[qi]


                if ti == "test":
                    df = df.sort_values(by=col_map[args.test_input][-1], ascending=False).reset_index()
                    cols = col_map[args.test_input]
                else:
                    df = df.sort_values(by=col_map[args.train_input][-1], ascending=False).reset_index()
                    cols = col_map[args.train_input]

                if args.rel_col:  # user-specified relevance data that is stored as a dict of UID to its relevance label
                    rel_df = pd.read_csv(args.src_data)
                    rel_maps = dict(zip(rel_df['UID'], rel_df[args.rel_col]))
                    df["judgment"] = df["UID"].apply(lambda x: rel_maps[x])
                    df.loc[df.index < k_list[qi], "judgment"] = 0  # filtered out top-k relevance label to optimize k

                else:  # automatically assign the top-k items in target have the relevance as its reversed ranks.
                    # df["judgment"] = list(range(df.shape[0], 0, -1)) # full list optimization
                    # print ("****",ri, ti, df.shape[0])
                    if df.shape[0] > k_list[qi]: # test set has items less than k
                        df["judgment"] = list(range(k_list[qi], 0, -1)) + [0 for _ in range(df.shape[0] - k_list[qi])]
                    else:
                        df["judgment"] = list(range(df.shape[0], 0, -1))

                df["query_id"] = "qid:" + str(qi + 1)

                if ti == "test":  # for test data
                    df["UID"] = df[["UID", "judgment", "G", "R"]].astype(str).apply(
                        lambda x: "#docid={};rel={};g={};r={};".format(x.iloc[0], x.iloc[1], x.iloc[2], x.iloc[3]),
                        axis=1)
                else:  # for train data
                    df["UID"] = df["UID"].apply(lambda x: "#docid=" + str(x))

                df["G"] = df["G"].apply(lambda x: GROUP_VALUE_MAP[x])
                df["R"] = df["R"].apply(lambda x: GROUP_VALUE_MAP[x])

                for idx, ci in enumerate(cols):
                    if args.data_flag == "mp" and ci == "X": # special norm for Age in MEPS
                        df[ci] = (df[ci] - df[ci].mean()) / df[ci].std()
                    df[ci] = df[ci].apply(lambda x: str(idx + 1) + ":" + str(x))

                # shuffle df
                df = df.sample(frac=1).reset_index(drop=True)
                df = df[["judgment", "query_id"] + cols + ["UID"]]

                output_f = os.path.join(args.repo_dir, "ranklib_data") + "/" + args.data_flag + "/" + args.model_flag + "/" + modeli + "/" + "__".join([args.train_input, args.test_input]) + "/R" + str(ri) + "_" + ti + "_ranklib.txt"
                writeToTXT(output_f, df)
                if args.verbose:
                    print("--- Save ranklib data in", output_f, " --- \n")


if __name__ == "__main__":
    repo_dir = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(description="Run Ranklib Data Generation")

    parser.add_argument("--data_flag", type=str)
    parser.add_argument("--model_flag", type=str, help="name of the causal model to locate estimation results")

    parser.add_argument("--opt_k", type=int, help="the top-k ranking to optimize for listNet algorithm")
    parser.add_argument("-l", "--opt_k_list", type=str, help="the top-k ranking to optimize for listNet algorithm for train and test, only work with split=True")

    parser.add_argument("--total_n", type=int)

    parser.add_argument("--settings", type=str, help="the ranklib training sets to run")

    parser.add_argument("--rel_col", type=str, help="name of the column that is used as the relevalance label", default="")
    parser.add_argument("--src_data", type=str, help="name of the data that is used to retreive the relevalance column")

    parser.add_argument("--test_input", type=str, help="what test data to feed into LTR ranker", default="bias")
    parser.add_argument("--train_input", type=str, help="what train data to feed into LTR ranker", default="bias")


    parser.add_argument("--file_n", type=str, help="the suffix of the counterfactual data", default="_count")

    parser.add_argument("--test_run", type=int, help="number of test datasets, ONLY FOR SYNTHETIC DATA", default=10)
    parser.add_argument("--train_start", type=int, help="index of test synthetic datasets, ONLY FOR SYNTHETIC DATA", default=1)
    parser.add_argument("--test_start", type=int, help="index of test synthetic datasets, ONLY FOR SYNTHETIC DATA", default=11)

    parser.add_argument("--split", type=str, default="None")

    parser.add_argument("--verbose", type=bool, default=True)


    args = parser.parse_args()
    args.repo_dir = repo_dir[0:repo_dir.find(os.getenv("PY_SRC_DIR"))] + "out/"

    if args.split.strip("None"):
        generate_ranklib_txt_single(args)
    else:
        generate_ranklib_txt_multiple(args)