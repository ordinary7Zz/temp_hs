USE `backup_system`;

-- t_backup_config: 调整为原始设计
ALTER TABLE `t_backup_config` 
  MODIFY `schedule_type` VARCHAR(20) NOT NULL COMMENT '周期类型',
  MODIFY `schedule_day` DATETIME NOT NULL COMMENT '周期内的执行日 (例如: 3.15)',
  MODIFY `is_enabled` INT NOT NULL DEFAULT 1 COMMENT '1=启用, 0=禁用';

-- t_backup_log: 将 tinyint 改为 int，移除未在设计中声明的索引
ALTER TABLE `t_backup_log` 
  MODIFY `backup_type` INT NOT NULL COMMENT '1=自动备份, 0=手动备份',
  MODIFY `status` INT NOT NULL COMMENT '1=成功, 0=失败';

ALTER TABLE `t_backup_log` DROP INDEX `idx_backup_time`;
ALTER TABLE `t_backup_log` DROP INDEX `idx_backup_type`;
ALTER TABLE `t_backup_log` DROP INDEX `idx_status`;

-- t_restore_log: 移除未在设计中声明的索引
ALTER TABLE `t_restore_log` DROP INDEX `idx_restore_time`;
ALTER TABLE `t_restore_log` DROP INDEX `idx_status`;