使用说明

1. 复制环境变量模板

cp .env.example .env

编辑 `.env`，填入你的 MySQL 连接配置：

- `DB_HOST` 主机地址
- `DB_PORT` 端口（默认 3306）
- `DB_USER` 用户名
- `DB_PASSWORD` 密码
- `DB_NAME` 数据库名称（默认 backup_system）

2. 安装依赖

npm install

3. 执行建表与验证

node src/setup.js

脚本功能：
- 使用连接池连接数据库并进行 `ping` 测试
- 执行 `src/schema.sql` 创建数据库与三张表
- 通过 `SHOW TABLES` 与 `SHOW FULL COLUMNS` 验证表结构
- 输出错误信息，并在结束时关闭连接池