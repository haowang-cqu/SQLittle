# 数据库原理课程Project

## 简介
该project实现一个元数据管理器，并基于该元数据管理器进行关系的存储与基本操作。我们基于[cyyself](https://github.com/cyyself)实现的基于json文件的元数据存储方案，进一步添加基本操作的SQL解析和命令行交互功能。

## 环境配置
```bash
# clone this repository
git clone https://github.com/iamwhcn/SQLittle.git
cd SQLittle
# create a python 3 virtual environment
python -m venv .venv
pip install -r requirements.txt
# run
python main.py
```

## 实现的命令
### 查看所有表
```
show tables;
```
![show tables](img/show_tables.png)

### 查看数据类型
```
show types;
show [numerical, string, time] types;
```
![show time types](img/show_time_types.png)

### 查看表信息
```
describe [table name];
```
![desc student](img/desc_student.png)

### 创建表


### 删除表
```
drop table [table name];
```

### 修改表

### 插入数据

### 删除数据

### 更新数据

### 查询数据
