from typing import Dict, List
import matplotlib
import pandas as pd
from statistics import mean

from scipy.interpolate import interp1d
import numpy as np
import sys
from slugify import slugify

import matplotlib.pyplot as plt
import os
import logging

from get_metric import METRICS_TO_GET, get_metric_from_summary_file, get_metric_per_endpoint

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
PLOT_FOLDER = os.path.join(THIS_FOLDER, "plot")

logging.basicConfig(
    format="%(asctime)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S", level=logging.INFO
)

# Configuration for managing the chart
COLOR = ["cyan", "purple", "olive", "grey", "orange", "tomato"]
HATCH = [None, "|||||", "/////", "\\\\\\\\\\", "+++", "---"]

# Exclude some endpoints from the chart
EXCLUDE_ENDPOINT_ALL = ["GET /sensor/1", "GET /sensor"]
ENDPOINT_EXCLUDE_VERSION = {
    "v1": EXCLUDE_ENDPOINT_ALL,
    "v2": EXCLUDE_ENDPOINT_ALL,
    "v3": EXCLUDE_ENDPOINT_ALL + ["POST /node", "PUT /node/1", "POST /channel", "GET /node/1"],
}

INCLUDE_ENDPOINT_ALL = ['GET /node', 'GET /node/1', 'PUT /node/1', 'POST /channel']
ENDPOINT_INCLUDE_VERSION = {
    "v1": INCLUDE_ENDPOINT_ALL,
    "v2": INCLUDE_ENDPOINT_ALL,
    "v3": ['GET /node'],
    "pool": ['PUT /node/1', 'POST /channel/'],
    "banding": ['GET /node/', 'GET /node/1', 'PUT /node/1', 'POST /channel/']
}

POOL = [
    "70_200k",
    "100_500k",
    "125_600k",
    "135_700k",
    "150_750k",
    "200_1000k"
]

BANDING = [
    "full_endpoint_125_600k",
    "konfigurasi_awal"
]

V1_SERVER = [
    "hanin",
    "alvin_v1",
    "grey_v1",
]

V1_SERVER_LABEL: Dict[str, str] = {
    "hanin": "Falcon",
    "alvin_v1": "Sanic",
    "grey_v1": "FastAPI",
}

V2_SERVER = [
    "alvin_v1",
    "alvin_v2",
    "grey_v1",
    "grey_v2",
]

V2_SERVER_LABEL: Dict[str, str] = {
    "alvin_v1": "Sanic v1",
    "alvin_v2": "Sanic v2",
    "grey_v1": "FastAPI v1",
    "grey_v2": "FastAPI v2",
}

V3_SERVER = [
    "grey_v2",
    "grey_v3",
]

V3_SERVER_LABEL: Dict[str, str] = {
    "grey_v2": "FastAPI REST API (Iterasi 2)",
    "grey_v3": "FastAPI Antarmuka Pengguna (Iterasi 3)",
}

SERVER = {
    "v1": V1_SERVER,
    "v2": V2_SERVER,
    "v3": V3_SERVER,
    "pool" : POOL,
    "banding" : BANDING
}

LABEL = {
    "v1": V1_SERVER_LABEL,
    "v2": V2_SERVER_LABEL,
    "v3": V3_SERVER_LABEL,
}


def split_dataframe_per_version(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Create a dictionary of dataframe per version

    Args:
        df (pd.DataFrame): _description_

    Returns:
        Dict[str, pd.DataFrame]: _description_
    """
    df_v1 = df[df["server"].isin(V1_SERVER)]
    df_v2 = df[df["server"].isin(V2_SERVER)]
    df_v3 = df[df["server"].isin(V3_SERVER)]
    return {
        "v1": df_v1,
        "v2": df_v2,
        "v3": df_v3,
    }


def create_time_chart(df: pd.DataFrame, version: str):
    """Create time chart for each server

    Args:
        df (pd.DataFrame): pandas dataframe that contains the data to be plotted
        version (str): version of the server
    """
    metrics = ["memory_usage_percent"]
    for metric in metrics:
        logging.info(f"Creating plot for {metric}")

        servers = df["server"].unique()
        title = f"{metric} comparison"
        new_df_data = {}
        for server in servers:
            plt.clf()
            plt.cla()
            server_df: pd.DataFrame = df[df["server"] == server].sort_values(
                by=["epoch"]
            )
            server_df_data = server_df[metric].to_list()
            new_df_data[server] = server_df_data
            min = server_df["epoch"].min()
            max = server_df["epoch"].max()
            xnew = np.linspace(min, max, num=1000, endpoint=True)
            f_cubic = interp1d(server_df["epoch"], server_df[metric], kind="cubic")

            x = xnew
            y = f_cubic(xnew)
            plt.plot(x, y)
            plt.fill_between(x, y)
            # plt.ylim(0, 100)
            # ax = server_df.plot(
            #     # rot=0,
            #     # kind="line",
            #     # title=to_title_case(title),
            #     x=xnew,
            #     # legend=True,
            #     y=f_cubic(xnew),
            #     figsize=(10, 5),
            # )

            filename = slugify(f"{version}-{title}-timechart-{server}") + ".png"
            logging.info(f"Saving {filename}")
            plt.savefig(os.path.join(PLOT_FOLDER, filename), bbox_inches="tight")
        # new_df = pd.DataFrame(new_df_data)


def create_bar_chart(df: pd.DataFrame, version: str):
    """Create bar chart for each server

    Args:
        df (pd.DataFrame): pandas dataframe that contains the data to be plotted
        version (str): version of the server
    """
    df_grouped_by_server = df.groupby("server").mean(numeric_only=True)
    # Create a dictionary to store the data
    metrics = METRICS_TO_GET + ["memory_usage_percent", "memory_usage" ,"memory_in_mb"]
    for metric in metrics:
        plt.clf()
        plt.cla()
        logging.info(f"Creating plot for {metric}")

        title = f"{metric} comparison"
        if metric == "memory_usage_percent":
            fmt = "%.2f%%"
            ylim = (0, 50)
        else:
            fmt = "%.2f"
            ylim = None

        server_labelled = []
        for server in SERVER[version]:
            server_labelled.append(LABEL[version][server])
        df_metric = df_grouped_by_server[metric].reindex(server_labelled)
        ax = df_metric.plot(
            kind="bar",
            rot=0,
            # title=to_title_case(title),
            ylim=ylim,  # type: ignore
            xlabel="Server",
            ylabel="Penggunaan memori (MB)",
            figsize=(10, 5),
            color=COLOR,
        )
        excel_filename = slugify(f"{version}-{title}") + ".xlsx"
        df_metric.to_excel(os.path.join(PLOT_FOLDER, excel_filename))

        bars = ax.patches
        hatches = [h for h in HATCH for j in range(len(df_metric))]

        for bar, hatch in zip(bars, hatches):
            bar.set_hatch(hatch)
        modify_ax(ax, title, font_size=12, show_legend=False, fmt=fmt)

        filename = slugify(f"{version}-{title}") + ".png"
        logging.info(f"Saving {filename}")
        plt.savefig(os.path.join(PLOT_FOLDER, filename), bbox_inches="tight")


def create_chart_metric(input_file):
    """Create chart for each metric in the input file and save it to the PLOT_FOLDER folder

    Args:
        input_file (_type_): xlsx file that contains the data to be plotted
    """
    df = get_metric_from_summary_file(input_file)
    df["memory_usage"] = df["memory_total"] - df["memory_available"]
    df["memory_in_mb"] = df["memory_usage"] / 1000000
    df["memory_usage_percent"] = df["memory_usage"] / df["memory_total"] * 100
    data_frames = split_dataframe_per_version(df)
    for version in data_frames:
        df_version = data_frames[version]
        label_version = LABEL[version]
        for old_label in label_version:
            new_label = label_version[old_label]
            df_version.loc[df_version["server"] == old_label, "server"] = new_label
        create_bar_chart(df_version, version)
        create_time_chart(df_version, version)

def create_average_chart_siege_and_metric(df_bar: pd.DataFrame, df_line: pd.DataFrame, server_list: str):
    font_size: int = 6 
    fmt: str = "%.1f"
    fig, ax = plt.subplots(1, facecolor='white', figsize=(10, 7))
    df_bar.plot(
        x='server',
        kind='bar',
        xlabel="Endpoint",
        ylabel="Transaction Per Second (TPS)",
        color=COLOR,
        ax=ax,
        legend=None
    )

    ab = df_line.plot(
        x='server',
        linestyle='-', 
        marker='o',
        secondary_y=True,
        ylabel="Memory Usage (MB)",
        ylim=(0,8000),
        ax=ax,
        legend=None
    )

    bars = ax.patches
    for bar, color in zip(bars, COLOR):
        bar.set_color(color)
    for container in ax.containers:  # type: ignore
        ax.bar_label(container, label_type="edge", fontsize=font_size, fmt=fmt)
    for index, v in df_line.iterrows():
        label = "{:.2f}".format(v['Mean Memory Usage'])
        plt.annotate(label, (index, v['Mean Memory Usage']), ha='left', fontsize=font_size)
    fig.legend(loc='upper center',
                    title=server_list,
                    ncol=4,
                    fancybox=True,
                    shadow=True
                    )

    filename = slugify(f"{server_list}-komparasi-rataan-memori-dan-tps") + ".png"
    logging.info(f"Saving {filename}")
    plt.savefig(os.path.join(PLOT_FOLDER, filename), bbox_inches="tight")

def create_chart_metric_with_siege(input_file):
    metric_dict = get_metric_per_endpoint(input_file)
    siege_dict = get_dict_from_siege(input_file)
    print(metric_dict)
    # version = ["v1", "v2", "v3"]
    # version = ["pool"]
    version = ["banding"]
    font_size: int = 6 
    fmt: str = "%.1f"
    for server_list in version:
        logging.info(f"Currently create {server_list}")
        version_dict_siege: Dict[str, list] = {}
        version_dict_metric: Dict[str, list] = {}
        for dict in (version_dict_siege, version_dict_metric):
            dict["endpoint"] = ENDPOINT_INCLUDE_VERSION[server_list]
            
        mean_dict_siege: Dict[str, list] = {}
        mean_dict_metric: Dict[str, list] = {}
        for dict in (mean_dict_metric, mean_dict_siege):
            dict["server"] = SERVER[server_list]

        mean_siege = []
        mean_metric = []
        for server in SERVER[server_list]:
            value_siege_endpoint = []
            value_chart_endpoint = []
            for endpoint in ENDPOINT_INCLUDE_VERSION[server_list]:
                value_siege_endpoint.append(siege_dict[server][endpoint])
                value_chart_endpoint.append(metric_dict[server][endpoint])
            version_dict_siege[server] = value_siege_endpoint
            version_dict_metric[server] = value_chart_endpoint
            mean_siege.append(mean(value_siege_endpoint))
            mean_metric.append(mean(value_chart_endpoint))
        mean_dict_siege["Mean TPS"] = mean_siege
        mean_dict_metric["Mean Memory Usage"] = mean_metric
        create_average_chart_siege_and_metric(pd.DataFrame(mean_dict_siege), pd.DataFrame(mean_dict_metric), server_list)
        siege_data = pd.DataFrame(version_dict_siege)
        metric_data = pd.DataFrame(version_dict_metric)
        
        fig, ax = plt.subplots(1, facecolor='white', figsize=(10, 7))
        siege_data.plot(
            x='endpoint',
            kind='bar',
            xlabel="Endpoint",
            ylabel="Transaction Per Second (TPS)",
            color=COLOR,
            ax=ax,
            legend=None
        )
        
        ab = metric_data.plot(
            x='endpoint',
            linestyle='-', 
            marker='o',
            secondary_y=True,
            ylabel="Memory Usage (MB)",
            ax=ax,
            legend=None
        )

        for container in ax.containers:  # type: ignore
            ax.bar_label(container, label_type="edge", fontsize=font_size, fmt=fmt)

        fig.legend(loc='upper center',
                    title=server_list,
                    ncol=4,
                    fancybox=True,
                    shadow=True
                    )

        filename = slugify(f"{server_list}-komparasi-memori-dan-tps") + ".png"
        logging.info(f"Saving {filename}")
        plt.savefig(os.path.join(PLOT_FOLDER, filename), bbox_inches="tight")

def to_title_case(inp: str):
    """Convert input string to title case

    Args:
        inp (str): input string

    Returns:
        _type_: string in title case
    """
    return inp.replace("_", " ").title()


def modify_ax(
    ax: plt.Axes, title: str, font_size: int = 6, show_legend=True, fmt: str = "%.1f", bar=True
):
    """Modify the axis of the plot

    Args:
        ax (plt.Axes): axis of the plot
        title (str): title of the plot
        font_size (int, optional): _description_. Defaults to 6.
        show_legend (bool, optional): _description_. Defaults to True.
        fmt (str, optional): _description_. Defaults to "%.1f".
    """
    if show_legend:
        ax.legend(
            loc="upper center",
            title=title,
            bbox_to_anchor=(0.5, 1.175),
            ncol=5,
            fancybox=True,
            shadow=True,
        )

    if bar:
        for container in ax.containers:  # type: ignore
            ax.bar_label(container, label_type="edge", fontsize=font_size, fmt=fmt)


def create_chart_per_endpoint(
    endpoint: str, df_version: pd.DataFrame, version: str, column_to_compare: str
):
    logging.info(f"Creating plot for {endpoint}")
    df_endpoint_separated = df_version.loc[df_version["endpoint"] == endpoint]
    concurrents = df_endpoint_separated["concurrent"].unique()
    data = {"concurrent": concurrents}
    for v1_server_name in SERVER[version]:
        df_v1_server = df_endpoint_separated.loc[
            df_endpoint_separated["server"] == v1_server_name
        ]
        df_v1_server = (
            df_v1_server.groupby(["concurrent"], dropna=False)
            .mean(numeric_only=True)
            .sort_values(by=["concurrent"])
        )
        label = LABEL[version][v1_server_name]
        data[label] = df_v1_server[column_to_compare].tolist()

    print(data)
    new_df = pd.DataFrame(data)

    title = f"{endpoint}"
    y_label = [l for l in LABEL[version].values()]
    ax = new_df.plot(
        kind="bar",
        x="concurrent",
        y=y_label,
        ylabel="Transaksi per detik",
        xlabel="Konkurensi",
        rot=0,
        width=0.85,
        figsize=(10, 5),
        color=COLOR,
        # fill=False,
    )
    bars = ax.patches
    hatches = [h for h in HATCH for j in range(len(new_df))]

    excel_filename = slugify(f"{version}-{title}") + ".xlsx"
    new_df.to_excel(os.path.join(PLOT_FOLDER, excel_filename))

    for bar, hatch in zip(bars, hatches):
        bar.set_hatch(hatch)

    modify_ax(ax, title)

    logging.info(f"{version} Saving {title}")
    filename = slugify(f"{version}-{title}") + ".png"
    plt.savefig(os.path.join(PLOT_FOLDER, filename), bbox_inches="tight")


def create_chart_all_endpoint(
    df_version: pd.DataFrame, column_to_compare: str, version: str
):
    endpoints = df_version["endpoint"].unique()
    datas = {"endpoint": endpoints}
    for v1_server_name in SERVER[version]:
        df_v1_server = df_version.loc[df_version["server"] == v1_server_name]
        df_endpoint_grouped = (
            df_v1_server.groupby(["endpoint"], dropna=False)
            .mean(numeric_only=True)
            .sort_values(by=["endpoint"])
        )
        label = LABEL[version][v1_server_name]
        datas[label] = df_endpoint_grouped[column_to_compare].tolist()

    new_df = pd.DataFrame(datas)
    title = f"Komparasi Semua Endpoint"
    y_label = [l for l in LABEL[version].values()]
    ax = new_df.plot(
        kind="bar",
        x="endpoint",
        y=y_label,
        ylabel="Transaksi per detik",
        xlabel="Endpoint",
        rot=0,
        width=0.85,
        figsize=(10, 5),
        color=COLOR,
        # fill=False,
    )
    bars = ax.patches
    hatches = [h for h in HATCH for j in range(len(new_df))]

    excel_filename = slugify(f"{version}-{title}") + ".xlsx"
    new_df.to_excel(os.path.join(PLOT_FOLDER, excel_filename))

    for bar, hatch in zip(bars, hatches):
        bar.set_hatch(hatch)

    modify_ax(ax, title)

    logging.info(f"{version} Saving {title}")
    filename = slugify(f"{version}-{title}") + ".png"
    plt.savefig(os.path.join(PLOT_FOLDER, filename), bbox_inches="tight")


def create_chart_combine_all_endpoint(
    df_version: pd.DataFrame, column_to_compare: str, version: str
):
    title = f"Kombinasi semua endpoint"
    df_server_grouped = df_version.groupby(["server"], dropna=False).mean(
        numeric_only=True
    )
    ax = df_server_grouped.plot(
        kind="bar",
        y="transaction_rate",
        ylabel="Transaksi per detik",
        xlabel="Endpoint",
        rot=0,
        width=0.85,
        figsize=(10, 5),
        color=COLOR,
    )
    bars = ax.patches
    hatches = [h for h in HATCH for j in range(len(df_server_grouped))]

    excel_filename = slugify(f"{version}-{title}") + ".xlsx"
    df_server_grouped.to_excel(os.path.join(PLOT_FOLDER, excel_filename))

    for bar, hatch in zip(bars, hatches):
        bar.set_hatch(hatch)

    modify_ax(ax, title)

    logging.info(f"{version} Saving {title}")
    filename = slugify(f"{version}-{title}") + ".png"
    plt.savefig(os.path.join(PLOT_FOLDER, filename), bbox_inches="tight")

def get_dict_from_siege(input_file):
    df = pd.read_excel(input_file, sheet_name="All")
    data: Dict[str, Dict[str, int]] = {}
    server_names = df["server"].unique()
    for name in server_names:
        df_server = df.loc[df["server"] == name]
        endpoints = df_server["endpoint"].unique()
        endpoint_server: Dict[str, int] = {}
        for endpoint in endpoints:
            df_endpoint = df_server.loc[df_server["endpoint"] == endpoint]
            mean_tps_endpoint = df_endpoint.mean(numeric_only=True)["transaction_rate"]
            endpoint_server[endpoint] = mean_tps_endpoint
        data[name] = endpoint_server
    return data

def create_chart_siege_result(input_file):
    logging.info(f"Creating chart from {input_file}")
    df = pd.read_excel(input_file, sheet_name="All")
    # df = df.loc[~df["endpoint"].isin(EXCLUDE_ENDPOINT_ALL)]

    data_frames = split_dataframe_per_version(df)
    column_to_compare = "transaction_rate"

    for version in data_frames:
        df_version = data_frames[version]
        excluded_endpoint = ENDPOINT_EXCLUDE_VERSION[version]
        df_version = df_version.loc[~df_version["endpoint"].isin(excluded_endpoint)]
        endpoints = df_version["endpoint"].unique()
        for endpoint in endpoints:
            create_chart_per_endpoint(endpoint, df_version, version, column_to_compare)
        create_chart_all_endpoint(df_version, column_to_compare, version)
        create_chart_combine_all_endpoint(df_version, column_to_compare, version)


def main():
    args = sys.argv
    if len(args) < 2:
        print(
            """Usage: python create_chart.py filename
filname is an xlsx file generated from get_summary.py script
example: create_chart.py summary/all.xlsx"""
        )
        sys.exit(1)

    create_chart_siege_result(args[1])
    create_chart_metric(args[1])
    # create_chart_metric_with_siege(args[1])


if __name__ == "__main__":
    main()
