import os, pathlib
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

def output_cat_plot(f_name, f_type, df, x, y, hue_list=None, hue="group", line_y=None, y_label=None,
                    y_max=None, color_p="Set2", legend_f=False, legend_p="upper right", order_f="higher is better",
                    l_col=None, shape_ratio=1.4, font_ratio=1.8, y_min=0):

    sns.set(style="whitegrid", font_scale=font_ratio)
    if hue_list:
        g = sns.catplot(x=x, y=y, hue=hue, hue_order=hue_list, data=df, kind=f_type, palette=color_p, ci="sd",
                        legend=legend_f, aspect=shape_ratio)
    else:
        g = sns.catplot(x=x, y=y, hue=hue, data=df, kind=f_type, palette=color_p, ci="sd", legend=legend_f,
                        aspect=shape_ratio)

    # plot the line at specified x
    x_max = len(df[x].unique())
    if line_y:
        plt.plot([-1] + [i for i in range(x_max)] + [x_max - 0.5], [line_y for _ in range(x_max + 2)], "black")
    plt.xlim([-0.5, x_max - 0.5])

    # decide y limit
    if not y_max:
        y_max = max(df[y])

    if not y_min and y_min != 0:
        y_min = min(df[y])

    if y_max <= 1.1:
        y_ticks = [x / 10 for x in range(int(y_min * 10), 11) if x % 2 == 0]
        plt.ylim([y_min, 1.0])
        plt.yticks(y_ticks)
    elif y_max < 10:
        plt.ylim([y_min, y_max + 0.01])
    else:
        plt.ylim([y_min - 1, y_max + 1])
        y_ticks = list(range(int(y_min), int(y_max), int((y_max - y_min) / 6)))
        plt.yticks(y_ticks)

    if y_label:
        if order_f:
            plt.ylabel(y_label + " (" + order_f + ")")
        else:
            plt.ylabel(y_label)
    else:
        plt.ylabel("")

    plt.xlabel("")
    if not legend_f:  # bbox_to_anchor=(1.01, 0.6)
        if "outside" in legend_p:
            plt.legend(bbox_to_anchor=(1.01, 0.6))
        else:
            if l_col:
                plt.legend(loc=legend_p, ncol=l_col, borderaxespad=0.1,
                           handlelength=0.7, handletextpad=0.3, columnspacing=0.3)
            else:
                plt.legend(loc=legend_p, ncol=4, borderaxespad=0.05,
                           handlelength=0.7, handletextpad=0.05, columnspacing=0.3)

    plt.tight_layout()

    cur_f_path = f_name[0:f_name.rfind("/") + 1]
    if not os.path.exists(cur_f_path):
        directory = os.path.dirname(cur_f_path)
        pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
    plt.savefig(f_name + ".pdf")
    plt.close()


def output_scatter_plot(f_name, _df, x_col="rank", y_col="group", color_p="Set2"):
    sns.set(style="whitegrid", font_scale=3.3)

    max_x = max(_df[x_col])
    plt.figure(figsize=(13, 6))

    _df.loc[:, x_col] = _df.loc[:, x_col].astype(int)

    ax = sns.boxplot(x=x_col, y=y_col, data=_df, whis=np.inf, width=0.99)
    ax = sns.swarmplot(x=x_col, y=y_col, data=_df, palette=color_p, dodge=False, size=18)

    ax.set_xlim(0, max_x + 1)
    if max_x > 200:
        ax.set_xticks([1] + [x for x in range(1, max_x + 1) if x % 200 == 0])
    elif max_x > 100:
        ax.set_xticks([1] + [x for x in range(1, max_x + 1) if x % 40 == 0])
    else:
        ax.set_xticks([1] + [x for x in range(1, max_x + 1) if x % 20 == 0])
    plt.tight_layout()

    cur_f_path = f_name[0:f_name.rfind("/") + 1]
    if not os.path.exists(cur_f_path):
        directory = os.path.dirname(cur_f_path)
        pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
    plt.savefig(f_name + ".pdf")
    plt.close()