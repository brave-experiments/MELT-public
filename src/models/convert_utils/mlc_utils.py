import glob
import json
import os
import re
import subprocess
import yaml

MLC_HOME = os.environ.get('MLC_HOME')


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
    if 'max_window_size' in model_config:
        model_config['max_window_size'] = \
            config['generation'].get('max_window_size', model_config['max_window_size'])
    model_config['vocab_size'] = \
        config['generation'].get('vocab_size', model_config['vocab_size'])

    model_config['conv_template'] = \
        config['prompt'].get('conv_template', model_config['conv_template'])

    with open(chat_config_path, 'w') as f:
        json.dump(model_config, f)

    return config


def convert_mlc(model_dir, args):
    model_name = os.path.basename(model_dir).lower()
    exec_path = os.path.join(MLC_HOME, "build.py")
    args_list = ["python", exec_path,
                 "--model", model_dir,
                 "--artifact-path", args.output_dir,
                 "--quantization", args.quantization_mode,
                 "--target", args.target,
                 "--max-seq-len", f"{args.max_seq_length}"]

    if ('tinyllama' in model_name) or ('stablelm-zephyr' in model_name):
        args_list.append("--use-safetensors")

    print(f"Running cmd: {' '.join(args_list)}")
    proc = subprocess.Popen(
        args_list,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,)
    stdout, stderr = proc.communicate()
    regex = "Finish exporting chat config to (.*)"
    match = re.search(regex, stdout.decode('utf-8'))
    chat_config = os.path.join(args.output_dir, '**', 'params', 'mlc-chat-config.json')
    chat_config_path = glob.glob(chat_config)[0]
    if match:
        chat_config_path = match.group(1)
    if args.verbose:
        print(stdout.decode('utf-8'))
        print(stderr.decode('utf-8'))

    return chat_config_path
