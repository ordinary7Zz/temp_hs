--- 创建数据库
create database DAMAssessment_DB;

use   DAMAssessment_DB;

-- drop table user_info;
drop table if exists Runway_Info;
drop table if exists Ammunition_Info;


drop table aircraft_shelter;
drop table airport_runway;
drop table underground_command_post;

drop table Ammunition_Info;
-- 弹药毁伤数据信息表
create table Ammunition_Info
(
   AMID                 int primary key auto_increment  COMMENT '弹药ID',
   AMName               varchar(100)  COMMENT '官方名称',
   AMImage        MEDIUMBLOB COMMENT '弹药照片',
   AMNameCN             varchar(100)  COMMENT '中文名称',
   AMAbbreviation       varchar(60)  COMMENT '简称',
   Country              varchar(60)  COMMENT '国家/地区',
   Base                 varchar(60)  COMMENT '基地/部队',
   AMType               varchar(60)  COMMENT '弹药类型',
   AMModel              varchar(60)  COMMENT '弹药型号',
   AMSubmodel           varchar(60)  COMMENT '型号子类',
   Manufacturer         varchar(60)  COMMENT '制造商',
   AttendedDate         varchar(60)  COMMENT '服役时间',
   AMWeight             decimal(10,2)  COMMENT '弹体全重',
   AMLength             decimal(10,2)  COMMENT '弹体长度',
   AMDiameter           decimal(10,2)  COMMENT '弹体直径',
   AMTexture            varchar(60)  COMMENT '弹体材质',
   WingspanClose        decimal(10,2)  COMMENT '翼展(闭合)',
   WingspanOpen         decimal(10,2)  COMMENT '翼展(张开)',
   AMStructure          varchar(60)  COMMENT '结构',
   MaxSpeed             decimal(10,2)  COMMENT '最大时速',
   RadarSection         varchar(60)  COMMENT '雷达截面',
   AMPower              varchar(60)  COMMENT '动力装置',
   LaunchWeight         decimal(10,2)  COMMENT '发射质量',
   WarheadType          varchar(60)  COMMENT '战斗部类型',
   WarheadName          varchar(60)  COMMENT '战斗部名称',
   Penetrator           varchar(60)  COMMENT '毁伤元',
   Fuze                 varchar(60)  COMMENT '引信',
   TNTEquivalent        decimal(10,2)  COMMENT '爆炸当量',
   CEP                  decimal(10,2)  COMMENT '精度(圆概率误差CEP)',
   DestroyMechanism     varchar(60)  COMMENT '破坏机制',
   Targets              varchar(60)  COMMENT '打击目标',
   Carrier              varchar(60)  COMMENT '载机(投放平台)',
   GuidanceMode         varchar(60)  COMMENT '制导方式',
   ChargeAmount         decimal(10,2)  COMMENT '装药量',
   PenetratePower       varchar(60)  COMMENT '穿透能力',
   DropHeight           varchar(60)  COMMENT '投弹高度范围',
   DropSpeed            decimal(10,2)  COMMENT '投弹速度',
   DropMode             varchar(60)  COMMENT '投弹方式',
   CoverageArea         varchar(60)  COMMENT '布撒范围',
   FlightRange          decimal(10,2)  COMMENT '射程',
   IsExplosiveBomb      int  COMMENT '爆破战斗部标识',
   EXBComponent         varchar(60)  COMMENT '炸药成分',
   EXBExplosion         decimal(10,2)  COMMENT '炸药热爆',
   EXBWeight            decimal(10,2)  COMMENT '装药质量',
   EXBMoreParameters    text  COMMENT '爆破弹其他参数',
   IsEnergyBomb         int  COMMENT '聚能战斗部标识',
   EBDensity            decimal(10,2)  COMMENT '炸药密度',
   EBVelocity           decimal(10,2)  COMMENT '装药爆速',
   EBPressure           decimal(10,2)  COMMENT '爆轰压',
   EBCoverMaterial      varchar(60)  COMMENT '药型罩材料',
   EBConeAngle          decimal(10,2)  COMMENT '药型罩锥角角度',
   EBMoreParameters     text  COMMENT '聚能弹其他参数',
   IsFragmentBomb       int  COMMENT '破片弹战斗部标识',
   FBBombExplosion      decimal(10,2)  COMMENT '炸弹热爆',
   FBFragmentShape      text  COMMENT '破片形状',
   FBSurfaceArea        decimal(10,2)  COMMENT '破片表面积',
   FBFragmentWeight     decimal(10,2)  COMMENT '破片质量',
   FBDiameter           decimal(10,2)  COMMENT '装药直径',
   FBLength             decimal(10,2)  COMMENT '装药长度',
   FBShellWeight        decimal(10,2)  COMMENT '壳体质量',
   FBMoreParameters     text  COMMENT '破片弹其他参数',
   IsArmorBomb          int  COMMENT '穿甲弹战斗部标识',
   ABBulletWeight       decimal(10,2)  COMMENT '弹丸质量',
   ABDiameter           decimal(10,2)  COMMENT '弹丸直径',
   ABHeadLength         decimal(10,2)  COMMENT '弹丸头部长度',
   ABMoreParameters     text  COMMENT '穿甲弹其他参数',
   IsClusterBomb        int  COMMENT '子母弹战斗部标识',
   CBMBulletWeight      decimal(10,2)  COMMENT '母弹质量',
   CBMBulletSection     decimal(10,2)  COMMENT '母弹最大横截面',
   CBMProjectile        decimal(10,2)  COMMENT '母弹阻力系数',
   CBSBulletCount       decimal(10,2)  COMMENT '子弹数量',
   CBSBulletModel       varchar(60)  COMMENT '子弹型号',
   CBSBulletWeight      decimal(10,2)  COMMENT '子弹质量',
   CBDiameter           decimal(10,2)  COMMENT '最大直径',
   CBSBulletLength      decimal(10,2)  COMMENT '子弹参考长度',
   CBMoreParameters     text  COMMENT '子母弹其他参数',
   AMStatus             int  COMMENT '弹药状态',
   CreatedTime          datetime  COMMENT '创建时间	',
   UpdatedTime          datetime  COMMENT '更新时间'
) COMMENT='弹药毁伤数据信息表';


drop table Runway_Info;

-- 机场跑道信息表
create table Runway_Info
(
   RunwayID             INT PRIMARY KEY AUTO_INCREMENT COMMENT '机场ID(自增)',
   RunwayCode           VARCHAR(60) COMMENT '机场代码',
   RunwayName           VARCHAR(60) COMMENT '机场名称',
   Country              VARCHAR(60) COMMENT '国家/地区',
   Base                 VARCHAR(60) COMMENT '基地/部队',
   RunwayPicture        MEDIUMBLOB COMMENT '机场照片',
   RLength              decimal(10,2) COMMENT '跑道长度',
   RWidth               decimal(10,2) COMMENT '跑道宽度',
   PCCSCThick           decimal(10,2) COMMENT '混凝土面层厚度',
   PCCSCStrength        decimal(10,2) COMMENT '混凝土面层抗压强度',
   PCCSCFlexural        decimal(10,2) COMMENT '混凝土面层抗折强度',
   PCCSCFreeze          decimal(10,2) COMMENT '抗冻融循环次数',
   PCCSCCement          VARCHAR(60) COMMENT '水泥类型',
   PCCSCBlockSize1      decimal(10,2) COMMENT '道面分块尺寸1',
   PCCSCBlockSize2      decimal(10,2) COMMENT '道面分块尺寸2',
   CTBCThick            decimal(10,2) COMMENT '水泥稳定碎石基层厚度',
   CTBCStrength         decimal(10,2) COMMENT '水泥稳定碎石基层抗压强度',
   CTBCFlexural         decimal(10,2) COMMENT '水泥稳定碎石基层抗折强度',
   CTBCCement           decimal(10,2) COMMENT '水泥掺量',
   CTBCCompaction       decimal(10,2) COMMENT '夯实密实度',
   GCSSThick            decimal(10,2) COMMENT '级配砂砾石垫层厚度',
   GCSSStrength         decimal(10,2) COMMENT '级配砂砾石垫层强度承载比',
   GCSSCompaction       decimal(10,2) COMMENT '级配砂砾石垫层压实模量',
   CSThick              decimal(10,2) COMMENT '土基压实层强度厚度',
   CSStrength           decimal(10,2) COMMENT '土基压实层强度承载比',
   CSCompaction         decimal(10,2) COMMENT '土基压实层压实模量',
   RunwayStatus         INT COMMENT '跑道状态',
   CreatedTime          DATETIME COMMENT '创建时间',
   UpdatedTime          DATETIME COMMENT '更新时间'
) COMMENT='机场跑道信息表';


-- 修改Runway_Info表的RunwayPicture字段为MEDIUMBLOB类型
ALTER TABLE Runway_Info MODIFY COLUMN RunwayPicture MEDIUMBLOB;

drop table Shelter_Info;

-- 单机掩蔽库信息表
create table Shelter_Info
(
   ShelterID            int PRIMARY KEY AUTO_INCREMENT  COMMENT '掩蔽库ID',
   ShelterCode          varchar(60)  COMMENT '掩蔽库代码',
   ShelterName          varchar(60)  COMMENT '掩蔽库名称',
   Country              varchar(60)  COMMENT '国家地区',
   Base                 varchar(60)  COMMENT '基地部队',
   ShelterPicture       MEDIUMBLOB  COMMENT '掩蔽库照片',
   ShelterWidth         decimal(10,2)  COMMENT '库容净宽',
   ShelterHeight        decimal(10,2)  COMMENT '库容净高',
   ShelterLength        decimal(10,2)  COMMENT '库容净长',
   CaveWidth            decimal(10,2)  COMMENT '洞门宽度',
   CaveHeight           decimal(10,2)  COMMENT '洞门高度',
   StructuralForm       varchar(60)  COMMENT '结构形式',
   DoorMaterial         varchar(60)  COMMENT '门体材料',
   DoorThick            decimal(10,2)  COMMENT '门体厚度',
   MaskLayerMaterial    varchar(60)  COMMENT '伪装层材料',
   MaskLayerThick       decimal(10,2)  COMMENT '伪装层厚度',
   SoilLayerMaterial    varchar(60)  COMMENT '遮弹层材料',
   SoilLayerThick       decimal(10,2)  COMMENT '遮弹层厚度',
   DisperLayerMaterial  varchar(60)  COMMENT '分散层材料',
   DisperLayerThick     decimal(10,2)  COMMENT '分散层厚度',
   DisperLayerReinforcement varchar(60)  COMMENT '分散层钢筋配置',
   StructureLayerMaterial varchar(60)  COMMENT '结构层材料',
   StructureLayerThick  decimal(10,2)  COMMENT '结构层厚度',
   StructureLayerReinforcement varchar(60)  COMMENT '结构层钢筋配置',
   ExplosionResistance  decimal(10,2)  COMMENT '抗爆能力',
   AntiKinetic          decimal(10,2)  COMMENT '抗动能穿透',
   ResistanceDepth      decimal(10,2)  COMMENT '抗穿透深度',
   NuclearBlast         decimal(10,2)  COMMENT '抗核冲波超压',
   RadiationShielding   decimal(10,2)  COMMENT '抗辐射屏蔽',
   FireResistance       int  COMMENT '耐火极限',
   ShelterStatus        int  COMMENT '掩蔽库状态',
   CreatedTime          datetime  COMMENT '创建时间',
   UpdatedTime          datetime  COMMENT '更新时间'
) COMMENT='单机掩蔽库信息表';

-- 修改Shelter_Info表的ShelterPicture字段为MEDIUMBLOB类型
ALTER TABLE Shelter_Info MODIFY COLUMN ShelterPicture MEDIUMBLOB;

ALTER TABLE Shelter_Info MODIFY COLUMN ShelterHeight DOUBLE;
ALTER TABLE Shelter_Info MODIFY COLUMN ShelterHeight decimal(10,2);

desc shelter_info;

drop table UCC_Info;

-- 地下指挥所信息表
create table UCC_Info
(
   UCCID                int PRIMARY KEY AUTO_INCREMENT   COMMENT '指挥所ID',
   UCCCode              varchar(60)  COMMENT '指挥所代码',
   UCCName              varchar(60)  COMMENT '指挥所名称',
   Country              varchar(60)  COMMENT '国家地区',
   Base                 varchar(60)  COMMENT '基地部队',
   ShelterPicture       MEDIUMBLOB COMMENT '指挥所照片',
   Location             varchar(60)  COMMENT '所在位置',
   RockLayerMaterials   varchar(60)  COMMENT '土壤岩层材料',
   RockLayerThick       decimal(10,2)  COMMENT '土壤岩层厚度',
   RockLayerStrength    decimal(10,2)  COMMENT '土壤岩层抗压强度',
   ProtectiveLayerMaterial varchar(60)  COMMENT '防护层材料',
   ProtectiveLayerThick decimal(10,2)  COMMENT '防护层厚度',
   ProtectiveLayerStrength decimal(10,2)  COMMENT '防护层抗压强度',
   LiningLayerMaterial  varchar(60)  COMMENT '衬砌层材料',
   LiningLayerThick     decimal(10,2)  COMMENT '衬砌层厚度',
   LiningLayerStrength  decimal(10,2)  COMMENT '衬砌层抗压强度',
   UCCWallMaterials     varchar(60)  COMMENT '指挥中心墙壁材料',
   UCCWallThick         decimal(10,2)  COMMENT '指挥中心墙壁厚度',
   UCCWallStrength      decimal(10,2)  COMMENT '指挥中心墙壁抗压强度',
   UCCWidth             decimal(10,2)  COMMENT '指挥中心宽度',
   UCCLength            decimal(10,2)  COMMENT '指挥中心长度',
   UCCHeight            decimal(10,2)  COMMENT '指挥中心高度',
   UCCStatus            int  COMMENT '指挥所状态',
   CreatedTime          datetime  COMMENT '创建时间',
   UpdatedTime          datetime  COMMENT '更新时间'
) COMMENT='地下指挥所信息表';

-- 毁伤场景数据表
create table DamageScene_Info
(
   DSID                 int PRIMARY KEY AUTO_INCREMENT  COMMENT '场景ID',
   DSCode               varchar(60)  COMMENT '场景编号',
   DSName               varchar(60)  COMMENT '场景名称',
   DSOffensive          varchar(60)  COMMENT '进攻方',
   DSDefensive          varchar(60)  COMMENT '假想敌',
   DSBattle             varchar(60)  COMMENT '所在战场',
   AMID                 int  COMMENT '弹药ID',
   AMCode               varchar(60)  COMMENT '弹药代码',
   TargetType           int  COMMENT '打击目标类型',
   TargetID             int  COMMENT '打击目标ID',
   TargetCode           varchar(60)  COMMENT '打击目标代码',
   DSStatus             int  COMMENT '场景状态',
   CreatedTime          datetime  COMMENT '创建时间',
   UpdatedTime          datetime  COMMENT '更新时间'
) COMMENT='毁伤场景数据表';


-- 毁伤参数信息表
create table DamageParameter_Info
(
   DPID                 int PRIMARY KEY AUTO_INCREMENT COMMENT '参数ID',
   DSID                 int  COMMENT '场景ID',
   DSCode               varchar(60)  COMMENT '场景编号',
   Carrier              varchar(60)  COMMENT '投放平台',
   GuidanceMode         varchar(60)  COMMENT '制导方式',
   WarheadType          varchar(60)  COMMENT '战斗部类型',
   ChargeAmount         decimal(10,2)  COMMENT '装药量',
   DropHeight           decimal(10,2)  COMMENT '投弹高度',
   DropSpeed            decimal(10,2)  COMMENT '投弹速度',
   DropMode             varchar(60)  COMMENT '投弹方式',
   FlightRange          decimal(10,2)  COMMENT '射程',
   ElectroInterference  varchar(60)  COMMENT '电磁干扰等级',
   WeatherConditions    varchar(60)  COMMENT '天气状况',
   WindSpeed            decimal(10,2)  COMMENT '环境风速',
   DPStatus             int  COMMENT '参数状态',
   CreatedTime          datetime  COMMENT '创建时间',
   UpdatedTime          datetime  COMMENT '更新时间'
) COMMENT='毁伤参数信息表';


-- 毁伤能力计算结果表
create table Assessment_Result
(
   DAID                 int PRIMARY KEY AUTO_INCREMENT COMMENT '结果ID',
   DSID                 int  COMMENT '场景ID',
   DPID                 int  COMMENT '参数ID',
   AMID                 int  COMMENT '弹药ID',
   TargetID             int  COMMENT '目标ID',
   TargetType           int  COMMENT '目标类型',
   DADepth              decimal(10,2)  COMMENT '弹坑深度',
   DADiameter           decimal(10,2)  COMMENT '弹坑直径',
   DAVolume             decimal(10,2)  COMMENT '弹坑容积',
   DAArea               decimal(10,2)  COMMENT '弹坑面积',
   DALength             decimal(10,2)  COMMENT '弹坑长度',
   DAWidth              decimal(10,2)  COMMENT '弹坑宽度',
   Discturction         decimal(10,2)  COMMENT '结构破坏程度',
   DamageDegree         varchar(60)  COMMENT '毁伤等级',
   CreatedTime          datetime  COMMENT '创建时间',
   UpdatedTime          datetime  COMMENT '更新时间'
) COMMENT='毁伤能力计算结果表';


-- 毁伤评估报告信息表
create table Assessment_Report
(
   ReportID             int PRIMARY KEY AUTO_INCREMENT COMMENT '报告ID',
   ReportCode           varchar(60)  COMMENT '报告编号',
   ReportName           varchar(60)  COMMENT '报告名称',
   DAID                 int  COMMENT '毁伤评估ID',
   DSID                 int  COMMENT '毁伤场景ID',
   DPID                 int  COMMENT '毁伤参数ID',
   AMID                 int  COMMENT '弹药数据ID',
   TargetID             int  COMMENT '打击目标ID',
   TargetType           int  COMMENT '目标类型',
   DamageDegree         varchar(60)  COMMENT '毁伤等级',
   Comment              text  COMMENT '评估结论',
   Creator              varchar(60)  COMMENT '报告操作人员',
   Reviewer             varchar(60)  COMMENT '报告审核人',
   CreatedTime          datetime  COMMENT '创建时间',
   UpdatedTime          datetime  COMMENT '更新时间'
) COMMENT='毁伤评估报告信息表';

-- 数据备份信息表
create table DataBackup_Records
(
   BackupID             int PRIMARY KEY AUTO_INCREMENT   COMMENT '备份记录ID',
   BackupType           int  COMMENT '备份类型',
   BackupCycle          varchar(60)  COMMENT '备份周期',
   CycleDetail          varchar(60)  COMMENT '周期详情',
   BackupPath           varchar(60)  COMMENT '备份文件存储路径',
   BackupFile           varchar(60)  COMMENT '备份文件名',
   VersionNo            varchar(60)  COMMENT '备份版本编号',
   BackupStatus         varchar(60)  COMMENT '备份状态',
   BackupTime           datetime  COMMENT '备份执行时间',
   Operator             varchar(60)  COMMENT '操作人',
   Remark               text  COMMENT '备注信息'
) COMMENT='数据备份信息表';

-- 数据恢复信息表
create table DataRestore_Records
(
   RestoreID            int PRIMARY KEY AUTO_INCREMENT  COMMENT '恢复记录ID',
   BackupID             int  COMMENT '备份记录ID',
   RestorePath          varchar(60)  COMMENT '恢复文件存储路径',
   RestoreFile          varchar(60)  COMMENT '恢复文件名',
   VersionNo            varchar(60)  COMMENT '恢复版本编号',
   RestoreStatus        int  COMMENT '恢复状态',
   RestoreTime          datetime  COMMENT '恢复执行时间',
   Operator             varchar(60)  COMMENT '操作人',
   Remark               text  COMMENT '备注信息'
) COMMENT='数据恢复信息表';

 drop table user_info;

--  用户信息表
CREATE TABLE User_Info (
    UID INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    UserName VARCHAR(100) NOT NULL COMMENT '用户名',
    UPassword VARCHAR(100) NOT NULL COMMENT '登录密码',
    URole VARCHAR(30) NOT NULL  COMMENT '用户角色',
    TrueName VARCHAR(100) COMMENT '真实姓名',
    Department VARCHAR(100) COMMENT '单位部门',
    UPosition VARCHAR(100) COMMENT '职务职位',
    Telephone VARCHAR(100) COMMENT '联系电话',
    Address VARCHAR(200) COMMENT '联系地址',
    UStatus INT COMMENT '用户状态',
    URemark TEXT COMMENT '备注',
	CreatedTime datetime  COMMENT '创建时间',
   UpdatedTime  datetime  COMMENT '更新时间'
) COMMENT='用户信息表';



--- 添加数据（INSERT） -- 示例：添加一条用户记录
INSERT INTO User_Info (UserName, UPassword, URole, TrueName, Department, UPosition, Telephone, Address, UStatus, URemark)
VALUES ('admin', '$2a$10$WkQWcxluJnMyylwc9XRv2eKo5a61GGYKWHkfMkJv7aCpCBnP8tdKy', '工作人员', '管理员', '技术部', '经理', '13800138000', '北京市海淀区', 0, '系统管理员');

INSERT INTO User_Info (UserName, UPassword, URole, TrueName, Department, UPosition, Telephone, Address, UStatus, URemark)
VALUES ('aa', '11', '工作人员', '管理员', '技术部', '经理', '13800138000', '北京市海淀区', 0, '');


--- 修改数据（UPDATE）-- 示例：修改用户ID为1的用户密码和状态
UPDATE User_Info SET UPassword = '654321', UStatus = 2 WHERE UID = 1;
 
--- 删除数据（DELETE）-- 示例：删除用户ID为2的记录
DELETE FROM User_Info WHERE UID <5;

 select * from user_info;
 
 
 -- 弹药数据
select * from Ammunition_Info;

update Ammunition_Info set amstatus=1 where amid>0;


 -- 机场跑道
select * from Runway_Info ;

update Runway_Info set RunwayStatus=1 where RunwayID>0;

 -- 单机掩蔽库
select * from Shelter_Info;

update Shelter_Info set ShelterStatus=1 where ShelterID>0;


 -- 地下指挥所
select * from UCC_Info;

update UCC_Info set UCCStatus=1 where UCCID>0;


-- 毁伤场景设置
select * from damagescene_info;


-- 毁伤参数管理
select * from damageparameter_info;


-- 毁伤能力计算
select * from assessment_result;

-- 毁伤报告
select * from assessment_report;


-- 数据备份
select * from databackup_records;

SELECT * FROM DataBackup_Records ORDER BY BackupTime DESC

