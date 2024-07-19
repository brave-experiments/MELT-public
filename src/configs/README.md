# Model Config Files

These are configuration files that describe various model and execution level parameters for how to run the models. You can think of them as hyperparameters in some cases.

They are typically initialised by what is found in `frameworks/MLC/mlc-llm/cpp/conv_templates.cc`, so as to provide a common ground between frameworks.

These are later used by jetsonlab and phonelab to be translated into target specific configuration parameters, such as CLI arguments in the case of llama.cpp or JSON configs in the case of LLMFarm.