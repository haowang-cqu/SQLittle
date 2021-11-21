#!/bin/python
from re import S
import tabulate
tabulate.WIDE_CHARS_MODE = True

from MetaDataManager import metadatabase
from MetaDataManager import utils
from MetaDataManager.utils import mdb
from tabulate import tabulate
from MetaDataManager import sqlparse

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


def drop_command_handler(command: str) -> bool:
    """
    drop table [table name];
    """
    command = command.split()
    if len(command) == 3 and command[1] == "table":
        table_name = command[2]
        # 表不存在
        if table_name not in utils.get_all_tables():
            print(f"ERROR: Unknown table '{ table_name }'")
        else:
            utils.delete_table(table_name)
            print("Query OK, 0 rows affected")
            print()
        return True
    return False


def insert_command_handler(command: str) -> bool:
    """
    INSERT INTO [table name] VALUES
    ( value1, value2,...valueN ),
    ( value1, value2,...valueN );
    """
    success, table_name, values = sqlparse.insert_command_parse(command)
    if not success:
        return False
    if table_name not in utils.get_all_tables():
        print(f"ERROR: Unknown table '{ table_name }'")
    else:
        for value in values:
            utils.add_record(table_name, value)
        print(f"Query OK, {len(values)} rows affected")
        print()
    return True


def select_command_handler(command: str) -> bool:
    """
    SELECT column_name,column_name
    FROM table_name
    [WHERE condition]
    """
    success, fields, table_name, condition = sqlparse.select_command_parse(command)
    if not success:
        return False
    if table_name not in utils.get_all_tables():
        print(f"ERROR: Unknown table '{ table_name }'")
        return True
    field_names, records = utils.show_table(table_name)
    # 查询所有列
    if len(fields) == 1 and fields[0] == "*":
        fields = field_names
    else:
        # 判断查询的列是否都存在
        for field in fields:
            if field not in field_names:
                print(f"ERROR: Unknown column '{field}' in 'field list'")
                return True
    # 无条件查询
    if condition == None:
        result = records
    else:
        if condition[0] not in field_names:
            print(f"ERROR: Unknown column '{condition[0]}' in 'field list'")
            return True
        query_column = field_names.index(condition[0])
        comparison_op =condition[1] 
        value = condition[2]
        result, _ = utils.query_records_by_condition(records, query_column, comparison_op, value)
    # 选择输出的列
    ouput_result = []
    for r in result:
        tmp = []
        for f in fields:
            tmp.append(r[field_names.index(f)])
        ouput_result.append(tmp)
    print_result(ouput_result, fields)
    return True


def create_command_handler(command: str) -> bool:
    """
    CREATE TABLE user(
        ID INT NOT NULL,
        Username VARCHAR NOT NULL,
        Password VARCHAR NOT NULL,
        CharID INT,
        PRIMARY KEY (ID),
        FOREIGN KEY (CharID) references ChineseCharInfo(ID)
    );
    """
    success, table_name, fields = sqlparse.create_command_parse(command)
    if not success:
        return False
    if utils.exists_table(table_name):
        print(f"ERROR: Table '{table_name}' already exists")
        return True
    utils.create_table(table_name, fields)
    print("Query OK, 0 rows affected")
    print()
    return True


def delete_command_handler(command: str) -> bool:
    """
    DELETE FROM [table name] WHERE condition;
    """
    success, table_name, condition = sqlparse.delete_command_parse(command)
    if not success:
        return False
    if not utils.exists_table(table_name):
        print(f"ERROR: Unknown table '{ table_name }'")
        return True
    field_names, records = utils.show_table(table_name)
    if condition[0] not in field_names:
        print(f"ERROR: Unknown column '{condition[0]}' in 'field list'")
        return True
    query_column = field_names.index(condition[0])
    comparison_op =condition[1] 
    value = condition[2]
    _, result_index = utils.query_records_by_condition(records, query_column, comparison_op, value)
    for i in result_index:
        utils.delete_record(table_name, i)
    print(f"Query OK, {len(result_index)} row affected")
    print()
    return True


def update_command_handler(command: str) -> bool:
    """
    UPDATE [table name] 
    SET field1=value1, field2=value2 
    [WHERE condition];
    """
    success, table_name, update_fields, condition = sqlparse.update_command_parse(command)
    if not success:
        return False
    if not utils.exists_table(table_name):
        print(f"ERROR: Unknown table '{ table_name }'")
        return True
    field_names, records = utils.show_table(table_name)
    # 无条件则更新所有记录
    if condition == None:
        update_records = records
        update_index = list(range(len(records)))
    else:
        query_column = field_names.index(condition[0])
        comparison_op =condition[1] 
        value = condition[2]
        update_records, update_index = utils.query_records_by_condition(records, query_column, comparison_op, value)
    # 更新update_records
    for k, v in update_fields.items():
        for i in range(len(update_records)):
            update_records[i][field_names.index(k)] = v
    for i in range(len(update_records)):
        utils.edit_record(table_name, update_index[i], update_records[i])
    print(f"Query OK, {len(update_records)} rows affected")
    print()
    return True


def command_handler(command: str) -> bool:
    """处理各种类型的命令
    """
    start = command.split()[0]
    if start == "show":
        return show_command_handler(command)
    if start in ["desc", "describe"]:
        return desc_command_handler(command)
    if start == "create":
        return create_command_handler(command)
    if start == "drop":
        return drop_command_handler(command)
    if start == "insert":
        return insert_command_handler(command)
    if start == "select":
        return select_command_handler(command)
    if start == "delete":
        return delete_command_handler(command)
    if start == "update":
        return update_command_handler(command)
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