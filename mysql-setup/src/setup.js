require('dotenv').config({ path: require('path').resolve(__dirname, '../.env') });
const fs = require('fs');
const path = require('path');
const { getPool, withRetry } = require('./db');

async function run() {
  // 先创建一个不选择数据库的连接池，用于创建数据库
  const serverPool = await getPool({ includeDatabase: false });

  // 连接测试
  try {
    await withRetry(async () => {
      const conn = await serverPool.getConnection();
      await conn.ping();
      conn.release();
    });
    console.log('连接测试成功');
  } catch (err) {
    console.error('连接测试失败:', err.message);
    process.exitCode = 1;
    return;
  }

  // 执行建表 SQL
  const sqlFile = path.resolve(__dirname, 'schema.sql');
  const sql = fs.readFileSync(sqlFile, 'utf8');

  try {
    const conn = await serverPool.getConnection();
    for (const stmt of sql.split(/;\s*\n/).map(s => s.trim()).filter(Boolean)) {
      await conn.query(stmt);
    }
    conn.release();
    console.log('建表SQL执行完成');
  } catch (err) {
    console.error('建表失败:', err.message);
    process.exitCode = 1;
    return;
  }

  // 验证表结构
  // 使用选择了数据库的连接池验证表结构
  const dbPool = await getPool();
  try {
    const conn = await dbPool.getConnection();
    const [tables] = await conn.query("SHOW TABLES");
    console.log('当前数据库包含的表:', tables.map(Object.values));

    const expect = ['t_backup_log', 't_backup_config', 't_restore_log'];
    for (const t of expect) {
      const [cols] = await conn.query(`SHOW FULL COLUMNS FROM \`${t}\``);
      console.log(`表 ${t} 字段:`, cols.map(c => ({ Field: c.Field, Type: c.Type, Null: c.Null, Key: c.Key, Default: c.Default, Comment: c.Comment })));
    }
    conn.release();
    console.log('表结构验证完成');
  } catch (err) {
    console.error('表结构验证失败:', err.message);
    process.exitCode = 1;
    return;
  }

  // 资源管理：关闭连接池
  await dbPool.end();
  await serverPool.end();
  console.log('连接池已关闭');
}

run().catch(err => {
  console.error('执行异常:', err);
});