import pandas as pd
import numpy as np
import os
from . import metadatabase

database_loc = metadatabase.database_loc

mdb = metadatabase.MetaDatabase()


def exists_table(table_name):
    return mdb.get_table(table_name) is not None


def create_table(table_name, columns):
    if exists_table(table_name):
        print("Table '%s' exists!" % table_name)
    else:
        mdb.add_table(table_name)
        df = pd.DataFrame(columns=columns)
        df.to_csv(database_loc+'%s.csv' % table_name, index=False)


def get_all_tables():
    return mdb.tables.keys()


def get_all_types():
    return mdb.types.keys()


def delete_table(table_name):
    file_name = database_loc + table_name + '.csv'
    mdb.remove_table(table_name)
    os.remove(file_name)


def show_table(table_name):
    field_items = mdb.get_table(table_name)['fields']
    field_names = ['name'] + mdb.field_keys
    fields = []
    for k in field_items:
        field = [k] + [field_items[k]["type"]]
        field.extend([field_items[k]["constraints"].get(_, False) for _ in mdb.field_keys[1:-1]])
        field.append(field_items[k].get("type_len", "None"))
        fields.append(field)
    field_indexes = [i for i in range(len(fields))]

    record_name = database_loc + table_name + '.csv'
    df = pd.read_csv(record_name)
    column_names = df.columns
    records = [row.to_list() for i, row in df.iterrows()]
    record_indexes = df.index.to_list()
    return field_names, zip(fields, field_indexes), column_names, zip(records, record_indexes)


def show_type(type_name):
    type_items = mdb.get_type(type_name)['types']
    type_col_names = mdb.type_keys[type_name]
    types = []
    for k in type_items:
        _type = [k]
        _type.extend([type_items[k].get(_, False) for _ in type_col_names])
        types.append(_type)

    type_indexes = [i for i in range(len(types))]
    type_col_names = ['name'] + type_col_names
    return type_col_names, zip(types, type_indexes)


def add_record(table_name, record):
    file_name = database_loc + table_name + '.csv'
    df = pd.read_csv(file_name)
    i = len(df.values.tolist())
    df.loc[i] = record
    df.to_csv(file_name, index=False)


def delete_record(table_name, index):
    file_name = database_loc + table_name + '.csv'
    df = pd.read_csv(file_name)
    df = df.drop(index)
    df.to_csv(file_name, index=False)


def get_record(table_name, index):
    file_name = database_loc + table_name + '.csv'
    df = pd.read_csv(file_name)
    return df.columns, df.loc[index]


def edit_record(table_name, index, record):
    file_name = database_loc + table_name + '.csv'
    df = pd.read_csv(file_name)
    df.loc[index] = record
    df.to_csv(file_name, index=False)


# 单条件查询
def query_records_by_condition(total_records, query_column, comparison_op, value):
    result_records = []
    for record in total_records:
        if comparison_op == '<' and str(record[query_column]) < value:
            result_records.append(record)
        elif comparison_op == '=' and str(record[query_column]) == value:
            result_records.append(record)
        elif comparison_op == '>' and str(record[query_column]) > value:
            result_records.append(record)
    return result_records


# 多条件查询
def query_records(table_name, query_columns, comparison_ops, values):
    query_columns = query_columns.split(',')
    comparison_ops = comparison_ops.split(',')
    values = values.split(',')
    # 检查table是否存在
    if not exists_table(table_name):
        print("the table does not exist")
        return
    file_name = database_loc + table_name + '.csv'
    df = pd.read_csv(file_name)
    columns = df.columns
    # 查询的列是否存在
    for column in query_columns:
        if column not in columns:
            print("column does not exist")
            return
    # 比较符是否合法
    for comparison_op in comparison_ops:
        if comparison_op not in ['<', '=', '>']:
            print("illegal comparison")
            return
    # 没一个查询需要对应
    if len(query_columns) != len(comparison_ops) or \
            len(query_columns) != len(values):
        print("incorrect query format")
        return
    total_records = df.values.tolist()
    columns = df.columns.tolist()
    tables = get_all_tables()
    # 多次查询
    for i in range(len(query_columns)):
        total_records = \
            query_records_by_condition(total_records, columns.index(query_columns[i]), comparison_ops[i], values[i])
    return [tables, columns, total_records]
