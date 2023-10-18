
import os
import pandas as pd

from utils import (
    parse_args,
    parse_file,
    parse_config,
    normalize_calls,
    merge_ops
)

def main(args):
    if args.mode == 'file':
        ops_metrics = parse_file(args.input)
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

            if args.verbose:
                print("==="*3,  op, "==="*3)
                print(device_metrics_df)
                print(config_df)
                print(calls_df)

    elif args.mode == 'logcat':
        raise NotImplementedError
    elif args.mode == 'ios':
        raise NotImplementedError
    else:
        ValueError('Invalid mode: {}'.format(args.mode))

    if args.merge:
        count_per_module = {}
        for k, df in calls_dfs.items():
            op = k.split('_')[0]
            df['Module'] = op
            count_per_module[op] = count_per_module.get(op, 0) + 1
        df_merged = pd.concat([*calls_dfs.values()])

        if args.merge == 'per_module':
            print(f"Merging per module: {set([k.split('_')[0] for k in calls_dfs.keys()])}")
            df_merged = merge_ops(df_merged, group_cols=['Module'], drop_cols=['Device', 'Name'])
            for module in df_merged.index:
                df_merged.loc[module, 'Count'] = count_per_module[module]

        elif args.merge == 'per_op':
            print(f"Merging across modules: {set([k.split('_')[0] for k in calls_dfs.keys()])}")
            df_merged = merge_ops(df_merged, ['Name', 'Device'], drop_cols=['Module'])

        else:
            ValueError(f"Invalid merge mode: {args.merge}")

        if args.verbose:
            print(df_merged)

    if args.output:
        os.makedirs(args.output, exist_ok=True)

        for key in calls_dfs.keys():
            calls_dfs[key].to_csv(os.path.join(args.output, f'calls_{key}.csv'), index=False)
            device_metrics_dfs[key].to_csv(os.path.join(args.output, f'device_metrics_{key}.csv'), index=False)
            config_dfs[key].to_csv(os.path.join(args.output, f'config_{key}.csv'), index=False)

        if args.merge:
            df_merged.to_csv(os.path.join(args.output, f'calls_merged_{args.merge}.csv'), index=True)


if __name__ == '__main__':
    args = parse_args()
    main(args)