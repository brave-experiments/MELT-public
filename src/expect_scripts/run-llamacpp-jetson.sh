#!/usr/bin/expect

package require json

#exp_internal 1

# Check if an argument is provided
if { $argc != 6 } {
    puts "Usage: $argv0 input_path model_name input_prompts_filename conversation_from conversation_to output_path"
    exit 1
}

# config
set timeout -1
set sleep_time 5
set input_path [lindex $argv 0]
set model_name [lindex $argv 1]
set input_prompts_filename [lindex $argv 2]
set conversation_from [expr {int([lindex $argv 3])}]
set conversation_to [expr {int([lindex $argv 4])}]
set output_path [lindex $argv 5]
set log_path "$output_path/llm_output.txt"
log_file $log_path
set measurements "$output_path/measurements_ts.csv"
set llama_cpp_path "$env(LLAMA_CPP_HOME)"

# This is the gguf file generated by melt/src/models/convert.py script.
set model_path "$input_path/$model_name"

# This is the file generated by melt/src/models/convert.py script.
set extra_args_path "$input_path/llama_main_args.txt"

# define store metrics function
proc store_metrics {start_time end_time state measurements} {
    set duration [expr {double($end_time - $start_time) / 1000.0}]
    set start_time_epoch [expr {$start_time / 1000.0}]
    exec echo "$start_time_epoch,$duration,$state\r" >> "$measurements"
}

# Read the JSON file
set file_data [read [open $input_prompts_filename r]]
set input_prompts [json::json2dict $file_data]

# set range
if {$conversation_to > [expr [llength $input_prompts] -1] } {
    set conversation_to [expr [llength $input_prompts] -1]
}
set input_prompts [lrange $input_prompts $conversation_from $conversation_to]

# init measurements file (write csv header)
exec echo "start_date,duration,state\r" > "$measurements"

# Read the file contents
set fd [open $extra_args_path]
set extra_args_str [read $fd]
close $fd

# debug
puts $extra_args_str

# get expect prompt
set expect_prompt ">"
regexp {in-prefix\s+"([^\"]+)"} $extra_args_str match expect_prompt
set expect_prompt [string map {"\\n" ""} $expect_prompt]
puts $expect_prompt


# init variables, this init states are proxy to model loading
set start_time [clock milliseconds]
set state "load_model"

# Use 'list' to construct the command and arguments properly
set command [list spawn $llama_cpp_path/build/bin/main \
    --model $model_path \
    --interactive \
    -e]

# Function to process and append arguments
proc append_args {cmd line} {
    set in_quote 0
    set arg ""
    foreach char [split $line ""] {
        if {$char eq "\""} {
            if {$in_quote} {
                lappend cmd $arg
                set arg ""
            }
            set in_quote [expr !$in_quote]
        } elseif {$in_quote || $char ne " "} {
            append arg $char
        } elseif {[string length $arg] > 0} {
            lappend cmd $arg
            set arg ""
        }
    }
    if {[string length $arg] > 0} {
        lappend cmd $arg
    }
    return $cmd
}

# Append arguments from the file to the command list
foreach line [split $extra_args_str \n] {
    # Trim the line to remove whitespace and backslashes
    set trimmed_line [string trimright $line \\\ ]
    if {[string length $trimmed_line] == 0} {
        continue
    }

    # Process and append the arguments
    set command [append_args $command $trimmed_line]
}

# Append the remaining arguments
lappend command "--interactive-first" "--log-file" "output_raw"

# Execute the command
eval $command

# save pid
set pid [exp_pid]

sleep $sleep_time

# iterate through conversations
foreach conversation $input_prompts {

    # iterate through prompts
    foreach prompt $conversation {

        expect -ex $expect_prompt {

            # save metrics of previous prompt (or model load if first iteration)
            set end_time [clock milliseconds]
            store_metrics $start_time $end_time $state $measurements

            sleep $sleep_time

            # save state vars for next iteration and send the prompt
            set state $prompt
            set start_time [clock milliseconds]
            send "$prompt\r"
        }
    }

    # TODO: clear context
}

# finish
expect -ex $expect_prompt {

    # save last metrics
    set end_time [clock milliseconds]
    store_metrics $start_time $end_time $prompt $measurements

    sleep $sleep_time

    # send SIGINT to report LLM stats and exit
    exec kill -2 $pid

    expect eof
}
