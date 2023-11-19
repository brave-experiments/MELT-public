#!/usr/bin/python

import sys
import os
import argparse

import pandas as pd

from libs import powerlib


# this is the last event in group of measurements; will also drive the timestamp
EVENT_DRIVER = "current_VDDQ_VDD2_1V8AO"


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

        # TODO: might crash if end match does not exist (never happened so far)
        end = edf[edf.index == end_key].value.values[0]

        duration = end - start

        # power consumption
        start_time = start / 1_000_000_000  # to sec
        end_time =  end / 1_000_000_000  # to sec
        monsoon_df_trimmed = mdf[(mdf.timestamp > start_time) & (mdf.timestamp < end_time)]

        entry = {
            "run": run,
            "stage": stage,
            "duration (ns)": duration,
        }

        relevant_power_events = ['VDD_GPU_SOC', 'VDD_CPU_CV', 'VIN_SYS_5V0', 'NC', 'VDDQ_VDD2_1V8AO']
        for power_event in relevant_power_events:
            total_energy, total_discharge = powerlib.compute_power_performance(monsoon_df_trimmed, f"current_{power_event} (mA)", f"voltage_{power_event} (V)")
            entry[f"energy {power_event} (mWh)"] = total_energy
            entry[f"discharge {power_event} (mAh)"] = total_discharge

        data.append(entry)
    
    # save
    odf = pd.DataFrame(data)
    return odf


def main(args):
    input_path = args.path
    output = args.output

    # load data
    edf = load_energy_events(os.path.join(input_path, "energy_events.txt"))
    mdf = load_energy_metrics(os.path.join(input_path, "energy_metrics.log"))

    # compute
    run = 0  # TODO: Are we going to run multiple times?
    odf = compute_detailed_performance_metrics(run, edf, mdf)
    odf.to_csv(output, index=False)


# argument parser
def __parse_arguments(args):

    parser = argparse.ArgumentParser(description="Analyze energy events from jetson devices.")

    parser.add_argument("-p", "--path",
        required=True,
        help="Input path where the two files (i.e., 'energy_events.txt' and 'energy_metrics.log') should be available.")

    parser.add_argument("-o", "--output",
        default="results.csv",
        help="Output file.")

    parsed = parser.parse_args(args)
    return parsed


if __name__ == '__main__':

    # parse args
    arguments = __parse_arguments(sys.argv[1:])
    main(arguments)