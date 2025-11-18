const mysql = require('mysql2/promise');

const config = {
  host: process.env.DB_HOST || 'localhost',
  port: Number(process.env.DB_PORT || 3306),
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'backup_system',
  charset: 'utf8mb4',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0,
};

// 支持通过 Unix Socket 连接（例如 /tmp/mysql.sock）
if (process.env.DB_SOCKET) {
  config.socketPath = process.env.DB_SOCKET;
}

const pools = new Map();

async function getPool(opts = {}) {
  const includeDatabase = opts.includeDatabase !== false;
  let pool = pools.get(includeDatabase);
  if (!pool) {
    const cfg = { ...config };
    if (!includeDatabase) {
      delete cfg.database;
    }
    pool = mysql.createPool(cfg);
    pools.set(includeDatabase, pool);
  }
  return pool;
}

async function withRetry(fn, { retries = 3, delayMs = 500 } = {}) {
  let lastErr;
  for (let i = 0; i < retries; i++) {
    try {
      return await fn();
    } catch (err) {
      lastErr = err;
      if (i < retries - 1) await new Promise(r => setTimeout(r, delayMs));
    }
  }
  throw lastErr;
}

module.exports = { getPool, withRetry };