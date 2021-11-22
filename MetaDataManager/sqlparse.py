from typing import Tuple
from typing import List
from typing import Dict
from MetaDataManager import utils


def insert_command_parse(command: str) -> Tuple[bool, str, Tuple]:
    """insert into 语法解析
    """
    words = command.split()
    if len(words) < 4 or \
        words[0] != "insert" or \
            words[1] != "into" or \
                words[3] != "values":
                return False, None, None
    table_name = words[2]
    try:
        values = eval(command.split("values", 1)[1])
        if type(values) == tuple and type(values[0]) != tuple:
            values = tuple([values])
    except Exception as e:
        return False, None, None
    if len(values) == 0:
        return False, None, None
    return True, table_name, values


def where_parse(where: str) -> Tuple:
    """where 子句解析
    """
    if "=" in where:
        query_column = where.split("=")[0].strip()
        comparison_op = "="
        value = where.split("=")[1].strip()
    if ">" in where:
        query_column = where.split(">")[0].strip()
        comparison_op = ">"
        value = where.split(">")[1].strip()
    if "<" in where:
        query_column = where.split("<")[0].strip()
        comparison_op = "<"
        value = where.split("<")[1].strip()
    value = value.strip("'")
    value = value.strip('"')
    return query_column, comparison_op, value


def select_command_parse(command: str) -> Tuple[bool, str, List[str], Tuple]:
    """select 语法解析
    """
    command = command.lstrip("select")
    # 分成三个子句
    if len(command.split("from", 1)) == 2:
        _select, command = command.split("from", 1)
    # 没有from子句返回False
    else:
        return False, None, None, None
    if len(command.split("where", 1)) == 2:
        _from, _where = command.split("where", 1)
    else:
        _from = command
        _where = None
    # 获取查询的列
    columns = _select.split(",")
    columns = [c.strip() for c in columns]
    if len(columns) == 0:
        return False, None, None, None
    # 获取查询的表名
    table_name = _from.strip()
    # 获取条件
    if _where == None:
        return True, columns, table_name, None
    return True, columns, table_name, where_parse(_where)


def is_primary_key(row: str) -> Tuple[bool, str]:
    """是否定义一个主键
    """
    words = row.split()
    if len(words) >= 3 and words[0] == "primary" and words[1] == "key":
        field_name = row.split("(", 1)[1].rstrip(")").strip()
        return True, field_name
    return False, None


def is_foreign_key(row: str) -> Tuple[bool, str, str]:
    """是否定义一个外键
    """
    words = row.split()
    if len(row.split("references", 1)) != 2:
        return False, None, None 
    if len(words) >= 5 and words[0] == "primary" and words[1] == "key":
        field_name = row.split("(", 1)[1].split(")", 1)[0].strip()
        foreign = row.split("references", 1)[1].strip()
        return True, field_name, foreign
    return False, None, None
    

def field_parse(row: str) -> Tuple[bool, str, Dict]:
    """解析字段
    """
    words = row.split()
    row = " ".join(words)
    if len(words) < 2:
        return False, None, None
    field_name, field_type = row.split()[:2]
    # 类型错误
    if not utils.is_valid_type(field_type.upper()):
        return False, None, None
    field_property = {
        "type": field_type.upper(),
        "constraints": {
            "check": "",
            "default": "",
            "primary": False,
            "unique": False,
            "not null": False
        }
    }
    if "not null" in row:
        field_property["constraints"]["not null"] = True
    if "unique" in row:
        field_property["constraints"]["unique"] = True
    if "default" in row:
        if words.index("default") >= len(words)-1:
            return False, None, None
        default = words[words.index("default")+1].strip("'").strip('"')
        field_property["constraints"]["default"] = default
    return True, field_name, field_property


def create_command_parse(command: str) -> Tuple[bool, str, Dict[str, Dict]] :
    """create table 语法解析
    """
    # 分成语句头和语句体
    if len(command.split("(", 1)) < 2:
        return False, None, None
    head = command.split("(", 1)[0].split()
    if len(head) == 3 and head[0] == "create" and head[1] == "table":
        table_name = head[2].strip()
    else:
        return False, None, None
    # 解析语句的主体部分
    # 去掉结尾多余的括号
    body = command.split("(", 1)[1]
    if body.endswith(")"):
        body = body[:-1]
    else:
        return False, None, None
    # 解析字段信息
    rows = body.split(",")
    rows = [row.strip() for row in rows]
    fields = {}
    has_primary = False
    for row in rows:
        is_primary, field_name = is_primary_key(row)
        if is_primary:
            # 主码不能有多个
            if (not has_primary) and field_name in fields.keys():
                fields[field_name]["constraints"]["primary"] = True
                has_primary = True
            else:
                return False, None, None
            continue
        is_foreign, field_name, foreign = is_foreign_key(row)
        if is_foreign:
            if field_name in fields.keys():
                fields[field_name]["constraints"]["foreign"] = foreign
                has_primary = True
            else:
                return False, None, None
            continue
        is_field, field_name, field_property = field_parse(row)
        if is_field:
            if field_name not in fields.keys():
                fields[field_name] = field_property
            # 重复列名
            else:
                return False, None, None
        else:
            return False, None, None
    return True, table_name, fields
    

def delete_command_parse(command: str) -> Tuple[bool, str, Tuple]:
    """delete 语法解析
    """
    words = command.split()
    if len(words) > 4 and words[0] == "delete" and words[1] == "from":
        table_name = words[2]
        if len(command.split("where", 1)) != 2:
            return False, None, None
        _where = command.split("where", 1)[1]
        return True, table_name, where_parse(_where)
    else:
        return False, None, None


def update_command_parse(command: str) -> Tuple[bool, str, Dict[str, str], Tuple]:
    """update 语法解析
    """
    command = command.lstrip("update")
    # 分成三个子句
    if len(command.split("set", 1)) == 2:
        _update, command = command.split("set", 1)
    # 没有set子句返回False
    else:
        return False, None, None, None
    if len(command.split("where", 1)) == 2:
        _set, _where = command.split("where", 1)
    else:
        _set = command
        _where = None
    table_name = _update.strip()
    _set = _set.split(",")
    update_fields = {}
    for s in _set:
        field_name, value = s.split("=")
        update_fields[field_name.strip()] = value.strip().strip("'").strip('"')
    # 获取条件
    if _where == None:
        return True, table_name, update_fields, None
    return True, table_name, update_fields, where_parse(_where)


def alter_add_proc(column:str,datatype:str):
    field={}
    field_property = {
        "type": datatype.upper(),
        "constraints": {
            "check": "",
            "default": "",
            "primary": False,
            "unique": False,
            "not null": False
        }
    }
    field[column]= field_property
    return field


def alter_drop_proc(column:str):
    field={}
    field[column]= None
    return field


def alter_command_parse(command: str) -> Tuple[bool, str,str, Dict[str, Dict]]:
    words=command.split()
    fileds={}
    if len(words)==6:
        if words[0] == "alter" and words[3] == "add":
            fileds = alter_add_proc(words[-2],words[-1])
            return True, words[2],"add",fileds
        elif words[0] == "alter" and words[3] == "drop":
            fileds = alter_drop_proc(words[-1])
            return True, words[2],"drop",fileds
    return False,None,None, None
