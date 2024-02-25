#!/usr/bin/python

import sys
import os
import argparse
import glob
import re
import json

import pandas as pd


def compute_power_performance(df, current_col="current", voltage_col="voltage"):
    # input is a df with columns: timestamp (sec), current (mA), voltage (V)

    power = df[current_col] * df[voltage_col]  # in mW
    time_diff = df.timestamp.diff().fillna(0) / 3600  # in hours

    # energy
    energy = power * time_diff  # in mWh
    total_energy_mWh = energy.sum()  # in mWh

    # discharge
    discharge = df[current_col] * time_diff  # in mAh
    total_discharge_mAh = discharge.sum()  # in mAh

    return total_energy_mWh, total_discharge_mAh


def __get_value_from_string(input_string, sep_after, sep_before):

    idx_to = input_string.rfind(sep_after)

    if idx_to == -1:
        return -1

    idx_from = input_string[:idx_to].rfind(sep_before) + 1

    idx_from = max(0, idx_from)

    return input_string[idx_from:idx_to]


def load_energy_events(filepath):

    df = pd.read_csv(filepath, header=None, delimiter=" ", index_col=0, names=['event', 'value'])
    return df


def load_energy_metrics(filepath):

    data = []
    
    with open(filepath, encoding='utf-8') as file:
        for line in file:
            
            values = line.split(" ")
            if len(values) != 4:
                continue
            
            timestamp = int(values[0])
            event = values[1][:-1]  # -1 to remove ':'
            metric = values[3][:-1]  # -1 to remove '\n'
            key = f"{event} ({metric})"
            value = float(values[2])

            data.append({
                "timestamp": timestamp,
                "event": key,
                key: value,
            })

    df = pd.DataFrame(data)

    # ns to sec
    df["timestamp"] /= 1_000_000_000  # to sec

    # mV to V for all relevant columns
    for column in df.columns:
        if column.endswith("(mV)"):
            new_column = column.replace("(mV)", "(V)")
            df[new_column] = df[column] / 1_000
    
    # back-fill NaNs and drop pending NaNs (last rows)
    df.bfill(inplace=True)
    df.dropna(inplace=True)

    return df


def load_ts_data(filepath):

    if not os.path.isfile(filepath):
        sys.exit(f"Error: Could not read '{filepath}'.")

    df = pd.read_csv(filepath, index_col=0)

    return df


def check_app_type(filepath):

    # if first line has substring "main" then it is LlamaCpp. If it has "mlc" then it is MLC.
    with open (filepath, encoding='utf-8') as file:
        first_line = file.readline()
        if "main" in first_line:
            return "llamacpp"

        elif "mlc" in first_line:
            return "mlc"

        else:
            sys.exit(f"Error: Could not infer application type from '{filepath}'.")


def compute_llamacpp_performance_metrics(filepath_csv, filepath_txt, iteration, conversation, mdf):

    # this is the measurements equivalent file for LlamaCpp (but in csv format)
    df = load_ts_data(filepath_csv)

    # load txt
    with open(filepath_txt, encoding='utf-8') as f:
        txt_lines = f.readlines()

    records_list = []
    load_model_list = []

    # Read all relevant timings
    TOTAL_STATS_LINES_PER_PROMPT = 5
    llama_cpp_stats = []
    regex = "llama_print_timings:.*"
    for line in txt_lines:
        if re.match(regex, line):
            llama_cpp_stats.append(line)
    first_idx = (len(llama_cpp_stats) // TOTAL_STATS_LINES_PER_PROMPT - (len(df) - 1)) * TOTAL_STATS_LINES_PER_PROMPT

    for start_time, row in df.iterrows():

        # properties
        duration = row.duration
        end_time = start_time + duration

        # power consumption
        df_trimmed = mdf[(mdf.timestamp > start_time) & (mdf.timestamp < end_time)]

        # all columns starting with current, removing "current_" prefix and " (mA)" postfix, e.g., 'current_VDD_GPU_SOC (mA)' to 'VDD_GPU_SOC'
        relevant_power_events = [column.replace("current_", "").replace(" (mA)", "") for column in df_trimmed.columns if column.startswith("current_")]

        if row.state == "load_model":
            entry = {
                "iteration": iteration,
                "conversation": conversation,
                "duration (sec)": duration,
            }

            for power_event in relevant_power_events:
                df_trimmed_current_events = df_trimmed[df_trimmed["event"] == f"current_{power_event} (mA)"]
                total_energy, total_discharge = compute_power_performance(df_trimmed_current_events, f"current_{power_event} (mA)", f"voltage_{power_event} (V)")
                entry[f"energy {power_event} (mWh)"] = total_energy
                entry[f"discharge {power_event} (mAh)"] = total_discharge

            load_model_list.append(entry)

        else:
            # get prompt index
            prompt_idx = df.index.get_loc(start_time) - 1  # 1st is always 'load_model' event
            real_idx = first_idx + prompt_idx * TOTAL_STATS_LINES_PER_PROMPT

            # get relevant metrics from txt file
            stats = llama_cpp_stats[real_idx:real_idx+TOTAL_STATS_LINES_PER_PROMPT]

            # example stats:
            # llama_print_timings:        load time =     525.17 ms
            # llama_print_timings:      sample time =       4.28 ms /    21 runs   (    0.20 ms per token,  4909.98 tokens per second)
            # llama_print_timings: prompt eval time =    2501.52 ms /    51 tokens (   49.05 ms per token,    20.39 tokens per second)
            # llama_print_timings:        eval time =    1041.43 ms /    20 runs   (   52.07 ms per token,    19.20 tokens per second)
            # llama_print_timings:       total time =   11653.83 ms
            original_session_tokens = -1  # TODO check
            input_tokens = int(__get_value_from_string(stats[2], "tokens (", "/"))  # 51 tokens
            output_tokens = int(__get_value_from_string(stats[3], "runs", "/"))  # 20 tokens
            tps = float(__get_value_from_string(stats[2], "tokens per second", ","))  # 20.39 tokens per second

            entry = {
                "iteration": iteration,
                "conversation": conversation,
                "prompt": prompt_idx,
                "duration (sec)": duration,
                "original_session_tokens": original_session_tokens,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "tps": tps,
            }

            for power_event in relevant_power_events:
                df_trimmed_current_events = df_trimmed[df_trimmed["event"] == f"current_{power_event} (mA)"]
                total_energy, total_discharge = compute_power_performance(df_trimmed_current_events, f"current_{power_event} (mA)", f"voltage_{power_event} (V)")
                entry[f"energy_pt {power_event} (mWh)"] = total_energy / output_tokens
                entry[f"discharge_pt {power_event} (mAh)"] = total_discharge / output_tokens

            records_list.append(entry)

    return pd.DataFrame.from_records(load_model_list), pd.DataFrame.from_records(records_list)


def compute_mlc_performance_metrics(filepath_csv, filepath_txt, iteration, conversation, mdf):

    # this is the measurements equivalent file for LlamaCpp (but in csv format)
    df = load_ts_data(filepath_csv)

    # load txt
    with open(filepath_txt, encoding='utf-8') as f:
        txt_lines = f.readlines()

    records_list = []
    load_model_list = []

    # Read all relevant timings
    TOTAL_STATS_LINES_PER_PROMPT = 12

    # find idx of all /stats jsons
    json_idxs = []
    for idx, line in enumerate(txt_lines):
        if "[INST]: /stats" in line:
            json_idxs.append(idx + 1)
    
    # parse jsons
    mlc_stats = []
    for idx in json_idxs:
        json_str = "".join(txt_lines[idx:idx+TOTAL_STATS_LINES_PER_PROMPT])
        stats = json.loads(json_str)
        mlc_stats.append(stats)

    for start_time, row in df.iterrows():

        # properties
        duration = row.duration
        end_time = start_time + duration

        # power consumption
        df_trimmed = mdf[(mdf.timestamp > start_time) & (mdf.timestamp < end_time)]

        # all columns starting with current, removing "current_" prefix and " (mA)" postfix, e.g., 'current_VDD_GPU_SOC (mA)' to 'VDD_GPU_SOC'
        relevant_power_events = [column.replace("current_", "").replace(" (mA)", "") for column in df_trimmed.columns if column.startswith("current_")]

        if row.state == "load_model":
            entry = {
                "iteration": iteration,
                "conversation": conversation,
                "duration (sec)": duration,
            }

            for power_event in relevant_power_events:
                df_trimmed_current_events = df_trimmed[df_trimmed["event"] == f"current_{power_event} (mA)"]
                total_energy, total_discharge = compute_power_performance(df_trimmed_current_events, f"current_{power_event} (mA)", f"voltage_{power_event} (V)")
                entry[f"energy {power_event} (mWh)"] = total_energy
                entry[f"discharge {power_event} (mAh)"] = total_discharge

            load_model_list.append(entry)

        else:
            # get prompt index
            prompt_idx = df.index.get_loc(start_time) - 1  # 1st is always 'load_model' event

            # get relevant metrics from txt file
            # TODO: its fixed to 0 because of a bug in the data collection
            stats = mlc_stats[0]

            # example stats:
            # {
            # 	"prefill": {
            # 		"throughput": "283.4 tok/s",
            # 		"total tokens": "47 tok",
            # 		"total time": "0.2 s"
            # 	},
            # 	"decode": {
            # 		"throughput": "22.7 tok/s",
            # 		"total tokens": "255 tok",
            # 		"total time": "11.3 s"
            # 	}
            # }
            original_session_tokens = -1  # TODO check
            input_tokens = int(stats["prefill"]["total tokens"].replace("tok", ""))
            output_tokens = int(stats["decode"]["total tokens"].replace("tok", ""))
            tps = float(stats["decode"]["throughput"].replace("tok/s", ""))

            entry = {
                "iteration": iteration,
                "conversation": conversation,
                "prompt": prompt_idx,
                "duration (sec)": duration,
                "original_session_tokens": original_session_tokens,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "tps": tps,
            }

            for power_event in relevant_power_events:
                df_trimmed_current_events = df_trimmed[df_trimmed["event"] == f"current_{power_event} (mA)"]
                total_energy, total_discharge = compute_power_performance(df_trimmed_current_events, f"current_{power_event} (mA)", f"voltage_{power_event} (V)")
                entry[f"energy_pt {power_event} (mWh)"] = total_energy / output_tokens
                entry[f"discharge_pt {power_event} (mAh)"] = total_discharge / output_tokens

            records_list.append(entry)

    return pd.DataFrame.from_records(load_model_list), pd.DataFrame.from_records(records_list)


def compute_detailed_performance_metrics(filepath, iteration, conversation, mdf, csv_sep=","):

    df = pd.read_csv(filepath, index_col=0, names=['value'], sep=csv_sep)

    data = []
    
    df_start = df[df.index.str.endswith("start")]
    for index, row in df_start.iterrows():

        start = row.value
        stage = index.replace(".start", "")
        end_key = index.replace("start", "end")

        end_event = df[df.index == end_key]
        if len(end_event) != 1:
            print(f"WARNING: Expecting one matching end_event for '{stage}' and discovered {len(end_event)}. Skipping...")
            continue
        else:
            end = end_event.value.values[0]

        duration = end - start

        # power consumption
        start_time = start / 1_000_000_000  # to sec
        end_time =  end / 1_000_000_000  # to sec
        df_trimmed = mdf[(mdf.timestamp > start_time) & (mdf.timestamp < end_time)]

        entry = {
            "iteration": iteration,
            "conversation": conversation,
            "stage": stage,
            "duration (ns)": duration,
        }

        # all columns starting with current, removing "current_" prefix and " (mA)" postfix, e.g., 'current_VDD_GPU_SOC (mA)' to 'VDD_GPU_SOC'
        relevant_power_events = [column.replace("current_", "").replace(" (mA)", "") for column in df_trimmed.columns if column.startswith("current_")]
        for power_event in relevant_power_events:
            df_trimmed_current_events = df_trimmed[df_trimmed["event"] == f"current_{power_event} (mA)"]
            total_energy, total_discharge = compute_power_performance(df_trimmed_current_events, f"current_{power_event} (mA)", f"voltage_{power_event} (V)")
            entry[f"energy {power_event} (mWh)"] = total_energy
            entry[f"discharge {power_event} (mAh)"] = total_discharge

        data.append(entry)
    
    # save
    odf = pd.DataFrame(data)
    return odf


def __get_iter_from_filename(filename):
    # e.g., from "path/to/measurements_iter0_conv1.csv" return int(0)

    match = re.search(r"iter(\d+)", filename)
    if match is None:
        sys.exit(f"Error: Could not infer iteration from filename '{filename}'.")
    return int(match.group(1))


def __get_conv_from_filename(filename):
    # e.g., from "path/to/measurements_iter0_conv1.csv" return int(1)

    match = re.search(r"conv(\d+)", filename)
    if match is None:
        sys.exit(f"Error: Could not infer conversation from filename '{filename}'.")
    return int(match.group(1))


def main(args):
    
    # get arguments
    path = args.path

    model_perf_metrics_list = []
    inf_perf_metrics_list = []
    detailed_metrics_list = []

    # per iteration (run)
    for filepath_log in glob.glob(os.path.join(path, "energy_iter[0-9]*.log")):

        # infer iteration number from filepath
        iteration = __get_iter_from_filename(filepath_log)

        energy = load_energy_metrics(filepath_log)

        # per csv file (regardless iteration/conversation)
        for filepath_csv in glob.glob(os.path.join(path, "melt_measurements", f"measurements_iter{iteration}_conv[0-9]*.csv")):
            # infer iteration/conversation number from filepath
            conversation = __get_conv_from_filename(filepath_csv)

            # compute the model and inf metrics
            filepath_txt = filepath_csv.replace("measurements_", "llm_output_").replace(".csv", ".txt")
            
            # check if LlamaCpp or MLC
            if check_app_type(filepath_txt) == "llamacpp":
                model_perf_metrics, inf_perf_metrics = compute_llamacpp_performance_metrics(filepath_csv, filepath_txt, iteration, conversation, energy)

            elif check_app_type(filepath_txt) == "mlc":
                model_perf_metrics, inf_perf_metrics = compute_mlc_performance_metrics(filepath_csv, filepath_txt, iteration, conversation, energy)

            model_perf_metrics_list.append(model_perf_metrics)
            inf_perf_metrics_list.append(inf_perf_metrics)

            # detailed metrics (tsv file in case of LlamaCpp)
            try:
                filepath_tsv = filepath_csv.replace(".csv", ".tsv")  # find the equivalent tsv file
                detailed_metrics_list.append(compute_detailed_performance_metrics(filepath_tsv, iteration, conversation, energy, csv_sep=" "))
            except FileNotFoundError:
                print(f"Warning: Could not find detailed measurements for iteration {iteration} and conversation {conversation}.")

    # merge metrics
    df_model_perf = pd.concat(model_perf_metrics_list, ignore_index=True)
    df_inf_perf = pd.concat(inf_perf_metrics_list, ignore_index=True)
    if len(detailed_metrics_list) > 0:
        df_detailed_perf = pd.concat(detailed_metrics_list, ignore_index=True)
    else:
        df_detailed_perf = pd.DataFrame()

    # save
    df_model_perf.to_csv(os.path.join(path, "results_model_load_performance.csv"), index=False)
    df_inf_perf.to_csv(os.path.join(path, "results_model_inference_measurements.csv"), index=False)
    df_detailed_perf.to_csv(os.path.join(path, "results_detailed_measurements.csv"), index=False)


# argument parser
def __parse_arguments(args):

    parser = argparse.ArgumentParser(description="Report measurements from an executed on-device LLM experiment.")

    parser.add_argument("-p", "--path",
        default="measurements",
        help='Data path of executed experiment.')

    parsed = parser.parse_args(args)
    return parsed


if __name__ == '__main__':

    # parse args
    arguments = __parse_arguments(sys.argv[1:])
    main(arguments)
