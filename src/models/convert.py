import argparse

from convert_utils.llama_utils import (
    llama_change_model_config_eos,
    llama_translate_config_to_model_config,
    convert_ggml,
    LLAMA_CPP_HOME
)
from convert_utils.mlc_utils import (
    mlc_get_max_length,
    mlc_change_model_template_eos,
    mlc_translate_config_to_model_config,
    convert_mlc,
    MLC_HOME
)


def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument('-m', '--model', type=str, required=True,
                      help='Model name to download (should be in hf format.)')
    args.add_argument('-d', '--output-dir', type=str, required=True,
                      help='Directory to download the model to.')
    args.add_argument('-b', '--backend', type=str, required=True,
                      choices=['mlc', 'ggml'],
                      help='Backend to convert to.')
    args.add_argument('-q', '--quantization-mode', type=str, required=True,
                      help='Quantization mode to use.')
    args.add_argument('-t', '--target', type=str,
                      choices=['android', 'ios', 'metal'],
                      help='Target to compile for.')
    args.add_argument('-c', '--config', type=str, required=True,
                      help='Path to config file.')
    args.add_argument('--ignore-eos', action='store_true',
                      help='Ignore EOS token (changes model config).')
    args.add_argument('-v', '--verbose', action='store_true',)

    return args.parse_args()

def validate_args(args):
    if args.backend == 'mlc':
        if not MLC_HOME:
            raise ValueError(
                'MLC_HOME is not set. Please set it to the root of your TVM installation.')
    elif args.backend == 'ggml':
        if not LLAMA_CPP_HOME:
            raise ValueError(
                'LLAMA_CPP_HOME is not set. Please set it to the root of your LLAMA_CPP installation.')


def main(args):
    if args.backend == 'mlc':
        args.max_seq_length = mlc_get_max_length(args.config)
        chat_config_path = convert_mlc(args.model, args)
        if chat_config_path and args.ignore_eos:
            mlc_change_model_template_eos(chat_config_path)
        mlc_translate_config_to_model_config(args.config, chat_config_path)
    elif args.backend == 'ggml':
        previous_eos = None
        if args.ignore_eos:
            previous_eos = llama_change_model_config_eos(args.model, 2335)
        convert_ggml(args.model, args)
        if args.ignore_eos:  # revert it back for indepotence
            llama_change_model_config_eos(args.model,
                                          previous_eos)
        llama_translate_config_to_model_config(args.config, args.output_dir,
                                               ignore_eos=args.ignore_eos)
    else:
        raise ValueError(f'Invalid mode: {args.mode}')


if __name__ == '__main__':
    args = parse_args()
    validate_args(args)
    main(args)
