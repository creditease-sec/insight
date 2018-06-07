## 说明

#### 1.安装依赖文件 

```
# pip install -r srcpm/requirement.txt --user

```

#### 2. 创建数据库表

```
$ mysql -h 127.0.0.1 -P 6606 -u root -p
Enter password:root

mysql> CREATE DATABASE IF NOT EXISTS vuldb DEFAULT CHARSET utf8 COLLATE utf8_general_ci;
mysql> grant all on vuldb.* to vuluser@'%' identified by 'vulpassword';
mysql> flush privileges;
mysql> quit

```

#### 3.导入sql文件

```
$ mysql -h127.0.0.1 -P3306 -uroot -p vuldb < srcpm/vuldb_init.sql
Enter password:root

```

### 4.添加本地环境变量

```
$ export DEV_DATABASE_URL=mysql://vuluser:vulpassword@localhost:3306/vuldb 

```

#### 5. 启动应用

```
# python manage.py runserver -h 0.0.0.0

```

#### 6. 登录主页 

```
http://127.0.0.1:5000/srcpm/

```
