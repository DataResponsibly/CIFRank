import pandas as pd
import os, argparse
from utils.basic_utils import get_prediction_scores, writeToCSV


def get_LTR_predict_data_multiple(args):
    m2_keep_cols = {"Full": {"fair_count": ["G", "R", "X_count", "Y_count"],
                             "bias": ["G", "R", "X", "Y"],
                             "fair_res": ["G", "R", "X", "Y_count_resolve"]},

                    "Unaware": {"fair_count": ["X_count", "Y_count"],
                                "bias": ["X", "Y"],
                                "fair_res": ["X", "Y_count_resolve"]}}

    m1_keep_cols = {"Full": {"fair_count": ["G", "R", "Y_count"],
                             "bias": ["G", "R", "Y"]}}

    for ri in range(args.test_run):
        count_df = pd.read_csv(os.path.join(args.repo_dir, "counterfactual_data") + "/" + args.data_flag + "/" + args.model_flag + "/R" + str(ri+args.test_start) + args.file_n + ".csv")
        print("*** Read counter at ", os.path.join(args.repo_dir, "counterfactual_data") + "/" + args.data_flag + "/" + args.model_flag + "/R" + str(ri+args.test_start) + args.file_n + ".csv")


        for expi in args.settings.split(","):
            if args.model_flag == "m2":
                col_map = m2_keep_cols[expi]
            else:
                col_map = m1_keep_cols[expi]
            # include all the prediction in this setting
            all_fair_settings = [f for f in os.listdir(
                os.path.join(args.repo_dir, "ranklib_data") + "/" + args.data_flag + "/" + args.model_flag + "/" + expi)
                                 if ~os.path.isfile(os.path.join(os.path.join(args.repo_dir,
                                                                              "ranklib_data") + "/" + args.data_flag + "/" + args.model_flag + "/" + expi,
                                                                 f)) and "." not in f]

            for pred_di in all_fair_settings:
                cols = col_map[pred_di.split("__")[-1]]
                train_cols = col_map[pred_di.split("__")[0]]

                ri_pred = get_prediction_scores(os.path.join(args.repo_dir, "ranklib_data")+"/" + args.data_flag + "/" + args.model_flag + "/" + expi + "/" + pred_di, "R" + str(ri+1), "ListNet")

                pred_y_col = train_cols[-1] + "__" + cols[-1] + "__" + expi.lower()

                count_df[pred_y_col] = count_df["UID"].apply(lambda x: ri_pred[str(x)])

        if args.output_n:
            output_f = os.path.join(args.repo_dir, "counterfactual_data") + "/" + args.data_flag + "/" + args.model_flag + "/R" + str(ri+args.test_start) + "_" + args.output_n + ".csv"
        else:
            output_f = os.path.join(args.repo_dir, "counterfactual_data") + "/" + args.data_flag + "/" + args.model_flag + "/R" + str(ri+args.test_start) + ".csv"

        writeToCSV(output_f, count_df)
        if args.verbose:
            print("--- Save LTR predict in ", output_f, " --- \n")

def get_LTR_predict_data_single(args):

    m2_keep_cols = {"Full": {"fair_count": ["G", "R", "X_count", "Y_count"],
                             "bias": ["G", "R", "X", "Y"],
                             "fair_res": ["G", "R", "X", "Y_count_resolve"]},

                    "Unaware": {"fair_count": ["X_count", "Y_count"],
                                "bias": ["X", "Y"],
                                "fair_res": ["X", "Y_count_resolve"]}}

    m1_keep_cols = {"Full": {"fair_count": ["G", "R", "Y_count"],
                             "bias": ["G", "R", "Y"]}}

    # special set for meps with a moderator age encoded as X
    meps_keep_cols = {"Full": {"fair_count": ["G", "R", "X", "Y_count"],
                               "bias": ["G", "R", "X", "Y"]}}


    for ri in range(1, args.test_run+1):
        count_df = pd.read_csv(os.path.join(args.repo_dir,"counterfactual_data") + "/" + args.data_flag + "/" + args.model_flag + "/R1"+args.file_n+".csv")

        for expi in args.settings.split(","):
            if args.model_flag == "m2":
                col_map = m2_keep_cols[expi]
            else:
                if args.data_flag == "mp":
                    col_map = meps_keep_cols[expi]
                else:
                    col_map = m1_keep_cols[expi]
            # include all the prediction in this setting
            all_fair_settings = [f for f in os.listdir(os.path.join(args.repo_dir,"ranklib_data") + "/" + args.data_flag + "/" + args.model_flag + "/"+expi) if ~os.path.isfile(os.path.join(os.path.join(args.repo_dir,"ranklib_data") + "/" + args.data_flag + "/" + args.model_flag + "/"+expi, f)) and "." not in f]
            for pred_di in all_fair_settings:
                cols = col_map[pred_di.split("__")[-1]]
                train_cols = col_map[pred_di.split("__")[0]]
                ri_pred = get_prediction_scores(os.path.join(args.repo_dir, "ranklib_data")+"/"+args.data_flag +"/" + args.model_flag + "/" + expi + "/" + pred_di, "R" + str(ri), "ListNet")

                pred_y_col = train_cols[-1]+ "__" + cols[-1] + "__" + expi.lower()

                count_df = count_df[count_df["UID"].isin([int(x) for x in ri_pred])]

                count_df[pred_y_col] = count_df["UID"].apply(lambda x: ri_pred[str(x)])


        if args.output_n:
            output_f = os.path.join(args.repo_dir, "counterfactual_data") + "/" + args.data_flag + "/" + args.model_flag + "/R" + str(ri) + "_" + args.output_n + ".csv"
        else:
            output_f = os.path.join(args.repo_dir, "counterfactual_data") + "/" + args.data_flag + "/" + args.model_flag + "/R" + str(ri) + ".csv"

        writeToCSV(output_f, count_df)
        if args.verbose:
            print("--- Save LTR predict in ", output_f, " --- \n")

if __name__ == "__main__":
    repo_dir = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(description="Get Ranklib Prediction")

    parser.add_argument("--data_flag", type=str)
    parser.add_argument("--model_flag", type=str, help="name of the causal model to locate estimation results")
    parser.add_argument("--settings", type=str, help="the ranklib training sets to run")

    parser.add_argument("--file_n", type=str, help="the name suffix for the data that stores the prediction of LTR", default="_count")

    parser.add_argument("--output_n", type=str, help="the name suffix for the data that stores the prediction of LTR", default="LTR")

    parser.add_argument("--test_run", type=int, help="number of test datasets", default=10)
    parser.add_argument("--train_start", type=int, help="index of test synthetic datasets", default=1)
    parser.add_argument("--test_start", type=int, help="index of test synthetic datasets", default=11)

    parser.add_argument("--split", type=str, default="")
    parser.add_argument("--verbose", type=bool, default=True)


    args = parser.parse_args()
    args.repo_dir = repo_dir[0:repo_dir.find(os.getenv("PY_SRC_DIR"))] + "out/"

    if args.split.strip("None"):
        get_LTR_predict_data_single(args)
    else:
        get_LTR_predict_data_multiple(args)

