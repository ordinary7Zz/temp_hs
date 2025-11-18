require('dotenv').config({ path: require('path').resolve(__dirname, '../.env') });
const fs = require('fs');
const path = require('path');
const mysql = require('mysql2/promise');

function normalizeTypeFromActual(type) {
  const raw = type.toLowerCase();
  const m = raw.match(/^(\w+)(?:\(([^)]+)\))?/);
  const base = m ? m[1] : raw;
  let length = null;
  if (m && m[2]) {
    const parts = m[2].split(',').map(s => s.trim());
    length = parts.length === 1 ? Number(parts[0]) : parts.map(Number);
  }
  return { base, length, raw };
}

function normalizeTypeFromDesign(type, len) {
  const base = String(type).trim().toLowerCase();
  let length = null;
  if (len && len !== '-' && len.trim().length > 0) {
    const v = len.replace(/[()]/g, '').split(',').map(s => s.trim());
    length = v.length === 1 ? Number(v[0]) : v.map(Number);
  }
  return { base, length, raw: `${base}${length ? `(${Array.isArray(length)?length.join(', '):length})` : ''}` };
}

function eqType(design, actual) {
  // Allow int(1) in design to match tinyint(1) in actual
  if (design.base === 'int' && design.length === 1 && actual.base === 'tinyint') return true;
  // Allow int vs int(11)
  if (design.base === 'int' && actual.base === 'int') return true;
  // Otherwise exact base match
  return design.base === actual.base && (design.length == null || actual.length == null || String(design.length) === String(actual.length));
}

async function getActualSchema(conn, dbName, table) {
  const [cols] = await conn.query(`SHOW FULL COLUMNS FROM \`${table}\``);
  const [idx] = await conn.query(`SHOW INDEX FROM \`${table}\``);
  const [create] = await conn.query(`SHOW CREATE TABLE \`${table}\``);
  const createSql = create[0]['Create Table'];

  const pkCols = [];
  const fkConstraints = [];
  // Parse PK from SHOW INDEX (Key_name='PRIMARY')
  for (const r of idx) {
    if (r.Key_name === 'PRIMARY') pkCols.push(r.Column_name);
  }
  // Parse FK from create SQL
  const fkRegex = /CONSTRAINT\s+`([^`]+)`\s+FOREIGN KEY\s+\(([^)]+)\)\s+REFERENCES\s+`([^`]+)`\s+\(([^)]+)\)/gi;
  let m;
  while ((m = fkRegex.exec(createSql)) !== null) {
    const constraint = m[1];
    const cols = m[2].replace(/`/g, '').split(',').map(s => s.trim());
    const refTable = m[3];
    const refCols = m[4].replace(/`/g, '').split(',').map(s => s.trim());
    fkConstraints.push({ constraint, columns: cols, referenced_table: refTable, referenced_columns: refCols });
  }

  return {
    columns: cols.map(c => ({
      name: c.Field,
      type: normalizeTypeFromActual(c.Type),
      nullable: c.Null === 'YES',
      default: c.Default,
      key: c.Key, // 'PRI','MUL',''
      extra: c.Extra,
      comment: c.Comment || ''
    })),
    indexes: idx.map(i => ({
      name: i.Key_name,
      nonUnique: !!i.Non_unique,
      column: i.Column_name,
      indexType: i.Index_type
    })),
    primaryKey: pkCols,
    foreignKeys: fkConstraints,
    createSql,
  };
}

function parseDesign(fileText) {
  const lines = fileText.split(/\r?\n/);
  const tables = {};
  let current = null;
  let headerSeen = false;
  for (const line of lines) {
    const l = line.trim();
    if (!l) { continue; }
    const tableMatch = l.match(/^(t_\w+)/);
    if (tableMatch) {
      current = tableMatch[1];
      tables[current] = { columns: [], indexes: [], foreignKeys: [] };
      headerSeen = false;
      continue;
    }
    if (!current) continue;
    if (!headerSeen) {
      // skip header line containing column titles
      if (/编号\s+字段名称/.test(l)) { headerSeen = true; }
      continue;
    }
    // data rows: tab or multiple spaces separated
    const parts = line.split(/\t+/).map(s => s.trim()).filter(Boolean);
    if (parts.length < 8) {
      // try splitting by multiple spaces
      const p2 = line.split(/\s{2,}/).map(s => s.trim()).filter(Boolean);
      if (p2.length >= 8) {
        parts.splice(0, parts.length, ...p2);
      } else {
        continue;
      }
    }
    const [no, fieldName, displayName, dataType, dataLen, isPK, isNull, remark] = parts;
    const type = normalizeTypeFromDesign(dataType, dataLen);
    const col = {
      name: fieldName,
      type,
      nullable: isNull === '是',
      primary: isPK === '是',
      default: /默认为\s*([\dA-Za-z_]+)/.test(remark || '') ? RegExp.$1 : null,
      comment: remark || ''
    };
    tables[current].columns.push(col);
    if (/外键/.test(remark || '')) {
      tables[current].foreignKeys.push({ columns: [fieldName], note: remark });
    }
  }
  return tables;
}

function compareTable(design, actual) {
  const report = { matches: [], diffs: [] };
  const aColsByName = new Map(actual.columns.map(c => [c.name, c]));
  for (const dcol of design.columns) {
    const acol = aColsByName.get(dcol.name);
    if (!acol) {
      report.diffs.push({ field: dcol.name, issue: '字段缺失', design: dcol, actual: null });
      continue;
    }
    const issues = [];
    if (!eqType(dcol.type, acol.type)) {
      issues.push(`数据类型不一致: 设计=${dcol.type.raw}, 实际=${acol.type.raw}`);
    }
    if (dcol.nullable !== acol.nullable) {
      issues.push(`空值属性不一致: 设计=${dcol.nullable?'可空':'不可空'}, 实际=${acol.nullable?'可空':'不可空'}`);
    }
    if (dcol.primary !== (acol.key === 'PRI')) {
      issues.push(`主键属性不一致: 设计=${dcol.primary?'主键':'非主键'}, 实际=${acol.key==='PRI'?'主键':'非主键'}`);
    }
    const dDefault = dcol.default;
    const aDefault = acol.default == null ? null : String(acol.default);
    if (dDefault != null && dDefault !== aDefault) {
      issues.push(`默认值不一致: 设计=${dDefault}, 实际=${aDefault}`);
    }
    if (issues.length === 0) {
      report.matches.push(dcol.name);
    } else {
      report.diffs.push({ field: dcol.name, issue: issues.join('; '), design: dcol, actual: acol });
    }
  }
  // extra actual columns not in design
  for (const acol of actual.columns) {
    if (!design.columns.find(d => d.name === acol.name)) {
      report.diffs.push({ field: acol.name, issue: '数据库存在额外字段', design: null, actual: acol });
    }
  }
  return report;
}

async function main() {
  const config = {
    host: process.env.DB_HOST || '127.0.0.1',
    port: Number(process.env.DB_PORT || 3306),
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD || '',
    database: process.env.DB_NAME || 'backup_system',
  };
  if (process.env.DB_SOCKET) config.socketPath = process.env.DB_SOCKET;
  const conn = await mysql.createConnection(config);

  const designText = fs.readFileSync(path.resolve(__dirname, '../../数据备份字段表.txt'), 'utf8');
  const design = parseDesign(designText);
  const tables = Object.keys(design);

  const result = {};
  for (const t of tables) {
    const actual = await getActualSchema(conn, config.database, t);
    const cmp = compareTable(design[t], actual);
    result[t] = { design: design[t], actual, compare: cmp };
  }

  const lines = [];
  lines.push(`# 数据库结构与设计对比报告`);
  lines.push(`数据库: \`${config.database}\``);
  lines.push(`生成时间: ${new Date().toISOString()}`);
  lines.push('');
  for (const t of tables) {
    const { design: d, actual: a, compare: c } = result[t];
    lines.push(`## 表 \`${t}\``);
    lines.push(`- 字段总数: 设计=${d.columns.length}, 实际=${a.columns.length}`);
    lines.push(`- 主键: 设计=${d.columns.filter(x=>x.primary).map(x=>x.name).join(', ')||'无'}, 实际=${a.primaryKey.join(', ')||'无'}`);
    lines.push(`- 外键: 设计标注=${d.foreignKeys.map(f=>f.columns.join(', ')).join('; ')||'无'}, 实际约束=${a.foreignKeys.map(f=>`${f.columns.join(', ')}->${f.referenced_table}`).join('; ')||'无'}`);
    const idxList = a.indexes.map(i=>`${i.name}(${i.column})`).join(', ');
    lines.push(`- 索引(实际): ${idxList || '无'}`);
    lines.push('');
    if (c.matches.length) {
      lines.push(`- 完全匹配字段: ${c.matches.join(', ')}`);
    } else {
      lines.push(`- 完全匹配字段: 无`);
    }
    if (c.diffs.length) {
      lines.push('');
      lines.push('### 差异项');
      for (const dff of c.diffs) {
        const dcol = dff.design ? `${dff.design.name} (${dff.design.type.raw}, ${dff.design.nullable?'可空':'不可空'}${dff.design.primary?', 主键':''}${dff.design.default?`, 默认=${dff.design.default}`:''})` : '设计中无';
        const acol = dff.actual ? `${dff.actual.name} (${dff.actual.type.raw}, ${dff.actual.nullable?'可空':'不可空'}${dff.actual.key==='PRI'?', 主键':''}${dff.actual.default!=null?`, 默认=${dff.actual.default}`:''})` : '数据库中无';
        lines.push(`- 字段 \`${dff.field}\`: ${dff.issue}`);
        lines.push(`  - 设计: ${dcol}`);
        lines.push(`  - 实际: ${acol}`);
      }
    }
    lines.push('');
  }

  // 差异总结分类
  lines.push('---');
  lines.push('## 差异分类与可能原因');
  lines.push('- 设计未明确默认值或索引：若备注未说明，视为设计缺失。');
  lines.push('- 枚举 vs 文本/整数：若设计为 varchar/int 而实际为 enum/tinyint，可能为优化或设计更新。');
  lines.push('- 外键备注 vs 实际约束：若备注提及外键但实际未建约束，属于未实施的设计要求。');

  const outDir = path.resolve(__dirname, '../mysql-setup/report');
  const outFile = path.resolve(__dirname, '../mysql-setup/report/schema_compare.md');
  try { fs.mkdirSync(outDir, { recursive: true }); } catch (e) {}
  fs.writeFileSync(outFile, lines.join('\n'), 'utf8');
  console.log('对比报告已生成:', outFile);
  await conn.end();
}

main().catch(err => {
  console.error('比较执行失败:', err);
  process.exitCode = 1;
});