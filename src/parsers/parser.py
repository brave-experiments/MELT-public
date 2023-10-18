
import os
import pandas as pd

from utils.utils import (
    parse_args,
    parse_file,
    merge_ops
)


def main(args):
    if args.mode == 'file':
        if args.backend == 'mlc':
            calls_dfs, device_metrics_dfs, config_dfs = parse_file(args.input,
                                                                   args.backend,
                                                                   args.verbose)
        elif args.backend == 'llama.cpp':
            weights_df, calls_summary_dfs, calls_dfs = parse_file(args.input, args.backend, args.verbose)

    elif args.mode == 'logcat':
        raise NotImplementedError
    elif args.mode == 'ios':
        raise NotImplementedError
    else:
        raise ValueError('Invalid mode: {}'.format(args.mode))

    if args.merge:
        if args.backend == 'mlc':
            count_per_module = {}
            for k, df in calls_dfs.items():
                op = k.split('_')[0]
                df['Module'] = op
                count_per_module[op] = count_per_module.get(op, 0) + 1
            df_merged = pd.concat([*calls_dfs.values()])

            if args.merge == 'per_module':
                print(f"Merging per module: {set([k.split('_')[0] for k in calls_dfs.keys()])}")
                df_merged = merge_ops(df_merged, group_cols=['Module'], drop_cols=['Device', 'Name', 'Percent', 'Argument Shapes',])
                for module in df_merged.index:
                    df_merged.loc[module, 'Count'] = count_per_module[module]

            elif args.merge == 'per_op':
                print(f"Merging across modules: {set([k.split('_')[0] for k in calls_dfs.keys()])}")
                df_merged = merge_ops(df_merged, ['Name', 'Device'], drop_cols=['Module', 'Percent', 'Argument Shapes',])

            else:
                raise ValueError(f"Invalid merge mode: {args.merge}")

            if args.verbose:
                print(df_merged)

        elif args.backend == 'llama.cpp':
            if args.merge == 'per_module':
                df_merged_detailed = merge_ops(calls_dfs, ['node_num', 'Name'],
                                      drop_cols=["Argument Shapes"])
            elif args.merge == 'per_op':
                df_merged_detailed = merge_ops(calls_dfs, ['Name'],
                                               drop_cols=["Argument Shapes", "node_num"])
                df_merged_summary = merge_ops(calls_summary_dfs, ['Name'])


    if args.output:
        os.makedirs(args.output, exist_ok=True)

        if args.backend == 'mlc':
            for key, _ in calls_dfs.items():
                calls_dfs[key].to_csv(os.path.join(args.output, f'calls_{key}.csv'), index=False)
                device_metrics_dfs[key].to_csv(os.path.join(args.output, f'device_metrics_{key}.csv'),
                                               index=False)
                config_dfs[key].to_csv(os.path.join(args.output, f'config_{key}.csv'), index=False)

            if args.merge:
                df_merged.to_csv(os.path.join(args.output, f'calls_merged_{args.merge}.csv'),
                                index=True)
        elif args.backend == 'llama.cpp':
            weights_df.to_csv(os.path.join(args.output, 'weights.csv'), index=False)
            calls_summary_dfs.to_csv(os.path.join(args.output, 'calls_summary.csv'), index=False)
            calls_dfs.to_csv(os.path.join(args.output, 'calls.csv'), index=False)

            if args.merge:
                df_merged_detailed.to_csv(
                    os.path.join(args.output, f'calls_merged_detailed_{args.merge}.csv'),
                    index=True)
                if args.merge == 'per_op':
                    df_merged_summary.to_csv(
                        os.path.join(args.output, f'calls_merged_summary_{args.merge}.csv'),
                        index=True)


if __name__ == '__main__':
    args = parse_args()
    main(args)
