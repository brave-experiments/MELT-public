# Note:   Script to easily download models from the Hugging Face Hub.
# Author: Stefanos Laskaridis (stefanos@brave.com)

import argparse
import os
from huggingface_hub import snapshot_download


def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument('-m', '--models', nargs='+', required=True,
                      help='Model name to download (should be in hf format.)')
    args.add_argument('-d', '--download-dir', type=str, required=True,
                      help='Directory to download the model to.')
    args.add_argument('-f', '--force', action='store_true',
                      help='Overwrite existing files.')
    args.add_argument('-t', '--token', type=str, required=False,)

    return args.parse_args()


def main(args):
    for model in args.models:
        model_dir_name = model.replace('/', '_')
        print(f'-> Downloading model: {model}')
        target_path = os.path.join(args.download_dir, model_dir_name)
        model_path = snapshot_download(repo_id=model,
                                       local_dir=target_path,
                                       cache_dir=os.environ.get('TRANSFORMERS_CACHE', None),
                                       force_download=args.force,
                                       token=args.token)
        print(f"-> Model {model} downloaded to {args.download_dir}/{model_path}.")


if __name__ == '__main__':
    args = parse_args()
    main(args)
