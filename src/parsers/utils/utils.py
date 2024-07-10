# Note:   Utility functions for parsing and merging the logs from the MLC and llama.cpp backends.
# Author: Stefanos Laskaridis (stefanos@brave.com)

import argparse

from .llamacpp_utils import parse_logfile as llamacpp_parse_logfile
from .mlc_utils import parse_logfile as mlc_parse_logfile


def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument(
        "-b", "--backend", type=str, choices=["mlc", "llama.cpp"], required=True
    )
    args.add_argument("-i", "--input", type=str)
    args.add_argument("-o", "--output", type=str)
    args.add_argument("-v", "--verbose", action="store_true", default=False)
    args.add_argument(
        "--merge", type=str, choices=["per_module", "per_op"], default=None
    )

    return args.parse_args()


def parse_file(log_file, backend, verbose):
    if backend == "mlc":
        return mlc_parse_logfile(log_file, verbose)

    if backend == "llama.cpp":
        return llamacpp_parse_logfile(log_file, verbose)

    raise ValueError(f"Invalid backend: {backend}")


def merge_ops(df_merged, group_cols=["Name", "Device"], drop_cols=[]):
    df_grouped = df_merged.groupby(group_cols)
    df_merged = df_grouped.sum()

    df_merged.drop(columns=drop_cols, inplace=True)

    return df_merged
