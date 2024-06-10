# Note:   Util functions for converting models to gguf format.
# Author: Stefanos Laskaridis (stefanos@brave.com)

import json
import os
import shutil
import subprocess
import yaml


LLAMA_CPP_HOME = os.environ.get('LLAMA_CPP_HOME')


def llama_change_model_config_eos(model_dir,  eos_token_id=2336):
    """
    Change the EOS token in the model config file.
    :param model_dir: The path to the model directory.
    :param eos_token_id: The new EOS token id (a random one that is seldom or never used).
    """
    config_json = os.path.join(model_dir, 'config.json')
    with open(config_json, 'r', encoding='utf-8') as f:
        config = json.load(f)

    previous_eos_token_id = config.get('eos_token_id', None)
    config['eos_token_id'] = eos_token_id

    with open(config_json, 'w', encoding='utf-8') as f:
        json.dump(config, f)

    return previous_eos_token_id


def llama_translate_config_to_model_config(config_path, model_path, ignore_eos=False):
    """
    Translates the model config file (from MELT/configs/) to the llama.cpp used format.
    :param config_path: The path to the config file.
    :param model_path: The path to the model directory.
    :param ignore_eos: Whether to ignore the EOS token.
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    main_args = {
        '-n': config['generation']['max_gen_len'],
        '-c': config['generation']['max_window_size'],
        '-b':  config['sampling']['n_batch'],
        '--top-k': config['sampling']['top_k'],
        '--top-p': config['sampling']['top_p'],
        '--repeat-last-n': config['sampling']['repeat_last_n'],
        '--repeat-penalty': config['sampling']['repetition_penalty'],
        '--temp': config['sampling']['temperature'],
        '-e': '',
        '-p': config['prompt'].get('text', ''),
        '--in-prefix': config['prompt'].get('in_prefix', None),
        '--in-suffix': config['prompt'].get('in_suffix', None),
        '-r': config['prompt'].get('reverse', None),
        '--chatml': config['prompt'].get('chatml', None),
    }

    if ignore_eos:
        main_args['--ignore-eos'] = ''

    print("Arguments to pass to main.py:")
    for arg, val in main_args.items():
        if val is not None:
            if val != '':
                print(f"\t{arg} {val} \\")
            else:
                print(f"\t{arg} \\")

    output_filename = os.path.join(model_path, 'llama_main_args.txt')
    print(f"Persisted in {output_filename}")
    with open(output_filename, 'w') as f:
        for arg, val in main_args.items():
            if val is not None:
                f.write(f"{arg} {val} \\\n")


def convert_ggml(model_dir, args):
    """
    Convert a model to gguf format.
    :param model_dir: The path to the model directory.
    :param args: The arguments to pass to the conversion script.
    """
    model_name = os.path.basename(model_dir)
    os.makedirs(args.output_dir, exist_ok=True)
    gguf_model = os.path.join(args.output_dir, model_name+".gguf")
    exec_path = os.path.join(LLAMA_CPP_HOME, 'convert.py')
    if 'tinyllama' in model_name:
        model_filename = os.path.join(model_dir, 'model.safetensors')
        args_list = ["python", exec_path,
                    "--outfile", gguf_model,
                     model_filename]
    elif 'starcoder' in model_name:
        exec_path = os.path.join(LLAMA_CPP_HOME, 'convert-starcoder-hf-to-gguf.py')
        args_list = ["python", exec_path,
                     model_dir,
                     "0",
                    "--outfile", gguf_model]
    elif 'zephyr-3b' in model_name or (model_name in ["google_gemma-2b-it", "google_gemma-7b-it"]):
        exec_path = os.path.join(LLAMA_CPP_HOME, 'convert-hf-to-gguf.py')
        args_list = ["python", exec_path,
                    "--outfile", gguf_model,
                     model_dir,]
    else:
        args_list = ["python", exec_path,
                     "--outfile", gguf_model,
                     model_dir]

    if model_name in ['google_gemma-2b', 'google_gemma-7b']:
        variant = model_name.split('-')[-1]
        print(f"Copying gemma gguf model to {gguf_model}")
        shutil.copyfile(os.path.join(model_dir, f'gemma-{variant}.gguf'), gguf_model)
    else:
        print(f"Running cmd: {' '.join(args_list)}")
        proc = subprocess.Popen(
            args_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,)
        stdout, stderr = proc.communicate()
        if args.verbose:
            print(stdout.decode('utf-8'))
            print(stderr.decode('utf-8'))

    tokens = gguf_model.split('.')
    name = '.'.join(tokens[:-1])
    extension = tokens[-1]
    gguf_quant_model = f"{name}-{args.quantization_mode}.{extension}"
    exec_path = os.path.join(LLAMA_CPP_HOME, 'build', 'bin', 'quantize')
    args_list = [exec_path,
         gguf_model,
         gguf_quant_model,
         args.quantization_mode,]

    print(f"Running cmd: {' '.join(args_list)}")
    proc = subprocess.Popen(
        args_list,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,)
    stdout, stderr = proc.communicate()
    if args.verbose:
        print(stdout.decode('utf-8'))
        print(stderr.decode('utf-8'))

def convert_yaml_to_json_config(yamlconfig, jsonconfig):
    """
    Convert a yaml config to a json config. This is consumed by LLMFarmEval.
    :param yamlconfig: The path to the yaml config file.
    :param jsonconfig: The path to the json config file.
    """
    print(f"Converting yaml config from {yamlconfig} to json config {jsonconfig}")
    with open(yamlconfig, 'r') as f:
        config = yaml.safe_load(f)

    with open(jsonconfig, 'w') as f:
        json.dump(config, f)
