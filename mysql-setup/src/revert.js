require('dotenv').config({ path: require('path').resolve(__dirname, '../.env') });
const fs = require('fs');
const path = require('path');
const { getPool, withRetry } = require('./db');

async function run() {
  const pool = await getPool();
  const sqlFile = path.resolve(__dirname, 'revert.sql');
  const sql = fs.readFileSync(sqlFile, 'utf8');

  try {
    await withRetry(async () => {
      const conn = await pool.getConnection();
      for (const stmt of sql.split(/;\s*\n/).map(s => s.trim()).filter(Boolean)) {
        await conn.query(stmt);
      }
      conn.release();
    });
    console.log('回改 SQL 执行完成');
  } catch (err) {
    console.error('回改失败:', err.message);
    process.exitCode = 1;
    return;
  }

  // 关闭连接池
  await pool.end();
  console.log('连接池已关闭');
}

run().catch(err => {
  console.error('执行异常:', err);
});