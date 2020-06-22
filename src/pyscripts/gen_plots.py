import pandas as pd
import os, argparse
from utils.basic_utils import get_files_with_name
from utils.vis_utils import output_cat_plot, output_scatter_plot

NAME_MAP = {'Y__Y__full': "original \n LTR", 'Y_count__Y__full': "non-res \n LTR",
                'Y_count__Y_count__full': "non-res \n cf-LTR",
                'Y_count_resolve__Y__full': "resolving \n LTR",
                'Y_count_resolve__Y_count_resolve__full': "resolving \n cf-LTR",
                'Y_count_resolve_pred': "resolving",
                "Y": "original", 'Y_count': "non-res", 'Y_count_resolve': "resolving",
                'Y_quotas_inter': "quotas", 'Y_quotas_G': "quotas G", 'Y_quotas_R': "quotas R",
                'Y_quotas_GR': "quotas"}
LABEL_MAP = {'select_rate': 'selection rate', 'sensitivity': 'sensitivity',
             'ap': 'AP', 'score_utility': 'Y utility loss', 'igf': 'ratio', 'rKL': 'rKL'}
LEGEND_LOC_MAP = {'select_rate': 'upper right', 'sensitivity': 'lower right',
                  'rKL': 'upper left'}
def gen_counter_plots(args):
    # for selection rate in counterfactual rankings

    k_range = [int(x) for x in args.plot_ks.split(",")]

    all_files = get_files_with_name(os.path.join(args.repo_dir, "evaluation_res") + "/" + args.data_flag + "/" + args.model_flag, args.y_col+args.file_n)
    df = pd.read_csv(os.path.join(args.repo_dir, "evaluation_res") + "/" + args.data_flag + "/" + args.model_flag + "/" + all_files[0])

    df["group"] = df["group"].apply(lambda x: x[::-1])

    for ranki in args.rankings.split(","):
        res_df = df[(df["rank"] == ranki) & (df["k"].isin(k_range))].copy()
        res_df["rank"] = res_df["rank"].apply(lambda x: NAME_MAP[x])


        output_f = os.path.join(args.repo_dir, "plots") + "/" + args.data_flag + "/" + args.model_flag + "/fairness/" + ranki + "_" + args.y_col
        if args.y_max:
            output_cat_plot(output_f, "bar", res_df, "k", args.y_col, hue_list=["WM", "BM", "WF", "BF"], line_y=1, y_label=LABEL_MAP[args.y_col], y_max=args.y_max, order_f="", legend_p=LEGEND_LOC_MAP[args.y_col], shape_ratio=1.8, font_ratio=2.5)
        else:
            output_cat_plot(output_f, "bar", res_df, "k", args.y_col, hue_list=["WM", "BM", "WF", "BF"], line_y=1, y_label=LABEL_MAP[args.y_col], y_max=args.y_max, order_f="", legend_p=LEGEND_LOC_MAP[args.y_col], shape_ratio=1.8, font_ratio=2.5)

        if args.verbose:
            print("--- Save plot file in ", output_f, ".pdf --- \n")


def gen_rKL_plots(args):
    # for rKL in counterfactual rankings

    k_range = [int(x) for x in args.plot_ks.split(",")]

    all_files = get_files_with_name(os.path.join(args.repo_dir, "evaluation_res") + "/" + args.data_flag + "/" + args.model_flag, args.y_col)
    df = pd.read_csv(os.path.join(args.repo_dir, "evaluation_res") + "/" + args.data_flag + "/" + args.model_flag + "/" + all_files[0])

    res_df = df[df["k"].isin(k_range)].copy()
    res_df = res_df[(res_df["rank"].isin(["Y","Y_count","Y_count_resolve"])) & (res_df["group"] == "all")]

    res_df["rank"] = res_df["rank"].apply(lambda x: NAME_MAP[x])
    output_f = os.path.join(args.repo_dir, "plots") + "/" + args.data_flag + "/" + args.model_flag + "/fairness/counter_" + args.y_col

    if args.y_max:
        output_cat_plot(output_f, "bar", res_df, "k", args.y_col, hue="rank", y_label=LABEL_MAP[args.y_col], y_max=args.y_max, order_f="", legend_p=LEGEND_LOC_MAP[args.y_col], shape_ratio=1.8, font_ratio=2.5, color_p="Set1")
    else:
        output_cat_plot(output_f, "bar", res_df, "k", args.y_col, hue="rank", y_label=LABEL_MAP[args.y_col], order_f="", legend_p=LEGEND_LOC_MAP[args.y_col], shape_ratio=1.8, font_ratio=2.5, color_p="Set1")

    if args.verbose:
        print("--- Save plot file in ", output_f, ".pdf --- \n")


def gen_LTR_plots(args):
    # for selection rate, sensitivity in LTR predictions
    if args.y_col == "sensitivity":
        p_type = "box"
    else:
        p_type = "bar"

    x_orders = args.rankings.split(",")

    all_files = get_files_with_name(os.path.join(args.repo_dir, "evaluation_res") + "/" + args.data_flag + "/" + args.model_flag, args.y_col+args.file_n)
    df = pd.read_csv(os.path.join(args.repo_dir, "evaluation_res") + "/" + args.data_flag + "/" + args.model_flag + "/" + all_files[0])


    df = df[(df["k"] == args.opt_k) & (df["group"] != "all")]
    vis_df = df[df["rank"].isin(x_orders)]

    key = vis_df['rank'].map({day: i for i, day in enumerate(x_orders)})
    res_df = vis_df.iloc[key.argsort()].copy()

    res_df["group"] = res_df["group"].apply(lambda x: x[::-1])
    res_df["rank"] = res_df["rank"].apply(lambda x: NAME_MAP[x])

    output_f = os.path.join(args.repo_dir, "plots") + "/" + args.data_flag + "/" + args.model_flag + "/LTR/pred_" + args.y_col
    if args.y_max:
        output_cat_plot(output_f, p_type, res_df, "rank", args.y_col, hue_list=["WM", "BM", "WF", "BF"], y_label=LABEL_MAP[args.y_col], legend_p=LEGEND_LOC_MAP[args.y_col], order_f="", y_max=args.y_max, shape_ratio=1.9, font_ratio=2.3)
    else:
        output_cat_plot(output_f, p_type, res_df, "rank", args.y_col, hue_list=["WM", "BM", "WF", "BF"], y_label=LABEL_MAP[args.y_col], legend_p=LEGEND_LOC_MAP[args.y_col], order_f="", shape_ratio=1.9, font_ratio=2.3)

    if args.verbose:
        print("--- Save plot file in ", output_f, ".pdf --- \n")

def gen_rank_plots(args, x_max=100, sensi_col="GR"):
    # for the rank plots of the counterfactual rankings
    GROUP_ORDER_MAP = {"cs": ["SS", "SW", "SN", "LS", "LW", "LN"],
                       "cm": ["FB", "FW", "MB", "MW"],
                       "mp": ["FB", "FW", "MB", "MW"],
                       "mv": ["FB", "FW", "MB", "MW"],
                       "mvp": ["FB", "FW", "MB", "MW"],
                       "mvr": ["FB", "FW", "MB", "MW"]
                       }
    all_files = get_files_with_name(os.path.join(args.repo_dir, "counterfactual_data") + "/" + args.data_flag + "/" + args.model_flag, args.file_n)
    df = pd.read_csv(os.path.join(args.repo_dir, "counterfactual_data") + "/" + args.data_flag + "/" + args.model_flag + "/" + all_files[0])

    if df.shape[0] < x_max:
        x_max = df.shape[0]

    for ranki in args.rankings.split(","):
        rank_df = pd.DataFrame(columns=["sort", "group", "rank", "group_y"])
        sort_df = df.sort_values(by=ranki, ascending=False).reset_index().head(x_max)
        for gi in list(df[sensi_col].unique()):
            gi_df = sort_df[sort_df[sensi_col] == gi]
            gi_rank = pd.DataFrame(columns=["sort", "group", "rank", "group_y"])
            gi_rank["rank"] = list(gi_df.index + 1)
            gi_rank["sort"] = ranki
            gi_rank["group"] = gi
            gi_rank["group_y"] = GROUP_ORDER_MAP[args.data_flag].index(gi)+1
            rank_df = pd.concat([rank_df, gi_rank])


        output_f = os.path.join(args.repo_dir, "plots") + "/" + args.data_flag + "/" + args.model_flag + "/rankings/rank_" + ranki
        output_scatter_plot(output_f, rank_df)

    if args.verbose:
        print("--- Save plot file in ", output_f, ".pdf --- \n")


if __name__ == "__main__":
    repo_dir = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(description="Generate Evaluation Plots")

    parser.add_argument("--data_flag", type=str, help="name of the dataset to locate results")
    parser.add_argument("--model_flag", type=str, help="name of the causal model to locate results")

    parser.add_argument("--plot_ks", type=str, help="the values of k to include in the plot of ranking position", default="50,100,200")
    parser.add_argument("--opt_k", type=int, help="the value of k that is chosen to include in the plot of prediction", default=500)

    parser.add_argument("--rankings", type=str, help="the rankings to be included in the plot", default="Y__Y__full,Y_count__Y__full,Y_count__Y_count__full,Y_count_resolve__Y__full,Y_count_resolve__Y_count_resolve__full")
    parser.add_argument("--y_col", type=str, help="the name of the Y axis in the plot", default="select_rate")
    parser.add_argument("--y_max", type=float, help="the max value of Y axis in the plot", default=0)

    parser.add_argument("--file_n", type=str, help="the file suffix that is used to identify the results for evaluation", default="")

    parser.add_argument("--verbose", type=bool, default=True)


    args = parser.parse_args()
    args.repo_dir = repo_dir[0:repo_dir.find(os.getenv("PY_SRC_DIR"))] + "out/"

    if args.y_col in ["select_rate", "sensitivity", "igf", "ap"]:
        if "__" in args.rankings:
            gen_LTR_plots(args)
        else:
            gen_counter_plots(args)
    elif args.y_col in ["rKL", "score_utility"]:
        gen_rKL_plots(args)
    elif args.y_col == "rank":
        gen_rank_plots(args)
    else:
        print("Only support visualization for 'select_rate, sensitivity, rKL, score_utility, igf, ap'!")
