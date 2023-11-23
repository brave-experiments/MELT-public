import argparse
import json
import os
import re
import subprocess
import yaml

MLC_HOME = os.environ.get('MLC_HOME')
LLAMA_CPP_HOME = os.environ.get('LLAMA_CPP_HOME')


def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument('-m', '--models', nargs='+', required=True,
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
            raise ValueError('MLC_HOME is not set. Please set it to the root of your TVM installation.')
    elif args.backend == 'ggml':
        if not LLAMA_CPP_HOME:
            raise ValueError('LLAMA_CPP_HOME is not set. Please set it to the root of your LLAMA_CPP installation.')


def convert_mlc(model_dir, args):
    exec_path = os.path.join(MLC_HOME, "build.py")
    proc = subprocess.Popen(
        ["python", exec_path,
         "--model", model_dir,
         "--artifact-path", args.output_dir,
         "--quantization", args.quantization_mode,
         "--target", args.target,
         "--use-cache=0",
         "--max-seq-len", f"{args.max_seq_length}"],
         stdout=subprocess.PIPE,
         stderr=subprocess.PIPE,)
    stdout, stderr = proc.communicate()
    regex = "Finish exporting chat config to (.*)"
    match = re.search(regex, stdout.decode('utf-8'))
    chat_config_path = None
    if match:
        chat_config_path = match.group(1)
    if args.verbose:
        print(stdout.decode('utf-8'))
        print(stderr.decode('utf-8'))

    return chat_config_path


def convert_ggml(model_dir, args):
    model_name = os.path.basename(model_dir)
    os.makedirs(args.output_dir, exist_ok=True)
    gguf_model = os.path.join(args.output_dir, model_name+".gguf")
    exec_path = os.path.join(LLAMA_CPP_HOME, 'convert.py')
    ignore_eos_flag = '--ignore-eos' if args.ignore_eos else ''
    proc = subprocess.Popen(
        ["python", exec_path,
         "--outfile", gguf_model,
         ignore_eos_flag,
         model_dir,],
         stdout=subprocess.PIPE,
         stderr=subprocess.PIPE,)
    stdout, stderr = proc.communicate()
    if args.verbose:
        print(stdout.decode('utf-8'))
        print(stderr.decode('utf-8'))

    name, extension = gguf_model.split('.')
    gguf_quant_model = f"{name}-{args.quantization_mode}.{extension}"
    exec_path = os.path.join(LLAMA_CPP_HOME, 'build', 'bin', 'quantize')
    proc = subprocess.Popen(
        [exec_path,
         gguf_model,
         gguf_quant_model,
         args.quantization_mode,],
         stdout=subprocess.PIPE,
         stderr=subprocess.PIPE,)
    stdout, stderr = proc.communicate()
    if args.verbose:
        print(stdout.decode('utf-8'))
        print(stderr.decode('utf-8'))


def llama_change_model_config_eos(model_dir,  eos_token_id=2336):
    config_json = os.path.join(model_dir, 'config.json')
    with open(config_json, 'r') as f:
        config = json.load(f)

    previous_eos_token_id = config.get('eos_token_id', None)
    config['eos_token_id'] = eos_token_id

    with open(config_json, 'w') as f:
        json.dump(config, f)

    return previous_eos_token_id


def mlc_translate_config_to_model_config(config_path, chat_config_path):
    with open(chat_config_path, 'r') as f:
        model_config = json.load(f)

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    model_config['temperature'] = config['sampling'].get('temperature', model_config['temperature'])
    model_config['repetition_penalty'] = \
        config['sampling'].get('repetition_penalty', model_config['repetition_penalty'])
    model_config['top_p'] = config['sampling'].get('top_p', model_config['top_p'])
    # model_config[''] = config['sampling'].get('top_k', model_config[''])  # TODO: Resolve in MLC
    # model_config[''] = config['sampling'].get('repeat_last_n', model_config[''])  # TODO: Resolve in MLC
    # model_config[''] = config['sampling'].get('n_batch', model_config[''])  # TODO: Resolve in MLC

    model_config['mean_gen_len'] = \
        config['generation'].get('mean_gen_len', model_config['mean_gen_len'])
    model_config['max_gen_len'] = \
        config['generation'].get('max_gen_len', model_config['max_gen_len'])
    model_config['max_window_size'] = \
        config['generation'].get('max_window_size', model_config['max_window_size'])
    model_config['vocab_size'] = \
        config['generation'].get('vocab_size', model_config['vocab_size'])

    with open(chat_config_path, 'w') as f:
        json.dump(model_config, f)

    return config


def mlc_get_max_length(config_path):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    return config['generation'].get('max_gen_len', None)


def mlc_change_model_template_eos(chat_config_path):
    with open(chat_config_path, 'r') as f:
        config = json.load(f)

    previous_template = config.get("conv_template", None)
    if previous_template:
        config["conv_template"] = f"{previous_template}-unconstrained"

    with open(chat_config_path, 'w') as f:
        json.dump(config, f)


def main(args):
    for model_dir in args.models:
        if args.backend == 'mlc':
            args.max_seq_length = mlc_get_max_length(args.config)
            chat_config_path = convert_mlc(model_dir, args)
            if chat_config_path and args.ignore_eos:
                mlc_change_model_template_eos(chat_config_path)
            if args.config:
                mlc_translate_config_to_model_config(args.config, chat_config_path)
        elif args.backend == 'ggml':
            previous_eos = None
            if args.ignore_eos:
                previous_eos = llama_change_model_config_eos(model_dir, 2335)
            convert_ggml(model_dir, args)
            if args.ignore_eos:  # revert it back for indepotence
                llama_change_model_config_eos(model_dir,
                                              previous_eos)
        else:
            raise ValueError(f'Invalid mode: {args.mode}')


if __name__ == '__main__':
    args = parse_args()
    validate_args(args)
    main(args)
