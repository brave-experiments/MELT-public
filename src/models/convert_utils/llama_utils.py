import json
import os
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


def llama_translate_config_to_model_config(config_path, model_path):
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
    }

    print("Arguments to pass to main.py:")
    for arg, val in main_args.items():
        print(f"\t{arg} {val} \\")
    output_filename = os.path.join(model_path, 'llama_main_args.txt')
    print(f"Persisted in {output_filename}")
    with open(output_filename, 'w') as f:
        for arg, val in main_args.items():
            f.write(f"{arg} {val} \\\n")


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
