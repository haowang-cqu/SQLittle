from re import T
import pandas as pd
import numpy as np
import os
from . import metadatabase

database_loc = metadatabase.database_loc

mdb = metadatabase.MetaDatabase()


def exists_table(table_name):
    return mdb.get_table(table_name) is not None


def create_table(table_name, fields):
    if exists_table(table_name):
        print("Table '%s' exists!" % table_name)
    else:
        mdb.add_table(table_name)
        mdb.modify_table(table_name, fields)
        df = pd.DataFrame(columns=fields.keys())
        df.to_csv(database_loc+'%s.csv' % table_name, index=False)


def get_all_tables():
    return mdb.tables.keys()


def get_all_types():
    return mdb.types.keys()


def delete_table(table_name):
    file_name = database_loc + table_name + '.csv'
    mdb.remove_table(table_name)
    os.remove(file_name)


def show_table_fields(table_name):
    field_items = mdb.get_table(table_name)['fields']
    field_names = ['name'] + mdb.field_keys
    fields = []
    for k in field_items:
        field = [k] + [field_items[k]["type"]]
        field.extend([field_items[k]["constraints"].get(_, False) for _ in mdb.field_keys[1:-1]])
        field.append(field_items[k].get("type_len", "None"))
        fields.append(field)
    return field_names, fields


def show_table(table_name):
    field_items = mdb.get_table(table_name)['fields']
    fields = []
    for k in field_items:
        field = [k] + [field_items[k]["type"]]
        field.extend([field_items[k]["constraints"].get(_, False) for _ in mdb.field_keys[1:-1]])
        field.append(field_items[k].get("type_len", "None"))
        fields.append(field)

    record_name = database_loc + table_name + '.csv'
    df = pd.read_csv(record_name)
    column_names = list(df.columns)
    records = [row.to_list() for _, row in df.iterrows()]
    return column_names, records


def is_valid_type(type_name):
    types = get_all_types()
    for type in types:
        type_items = mdb.get_type(type)['types']
        if type_name in type_items.keys():
            return True
    return False


def show_type(type_name):
    type_items = mdb.get_type(type_name)['types']
    type_col_names = mdb.type_keys[type_name]
    types = []
    for k in type_items:
        _type = [k]
        _type.extend([type_items[k].get(_, False) for _ in type_col_names])
        types.append(_type)

    type_col_names = ['name'] + type_col_names
    return type_col_names, types


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
    result_index = []
    for i, record in enumerate(total_records):
        if comparison_op == '<' and str(record[query_column]) < value:
            result_records.append(record)
            result_index.append(i)
        elif comparison_op == '=' and str(record[query_column]) == value:
            result_records.append(record)
            result_index.append(i)
        elif comparison_op == '>' and str(record[query_column]) > value:
            result_records.append(record)
            result_index.append(i)
    return result_records, result_index


def add_column(table_name, column_name,fields) -> bool:
    file_name = database_loc + table_name + '.csv'
    df = pd.read_csv(file_name)
    if column_name in list(df.columns.values):
        return False
    df[column_name] = ''
    df.to_csv(file_name, index=False)
    mdb.add_column(table_name,fields)
    return True


def drop_column(table_name, column_name) -> bool:
    file_name = database_loc + table_name + '.csv'
    df = pd.read_csv(file_name)
    if column_name not in list(df.columns.values):
        return False
    df.drop(column_name, axis=1, inplace=True)
    df.to_csv(file_name, index=False)
    mdb.drop_column(table_name,column_name)
    return True
