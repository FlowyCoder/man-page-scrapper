import os
import json
from enum import Enum

# Get man page into file man
man_page_name = "git stash"
# man_page_name = "node"
os.system('man {} >> man'.format(man_page_name))

# Get right lines from man page
# We need SYNOPSIS
# First line DESCRIPTION
# maybe commands
# OPTIONS


class Keyword(Enum):
    BEF = 0
    SYN = 1
    DESC = 2
    COM = 3
    OPT = 4


# Create section line arrays
syn = []
desc = []
com = []
opt = []

current_section = 0

print("here")


def handle_syn():
    global current_section
    # Section has to be zero before
    #assert(current_section == Keyword.BEF)
    print("here2")
    current_section = Keyword.SYN
    return


print("here")


def handle_desc():
    global current_section
    # Section has to be zero before
    assert(current_section == Keyword.SYN)
    current_section = Keyword.DESC
    return


def handle_com():
    global current_section
    # Section has to be zero before
    assert(current_section == Keyword.DESC)
    current_section = Keyword.COM
    return


def handle_opt():
    global current_section
    # Section has to be zero before
    # assert(current_section == Keyword.COM)
    current_section = Keyword.OPT
    return


def handle_def(line):
    global current_section
    if current_section == Keyword.BEF:
        # Do not care about this case
        pass
    elif current_section == Keyword.SYN:
        syn.append(line)
    elif current_section == Keyword.DESC:
        desc.append(line)
    elif current_section == Keyword.COM:
        com.append(line)
    elif current_section == Keyword.OPT:
        opt.append(line)
    else:
        # Error Case
        print("unexpected", current_section)
    return


switch_sections = {
    "SYNOPSIS": handle_syn,
    "DESCRIPTION": handle_desc,
    "COMMANDS": handle_com,
    "OPTIONS": handle_opt
}

if __name__ == '__main__':
    with open("man") as file:  # Use man page
        lines = file.readlines()
        for line in lines:
            # Get first word
            first_word = line.lstrip().split(" ")[0].strip()
            if first_word in switch_sections.keys():
                # Call function for handling section
                switch_sections[first_word]()
            else:
                handle_def(line)

# Now we have the context of the sections that we need
# We can start parsing

# Steps for parsing
# 1. Get tokens from options section
# 2. Create parsing for each line of synopsis
# 3. Create tree dictionary for each entry

# Get all tokens
# Structure is the following:
# 1. Command line argument -x, --x
# 2. Valid for
# 3. Description for the Command line argument

# Splitted absed on option
options = []


def handle_opt_options(line):
    global options
    # We have 3 different possibilities for the number of options
    # 1. --x
    # 2. -x, --x
    # 3. -x, --x, --no-x
    # and each option can have its own arguments
    args = line.split(',')
    option_dict = {"args": args}
    options.append(option_dict)


def handle_opt_def(line):
    # Handle description
    global options
    options_dict = options[-1]
    if "desc" in options_dict.keys():
        options_dict["desc"].append(line)
    else:
        options_dict["desc"] = [line]


for option_line in opt:
    line = option_line.strip()
    print(line)
    if line != '' and line[0] == '-':
        # Have option
        handle_opt_options(line)
    else:
        handle_opt_def(line)

# Options are parsed
# Care there are still empty lines in it. Will be used for later

# Parse SYN
# []... Option
# <>... args
# x|y... different names for the same set of options and args

# String in that all syn are combined
string_syn = ' '.join(syn)
syns = string_syn.strip().split(man_page_name)
syn_strip = [syn.strip() for syn in syns if syn != '']

# Parsing idea bottom up
# 1. Split into smallest token


def parsing_pipe(symboles):
    # TODO: more than 1 pipe symbol
    len_symboles = len(symboles)
    index = 0
    while index < len_symboles:
        if symboles[index] == '|':
            # 2 possibilities
            # it is subcommand name
            # or options

            # Check if hyphen is in index-1
            # If it is the case then we have an option
            if '-' in symboles[index-1]:
                temp_dict = {
                    "name": [symboles[index-1], symboles[index+1]]
                }
                # Remove the 2 symboles around |
                del symboles[(index-1):(index+2)]
                symboles.insert(index-1, temp_dict.copy())
                # Removed symboles -> list gets smaller
                # Dont add 1 to index
                len_symboles -= 2
            else:
                # TODO: needs to be implemented
                temp_dict = {
                    "name1": symboles[index-1],
                    "name2": symboles[index+1]
                }
                # Remove the 2 symboles around |
                del symboles[(index-1):(index+2)]
                symboles.insert(index-1, temp_dict.copy())
                # Removed symboles -> list gets smaller
                # Dont add 1 to index
                len_symboles -= 2
        else:
            index += 1
    return symboles


def parsing_parenthese(symboles):
    # TODO: how to implement this
    return symboles


def parsing_less_than(symboles):
    # Idea: find all opening brackets. Store them in queue
    # If you find closing bracket. Pop last index from queue
    # at the items between to options
    index_open = []
    len_symboles = len(symboles)
    index = 0
    while index < len_symboles:
        if symboles[index] == '<':
            index_open.append(index)
            index += 1
        elif symboles[index] == '>':
            index_open_bracket = index_open.pop()
            # Range from index_open_bracket to index is option
            range_options = symboles[(index_open_bracket+1):(index)]

            args = {"args": []}
            for option in range_options:
                # TODO: check for type of option
                # Dict or list or string
                args["args"].append({
                    "name": option
                })
            del symboles[index_open_bracket:(index+1)]
            symboles.insert(index_open_bracket, args)
            len_symboles = len_symboles - (index - index_open_bracket)
            index = index_open_bracket+1

        else:
            index += 1

    return symboles


def parsing_bracket(symboles):
    # Idea: find all opening brackets. Store them in queue
    # If you find closing bracket. Pop last index from queue
    # at the items between to options
    index_open = []
    len_symboles = len(symboles)
    index = 0
    while index < len_symboles:
        if symboles[index] == '[':
            index_open.append(index)
            index += 1
        elif symboles[index] == ']':
            index_open_bracket = index_open.pop()
            # Range from index_open_bracket to index is option
            range_options = symboles[(index_open_bracket+1):(index)]

            option_list = []
            for option in range_options:
                # TODO: check for type of option
                # Dict or list or string
                option_list.append({
                    "option": option
                })
            del symboles[index_open_bracket:(index+1)]
            symboles.insert(index_open_bracket, option_list)
            len_symboles = len_symboles - (index - index_open_bracket)
            index = index_open_bracket+1

        else:
            index += 1

    return symboles


split_symboles = [
    '[', '<', '(',
    ']', '>', ')',
    '|',
]

syn_symbol_trees = []

# TODO: git stash not working prob
for line_sync in syn_strip[:5]:
    symboles = [line_sync]

    for split_symbole in split_symboles:
        temp_symboles = []
        for symbole in symboles:
            splitted = symbole.split(split_symbole)
            # Check if it is at the beginning
            number_splits = len(splitted)
            # If first split index is '' then there where the split symbol
            if splitted[0] == '':
                temp_symboles.append(split_symbole)
                del splitted[0]

            remove_last_symbol = True
            if splitted[-1] == '':
                del splitted[-1]
                remove_last_symbol = False

            for split in splitted:
                # Append splitted string and split symbol after that
                temp_symboles.append(split.strip())
                temp_symboles.append(split_symbole)

            # If last splitted is not -1 that means that there should
            # not be the split symbol
            if remove_last_symbol:
                del temp_symboles[-1]

        symboles = temp_symboles.copy()
    print("here")
    # Put them back together
    # Following order:
    # |, (), <>, []
    concat_functions = [
        parsing_pipe, parsing_parenthese, parsing_less_than, parsing_bracket
    ]
    for concat_function in concat_functions:
        symboles = concat_function(symboles)

    syn_symbol_trees.append(symboles)

with open('dict.txt', 'w') as file:
    # use `json.loads` to do the reverse
    file.write(json.dumps(syn_symbol_trees, indent=4))

# Delete temp file man
os.system('rm man')
