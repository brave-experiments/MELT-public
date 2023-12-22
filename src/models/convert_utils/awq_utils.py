import re

from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer


def decode_quant_method(quant_string):
    quant_config = {}
    regex = r'q(\d+)g(\d+)_(\S+)'
    match = re.match(regex, quant_string)
    if match:
        w_bit = int(match.group(1))
        q_group_size = int(match.group(2))
        q_version = match.group(3)
    else:
        w_bit, q_group_size, q_version = None, None, None

    quant_config = { "zero_point": True,
                     "q_group_size": q_group_size,
                     "w_bit": w_bit,
                     "version": q_version.upper() }

    return quant_config


def quantize_awq(model_path, output_path, quant_config):
    # Load model
    model = AutoAWQForCausalLM.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

    # Quantize
    model.quantize(tokenizer, quant_config=quant_config)

    # Save quantized model
    model.save_quantized(output_path)
    tokenizer.save_pretrained(output_path)
