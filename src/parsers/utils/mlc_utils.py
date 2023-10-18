import re
import json
from json.decoder import JSONDecodeError

import pandas as pd


def parse_json(json_string):
    metrics_dict = json.loads(json_string)

    return metrics_dict


def parse_logfile(log_file, verbose=False):
    with open(log_file, 'r') as f:
        lines = f.readlines()

    ops_metrics = []
    regex = r"(.*)Report from function (.+):$"

    idx = 0
    while idx < len(lines):
        line = lines[idx]
        match = re.match(regex, line)
        if match:
            _, func_name = match.groups()
            try:
                ops_metrics.append((func_name, parse_json(lines[idx + 1])))
            except JSONDecodeError:
                print(f"Invalid line: {lines[idx + 1]}")
            idx += 1
        idx += 1

    ops_count = {op: 0 for op in list(set([op for op, _ in ops_metrics]))}
    calls_dfs = {}
    device_metrics_dfs = {}
    config_dfs = {}
    for op, metrics_dict in ops_metrics:
        calls_df = pd.DataFrame(metrics_dict['calls'])
        device_metrics_df = pd.DataFrame(metrics_dict['device_metrics'])
        config_df = pd.DataFrame(parse_config(metrics_dict['configuration']))

        calls_df = normalize_calls(calls_df)
        device_metrics_df = normalize_calls(device_metrics_df.transpose())

        calls_dfs[f"{op}_{ops_count[op]}"] = calls_df
        device_metrics_dfs[f"{op}_{ops_count[op]}"] = device_metrics_df
        config_dfs[f"{op}_{ops_count[op]}"] = config_df
        ops_count[op] += 1

        if verbose:
            print("==="*3,  op, "==="*3)
            print("device_metrics_df\n", device_metrics_df)
            print("config_df\n", config_df)
            print("calls_df\n", calls_df)

    return calls_dfs, device_metrics_dfs, config_dfs


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


def parse_config(config_dict):
    ret_dict = {}
    ret_dict['num_threads'] = config_dict['Number of threads']
    ret_dict['executor'] = config_dict['Executor']['string']

    return ret_dict