#!/usr/bin/python

import sys
import os
import argparse

import pandas as pd


# this is the last event in group of measurements; will also drive the timestamp
EVENT_DRIVER = "current_VDDQ_VDD2_1V8AO"


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



def load_energy_events(filepath):

    df = pd.read_csv(filepath, header=None, delimiter=" ", index_col=0, names=['event', 'value'])
    return df


def load_energy_metrics(filepath):

    data = []
    last_entry_buffer = {}
    
    with open(filepath) as file:
        for line in file:
            
            values = line.split(" ")
            if len(values) != 4:
                continue
            
            timestamp = int(values[0])
            event = values[1][:-1]  # -1 to remove ':'
            metric = values[3][:-1]  # -1 to remove '\n'
            key = f"{event} ({metric})"
            value = float(values[2])

            last_entry_buffer["timestamp"] = timestamp
            last_entry_buffer[key] = value

            if event == EVENT_DRIVER:
                data.append(last_entry_buffer)
                last_entry_buffer = {}

    df = pd.DataFrame(data)

    # ns to sec
    df["timestamp"] /= 1_000_000_000  # to sec

    # mV to V for all relevant columns
    for column in df.columns:
        if column.endswith("(mV)"):
            new_column = column.replace("(mV)", "(V)")
            df[new_column] = df[column] / 1_000

    return df


def compute_detailed_performance_metrics(run, edf, mdf):

    data = []
    
    df_start = edf[edf.index.str.endswith("start")]
    for index, row in df_start.iterrows():

        start = row.value
        stage = index.replace(".start", "")
        end_key = index.replace("start", "end")

        end_event = edf[edf.index == end_key]
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
            "run": run,
            "stage": stage,
            "duration (ns)": duration,
        }

        # all columns starting with current, removing "current_" prefix and " (mA)" postfix, e.g., 'current_VDD_GPU_SOC (mA)' to 'VDD_GPU_SOC'
        relevant_power_events = [column.replace("current_", "").replace(" (mA)", "") for column in df_trimmed.columns if column.startswith("current_")]
        for power_event in relevant_power_events:
            total_energy, total_discharge = compute_power_performance(df_trimmed, f"current_{power_event} (mA)", f"voltage_{power_event} (V)")
            entry[f"energy {power_event} (mWh)"] = total_energy
            entry[f"discharge {power_event} (mAh)"] = total_discharge

        data.append(entry)
    
    # save
    odf = pd.DataFrame(data)
    return odf


def main(args):
    input_event_file = args.input_event_file
    input_metrics_file = args.input_metrics_file
    output_file = args.output_file

    # load data
    edf = load_energy_events(input_event_file)
    mdf = load_energy_metrics(input_metrics_file)

    # compute
    run = 0  # TODO: Are we going to run multiple times?
    odf = compute_detailed_performance_metrics(run, edf, mdf)
    odf.to_csv(output_file, index=False)


# argument parser
def __parse_arguments(args):

    parser = argparse.ArgumentParser(description="Analyze energy events from jetson devices.")

    parser.add_argument("-ief", "--input-event-file",
        required=True,
        help="Input energy events file.")
    
    parser.add_argument("-imf", "--input-metrics-file",
        required=True,
        help="Input energy metrics file.")

    parser.add_argument("-of", "--output-file",
        required=True,
        help="Output CSV file.")

    parsed = parser.parse_args(args)
    return parsed


if __name__ == '__main__':

    # parse args
    arguments = __parse_arguments(sys.argv[1:])
    main(arguments)