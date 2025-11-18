-- MySQL dump 10.13  Distrib 8.0.30, for Win64 (x86_64)
--
-- Host: localhost    Database: damassessment_db
-- ------------------------------------------------------
-- Server version	8.0.30

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `ammunition_info`
--

DROP TABLE IF EXISTS `ammunition_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ammunition_info` (
  `AMID` int NOT NULL AUTO_INCREMENT COMMENT '弹药ID',
  `AMName` varchar(100) DEFAULT NULL COMMENT '官方名称',
  `AMNameCN` varchar(100) DEFAULT NULL COMMENT '中文名称',
  `AMAbbreviation` varchar(60) DEFAULT NULL COMMENT '简称',
  `Country` varchar(60) DEFAULT NULL COMMENT '国家/地区',
  `Base` varchar(60) DEFAULT NULL COMMENT '基地/部队',
  `AMType` varchar(60) DEFAULT NULL COMMENT '弹药类型',
  `AMModel` varchar(60) DEFAULT NULL COMMENT '弹药型号',
  `AMSubmodel` varchar(60) DEFAULT NULL COMMENT '型号子类',
  `Manufacturer` varchar(60) DEFAULT NULL COMMENT '制造商',
  `AttendedDate` varchar(60) DEFAULT NULL COMMENT '服役时间',
  `AMWeight` decimal(10,0) DEFAULT NULL COMMENT '弹体全重',
  `AMLength` decimal(10,0) DEFAULT NULL COMMENT '弹体长度',
  `AMDiameter` decimal(10,0) DEFAULT NULL COMMENT '弹体直径',
  `AMTexture` varchar(60) DEFAULT NULL COMMENT '弹体材质',
  `WingspanClose` decimal(10,0) DEFAULT NULL COMMENT '翼展(闭合)',
  `WingspanOpen` decimal(10,0) DEFAULT NULL COMMENT '翼展(张开)',
  `AMStructure` varchar(60) DEFAULT NULL COMMENT '结构',
  `MaxSpeed` decimal(10,0) DEFAULT NULL COMMENT '最大时速',
  `RadarSection` varchar(60) DEFAULT NULL COMMENT '雷达截面',
  `AMPower` varchar(60) DEFAULT NULL COMMENT '动力装置',
  `LaunchWeight` decimal(10,0) DEFAULT NULL COMMENT '发射质量',
  `WarheadType` varchar(60) DEFAULT NULL COMMENT '战斗部类型',
  `WarheadName` varchar(60) DEFAULT NULL COMMENT '战斗部名称',
  `Penetrator` varchar(60) DEFAULT NULL COMMENT '毁伤元',
  `Fuze` varchar(60) DEFAULT NULL COMMENT '引信',
  `TNTEquivalent` decimal(10,0) DEFAULT NULL COMMENT '爆炸当量',
  `CEP` decimal(10,0) DEFAULT NULL COMMENT '精度(圆概率误差CEP)',
  `DestroyMechanism` varchar(60) DEFAULT NULL COMMENT '破坏机制',
  `Targets` varchar(60) DEFAULT NULL COMMENT '打击目标',
  `Carrier` varchar(60) DEFAULT NULL COMMENT '载机(投放平台)',
  `GuidanceMode` varchar(60) DEFAULT NULL COMMENT '制导方式',
  `ChargeAmount` decimal(10,0) DEFAULT NULL COMMENT '装药量',
  `PenetratePower` varchar(60) DEFAULT NULL COMMENT '穿透能力',
  `DropHeight` varchar(60) DEFAULT NULL COMMENT '投弹高度范围',
  `DropSpeed` decimal(10,0) DEFAULT NULL COMMENT '投弹速度',
  `DropMode` varchar(60) DEFAULT NULL COMMENT '投弹方式',
  `CoverageArea` varchar(60) DEFAULT NULL COMMENT '布撒范围',
  `FlightRange` decimal(10,0) DEFAULT NULL COMMENT '射程',
  `IsExplosiveBomb` int DEFAULT NULL COMMENT '爆破战斗部标识',
  `EXBComponent` varchar(60) DEFAULT NULL COMMENT '炸药成分',
  `EXBExplosion` decimal(10,0) DEFAULT NULL COMMENT '炸药热爆',
  `EXBWeight` decimal(10,0) DEFAULT NULL COMMENT '装药质量',
  `EXBMoreParameters` text COMMENT '爆破弹其他参数',
  `IsEnergyBomb` int DEFAULT NULL COMMENT '聚能战斗部标识',
  `EBDensity` decimal(10,0) DEFAULT NULL COMMENT '炸药密度',
  `EBVelocity` decimal(10,0) DEFAULT NULL COMMENT '装药爆速',
  `EBPressure` decimal(10,0) DEFAULT NULL COMMENT '爆轰压',
  `EBCoverMaterial` varchar(60) DEFAULT NULL COMMENT '药型罩材料',
  `EBConeAngle` decimal(10,0) DEFAULT NULL COMMENT '药型罩锥角角度',
  `EBMoreParameters` text COMMENT '聚能弹其他参数',
  `IsFragmentBomb` int DEFAULT NULL COMMENT '破片弹战斗部标识',
  `FBBombExplosion` decimal(10,0) DEFAULT NULL COMMENT '炸弹热爆',
  `FBFragmentShape` text COMMENT '破片形状',
  `FBSurfaceArea` decimal(10,0) DEFAULT NULL COMMENT '破片表面积',
  `FBFragmentWeight` decimal(10,0) DEFAULT NULL COMMENT '破片质量',
  `FBDiameter` decimal(10,0) DEFAULT NULL COMMENT '装药直径',
  `FBLength` decimal(10,0) DEFAULT NULL COMMENT '装药长度',
  `FBShellWeight` decimal(10,0) DEFAULT NULL COMMENT '壳体质量',
  `FBMoreParameters` text COMMENT '破片弹其他参数',
  `IsArmorBomb` int DEFAULT NULL COMMENT '穿甲弹战斗部标识',
  `ABBulletWeight` decimal(10,0) DEFAULT NULL COMMENT '弹丸质量',
  `ABDiameter` decimal(10,0) DEFAULT NULL COMMENT '弹丸直径',
  `ABHeadLength` decimal(10,0) DEFAULT NULL COMMENT '弹丸头部长度',
  `ABMoreParameters` text COMMENT '穿甲弹其他参数',
  `IsClusterBomb` int DEFAULT NULL COMMENT '子母弹战斗部标识',
  `CBMBulletWeight` decimal(10,0) DEFAULT NULL COMMENT '母弹质量',
  `CBMBulletSection` decimal(10,0) DEFAULT NULL COMMENT '母弹最大横截面',
  `CBMProjectile` decimal(10,0) DEFAULT NULL COMMENT '母弹阻力系数',
  `CBSBulletCount` decimal(10,0) DEFAULT NULL COMMENT '子弹数量',
  `CBSBulletModel` varchar(60) DEFAULT NULL COMMENT '子弹型号',
  `CBSBulletWeight` decimal(10,0) DEFAULT NULL COMMENT '子弹质量',
  `CBDiameter` decimal(10,0) DEFAULT NULL COMMENT '最大直径',
  `CBSBulletLength` decimal(10,0) DEFAULT NULL COMMENT '子弹参考长度',
  `CBMoreParameters` text COMMENT '子母弹其他参数',
  `AMStatus` int DEFAULT NULL COMMENT '弹药状态',
  `CreatedTime` datetime DEFAULT NULL COMMENT '创建时间	',
  `UpdatedTime` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`AMID`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ammunition_info`
--

LOCK TABLES `ammunition_info` WRITE;
/*!40000 ALTER TABLE `ammunition_info` DISABLE KEYS */;
INSERT INTO `ammunition_info` VALUES (1,'11','11',NULL,'中国','空军','钻地弹','11',NULL,NULL,NULL,11,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,11,'爆破战斗部','11',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,'球形',NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,NULL),(3,'12','12','12','中国','空军','钻地弹','12',NULL,NULL,NULL,12,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,12,'爆破战斗部','12',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,'球形',NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,NULL),(4,'11','11','1','中国','空军','钻地弹','11',NULL,NULL,NULL,11,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,111,'爆破战斗部','11',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,'球形',NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(5,'我','我',NULL,'中国','空军','钻地弹','1111','111',NULL,NULL,111,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,111,'爆破战斗部','111',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,'球形',NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `ammunition_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `assessment_report`
--

DROP TABLE IF EXISTS `assessment_report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assessment_report` (
  `ReportID` int NOT NULL AUTO_INCREMENT COMMENT '报告ID',
  `ReportCode` varchar(60) DEFAULT NULL COMMENT '报告编号',
  `ReportName` varchar(60) DEFAULT NULL COMMENT '报告名称',
  `DAID` int DEFAULT NULL COMMENT '毁伤评估ID',
  `DSID` int DEFAULT NULL COMMENT '毁伤场景ID',
  `DPID` int DEFAULT NULL COMMENT '毁伤参数ID',
  `AMID` int DEFAULT NULL COMMENT '弹药数据ID',
  `TargetID` int DEFAULT NULL COMMENT '打击目标ID',
  `DamageDegree` varchar(60) DEFAULT NULL COMMENT '毁伤等级',
  `Comment` text COMMENT '评估结论',
  `Creator` varchar(60) DEFAULT NULL COMMENT '报告操作人员',
  `Reviewer` varchar(60) DEFAULT NULL COMMENT '报告审核人',
  `CreatedTime` datetime DEFAULT NULL COMMENT '创建时间',
  `UpdatedTime` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`ReportID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='毁伤评估报告信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assessment_report`
--

LOCK TABLES `assessment_report` WRITE;
/*!40000 ALTER TABLE `assessment_report` DISABLE KEYS */;
/*!40000 ALTER TABLE `assessment_report` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `assessment_result`
--

DROP TABLE IF EXISTS `assessment_result`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assessment_result` (
  `DAID` int NOT NULL AUTO_INCREMENT COMMENT '结果ID',
  `DSID` int DEFAULT NULL COMMENT '场景ID',
  `DPID` int DEFAULT NULL COMMENT '参数ID',
  `AMID` int DEFAULT NULL COMMENT '弹药ID',
  `TargetID` int DEFAULT NULL COMMENT '目标ID',
  `TargetType` int DEFAULT NULL COMMENT '目标类型',
  `DADepth` decimal(10,0) DEFAULT NULL COMMENT '弹坑深度',
  `DADiameter` decimal(10,0) DEFAULT NULL COMMENT '弹坑直径',
  `DAVolume` decimal(10,0) DEFAULT NULL COMMENT '弹坑容积',
  `DAArea` decimal(10,0) DEFAULT NULL COMMENT '弹坑面积',
  `DALength` decimal(10,0) DEFAULT NULL COMMENT '弹坑长度',
  `DAWidth` decimal(10,0) DEFAULT NULL COMMENT '弹坑宽度',
  `Discturction` decimal(10,0) DEFAULT NULL COMMENT '结构破坏程度',
  `DamageDegree` varchar(60) DEFAULT NULL COMMENT '毁伤等级',
  `CreatedTime` datetime DEFAULT NULL COMMENT '创建时间',
  `UpdatedTime` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`DAID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='毁伤能力计算结果表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assessment_result`
--

LOCK TABLES `assessment_result` WRITE;
/*!40000 ALTER TABLE `assessment_result` DISABLE KEYS */;
INSERT INTO `assessment_result` VALUES (1,1,3,3,1,1,1,1,1,1,1,1,1,'重度毁伤','2025-11-10 16:40:30','2025-11-10 16:40:43'),(2,1,3,3,1,1,1,1,1,1,1,1,1,'重度毁伤','2025-11-10 21:02:16','2025-11-10 21:02:16'),(3,1,3,3,1,1,1,1,1,1,1,1,1,'重度毁伤','2025-11-12 21:01:58','2025-11-12 21:01:58');
/*!40000 ALTER TABLE `assessment_result` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `damageparameter_info`
--

DROP TABLE IF EXISTS `damageparameter_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `damageparameter_info` (
  `DPID` int NOT NULL AUTO_INCREMENT COMMENT '参数ID',
  `DSID` int DEFAULT NULL COMMENT '场景ID',
  `DSCode` varchar(60) DEFAULT NULL COMMENT '场景编号',
  `Carrier` varchar(60) DEFAULT NULL COMMENT '投放平台',
  `GuidanceMode` varchar(60) DEFAULT NULL COMMENT '制导方式',
  `WarheadType` varchar(60) DEFAULT NULL COMMENT '战斗部类型',
  `ChargeAmount` decimal(10,0) DEFAULT NULL COMMENT '装药量',
  `DropHeight` decimal(10,0) DEFAULT NULL COMMENT '投弹高度',
  `DropSpeed` decimal(10,0) DEFAULT NULL COMMENT '投弹速度',
  `DropMode` varchar(60) DEFAULT NULL COMMENT '投弹方式',
  `FlightRange` decimal(10,0) DEFAULT NULL COMMENT '射程',
  `ElectroInterference` varchar(60) DEFAULT NULL COMMENT '电磁干扰等级',
  `WeatherConditions` varchar(60) DEFAULT NULL COMMENT '天气状况',
  `WindSpeed` decimal(10,0) DEFAULT NULL COMMENT '环境风速',
  `DPStatus` int DEFAULT NULL COMMENT '参数状态',
  `CreatedTime` datetime DEFAULT NULL COMMENT '创建时间',
  `UpdatedTime` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`DPID`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='毁伤参数信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `damageparameter_info`
--

LOCK TABLES `damageparameter_info` WRITE;
/*!40000 ALTER TABLE `damageparameter_info` DISABLE KEYS */;
INSERT INTO `damageparameter_info` VALUES (1,1,'DS_20251110161239','11','11','爆破战斗部',11,11,11,'11',11,'无','晴',NULL,0,'2025-11-10 16:28:00','2025-11-10 16:28:00'),(2,1,'DS_20251110161239','212','1212','破片战斗部',21212,12,12,'12',12,'低','晴',1212,0,'2025-11-10 16:28:00','2025-11-10 16:28:00'),(3,1,'DS_20251110161239','121','1212','爆破战斗部',1212,121,121,'12',1212,'无','晴',121212,0,'2025-11-10 16:28:00','2025-11-10 16:28:00'),(4,1,'DS_20251110161239','111','111','破片战斗部',NULL,11,11,'11',11,'无','晴',11,1,'2025-11-12 22:19:41','2025-11-12 22:19:41');
/*!40000 ALTER TABLE `damageparameter_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `damagescene_info`
--

DROP TABLE IF EXISTS `damagescene_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `damagescene_info` (
  `DSID` int NOT NULL AUTO_INCREMENT COMMENT '场景ID',
  `DSCode` varchar(60) DEFAULT NULL COMMENT '场景编号',
  `DSName` varchar(60) DEFAULT NULL COMMENT '场景名称',
  `DSOffensive` varchar(60) DEFAULT NULL COMMENT '进攻方',
  `DSDefensive` varchar(60) DEFAULT NULL COMMENT '假想敌',
  `DSBattle` varchar(60) DEFAULT NULL COMMENT '所在战场',
  `AMID` int DEFAULT NULL COMMENT '弹药ID',
  `AMCode` varchar(60) DEFAULT NULL COMMENT '弹药代码',
  `TargetType` int DEFAULT NULL COMMENT '打击目标类型',
  `TargetID` int DEFAULT NULL COMMENT '打击目标ID',
  `TargetCode` varchar(60) DEFAULT NULL COMMENT '打击目标代码',
  `DSStatus` int DEFAULT NULL COMMENT '场景状态',
  `CreatedTime` datetime DEFAULT NULL COMMENT '创建时间',
  `UpdatedTime` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`DSID`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='毁伤场景数据表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `damagescene_info`
--

LOCK TABLES `damagescene_info` WRITE;
/*!40000 ALTER TABLE `damagescene_info` DISABLE KEYS */;
INSERT INTO `damagescene_info` VALUES (1,'DS_20251110161239','12121212','我方空军','敌方防空力量','东部海域作战区',3,'12',1,1,'111',1,'2025-11-10 16:28:00','2025-11-12 22:19:41');
/*!40000 ALTER TABLE `damagescene_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `databackup_records`
--

DROP TABLE IF EXISTS `databackup_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `databackup_records` (
  `BackupID` int NOT NULL AUTO_INCREMENT COMMENT '备份记录ID',
  `BackupType` int DEFAULT NULL COMMENT '备份类型',
  `BackupCycle` varchar(60) DEFAULT NULL COMMENT '备份周期',
  `CycleDetail` varchar(60) DEFAULT NULL COMMENT '周期详情',
  `BackupPath` varchar(60) DEFAULT NULL COMMENT '备份文件存储路径',
  `BackupFile` varchar(60) DEFAULT NULL COMMENT '备份文件名',
  `VersionNo` varchar(60) DEFAULT NULL COMMENT '备份版本编号',
  `BackupStatus` varchar(60) DEFAULT NULL COMMENT '备份状态',
  `BackupTime` datetime DEFAULT NULL COMMENT '备份执行时间',
  `Operator` varchar(60) DEFAULT NULL COMMENT '操作人',
  `Remark` text COMMENT '备注信息',
  PRIMARY KEY (`BackupID`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='数据备份信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `databackup_records`
--

LOCK TABLES `databackup_records` WRITE;
/*!40000 ALTER TABLE `databackup_records` DISABLE KEYS */;
INSERT INTO `databackup_records` VALUES (1,2,'',NULL,'d:\\','manual_20251114102022.sql','V20251114102022_853a0e','成功','2025-11-14 10:20:22','admin',''),(2,2,'',NULL,'d:\\','manual_20251114111836.sql','V20251114111836_e6683e','成功','2025-11-14 11:18:37','admin',''),(3,1,'每周',NULL,'D:\\Code_Pycharm\\A_KJ2025\\HS_2025-main\\auto_backups','auto_20251114162719.sql','V20251114162719_2cd3a5','成功','2025-11-14 16:27:20','admin',''),(4,1,'每周',NULL,'D:\\Code_Pycharm\\A_KJ2025\\HS_2025-main\\auto_backups','auto_20251114162752.sql','V20251114162752_10ddd5','成功','2025-11-14 16:27:53','admin','');
/*!40000 ALTER TABLE `databackup_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `datarestore_records`
--

DROP TABLE IF EXISTS `datarestore_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `datarestore_records` (
  `RestoreID` int NOT NULL AUTO_INCREMENT COMMENT '恢复记录ID',
  `BackupID` int DEFAULT NULL COMMENT '备份记录ID',
  `RestorePath` varchar(60) DEFAULT NULL COMMENT '恢复文件存储路径',
  `RestoreFile` varchar(60) DEFAULT NULL COMMENT '恢复文件名',
  `VersionNo` varchar(60) DEFAULT NULL COMMENT '恢复版本编号',
  `RestoreStatus` int DEFAULT NULL COMMENT '恢复状态',
  `RestoreTime` datetime DEFAULT NULL COMMENT '恢复执行时间',
  `Operator` varchar(60) DEFAULT NULL COMMENT '操作人',
  `Remark` text COMMENT '备注信息',
  PRIMARY KEY (`RestoreID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='数据恢复信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `datarestore_records`
--

LOCK TABLES `datarestore_records` WRITE;
/*!40000 ALTER TABLE `datarestore_records` DISABLE KEYS */;
INSERT INTO `datarestore_records` VALUES (1,1,'d:\\','manual_20251114102022.sql','V20251114102022_853a0e',0,'2025-11-14 15:33:33','admin','恢复失败: Command \'mysql -uroot -p123456 -hlocalhost damassessment_db < d:\\manual_20251114102022.sql\' returned non-zero exit status 1.'),(2,2,'d:\\','manual_20251114111836.sql','V20251114111836_e6683e',0,'2025-11-14 15:40:10','admin','恢复失败: \'mysql_path\''),(3,2,'d:\\','manual_20251114111836.sql','V20251114111836_e6683e',0,'2025-11-14 15:41:07','admin','恢复失败: \'DataRestore\' object has no attribute \'mysqldump_path\'');
/*!40000 ALTER TABLE `datarestore_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `runway_info`
--

DROP TABLE IF EXISTS `runway_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `runway_info` (
  `RunwayID` int NOT NULL AUTO_INCREMENT COMMENT '机场ID(自增)',
  `RunwayCode` varchar(60) DEFAULT NULL COMMENT '机场代码',
  `RunwayName` varchar(60) DEFAULT NULL COMMENT '机场名称',
  `Country` varchar(60) DEFAULT NULL COMMENT '国家/地区',
  `Base` varchar(60) DEFAULT NULL COMMENT '基地/部队',
  `RunwayPicture` varchar(90) DEFAULT NULL COMMENT '机场照片',
  `RLength` decimal(10,0) DEFAULT NULL COMMENT '跑道长度',
  `RWidth` decimal(10,0) DEFAULT NULL COMMENT '跑道宽度',
  `PCCSCThick` decimal(10,0) DEFAULT NULL COMMENT '混凝土面层厚度',
  `PCCSCStrength` decimal(10,0) DEFAULT NULL COMMENT '混凝土面层抗压强度',
  `PCCSCFlexural` decimal(10,0) DEFAULT NULL COMMENT '混凝土面层抗折强度',
  `PCCSCFreeze` decimal(10,0) DEFAULT NULL COMMENT '抗冻融循环次数',
  `PCCSCCement` varchar(60) DEFAULT NULL COMMENT '水泥类型',
  `PCCSCBlockSize1` decimal(10,0) DEFAULT NULL COMMENT '道面分块尺寸1',
  `PCCSCBlockSize2` decimal(10,0) DEFAULT NULL COMMENT '道面分块尺寸2',
  `CTBCThick` decimal(10,0) DEFAULT NULL COMMENT '水泥稳定碎石基层厚度',
  `CTBCStrength` decimal(10,0) DEFAULT NULL COMMENT '水泥稳定碎石基层抗压强度',
  `CTBCFlexural` decimal(10,0) DEFAULT NULL COMMENT '水泥稳定碎石基层抗折强度',
  `CTBCCement` decimal(10,0) DEFAULT NULL COMMENT '水泥掺量',
  `CTBCCompaction` decimal(10,0) DEFAULT NULL COMMENT '夯实密实度',
  `GCSSThick` decimal(10,0) DEFAULT NULL COMMENT '级配砂砾石垫层厚度',
  `GCSSStrength` decimal(10,0) DEFAULT NULL COMMENT '级配砂砾石垫层强度承载比',
  `GCSSCompaction` decimal(10,0) DEFAULT NULL COMMENT '级配砂砾石垫层压实模量',
  `CSThick` decimal(10,0) DEFAULT NULL COMMENT '土基压实层强度厚度',
  `CSStrength` decimal(10,0) DEFAULT NULL COMMENT '土基压实层强度承载比',
  `CSCompaction` decimal(10,0) DEFAULT NULL COMMENT '土基压实层压实模量',
  `RunwayStatus` int DEFAULT NULL COMMENT '跑道状态',
  `CreatedTime` datetime DEFAULT NULL COMMENT '创建时间',
  `UpdatedTime` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`RunwayID`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `runway_info`
--

LOCK TABLES `runway_info` WRITE;
/*!40000 ALTER TABLE `runway_info` DISABLE KEYS */;
INSERT INTO `runway_info` VALUES (1,'111','模拟机场跑道1','美国',NULL,NULL,3600,80,34,50,5,250,'硅酸盐水泥',5,5,36,3,1,NULL,95,50,80,5,50,80,5,1,'2025-11-08 03:39:54','2025-11-08 03:40:12');
/*!40000 ALTER TABLE `runway_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `shelter_info`
--

DROP TABLE IF EXISTS `shelter_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `shelter_info` (
  `ShelterID` int NOT NULL AUTO_INCREMENT COMMENT '掩蔽库ID',
  `ShelterCode` varchar(60) DEFAULT NULL COMMENT '掩蔽库代码',
  `ShelterName` varchar(60) DEFAULT NULL COMMENT '掩蔽库名称',
  `Country` varchar(60) DEFAULT NULL COMMENT '国家地区',
  `Base` varchar(60) DEFAULT NULL COMMENT '基地部队',
  `ShelterPicture` varchar(90) DEFAULT NULL COMMENT '掩蔽库照片',
  `ShelterWidth` decimal(10,0) DEFAULT NULL COMMENT '库容净宽',
  `ShelterHeight` decimal(10,0) DEFAULT NULL COMMENT '库容净高',
  `ShelterLength` decimal(10,0) DEFAULT NULL COMMENT '库容净长',
  `CaveWidth` decimal(10,0) DEFAULT NULL COMMENT '洞门宽度',
  `CaveHeight` decimal(10,0) DEFAULT NULL COMMENT '洞门高度',
  `StructuralForm` varchar(60) DEFAULT NULL COMMENT '结构形式',
  `DoorMaterial` varchar(60) DEFAULT NULL COMMENT '门体材料',
  `DoorThick` decimal(10,0) DEFAULT NULL COMMENT '门体厚度',
  `MaskLayerMaterial` varchar(60) DEFAULT NULL COMMENT '伪装层材料',
  `MaskLayerThick` decimal(10,0) DEFAULT NULL COMMENT '伪装层厚度',
  `SoilLayerMaterial` varchar(60) DEFAULT NULL COMMENT '遮弹层材料',
  `SoilLayerThick` decimal(10,0) DEFAULT NULL COMMENT '遮弹层厚度',
  `DisperLayerMaterial` varchar(60) DEFAULT NULL COMMENT '分散层材料',
  `DisperLayerThick` decimal(10,0) DEFAULT NULL COMMENT '分散层厚度',
  `DisperLayerReinforcement` varchar(60) DEFAULT NULL COMMENT '分散层钢筋配置',
  `StructureLayerMaterial` varchar(60) DEFAULT NULL COMMENT '结构层材料',
  `StructureLayerThick` decimal(10,0) DEFAULT NULL COMMENT '结构层厚度',
  `StructureLayerReinforcement` varchar(60) DEFAULT NULL COMMENT '结构层钢筋配置',
  `ExplosionResistance` decimal(10,0) DEFAULT NULL COMMENT '抗爆能力',
  `AntiKinetic` decimal(10,0) DEFAULT NULL COMMENT '抗动能穿透',
  `ResistanceDepth` decimal(10,0) DEFAULT NULL COMMENT '抗穿透深度',
  `NuclearBlast` decimal(10,0) DEFAULT NULL COMMENT '抗核冲波超压',
  `RadiationShielding` decimal(10,0) DEFAULT NULL COMMENT '抗辐射屏蔽',
  `FireResistance` int DEFAULT NULL COMMENT '耐火极限',
  `ShelterStatus` int DEFAULT NULL COMMENT '掩蔽库状态',
  `CreatedTime` datetime DEFAULT NULL COMMENT '创建时间',
  `UpdatedTime` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`ShelterID`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='单机掩蔽库信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `shelter_info`
--

LOCK TABLES `shelter_info` WRITE;
/*!40000 ALTER TABLE `shelter_info` DISABLE KEYS */;
INSERT INTO `shelter_info` VALUES (1,'11','11','中国',NULL,'C:/Users/Lenovo/Pictures/{2D11E31B-D1CC-4ECD-B80D-E4C04693B7D4}.png',3,3,3,3,3,NULL,NULL,2,'22',2,'22',2,'22',2,'HRB500','22',2,'HRB400',100,2000,2,200,100,3,1,'2025-11-09 13:49:21','2025-11-09 13:49:43');
/*!40000 ALTER TABLE `shelter_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ucc_info`
--

DROP TABLE IF EXISTS `ucc_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ucc_info` (
  `UCCID` int NOT NULL AUTO_INCREMENT COMMENT '指挥所ID',
  `UCCCode` varchar(60) DEFAULT NULL COMMENT '指挥所代码',
  `UCCName` varchar(60) DEFAULT NULL COMMENT '指挥所名称',
  `Country` varchar(60) DEFAULT NULL COMMENT '国家地区',
  `Base` varchar(60) DEFAULT NULL COMMENT '基地部队',
  `ShelterPicture` varchar(90) DEFAULT NULL COMMENT '指挥所照片',
  `Location` varchar(60) DEFAULT NULL COMMENT '所在位置',
  `RockLayerMaterials` varchar(60) DEFAULT NULL COMMENT '土壤岩层材料',
  `RockLayerThick` decimal(10,0) DEFAULT NULL COMMENT '土壤岩层厚度',
  `RockLayerStrength` decimal(10,0) DEFAULT NULL COMMENT '土壤岩层抗压强度',
  `ProtectiveLayerMaterial` varchar(60) DEFAULT NULL COMMENT '防护层材料',
  `ProtectiveLayerThick` decimal(10,0) DEFAULT NULL COMMENT '防护层厚度',
  `ProtectiveLayerStrength` decimal(10,0) DEFAULT NULL COMMENT '防护层抗压强度',
  `LiningLayerMaterial` varchar(60) DEFAULT NULL COMMENT '衬砌层材料',
  `LiningLayerThick` decimal(10,0) DEFAULT NULL COMMENT '衬砌层厚度',
  `LiningLayerStrength` decimal(10,0) DEFAULT NULL COMMENT '衬砌层抗压强度',
  `UCCWallMaterials` varchar(60) DEFAULT NULL COMMENT '指挥中心墙壁材料',
  `UCCWallThick` decimal(10,0) DEFAULT NULL COMMENT '指挥中心墙壁厚度',
  `UCCWallStrength` decimal(10,0) DEFAULT NULL COMMENT '指挥中心墙壁抗压强度',
  `UCCWidth` decimal(10,0) DEFAULT NULL COMMENT '指挥中心宽度',
  `UCCLength` decimal(10,0) DEFAULT NULL COMMENT '指挥中心长度',
  `UCCHeight` decimal(10,0) DEFAULT NULL COMMENT '指挥中心高度',
  `UCCStatus` int DEFAULT NULL COMMENT '指挥所状态',
  `CreatedTime` datetime DEFAULT NULL COMMENT '创建时间',
  `UpdatedTime` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`UCCID`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='地下指挥所信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ucc_info`
--

LOCK TABLES `ucc_info` WRITE;
/*!40000 ALTER TABLE `ucc_info` DISABLE KEYS */;
INSERT INTO `ucc_info` VALUES (1,'11','11','中国','11','C:/Users/Lenovo/Pictures/{D9D68C6B-1A48-4A6D-9F28-EE0A0639F6A5}.png','11','11',1000,50,'11',200,50,'11',60,30,'111',60,30,20,30,4,1,'2025-11-09 13:50:06','2025-11-09 13:50:18');
/*!40000 ALTER TABLE `ucc_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_info`
--

DROP TABLE IF EXISTS `user_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_info` (
  `UID` int NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `UserName` varchar(100) NOT NULL COMMENT '用户名',
  `UPassword` varchar(100) NOT NULL COMMENT '登录密码',
  `URole` varchar(30) NOT NULL COMMENT '用户角色',
  `TrueName` varchar(100) DEFAULT NULL COMMENT '真实姓名',
  `Department` varchar(100) DEFAULT NULL COMMENT '单位部门',
  `UPosition` varchar(100) DEFAULT NULL COMMENT '职务职位',
  `Telephone` varchar(100) DEFAULT NULL COMMENT '联系电话',
  `Address` varchar(200) DEFAULT NULL COMMENT '联系地址',
  `UStatus` int DEFAULT NULL COMMENT '用户状态',
  `URemark` text COMMENT '备注',
  PRIMARY KEY (`UID`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_info`
--

LOCK TABLES `user_info` WRITE;
/*!40000 ALTER TABLE `user_info` DISABLE KEYS */;
INSERT INTO `user_info` VALUES (5,'use','$2b$12$CYLi/cJ97ODCiF1xl.78xucOLodf22M.2xjsKDsOT8p0kINJNNUBC','0','陈工','天','无','120','无',2,''),(6,'user2','$2b$12$YXWS5z5cLYmiwStcogNgLOLMmErmKPS.UTp/Tiee6.C14dzso.9VK','0','吴','天工','2','120','12',0,''),(7,'u3','$5$rounds=535000$sc47oAPxPlB80sQ0$q1VoloTenDzgABBIzfkgsVUu/RafSYIkIGQCg5Qjzl9','0','aaaa','aa','aa','aa','',0,''),(8,'11','$2b$12$XAkZZcvR/Vg/Whv8sXdye.xYN0nRVI.2zsLt/BdtHy/HngNiEonU2','0','11','11','11','11','',0,''),(9,'user12','$2b$12$PsORs.jEuAjnaEnQU9Inc.PHNECbZGVviViEoQHpmfeXtba9bTz3u','0','12','12','','12212121','',0,''),(10,'112','$2b$12$HB5n3dq3OQa4npottLEJLOtuKCpvKumah/KCZ82d9CdtRi2wJiVT6','0','你好','1','','1','',0,''),(11,'111','$2b$12$PnH2T5Cb3Eu4v7lzjsZ/1ufYNkamGgiROI9BtwWBXmNwmhNtydA8S','0','陈主任','11','','11','',0,''),(12,'111','$2b$12$/uCTp27VVYFFsfmLhE2KTuerEzl0u6SIf4NcsVOXVFCLYltqR3rha','1','11','11','','11','111',1,'1221'),(13,'121','$2b$12$H5CpNc4ogzTCofkliOln1eDyLp8keKdax5CWXLdgcxHRO7TTNmFre','0','你好','技术部','11','11','',0,''),(14,'u4','$2b$12$IFhZ/meGIXBuZbG1QG15E.x2J9tlDe1AGBGtP62Q05SvmtUTPKsZ6','0','王小明','11','','11','',0,''),(15,'admin','$2b$12$x6BUAytb1VOBUj0NDgOTqurgS0D6UP6OiaQ7aBOXM3g3cirLyZdhC','0','王小明','二室','','132','',0,''),(16,'zhangxx','$2b$12$YimPXWfrXje5mKSeLw9jIuDNRFsYlqWNmo.tptoeTkp5OmMt4QsCO','0','张XXX','科研一处','','1390000000','',0,'');
/*!40000 ALTER TABLE `user_info` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-14 16:28:24
