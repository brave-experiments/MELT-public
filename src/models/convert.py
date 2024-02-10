import argparse
import os

from convert_utils.llama_utils import (
    llama_change_model_config_eos,
    llama_translate_config_to_model_config,
    convert_ggml,
    convert_yaml_to_json_config,
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
                      choices=['mlc', 'ggml', 'awq'],
                      help='Backend to convert to.')
    args.add_argument('-q', '--quantization-mode', type=str, required=True,
                      help='Quantization mode to use.')
    args.add_argument('-t', '--target', type=str,
                      choices=['android', 'iphone', 'metal', 'cuda'],
                      help='Target to compile for.')
    args.add_argument('-c', '--config', type=str, required=False,
                      help='Path to config file.')
    args.add_argument('--only-config', action='store_true',
                      help='Produce only the config file')
    args.add_argument('--ignore-eos', action='store_true',
                      help='Ignore EOS token (changes model config).')
    args.add_argument('-v', '--verbose', action='store_true',)

    return args.parse_args()

def validate_args(args):
    if args.backend == 'mlc':
        if not MLC_HOME:
            raise ValueError(
                'MLC_HOME is not set. Please set it to the root of your TVM installation.')
        if not args.config:
            raise ValueError(
                'MLC requires a config file to be specified.')
    elif args.backend == 'ggml':
        if not LLAMA_CPP_HOME:
            raise ValueError(
                'LLAMA_CPP_HOME is not set. Please set it to the root of your LLAMA_CPP installation.')
        if not args.config:
            raise ValueError(
                'MLC requires a config file to be specified.')
    elif args.backend == 'awq':
        try:
            from convert_utils.awq_utils import (
                decode_quant_method,
                quantize_awq
            )
        except ModuleNotFoundError as e:
            print('Please install awq on an nvidia-machine to use the awq backend.')
            exit(1)


def main(args):
    if args.backend == 'mlc':
        if args.only_config:
            raise NotImplementedError('Only config is only supported for ggml.')
        args.max_seq_length = mlc_get_max_length(args.config)
        chat_config_path = convert_mlc(args.model, args)
        if chat_config_path and args.ignore_eos:
            mlc_change_model_template_eos(chat_config_path)
        mlc_translate_config_to_model_config(args.config, chat_config_path)
    elif args.backend == 'ggml':
        if not args.only_config:
            previous_eos = None
            if args.ignore_eos:
                previous_eos = llama_change_model_config_eos(args.model, 2335)
            convert_ggml(args.model, args)
        if args.ignore_eos:  # revert it back for indepotence
            llama_change_model_config_eos(args.model,
                                          previous_eos)
        llama_translate_config_to_model_config(args.config, args.output_dir,
                                               ignore_eos=args.ignore_eos)
        convert_yaml_to_json_config(args.config, os.path.join(args.output_dir, 'model_config.json'))
    elif args.backend == 'awq':
        from convert_utils.awq_utils import (
                decode_quant_method,
                quantize_awq
        )
        quant_config = decode_quant_method(args.quantization_mode)
        quantize_awq(args.model, args.output_dir, quant_config)
    else:
        raise ValueError(f'Invalid mode: {args.mode}')


if __name__ == '__main__':
    args = parse_args()
    validate_args(args)
    main(args)
