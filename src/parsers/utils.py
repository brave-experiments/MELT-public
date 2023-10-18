import json
from json.decoder import JSONDecodeError
import argparse
import re


def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument('-m', '--mode', type=str, choices=['file', 'logcat', 'ios'], required=True)
    args.add_argument('-i', '--input', type=str)
    args.add_argument('-o', '--output', type=str)
    args.add_argument('-v', '--verbose', action='store_true', default=False)
    args.add_argument('--merge', type=str, choices=['per_module', 'per_op'], default=None)

    return args.parse_args()


def parse_json(json_string):
    metrics_dict = json.loads(json_string)

    return metrics_dict


def parse_file(log_file):
    with open(log_file, 'r') as f:
        lines = f.readlines()

    filtered_lines = []
    regex = r"(.*)Report from function (.+):$"

    idx = 0
    while idx < len(lines):
        line = lines[idx]
        match = re.match(regex, line)
        if match:
            _, func_name = match.groups()
            print('---->', match.groups())
            print(idx, lines[idx])
            print(idx + 1, lines[idx + 1])
            try:
                filtered_lines.append((func_name, parse_json(lines[idx + 1])))
            except JSONDecodeError:
                print("Invalid line: {}".format(lines[idx + 1]))
            idx += 1
        idx += 1

    return filtered_lines


def normalize_calls(calls_df):
    assoc = {
        'Percent': 'percent',
        'Count': 'count',
        'Device': 'string',
        'Duration (us)': 'microseconds',
        'Name': 'string',
        'Argument Shapes': 'string'
    }
    for col in calls_df.columns:
        # print(col, calls_df[col].dtype)
        calls_df[col] = calls_df[col].str.get(assoc[col])

    return calls_df


def merge_ops(df_merged, group_cols=['Name', 'Device'], drop_cols=[]):
    df_grouped = df_merged.groupby(group_cols)
    df_merged = df_grouped.sum()
    print(df_merged)

    df_merged.drop(columns=[
                    'Percent',
                    'Argument Shapes',
                    *drop_cols,
                    ], inplace=True)
    return df_merged


def parse_config(config_dict):
    ret_dict = {}
    ret_dict['num_threads'] = config_dict['Number of threads']
    ret_dict['executor'] = config_dict['Executor']['string']

    return ret_dict