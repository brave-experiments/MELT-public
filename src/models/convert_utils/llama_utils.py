import json
import os
import requests
import subprocess
import yaml

LLAMA_CPP_HOME = os.environ.get('LLAMA_CPP_HOME')


def llama_change_model_config_eos(model_dir,  eos_token_id=2336):
    config_json = os.path.join(model_dir, 'config.json')
    with open(config_json, 'r') as f:
        config = json.load(f)

    previous_eos_token_id = config.get('eos_token_id', None)
    config['eos_token_id'] = eos_token_id

    with open(config_json, 'w') as f:
        json.dump(config, f)

    return previous_eos_token_id


def llama_translate_config_to_model_config(config_path, model_path, ignore_eos=False):
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
            if val != '':
                f.write(f"{arg} {val} \\\n")


def convert_ggml(model_dir, args):
    model_name = os.path.basename(model_dir).lower()
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
    else:
        args_list = ["python", exec_path,
                     "--outfile", gguf_model,
                     model_dir]

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


def llama_download_gguf_zephyr(quantization_mode, output_dir):
    url_prefix = "https://huggingface.co/TheBloke/stablelm-zephyr-3b-GGUF/resolve/main"
    url_suffix = f"stablelm-zephyr-3b.{quantization_mode.upper()}.gguf"
    the_url = '/'.join([url_prefix, url_suffix])
    outfile = os.path.join(output_dir, url_suffix)

    if not os.path.isfile(outfile):
        with open(outfile, 'wb') as f:
            r = requests.get(the_url, stream=True, allow_redirects=True)
            f.write(r.content)
    else:
        print("File exists. Skipping download.")
