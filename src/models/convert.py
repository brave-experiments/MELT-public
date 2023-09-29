import argparse
import subprocess
import os

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
    args.add_argument('-q', '--quantization-mode', type=str, required=True,)
    args.add_argument('-t', '--target', type=str,
                      choices=['android', 'ios', 'metal'])
    args.add_argument('--max-seq-length', type=str, required=True,)
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
    model_name = os.path.basename(model_dir)
    exec_path = os.path.join(MLC_HOME, "build.py")
    proc = subprocess.Popen(
        ["python", exec_path,
         "--model", model_dir,
         "--artifact-path", model_name,
         "--quantization", args.quantization_mode,
         "--target", args.target,
         "--max-seq-len", args.max_seq_length],
         stdout=subprocess.PIPE,
         stderr=subprocess.PIPE,)
    stdout, stderr = proc.communicate()
    if args.verbose:
        print(stdout.decode('utf-8'))
        print(stderr.decode('utf-8'))


def convert_ggml(model_dir, args):
    model_name = os.path.basename(model_dir)
    os.makedirs(args.output_dir, exist_ok=True)
    gguf_model = os.path.join(args.output_dir, model_name+".gguf")
    exec_path = os.path.join(LLAMA_CPP_HOME, 'convert.py')
    proc = subprocess.Popen(
        ["python", exec_path,
         "--outfile", gguf_model,
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


def main(args):
    for model_dir in args.models:
        if args.backend == 'mlc':
            convert_mlc(model_dir, args)
        elif args.backend == 'ggml':
            convert_ggml(model_dir, args)
        else:
            raise ValueError(f'Invalid mode: {args.mode}')


if __name__ == '__main__':
    args = parse_args()
    validate_args(args)
    main(args)
