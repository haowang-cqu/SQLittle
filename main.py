#!/bin/python
import tabulate
tabulate.WIDE_CHARS_MODE = True

from MetaDataManager import metadatabase
from MetaDataManager import utils
from MetaDataManager.utils import mdb
from tabulate import tabulate

prompt1 = "SQLittle> "
prompt2 = "       -> "
delimiter = ";"


def print_result(table, header, tablefmt="psql"):
    """输出一个表格
    """
    print(tabulate(table, header, tablefmt=tablefmt))
    print(f"{len(table)} rows in set")
    print()


def show_command_handler(command: str) -> bool:
    """
    show tables;
    show types;
    show [numerical, string, time] types;
    """
    command = command.split()
    if len(command) == 2 and command[1] == "tables":
        tables = [[name] for name in utils.get_all_tables()]
        print_result(tables, ["Tables"])
        return True
    if len(command) == 2 and command[1] == "types":
        for type_name in utils.get_all_types():
            type_col_names, types = utils.show_type(type_name)
            print_result(types, type_col_names)
        return True
    if len(command) == 3 and command[2] == "types"  \
        and command[1] in utils.get_all_types():
        type_col_names, types = utils.show_type(command[1])
        print_result(types, type_col_names)
        return True
    return False


def desc_command_handler(command: str) -> bool:
    """
    describe [table name];
    """
    command = command.split()
    if len(command) == 2 and command[1] in utils.get_all_tables():
        field_names, fields = utils.show_table_fields(command[1])
        print_result(fields, field_names)
        return True
    return False


def command_handler(command: str) -> bool:
    """处理各种类型的命令
    """
    start = command.split()[0]
    if start == "show":
        return show_command_handler(command)
    if start in ["desc", "describe"]:
        return desc_command_handler(command)
    else:
        return False


def main_loop():
    """主循环，从命令行读入用户输入
    """
    while True:
        print(prompt1, end="")
        firstline = input().strip().lower()
        # 空命令
        if len(firstline) == 0:
            continue
        # 退出程序
        if firstline.startswith("exit"):
            break
        command = [firstline]
        # 循环读入多行命令，直到delimiter
        while not command[-1].endswith(delimiter):
            print(prompt2, end="")
            command.append(input().strip().lower())
        command[-1] = command[-1].rstrip(delimiter)
        if not command_handler(" ".join(command)):
            print("ERROR: You have an error in your SQL syntax;")
        

if __name__ == '__main__': 
    main_loop()