import pandas as pd
import os, argparse
from utils.basic_utils import writeToCSV

def get_counterfactual_data_real(args):
    for ri in range(1, args.counter_run + 1):
        if args.src_data.strip("None"):
            cur_df = pd.read_csv(args.src_data + ".csv")
        else:
            print("Need to specify the raw real data!!")
            exit()
        group_list = [x for x in cur_df["GR"].unique() if x!= args.counter_g]
        orig_cols = list(cur_df.columns)

        data_name = os.path.join(args.repo_dir,"parameter_data") + "/" + args.data_flag + "/" + args.model_flag + "/R" + str(ri)

        if args.model_flag in ["m2", "m4"]:
            x_res = pd.read_csv(data_name + "_x.csv")
            counter_g_base = x_res[x_res["Unnamed: 0"] == "GR" + args.counter_g]["Estimate"].values[0]

            x_shifts = {args.counter_g: 0}
            for gi in group_list:
                x_shifts[gi] = counter_g_base - x_res[x_res["Unnamed: 0"] == "GR" + gi]["Estimate"].values[0]

            cur_df["X_shift"] = cur_df["GR"].apply(lambda x: x_shifts[x])
            cur_df["X_count"] = cur_df["X"] + cur_df["X_shift"]

        # get y shift
        if args.model_flag in ["m1", "m3"]:
            y_res = pd.read_csv(data_name + "_y.csv")
            counter_g_base = y_res[y_res["Unnamed: 0"] == "GR" + args.counter_g]["Estimate"].values[0]
            y_shifts = {args.counter_g: 0}
            for gi in group_list:
                y_shifts[gi] = counter_g_base - y_res[y_res["Unnamed: 0"] == "GR" + gi]["Estimate"].values[0]
        else:
            y_shifts = {args.counter_g: 0}
            y_shifts_resolve = {args.counter_g: 0}
            for gi in group_list:
                g_res = pd.read_csv(data_name + "_" + gi + "_med.csv")["Estimate"]
                y_shifts[gi] = -g_res[2]
                y_shifts_resolve[gi] = -g_res[1]

        cur_df["Y_shift"] = cur_df["GR"].apply(lambda x: y_shifts[x])
        cur_df["Y_count"] = cur_df["Y"] + cur_df["Y_shift"]

        if args.model_flag in ["m2", "m4"]:
            cur_df["Y_shift_resolve"] = cur_df["GR"].apply(lambda x: y_shifts_resolve[x])
            cur_df["Y_count_resolve"] = cur_df["Y"] + cur_df["Y_shift_resolve"]
            cur_df = cur_df.loc[:, orig_cols + ["X_count", "Y_count", "Y_count_resolve"]]
        else:
            cur_df = cur_df.loc[:, orig_cols + ["Y_count"]]

        output_f = os.path.join(args.repo_dir,"counterfactual_data") + "/" + args.data_flag + "/" + args.model_flag +"/R" + str(ri) + "_count.csv"
        writeToCSV(output_f, cur_df)
        if cur_df.shape[0] != args.val_n:
            print ("Error !!!!!", ri)
            exit()
        if args.verbose:
            print ("--- Save counterfactual in", output_f, " --- \n")

def get_counterfactual_data_syn(args):
    for ri in range(1, args.counter_run + 1):
        cur_df = pd.read_csv(os.path.join(args.repo_dir, args.data_dir) + "/" + args.data_flag + "/R" + str(ri) + ".csv")

        group_list = [x for x in cur_df["GR"].unique() if x!= args.counter_g]
        orig_cols = list(cur_df.columns)

        data_name = os.path.join(args.repo_dir,"parameter_data") + "/" + args.data_flag + "/" + args.model_flag + "/R" + str(ri)
        y_res = pd.read_csv(data_name + "_y.csv")

        if args.model_flag in ["m2", "m4"]:
            x_res = pd.read_csv(data_name + "_x.csv")
            counter_g_base_x = x_res[x_res["Unnamed: 0"] == "GR" + args.counter_g]["Estimate"].values[0]

            x_shifts = {args.counter_g: 0}
            for gi in group_list:
                x_shifts[gi] = counter_g_base_x - x_res[x_res["Unnamed: 0"] == "GR" + gi]["Estimate"].values[0]

            cur_df["X_shift"] = cur_df["GR"].apply(lambda x: x_shifts[x])
            cur_df["X_count"] = cur_df["X"] + cur_df["X_shift"]

        counter_g_base = y_res[y_res["Unnamed: 0"] == "GR" + args.counter_g]["Estimate"].values[0]
        y_shifts = {args.counter_g: 0}
        for gi in group_list:
            y_shifts[gi] = counter_g_base - y_res[y_res["Unnamed: 0"] == "GR" + gi]["Estimate"].values[0]

        x_weight = y_res[y_res["Unnamed: 0"] == "X"]["Estimate"].values[0]

        cur_df["Y_shift"] = cur_df["GR"].apply(lambda x: y_shifts[x])
        cur_df["Y_count"] = cur_df["Y_shift"] + x_weight * cur_df["X_count"]

        if args.model_flag in ["m2", "m4"]:
            cur_df["Y_count_resolve"] = cur_df["Y_shift"] + x_weight * cur_df["X"]

            cur_df = cur_df.loc[:, orig_cols + ["X_count", "Y_count", "Y_count_resolve"]]
        else:
            cur_df = cur_df.loc[:, orig_cols + ["Y_count"]]

        output_f = os.path.join(args.repo_dir,"counterfactual_data") + "/" + args.data_flag + "/" + args.model_flag +"/R" + str(ri) + "_count.csv"
        writeToCSV(output_f, cur_df)
        if cur_df.shape[0] != args.val_n:
            print ("Error !!!!!", ri)
            exit()
        if args.verbose:
            print ("--- Save counterfactual in", output_f, " --- \n")


def get_counterfactual_data_single_m(args):
    # Only support mediation on gender now
    for ri in range(1, args.counter_run + 1):
        cur_df = pd.read_csv(os.path.join(args.repo_dir, args.data_dir) + "/" + args.data_flag + "/R" + str(ri) + ".csv")

        group_list = [x for x in cur_df["GR"].unique() if x!= args.counter_g]
        orig_cols = list(cur_df.columns)

        data_name = os.path.join(args.repo_dir,"parameter_data") + "/" + args.data_flag + "/" + args.model_flag + "/R" + str(ri)

        if args.model_flag in ["m2", "m4"]:
            x_res = pd.read_csv(data_name + "_x.csv")

            counter_g_base = x_res[x_res["Unnamed: 0"] == args.med_s + args.counter_g]["Estimate"].values[0]
            other_g_base = x_res[x_res["Unnamed: 0"] == args.med_s + args.other_g]["Estimate"].values[0]
            x_shifts = {}
            for gi in group_list:
                if args.counter_g in gi:
                    x_shifts[gi] = 0
                else:
                    x_shifts[gi] = counter_g_base - other_g_base

            cur_df["X_shift"] = cur_df["GR"].apply(lambda x: x_shifts[x])
            cur_df["X_count"] = cur_df["X"] + cur_df["X_shift"]

        # get y shift
        if args.model_flag in ["m1", "m3"]:
            print ("Only support model m2 and m4 for mediation on single attribute!")
            exit()
        else:
            y_res = pd.read_csv(data_name + "_y.csv")

            y_shifts = {}

            for gi in group_list:
                if args.hidden_g in gi: # for BM and BF
                    gi_inter = y_res[y_res["Unnamed: 0"] == "G"+gi[0]]["Estimate"].values[0]
                else:
                    if "MW" in gi:
                        gi_inter = y_res[y_res["Unnamed: 0"] == "G" + gi[0]]["Estimate"].values[0] + \
                               y_res[y_res["Unnamed: 0"] == "R" + gi[1]]["Estimate"].values[0] + y_res[y_res["Unnamed: 0"] == "GM:RW"]["Estimate"].values[0]
                    else:
                        gi_inter = y_res[y_res["Unnamed: 0"] == "G" + gi[0]]["Estimate"].values[0] + \
                                   y_res[y_res["Unnamed: 0"] == "R" + gi[1]]["Estimate"].values[0]

                y_shifts[gi] = - gi_inter + y_res[y_res["Unnamed: 0"] == "GF"]["Estimate"].values[0]


            med_weight = pd.read_csv(data_name + "_" + args.other_g + "_med.csv")["Estimate"][0]

        cur_df["Y_shift"] = cur_df["GR"].apply(lambda x: y_shifts[x])
        cur_df["Y_count"] = cur_df["Y_shift"] + med_weight * cur_df["X_count"]

        if args.model_flag in ["m2", "m4"]:
            cur_df["Y_count_resolve"] = cur_df["Y_shift"] + med_weight * cur_df["X"]
            cur_df = cur_df.loc[:, orig_cols + ["X_count", "Y_count", "Y_count_resolve"]]
        else:
            cur_df = cur_df.loc[:, orig_cols + ["Y_count"]]

        output_f = os.path.join(args.repo_dir,"counterfactual_data") + "/" + args.data_flag + "/" + args.model_flag +"/R" + str(ri) +"_count.csv"
        writeToCSV(output_f, cur_df)
        if cur_df.shape[0] != args.val_n:
            print ("Error !!!!!", ri)
            exit()
        if args.verbose:
            print ("--- Save counterfactual in", output_f, " --- \n")

def get_counterfactual_mp(args):
    # special setting for MEPS
    for ri in range(1, args.counter_run + 1):
        if args.src_data.strip("None"):
            cur_df = pd.read_csv(args.src_data + ".csv")
        else:
            print("Need to specify the raw real data!!")
            exit()
        data_name = os.path.join(args.repo_dir,"parameter_data") + "/" + args.data_flag + "/" + args.model_flag + "/R" + str(ri)

        # get y shift
        if args.model_flag != "m1":
            print ("Only support m1 model for MEPS as a special case!")
            exit()
        else:
            y_res = pd.read_csv(data_name + "_y_counter.csv")
            cur_df["Y_count"] = y_res["y_counter"]


        output_f = os.path.join(args.repo_dir,"counterfactual_data") + "/" + args.data_flag + "/" + args.model_flag +"/R" + str(ri) + "_count.csv"
        writeToCSV(output_f, cur_df)
        if cur_df.shape[0] != args.val_n:
            print ("Error !!!!!", ri)
            exit()
        if args.verbose:
            print ("--- Save counterfactual in", output_f, " --- \n")

if __name__ == "__main__":
    repo_dir = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(description="Get Counterfactual Data")

    parser.add_argument("--data_flag", type=str)
    parser.add_argument("--model_flag", type=str, help="name of the causal model to locate estimation results")

    parser.add_argument("--data_dir", type=str, help="the name of the folder to read the raw data. Only for synthetic data.")
    parser.add_argument("--src_data", type=str, default=None, help="the name of the raw data. Only for real data.")

    parser.add_argument("--counter_g", type=str, default="FB")
    parser.add_argument("--hidden_g", type=str)
    parser.add_argument("--other_g", type=str)
    parser.add_argument("--med_s", type=str, default="GR")

    parser.add_argument("--counter_run", type=int, help="number of counterfactual datasets", default=20)
    parser.add_argument("--val_n", type=int)

    parser.add_argument('--verbose', type=bool, default=True)


    args = parser.parse_args()
    args.repo_dir = repo_dir[0:repo_dir.find(os.getenv("PY_SRC_DIR"))] + "out/"

    if args.med_s != "GR": # only support mediation on G now
        get_counterfactual_data_single_m(args)
    else:
        if args.data_flag == "mp" and args.model_flag == "m1": # special setting for MEPS considering age groups
            get_counterfactual_mp(args)
        else:
            if args.data_flag in ["cm", "cs", "mp"]:
                get_counterfactual_data_real(args)
            else:
                get_counterfactual_data_syn(args)