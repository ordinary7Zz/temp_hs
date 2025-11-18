# 数据库结构与设计对比报告
数据库: `backup_system`
生成时间: 2025-10-29T02:59:25.550Z

## 表 `t_backup_log`
- 字段总数: 设计=7, 实际=7
- 主键: 设计=log_id, 实际=log_id
- 外键: 设计标注=operator_id, 实际约束=无
- 索引(实际): PRIMARY(log_id)

- 完全匹配字段: log_id, backup_time, backup_type, file_path, status, file_size_mb, operator_id

## 表 `t_backup_config`
- 字段总数: 设计=4, 实际=4
- 主键: 设计=config_id, 实际=config_id
- 外键: 设计标注=无, 实际约束=无
- 索引(实际): PRIMARY(config_id)

- 完全匹配字段: config_id, schedule_type, schedule_day, is_enabled

## 表 `t_restore_log`
- 字段总数: 设计=6, 实际=6
- 主键: 设计=log_id, 实际=log_id
- 外键: 设计标注=operator_id, 实际约束=无
- 索引(实际): PRIMARY(log_id)

- 完全匹配字段: log_id, restore_time, backup_file_path, status, operator_id, details

---
## 差异分类与可能原因
- 设计未明确默认值或索引：若备注未说明，视为设计缺失。
- 枚举 vs 文本/整数：若设计为 varchar/int 而实际为 enum/tinyint，可能为优化或设计更新。
- 外键备注 vs 实际约束：若备注提及外键但实际未建约束，属于未实施的设计要求。