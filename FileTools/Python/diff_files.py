#!/usr/bin/python
# -*- coding: UTF-8 -*-

#################################################################
#   author: zhanghong.personal@outlook.com
#  version: 1.0
#    usage:
#    - compare files: diff_files.py <file/folder to be compared> -db <comparison database file> [-filter <Regular expressions>] [-not-filter <Regular expressions>]
#    - create filedb: diff_files.py <file/folder path> -o <files db name> [-filter <Regular expressions>] [-not-filter <Regular expressions>]
# describe: Find different files based on db
#
# release nodes:
#   2022.**.** - first release
#################################################################

import os
import re
import sys
import pickle
import hashlib

def check_args(input_args):
    """
    检查输入的参数, 并返回需要执行的分支所对于的值
    :param input_args:
    :return: dict, values: compare_dict / create_dict / help_dict
    """
    args_db = "Null"
    args_filter = ".*"
    args_not_filter = None
    args_output = "Null"
    args_dst_folder = "Null"

    if len(input_args) > 1:
        args_dst_folder = input_args[1]
    else:
        return {"mode" : "help"}

    for args in input_args:
        if args in ["-h", "help"]:
            return {"mode" : "help"}
        elif args == "-db":
            args_db = input_args[input_args.index("-db") + 1]
        elif args == "-o":
            args_output = input_args[input_args.index("-o") + 1]
        elif args == "-filter":
            args_filter = input_args[input_args.index("-filter") + 1]
        elif args == "-not-filter":
            args_not_filter = input_args[input_args.index("-not-filter") + 1]

    # 指定了 -db 参数, 说明是比对模式
    if args_dst_folder != "Null" and args_db != "Null":
        return {"mode": "compare",
                "args_dst_folder": args_dst_folder,
                "args_db": args_db,
                "args_filter": args_filter,
                "args_not_filter": args_not_filter}
    # 指定了 -o 参数, 说明是写入模式
    elif args_dst_folder != "Null" and args_output != "Null":
        return {"mode": "create",
                "args_dst_folder": args_dst_folder,
                "args_output": args_output,
                "args_filter": args_filter,
                "args_not_filter": args_not_filter}
    # 其余情况
    else:
        return {"mode" : "help"}

def file_hash(file_path):
    """
    读取文件并返回文件的 SHA1 值
    :param file_path:
    :return:
    """
    h = hashlib.sha1()
    with open(file_path, 'rb') as f:
        while b := f.read(8192):
            h.update(b)
    return h.hexdigest()

def create_diff_db(args_dict):
    """
    读取指定文件夹, 并将文件所对于的 SHA1 保存为字典, 并进行序列化保存
    :param args_dict:
    :return:
    """
    dst_folder = args_dict.get("args_dst_folder")
    filter = args_dict.get("args_filter")
    not_filter = args_dict.get("args_not_filter")
    dbname = args_dict.get("args_output")
    diffdb = {}

    if not_filter != None:
        for root, dirs, files in os.walk(dst_folder):
            for file in files:
                filepath = os.path.abspath(os.path.join(root, file))
                if re.findall(not_filter, filepath, re.IGNORECASE) == [] and re.findall(filter, filepath, re.IGNORECASE):
                    filehash = file_hash(filepath)
                    diffdb[filepath] = filehash
    else:
        for root, dirs, files in os.walk(dst_folder):
            for file in files:
                filepath = os.path.abspath(os.path.join(root, file))
                if re.findall(filter, filepath, re.IGNORECASE):
                    filehash = file_hash(filepath)
                    diffdb[filepath] = filehash

    with open(dbname, "wb") as f:
        pickle.dump(diffdb, f)
        print("diff db write finish, save path is: {}".format(os.path.abspath(dbname)))

def compare_diff_file(args_dict):
    """
    读取指定文件夹, 并指出和记录中不相同的文件
    :param args_dict:
    :return:
    """
    dst_folder = args_dict.get("args_dst_folder")
    filter = args_dict.get("args_filter")
    not_filter = args_dict.get("args_not_filter")
    with open(args_dict.get("args_db"), 'rb') as f:
        diffdb = pickle.load(f)

    diff_count = 0

    if not_filter != None:
        for root, dirs, files in os.walk(dst_folder):
            for file in files:
                filepath = os.path.abspath(os.path.join(root, file))
                if re.findall(not_filter, filepath, re.IGNORECASE) == [] and re.findall(filter, filepath, re.IGNORECASE):
                    filehash = file_hash(filepath)
                    if filehash != diffdb.get(filepath):
                        print("Diff found: {}".format(filepath))
                        diff_count += 1
    else:
        for root, dirs, files in os.walk(dst_folder):
            for file in files:
                filepath = os.path.abspath(os.path.join(root, file))
                if re.findall(filter, filepath, re.IGNORECASE):
                    filehash = file_hash(filepath)
                    if filehash != diffdb.get(filepath):
                        print("Diff found: {}".format(filepath))
                        diff_count += 1

    if diff_count == 0:
        print("Comparison completed, no different files found.")
    else:
        print("Total of {} different files were found!".format(str(diff_count)))

if __name__ == "__main__":
    input_args = sys.argv
    checked = check_args(input_args)
    try:
        if checked.get("mode") == "help":
            print("please reference help info")
        elif checked.get("mode") == "compare":
            compare_diff_file(checked)
        elif checked.get("mode") == "create":
            create_diff_db(checked)
    except Exception as e:
        print(e)