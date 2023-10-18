import re

import pandas as pd

def parse_logfile(log_file, verbose=False):
    with open(log_file, 'r') as f:
        lines = f.readlines()

    weights_pattern = r"llama_model_loader:\s+-\s+tensor\s+(\d+):\s+(\S+)\s+(\S+)\s+\[\s+(\d+),\s+(\d+),\s+(\d+),\s+(\d+)\s+\]"
    weights_regex = re.compile(weights_pattern)
    weights_delimiter = "." * 98

    totals_pattern = r"perf_total_per_op_us\[\s*(\w+)\]\s*=\s*([\d.]+)\s*ms"
    totals_regex = re.compile(totals_pattern)
    totals_delimiter = "=" * 40

    per_op_delimiter_pattern = r'n_nodes = (\d+)'
    per_op_delimiter_regex = re.compile(per_op_delimiter_pattern)
    per_op_pattern = r"\s*-\s*(\d+): \[\s*(\d+),\s*(\d+),\s*(\d+)\]\s+([\S+]+)\s+\(\s*(\d+)\) cpu\s*=\s*(\d+\.?\d+)\s*/\s*(\d+\.?\d+) ms, \s*wall\s*=\s*(\d+\.?\d+)\s*/\s*(\d+\.?\d+) ms\s*"
    per_op_regex = re.compile(per_op_pattern)

    weights_details = []
    current_token_op_summary_latencies = []
    current_token_op_detailed_latencies = []
    idx = 0
    weights_parsed_flag = False
    while idx < len(lines):
        line = lines[idx]
        if not weights_parsed_flag:
            if match := re.match(weights_regex, line):
                tensor_num = match.groups()[0]
                tensor_name = match.groups()[1]
                tensor_qtype = match.groups()[2]
                dimensions = [int(match.groups()[i]) for i in range(3, 7)]
                weights_details.append({
                    'Name': tensor_name,
                    'Quantization': tensor_qtype,
                    'Dimensions': dimensions
                })

        if match := re.match(totals_regex, line):
            while line.strip() != totals_delimiter and idx < len(lines):
                match = re.match(totals_regex, line)
                if match is None:
                    raise ValueError(f"Invalid line: {line}")
                op, duration_ms = match.groups()
                current_token_op_summary_latencies.append({
                    'Name': op,
                    'Duration (ms)': float(duration_ms)
                })
                idx += 1
                line = lines[idx]
        elif match := re.match(per_op_delimiter_regex, line):
            num_nodes = int(match.groups()[0])
            for jdx in range(1, num_nodes + 1):
                line = lines[idx + jdx]
                match = re.match(per_op_regex, line)
                if match is None:
                    raise ValueError(f"Invalid line: {line}")

                node_num = int(match.group(1))
                dimensions = [int(match.group(i)) for i in range(2, 5)]
                wall_time = float(match.group(9))
                op = match.group(5)
                cpu_time_ms = float(match.group(7))

                current_token_op_detailed_latencies.append({
                    'Name': op,
                    'Duration (ms)': cpu_time_ms,
                    'Wall time (ms)': wall_time,
                    'Argument Shapes': dimensions,
                    'node_num': node_num
                })
            idx += jdx
        else:
            idx += 1

    weights_df = pd.DataFrame(weights_details)
    summary_df = pd.DataFrame(current_token_op_summary_latencies)
    detailed_df = pd.DataFrame(current_token_op_detailed_latencies)

    if verbose:
        print("weights_details\n", weights_df)
        print("summary_df\n", summary_df)
        print("detailed_df\n", detailed_df)

    return weights_df, summary_df, detailed_df