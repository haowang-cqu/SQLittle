import os
import json


database_loc = "metadata/"
table_loc = database_loc + "tables/"
type_loc = database_loc + "types/"


def save_dict2json(dct, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(dct, f, ensure_ascii=False)
        f.close()


def load_json2dict(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


class MetaDatabase(object):

    def __init__(self):
        # Load database summary information
        self.tables_filename = database_loc + "tables.json"
        self.types_filename = database_loc + "types.json"
        self.reload()

    def reload(self):
        self.tables = load_json2dict(self.tables_filename)
        self.types = load_json2dict(self.types_filename)

        # Load tables
        for k in self.tables:
            fields = load_json2dict(table_loc + self.tables[k])
            self.tables[k] = {
                "filename": self.tables[k],
                "fields": fields
            }

        # Load types
        for k in self.types:
            types = load_json2dict(type_loc + self.types[k])
            self.types[k] = {
                "filename": self.types[k],
                "types": types
            }
        self.field_keys = ["type", "unique", "primary", "foreign", "check", "not null", "default", "type_len"]
        self.num_type_keys = [k for k in self.types["numerical"]["types"]["INT"]]
        self.str_type_keys = [k for k in self.types["string"]["types"]["CHAR"]]
        self.time_type_keys = [k for k in self.types["time"]["types"]["DATE"]]
        self.type_keys = {
            'numerical': self.num_type_keys,
            'string': self.str_type_keys,
            'time': self.time_type_keys
        }

    def get_table(self, tb_name):
        return self.tables.get(tb_name, None)

    def get_type(self, tp_name):
        return self.types.get(tp_name, None)
    
    def add_table(self, table_name):
        if table_name in self.tables:
            return
        try:
            max_filename = max(self.tables[x]['filename'] for x in self.tables)
            number = int("".join(max_filename.split(".")[0].split("-"))) + 1
        except:
            number = 0
        file_name_for_table = "0000-{:04d}.json".format(number)
        if number > 9999:
            return None
        else:
            filenames = load_json2dict(self.tables_filename)
            filenames[table_name] = file_name_for_table
            save_dict2json(filenames,self.tables_filename)
            save_dict2json(dict(),table_loc + file_name_for_table)
            self.reload()
    
    def modify_table(self, table_name, fields):
        file_name_for_table = self.tables[table_name]['filename']
        save_dict2json(fields,table_loc + file_name_for_table)
        self.reload()

    def remove_table(self, table_name):
        file_name = self.tables[table_name]['filename']
        os.remove(table_loc + file_name)
        filenames = load_json2dict(self.tables_filename)
        filenames.pop(table_name)
        save_dict2json(filenames,self.tables_filename)
        self.reload()
    
    def add_column(self, table_name, fields):
        file_name_for_table = self.tables[table_name]['filename']
        old_data=load_json2dict(table_loc + file_name_for_table)
        old_data.update(fields)
        save_dict2json(old_data,table_loc + file_name_for_table)
        self.reload()

    def drop_column(self, table_name,column_name):
        file_name_for_table = self.tables[table_name]['filename']
        old_data=load_json2dict(table_loc + file_name_for_table)
        old_data.pop(column_name)
        save_dict2json(old_data,table_loc + file_name_for_table)
        self.reload()


if __name__ == '__main__':
    db = MetaDatabase()