-- 数据库与表创建，字符集 utf8mb4，存储引擎 InnoDB
CREATE DATABASE IF NOT EXISTS `backup_system` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE `backup_system`;

-- t_backup_log 数据备份日志表
CREATE TABLE IF NOT EXISTS `t_backup_log` (
  `log_id` INT NOT NULL AUTO_INCREMENT COMMENT '唯一自增主键',
  `backup_time` DATETIME NOT NULL COMMENT '备份时间',
  `backup_type` TINYINT NOT NULL COMMENT '1=自动备份, 0=手动备份',
  `file_path` VARCHAR(500) NOT NULL COMMENT '备份文件的完整路径',
  `status` TINYINT NOT NULL COMMENT '1=成功, 0=失败',
  `file_size_mb` DECIMAL(10,2) NULL COMMENT '备份文件的大小',
  `operator_id` VARCHAR(50) NULL COMMENT '外键, 关联用户',
  PRIMARY KEY (`log_id`),
  KEY `idx_backup_time` (`backup_time`),
  KEY `idx_backup_type` (`backup_type`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据备份日志表';

-- t_backup_config 自动备份配置表（单行配置）
CREATE TABLE IF NOT EXISTS `t_backup_config` (
  `config_id` INT NOT NULL DEFAULT 1 COMMENT '默认为 1 (单行配置)',
  `schedule_type` ENUM('NONE','WEEKLY','MONTHLY','QUARTERLY','ANNUALLY') NOT NULL COMMENT '周期类型',
  `schedule_day` VARCHAR(20) NOT NULL COMMENT '周期内的执行日 (例如: 3.15)',
  `is_enabled` TINYINT NOT NULL DEFAULT 1 COMMENT '1=启用, 0=禁用',
  PRIMARY KEY (`config_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='自动备份配置表';

-- t_restore_log 数据还原日志表
CREATE TABLE IF NOT EXISTS `t_restore_log` (
  `log_id` INT NOT NULL AUTO_INCREMENT COMMENT '唯一自增主键',
  `restore_time` DATETIME NOT NULL COMMENT '执行数据恢复的时间',
  `backup_file_path` VARCHAR(500) NOT NULL COMMENT '所用备份文件路径',
  `status` TINYINT NOT NULL COMMENT '1=成功, 0=失败',
  `operator_id` VARCHAR(50) NOT NULL COMMENT '外键，关联执行操作的用户',
  `details` TEXT NULL COMMENT '记录还原过程的日志或错误信息',
  PRIMARY KEY (`log_id`),
  KEY `idx_restore_time` (`restore_time`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据还原日志表';

-- t_user 用户信息表（供用户管理界面使用）
CREATE TABLE IF NOT EXISTS `t_user` (
  `user_id` INT NOT NULL AUTO_INCREMENT COMMENT '唯一自增主键',
  `real_name` VARCHAR(100) NOT NULL COMMENT '真实姓名',
  `org` VARCHAR(200) NULL COMMENT '单位/部门',
  `job_title` VARCHAR(100) NULL COMMENT '职务职位',
  `username` VARCHAR(100) NOT NULL UNIQUE COMMENT '用户名',
  `password_hash` VARCHAR(255) NOT NULL COMMENT '加密后的密码',
  `phone` VARCHAR(50) NULL COMMENT '联系电话',
  `address` VARCHAR(300) NULL COMMENT '联系地址',
  `note` VARCHAR(500) NULL COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  KEY `idx_username` (`username`),
  KEY `idx_real_name` (`real_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户信息表';