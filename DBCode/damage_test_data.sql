-- ============================================
-- 弹药和打击目标数据库完整脚本
-- 创建时间: 2025-11-05
-- 数据库: DAMAssessment_DB
-- 说明: 包含建表和测试数据插入
-- ============================================

USE DAMAssessment_DB;

-- ============================================
-- 第一部分: 建表语句
-- ============================================

-- ============================================
-- 1. 弹药毁伤数据模型表 (Ammunition_Info)
-- ============================================
DROP TABLE IF EXISTS Ammunition_Info;

CREATE TABLE Ammunition_Info (
    -- 基本信息
    AMID INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
    AMName VARCHAR(100) NOT NULL COMMENT '官方名称',
    AMNameCN VARCHAR(100) COMMENT '中文名称',
    AMAbbreviation VARCHAR(60) COMMENT '简称',
    Country VARCHAR(60) COMMENT '国家/地区',
    Base VARCHAR(60) COMMENT '基地/部队',
    AMType VARCHAR(60) NOT NULL COMMENT '弹药类型',
    AMModel VARCHAR(60) NOT NULL COMMENT '弹药型号',
    AMSubmodel VARCHAR(60) COMMENT '型号子类',
    Manufacturer VARCHAR(60) COMMENT '制造商',
    AttendedDate VARCHAR(60) COMMENT '服役时间',

    -- 物理参数
    AMWeight DECIMAL(10,2) NOT NULL COMMENT '弹体全重(kg)',
    AMLength DECIMAL(10,2) COMMENT '弹体长度(m)',
    AMDiameter DECIMAL(10,2) COMMENT '弹体直径(m)',
    AMTexture VARCHAR(60) COMMENT '弹体材质',
    WingspanClose DECIMAL(10,2) COMMENT '翼展(闭合)(mm)',
    WingspanOpen DECIMAL(10,2) COMMENT '翼展(张开)(mm)',
    AMStructure VARCHAR(60) COMMENT '结构',
    MaxSpeed DECIMAL(10,2) COMMENT '最大时速(Ma)',
    RadarSection VARCHAR(60) COMMENT '雷达截面',
    AMPower VARCHAR(60) COMMENT '动力装置',
    LaunchWeight DECIMAL(10,2) NOT NULL COMMENT '发射质量(kg)',

    -- 战斗部信息
    WarheadType VARCHAR(60) NOT NULL COMMENT '战斗部类型',
    WarheadName VARCHAR(60) NOT NULL COMMENT '战斗部名称',
    Penetrator VARCHAR(60) COMMENT '毁伤元',
    Fuze VARCHAR(60) COMMENT '引信',
    TNTEquivalent DECIMAL(10,2) COMMENT '爆炸当量(TNT吨)',
    CEP DECIMAL(10,2) COMMENT '精度(圆概率误差CEP米)',
    DestroyMechanism VARCHAR(60) COMMENT '破坏机制',
    Targets VARCHAR(60) COMMENT '打击目标',

    -- 投放参数
    Carrier VARCHAR(60) COMMENT '载机(投放平台)',
    GuidanceMode VARCHAR(60) COMMENT '制导方式',
    ChargeAmount DECIMAL(10,2) COMMENT '装药量(kg)',
    PenetratePower VARCHAR(60) COMMENT '穿透能力',
    DropHeight VARCHAR(60) COMMENT '投弹高度范围(m)',
    DropSpeed DECIMAL(10,2) COMMENT '投弹速度(km/h)',
    DropMode VARCHAR(60) COMMENT '投弹方式',
    CoverageArea VARCHAR(60) COMMENT '布撒范围',
    FlightRange DECIMAL(10,2) COMMENT '射程(km)',

    -- 爆破战斗部参数
    IsExplosiveBomb INT NOT NULL DEFAULT 0 COMMENT '爆破战斗部标识(0-否,1-是)',
    EXBComponent VARCHAR(60) COMMENT '炸药成分',
    EXBExplosion DECIMAL(10,2) COMMENT '炸药热爆(kJ/kg)',
    EXBWeight DECIMAL(10,2) COMMENT '装药质量(kg)',
    EXBMoreParameters TEXT COMMENT '爆破弹其他参数(JSON)',

    -- 聚能战斗部参数
    IsEnergyBomb INT NOT NULL DEFAULT 0 COMMENT '聚能战斗部标识(0-否,1-是)',
    EBDensity DECIMAL(10,2) COMMENT '炸药密度(g/cm³)',
    EBVelocity DECIMAL(10,2) COMMENT '装药爆速(m/s)',
    EBPressure DECIMAL(10,2) COMMENT '爆轰压(GPa)',
    EBCoverMaterial VARCHAR(60) COMMENT '药型罩材料',
    EBConeAngle DECIMAL(10,2) COMMENT '药型罩锥角角度(度)',
    EBMoreParameters TEXT COMMENT '聚能弹其他参数(JSON)',

    -- 破片战斗部参数
    IsFragmentBomb INT NOT NULL DEFAULT 0 COMMENT '破片弹战斗部标识(0-否,1-是)',
    FBBombExplosion DECIMAL(10,2) COMMENT '炸弹热爆(kJ/kg)',
    FBFragmentShape TEXT COMMENT '破片形状',
    FBSurfaceArea DECIMAL(10,2) COMMENT '破片表面积(mm²)',
    FBFragmentWeight DECIMAL(10,2) COMMENT '破片质量(g)',
    FBDiameter DECIMAL(10,2) COMMENT '装药直径(mm)',
    FBLength DECIMAL(10,2) COMMENT '装药长度(mm)',
    FBShellWeight DECIMAL(10,2) COMMENT '壳体质量(kg)',
    FBMoreParameters TEXT COMMENT '破片弹其他参数(JSON)',

    -- 穿甲战斗部参数
    IsArmorBomb INT NOT NULL DEFAULT 0 COMMENT '穿甲弹战斗部标识(0-否,1-是)',
    ABBulletWeight DECIMAL(10,2) COMMENT '弹丸质量(kg)',
    ABDiameter DECIMAL(10,2) COMMENT '弹丸直径(mm)',
    ABHeadLength DECIMAL(10,2) COMMENT '弹丸头部长度(mm)',
    ABMoreParameters TEXT COMMENT '穿甲弹其他参数(JSON)',

    -- 子母弹战斗部参数
    IsClusterBomb INT NOT NULL DEFAULT 0 COMMENT '子母弹战斗部标识(0-否,1-是)',
    CBMBulletWeight DECIMAL(10,2) COMMENT '母弹质量(kg)',
    CBMBulletSection DECIMAL(10,2) COMMENT '母弹最大横截面(m²)',
    CBMProjectile DECIMAL(10,2) COMMENT '母弹阻力系数',
    CBSBulletCount DECIMAL(10,2) COMMENT '子弹数量',
    CBSBulletModel VARCHAR(60) COMMENT '子弹型号',
    CBSBulletWeight DECIMAL(10,2) COMMENT '子弹质量(kg)',
    CBDiameter DECIMAL(10,2) COMMENT '最大直径(mm)',
    CBSBulletLength DECIMAL(10,2) COMMENT '子弹参考长度(mm)',
    CBMoreParameters TEXT COMMENT '子母弹其他参数(JSON)',

    -- 状态和时间
    AMStatus INT DEFAULT 1 COMMENT '弹药状态(0-已删除,1-正常)',
    CreatedTime DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间(UTC)',
    UpdatedTime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间(UTC)',

    -- 索引
    INDEX idx_amname (AMName),
    INDEX idx_amtype (AMType),
    INDEX idx_country (Country),
    INDEX idx_status (AMStatus)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='弹药毁伤数据模型表';


-- ============================================
-- 2. 机场跑道表 (Runway_Info)
-- ============================================
DROP TABLE IF EXISTS Runway_Info;

CREATE TABLE Runway_Info (
    RunwayID INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键，自增长',
    RunwayCode VARCHAR(60) NOT NULL UNIQUE COMMENT '机场代码（唯一）',
    RunwayName VARCHAR(60) NOT NULL UNIQUE COMMENT '机场名称（唯一）',
    Country VARCHAR(60) COMMENT '国家/地区',
    Base VARCHAR(60) COMMENT '基地/部队',
    RunwayPicture VARCHAR(90) COMMENT '机场照片路径',

    -- 跑道基本参数
    RLength DECIMAL(10,2) NOT NULL COMMENT '跑道长度(m)',
    RWidth DECIMAL(10,2) NOT NULL COMMENT '跑道宽度(m)',

    -- 混凝土面层参数
    PCCSCThick DECIMAL(10,2) NOT NULL COMMENT '混凝土面层厚度(cm)',
    PCCSCStrength DECIMAL(10,2) COMMENT '混凝土面层抗压强度(MPa)',
    PCCSCFlexural DECIMAL(10,2) COMMENT '混凝土面层抗折强度(MPa)',
    PCCSCFreeze DECIMAL(10,2) COMMENT '抗冻融循环次数',
    PCCSCCement VARCHAR(60) COMMENT '水泥类型',
    PCCSCBlockSize1 DECIMAL(10,2) COMMENT '道面分块尺寸1(m)',
    PCCSCBlockSize2 DECIMAL(10,2) COMMENT '道面分块尺寸2(m)',

    -- 水泥稳定碎石基层参数
    CTBCThick DECIMAL(10,2) NOT NULL COMMENT '水泥稳定碎石基层厚度(cm)',
    CTBCStrength DECIMAL(10,2) COMMENT '水泥稳定碎石基层抗压强度(MPa)',
    CTBCFlexural DECIMAL(10,2) COMMENT '水泥稳定碎石基层抗折强度(MPa)',
    CTBCCement DECIMAL(10,2) COMMENT '水泥掺量(%)',
    CTBCCompaction DECIMAL(10,2) COMMENT '夯实密实度(%)',

    -- 级配砂砾石垫层参数
    GCSSThick DECIMAL(10,2) NOT NULL COMMENT '级配砂砾石垫层厚度(cm)',
    GCSSStrength DECIMAL(10,2) COMMENT '级配砂砾石垫层强度承载比(%)',
    GCSSCompaction DECIMAL(10,2) COMMENT '级配砂砾石垫层压实模量(MPa)',

    -- 土基压实层参数
    CSThick DECIMAL(10,2) NOT NULL COMMENT '土基压实层强度厚度(cm)',
    CSStrength DECIMAL(10,2) COMMENT '土基压实层强度承载比(%)',
    CSCompaction DECIMAL(10,2) COMMENT '土基压实层压实模量(MPa)',

    -- 状态和时间
    RunwayStatus INT DEFAULT 1 COMMENT '跑道状态(0-已删除,1-正常)',
    CreatedTime DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UpdatedTime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 索引
    INDEX idx_runway_code (RunwayCode),
    INDEX idx_country (Country),
    INDEX idx_status (RunwayStatus)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='机场跑道数据表';


-- ============================================
-- 3. 单机掩蔽库表 (Shelter_Info)
-- ============================================
DROP TABLE IF EXISTS Shelter_Info;

CREATE TABLE Shelter_Info (
    ShelterID INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID,自增长',
    ShelterCode VARCHAR(60) NOT NULL UNIQUE COMMENT '掩蔽库代码（唯一）',
    ShelterName VARCHAR(60) NOT NULL UNIQUE COMMENT '掩蔽库名称（唯一）',
    Country VARCHAR(60) COMMENT '国家/地区',
    Base VARCHAR(60) COMMENT '基地/部队',
    ShelterPicture VARCHAR(90) COMMENT '掩蔽库照片路径',

    -- 库容参数
    ShelterWidth DECIMAL(10,2) NOT NULL COMMENT '库容净宽(m)',
    ShelterHeight DECIMAL(10,2) NOT NULL COMMENT '库容净高(m)',
    ShelterLength DECIMAL(10,2) NOT NULL COMMENT '库容净长(m)',
    CaveWidth DECIMAL(10,2) COMMENT '洞门宽度(m)',
    CaveHeight DECIMAL(10,2) COMMENT '洞门高度(m)',

    -- 结构参数
    StructuralForm VARCHAR(60) COMMENT '结构形式',
    DoorMaterial VARCHAR(60) COMMENT '门体材料',
    DoorThick DECIMAL(10,2) COMMENT '门体厚度(cm)',

    -- 防护层参数
    MaskLayerMaterial VARCHAR(60) NOT NULL COMMENT '伪装层材料',
    MaskLayerThick DECIMAL(10,2) NOT NULL COMMENT '伪装层厚度(cm)',
    SoilLayerMaterial VARCHAR(60) NOT NULL COMMENT '遮弹层材料',
    SoilLayerThick DECIMAL(10,2) NOT NULL COMMENT '遮弹层厚度(cm)',
    DisperLayerMaterial VARCHAR(60) NOT NULL COMMENT '分散层材料',
    DisperLayerThick DECIMAL(10,2) NOT NULL COMMENT '分散层厚度(cm)',
    DisperLayerReinforcement VARCHAR(60) COMMENT '分散层钢筋配置',
    StructureLayerMaterial VARCHAR(60) NOT NULL COMMENT '结构层材料',
    StructureLayerThick DECIMAL(10,2) NOT NULL COMMENT '结构层厚度(cm)',
    StructureLayerReinforcement VARCHAR(60) COMMENT '结构层钢筋配置',

    -- 防护能力参数
    ExplosionResistance DECIMAL(10,2) COMMENT '抗爆能力(MPa)',
    AntiKinetic DECIMAL(10,2) COMMENT '抗动能穿透(m/s)',
    ResistanceDepth DECIMAL(10,2) COMMENT '抗穿透深度(m)',
    NuclearBlast DECIMAL(10,2) COMMENT '抗核冲波超压(MPa)',
    RadiationShielding DECIMAL(10,2) COMMENT '抗辐射屏蔽(Sv)',
    FireResistance DECIMAL(10,2) COMMENT '耐火极限(h)',

    -- 状态和时间
    ShelterStatus INT DEFAULT 1 COMMENT '掩蔽库状态(0-已删除,1-正常)',
    CreatedTime DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间(UTC)',
    UpdatedTime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间(UTC)',

    -- 索引
    INDEX idx_shelter_code (ShelterCode),
    INDEX idx_country (Country),
    INDEX idx_status (ShelterStatus)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='单机掩蔽库数据表';


-- ============================================
-- 4. 地下指挥所表 (UCC_Info)
-- ============================================
DROP TABLE IF EXISTS UCC_Info;

CREATE TABLE UCC_Info (
    UCCID INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID,自增长',
    UCCCode VARCHAR(60) NOT NULL UNIQUE COMMENT '指挥所代码（唯一）',
    UCCName VARCHAR(60) NOT NULL UNIQUE COMMENT '指挥所名称（唯一）',
    Country VARCHAR(60) COMMENT '国家/地区',
    Base VARCHAR(60) COMMENT '基地/部队',
    ShelterPicture VARCHAR(90) COMMENT '指挥所照片路径',
    Location VARCHAR(60) COMMENT '所在位置',

    -- 岩层参数
    RockLayerMaterials VARCHAR(60) NOT NULL COMMENT '土壤岩层材料',
    RockLayerThick DECIMAL(10,2) NOT NULL COMMENT '土壤岩层厚度(m)',
    RockLayerStrength DECIMAL(10,2) COMMENT '土壤岩层抗压强度(MPa)',

    -- 防护层参数
    ProtectiveLayerMaterial VARCHAR(60) NOT NULL COMMENT '防护层材料',
    ProtectiveLayerThick DECIMAL(10,2) NOT NULL COMMENT '防护层厚度(m)',
    ProtectiveLayerStrength DECIMAL(10,2) COMMENT '防护层抗压强度(MPa)',

    -- 衬砌层参数
    LiningLayerMaterial VARCHAR(60) NOT NULL COMMENT '衬砌层材料',
    LiningLayerThick DECIMAL(10,2) NOT NULL COMMENT '衬砌层厚度(m)',
    LiningLayerStrength DECIMAL(10,2) COMMENT '衬砌层抗压强度(MPa)',

    -- 指挥中心墙壁参数
    UCCWallMaterials VARCHAR(60) NOT NULL COMMENT '指挥中心墙壁材料',
    UCCWallThick DECIMAL(10,2) COMMENT '指挥中心墙壁厚度(m)',
    UCCWallStrength DECIMAL(10,2) COMMENT '指挥中心墙壁抗压强度(MPa)',

    -- 指挥中心尺寸
    UCCWidth DECIMAL(10,2) COMMENT '指挥中心宽度(m)',
    UCCLength DECIMAL(10,2) COMMENT '指挥中心长度(m)',
    UCCHeight DECIMAL(10,2) COMMENT '指挥中心高度(m)',

    -- 状态和时间
    UCCStatus INT DEFAULT 1 COMMENT '指挥所状态(0-已删除,1-正常)',
    CreatedTime DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UpdatedTime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 索引
    INDEX idx_ucc_code (UCCCode),
    INDEX idx_country (Country),
    INDEX idx_status (UCCStatus)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='地下指挥所数据表';


-- ============================================
-- 5. 毁伤场景表 (DamageScene_Info)
-- ============================================
DROP TABLE IF EXISTS DamageScene_Info;

CREATE TABLE DamageScene_Info (
    DSID INT AUTO_INCREMENT PRIMARY KEY COMMENT '场景ID，主键，自增',
    DSCode VARCHAR(60) NOT NULL UNIQUE COMMENT '场景编号（唯一）',
    DSName VARCHAR(60) NOT NULL UNIQUE COMMENT '场景名称（唯一）',
    DSOffensive VARCHAR(60) COMMENT '进攻方',
    DSDefensive VARCHAR(60) COMMENT '假想敌',
    DSBattle VARCHAR(60) COMMENT '所在战场',

    -- 弹药信息
    AMID INT NOT NULL COMMENT '弹药ID',
    AMCode VARCHAR(60) NOT NULL COMMENT '弹药代码',

    -- 目标信息
    TargetType INT NOT NULL COMMENT '打击目标类型(1-机场跑道,2-单机掩蔽库,3-地下指挥所)',
    TargetID INT NOT NULL COMMENT '打击目标ID',
    TargetCode VARCHAR(60) NOT NULL COMMENT '打击目标代码',

    -- 状态信息
    DSStatus INT DEFAULT 1 COMMENT '场景状态(0-草稿,1-活跃,2-归档)',
    CreatedTime DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UpdatedTime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 索引
    INDEX idx_dscode (DSCode),
    INDEX idx_amid (AMID),
    INDEX idx_target (TargetType, TargetID),
    INDEX idx_status (DSStatus)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='毁伤场景信息表';


-- ============================================
-- 6. 毁伤参数表 (DamageParameter_Info)
-- ============================================
DROP TABLE IF EXISTS DamageParameter_Info;

CREATE TABLE DamageParameter_Info (
    DPID INT AUTO_INCREMENT PRIMARY KEY COMMENT '参数ID，主键，自增',

    -- 场景关联
    DSID INT NOT NULL COMMENT '场景ID',
    DSCode VARCHAR(60) NOT NULL COMMENT '场景编号',

    -- 基本参数
    Carrier VARCHAR(60) COMMENT '投放平台',
    GuidanceMode VARCHAR(60) COMMENT '制导方式',
    WarheadType VARCHAR(60) NOT NULL COMMENT '战斗部类型',
    ChargeAmount DECIMAL(10,2) COMMENT '装药量(kg)',

    -- 投放参数
    DropHeight DECIMAL(10,2) COMMENT '投弹高度(m)',
    DropSpeed DECIMAL(10,2) COMMENT '投弹速度(m/s)',
    DropMode VARCHAR(60) COMMENT '投弹方式',
    FlightRange DECIMAL(10,2) COMMENT '射程(km)',

    -- 环境参数
    ElectroInterference VARCHAR(60) COMMENT '电磁干扰等级',
    WeatherConditions VARCHAR(60) COMMENT '天气状况',
    WindSpeed DECIMAL(10,2) COMMENT '环境风速(m/s)',

    -- 状态信息
    DPStatus INT DEFAULT 0 COMMENT '参数状态(0-草稿,1-验证通过,2-已使用)',
    CreatedTime DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UpdatedTime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 索引
    INDEX idx_dsid (DSID),
    INDEX idx_dscode (DSCode),
    INDEX idx_status (DPStatus)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='毁伤参数信息表';


-- ============================================
-- 7. 毁伤效能计算评估表 (Assessment_Result)
-- ============================================
DROP TABLE IF EXISTS Assessment_Result;

CREATE TABLE Assessment_Result (
    DAID INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID，自增',

    -- 关联信息
    DSID INT NOT NULL COMMENT '场景ID',
    DPID INT NOT NULL COMMENT '参数ID',
    AMID INT NOT NULL COMMENT '弹药ID',
    TargetType INT NOT NULL COMMENT '打击目标类型(1-机场跑道,2-单机掩蔽库,3-地下指挥所)',
    TargetID INT NOT NULL COMMENT '打击目标ID',

    -- 弹坑参数
    DADepth DECIMAL(10,2) COMMENT '弹坑深度(m)',
    DADiameter DECIMAL(10,2) COMMENT '弹坑直径(m)',
    DAVolume DECIMAL(10,2) COMMENT '弹坑容积(m³)',
    DAArea DECIMAL(10,2) COMMENT '弹坑面积(m²)',
    DALength DECIMAL(10,2) COMMENT '弹坑长度(m)',
    DAWidth DECIMAL(10,2) COMMENT '弹坑宽度(m)',

    -- 毁伤评估
    Discturction DECIMAL(10,2) COMMENT '结构破坏程度(0-1)',
    DamageDegree VARCHAR(60) COMMENT '毁伤等级',

    -- 时间信息
    CreatedTime DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UpdatedTime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 索引
    INDEX idx_dsid (DSID),
    INDEX idx_dpid (DPID),
    INDEX idx_amid (AMID),
    INDEX idx_target (TargetType, TargetID),
    INDEX idx_damage_degree (DamageDegree)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='毁伤效能计算评估表';


-- ============================================
-- 8. 毁伤评估报告表 (Assessment_Report)
-- ============================================
DROP TABLE IF EXISTS Assessment_Report;

CREATE TABLE Assessment_Report (
    ReportID INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID，自增',

    -- 报告基本信息
    ReportCode VARCHAR(60) NOT NULL UNIQUE COMMENT '报告编号（唯一）',
    ReportName VARCHAR(60) NOT NULL COMMENT '报告名称',

    -- 关联信息
    DAID INT NOT NULL COMMENT '毁伤评估ID',
    DSID INT COMMENT '毁伤场景ID',
    DPID INT COMMENT '毁伤参数ID',
    AMID INT COMMENT '弹药数据ID',
    TargetType INT NOT NULL COMMENT '打击目标类型(1-机场跑道,2-单机掩蔽库,3-地下指挥所)',
    TargetID INT COMMENT '打击目标ID',

    -- 评估结果
    DamageDegree VARCHAR(60) COMMENT '毁伤等级',
    Comment TEXT COMMENT '评估结论',

    -- 报告人员信息
    Creator INT COMMENT '报告操作人员ID',
    Reviewer VARCHAR(60) COMMENT '报告审核人',

    -- 时间信息
    CreatedTime DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UpdatedTime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 索引
    INDEX idx_report_code (ReportCode),
    INDEX idx_daid (DAID),
    INDEX idx_dsid (DSID),
    INDEX idx_target (TargetType, TargetID),
    INDEX idx_creator (Creator)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='毁伤评估报告表';


-- ============================================
-- 第二部分: 测试数据插入
-- ============================================

-- ============================================
-- 1. 弹药毁伤数据模型表 测试数据
-- ============================================

-- 插入第1条: GBU-28钻地炸弹
INSERT INTO Ammunition_Info (
    AMName, AMNameCN, AMAbbreviation, Country, Base, AMType, AMModel, AMSubmodel,
    Manufacturer, AttendedDate, AMWeight, AMLength, AMDiameter, AMTexture,
    WingspanClose, WingspanOpen, AMStructure, MaxSpeed, RadarSection, AMPower,
    LaunchWeight, WarheadType, WarheadName, Penetrator, Fuze, TNTEquivalent,
    CEP, DestroyMechanism, Targets, Carrier, GuidanceMode, ChargeAmount,
    PenetratePower, DropHeight, DropSpeed, DropMode, CoverageArea, FlightRange,
    IsExplosiveBomb, EXBComponent, EXBExplosion, EXBWeight, EXBMoreParameters,
    IsEnergyBomb, EBDensity, EBVelocity, EBPressure, EBCoverMaterial, EBConeAngle, EBMoreParameters,
    IsFragmentBomb, FBBombExplosion, FBFragmentShape, FBSurfaceArea, FBFragmentWeight,
    FBDiameter, FBLength, FBShellWeight, FBMoreParameters,
    IsArmorBomb, ABBulletWeight, ABDiameter, ABHeadLength, ABMoreParameters,
    IsClusterBomb, CBMBulletWeight, CBMBulletSection, CBMProjectile, CBSBulletCount,
    CBSBulletModel, CBSBulletWeight, CBDiameter, CBSBulletLength, CBMoreParameters,
    AMStatus
) VALUES (
    'GBU-28 Bunker Buster', 'GBU-28钻地炸弹', 'GBU-28', '美国', '美国空军',
    '钻地弹', 'GBU-28', 'BLU-113/B', '雷神公司', '1991年',
    2268.0, 5.84, 0.368, '合金钢', NULL, NULL, '整体式弹体',
    0.85, '小型', '无动力', 2268.0, '钻地爆破战斗部', 'BLU-113',
    '动能穿透+延时爆破', 'FMU-143/B延时引信', 0.295, 3.0,
    '动能穿透后爆破', '地下掩体、指挥所', 'F-15E、B-2轰炸机',
    'GPS/INS制导', 295.0, '穿透6米钢筋混凝土', '10000-12000',
    800.0, '水平投弹', NULL, 20.0,
    1, 'Tritonal', 4520.0, 295.0, '{"penetration_depth": "6m reinforced concrete", "delay_time": "variable"}',
    0, NULL, NULL, NULL, NULL, NULL, NULL,
    0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    1, 2268.0, 368.0, 1200.0, '{"nose_shape": "conical", "material": "hardened_steel"}',
    0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    1
);

-- 插入第2条: AGM-158 JASSM巡航导弹
INSERT INTO Ammunition_Info (
    AMName, AMNameCN, AMAbbreviation, Country, Base, AMType, AMModel, AMSubmodel,
    Manufacturer, AttendedDate, AMWeight, AMLength, AMDiameter, AMTexture,
    WingspanClose, WingspanOpen, AMStructure, MaxSpeed, RadarSection, AMPower,
    LaunchWeight, WarheadType, WarheadName, Penetrator, Fuze, TNTEquivalent,
    CEP, DestroyMechanism, Targets, Carrier, GuidanceMode, ChargeAmount,
    PenetratePower, DropHeight, DropSpeed, DropMode, CoverageArea, FlightRange,
    IsExplosiveBomb, EXBComponent, EXBExplosion, EXBWeight, EXBMoreParameters,
    IsEnergyBomb, EBDensity, EBVelocity, EBPressure, EBCoverMaterial, EBConeAngle, EBMoreParameters,
    IsFragmentBomb, FBBombExplosion, FBFragmentShape, FBSurfaceArea, FBFragmentWeight,
    FBDiameter, FBLength, FBShellWeight, FBMoreParameters,
    IsArmorBomb, ABBulletWeight, ABDiameter, ABHeadLength, ABMoreParameters,
    IsClusterBomb, CBMBulletWeight, CBMBulletSection, CBMProjectile, CBSBulletCount,
    CBSBulletModel, CBSBulletWeight, CBDiameter, CBSBulletLength, CBMoreParameters,
    AMStatus
) VALUES (
    'AGM-158 JASSM', 'AGM-158联合防区外空对地导弹', 'JASSM', '美国', '美国空军',
    '巡航导弹', 'AGM-158', 'JASSM-ER', '洛克希德·马丁', '2003年',
    1021.0, 4.27, 0.610, '复合材料', 600.0, 2400.0, '隐身设计',
    0.85, '0.01m²', '涡轮喷气发动机', 1021.0, '爆破战斗部', 'WDU-42/B',
    '爆破破坏', '多模引信', 0.450, 3.0, '精确打击+爆破',
    '机场、指挥所、雷达站', 'F-16、F-15、B-1B', 'GPS/INS+红外成像',
    450.0, '一般穿透能力', '0-15000', 900.0, '空射巡航',
    NULL, 980.0,
    1, 'AFX-757', 4200.0, 450.0, '{"stealth": true, "range_extended": "ER version 1000km"}',
    0, NULL, NULL, NULL, NULL, NULL, NULL,
    0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    0, NULL, NULL, NULL, NULL,
    0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    1
);


-- ============================================
-- 2. 机场跑道表 测试数据
-- ============================================

-- 插入第1条: 某东部战区机场跑道
INSERT INTO Runway_Info (
    RunwayCode, RunwayName, Country, Base, RunwayPicture,
    RLength, RWidth,
    PCCSCThick, PCCSCStrength, PCCSCFlexural, PCCSCFreeze, PCCSCCement,
    PCCSCBlockSize1, PCCSCBlockSize2,
    CTBCThick, CTBCStrength, CTBCFlexural, CTBCCement, CTBCCompaction,
    GCSSThick, GCSSStrength, GCSSCompaction,
    CSThick, CSStrength, CSCompaction,
    RunwayStatus
) VALUES (
    'RW_EAST_001', '东部战区某军用机场主跑道', '中国', '东部战区空军基地',
    '/images/runways/rw_east_001.jpg',
    3200.0, 50.0,
    40.0, 45.0, 5.5, 300.0, 'P.O 42.5级',
    6.0, 6.0,
    35.0, 8.0, 1.2, 5.0, 97.0,
    30.0, 80.0, 180.0,
    150.0, 8.0, 50.0,
    1
);

-- 插入第2条: 某南部战区机场跑道
INSERT INTO Runway_Info (
    RunwayCode, RunwayName, Country, Base, RunwayPicture,
    RLength, RWidth,
    PCCSCThick, PCCSCStrength, PCCSCFlexural, PCCSCFreeze, PCCSCCement,
    PCCSCBlockSize1, PCCSCBlockSize2,
    CTBCThick, CTBCStrength, CTBCFlexural, CTBCCement, CTBCCompaction,
    GCSSThick, GCSSStrength, GCSSCompaction,
    CSThick, CSStrength, CSCompaction,
    RunwayStatus
) VALUES (
    'RW_SOUTH_001', '南部战区某海军航空兵基地跑道', '中国', '南部战区海军航空兵',
    '/images/runways/rw_south_001.jpg',
    3500.0, 60.0,
    45.0, 50.0, 6.0, 350.0, 'P.O 52.5级',
    6.0, 6.0,
    40.0, 9.0, 1.5, 6.0, 98.0,
    35.0, 85.0, 200.0,
    180.0, 10.0, 60.0,
    1
);


-- ============================================
-- 3. 单机掩蔽库表 测试数据
-- ============================================

-- 插入第1条: 标准单机掩蔽库
INSERT INTO Shelter_Info (
    ShelterCode, ShelterName, Country, Base, ShelterPicture,
    ShelterWidth, ShelterHeight, ShelterLength, CaveWidth, CaveHeight,
    StructuralForm, DoorMaterial, DoorThick,
    MaskLayerMaterial, MaskLayerThick, SoilLayerMaterial, SoilLayerThick,
    DisperLayerMaterial, DisperLayerThick, DisperLayerReinforcement,
    StructureLayerMaterial, StructureLayerThick, StructureLayerReinforcement,
    ExplosionResistance, AntiKinetic, ResistanceDepth, NuclearBlast,
    RadiationShielding, FireResistance,
    ShelterStatus
) VALUES (
    'SH_TYPE_A_001', 'A型标准单机掩蔽库01', '中国', '某空军基地',
    '/images/shelters/sh_a_001.jpg',
    18.0, 8.0, 25.0, 12.0, 6.0,
    '钢筋混凝土拱形结构', '高强度钢板', 25.0,
    '土壤+植被', 50.0, '砂土+碎石', 120.0,
    'C40钢筋混凝土', 80.0, 'Φ16@200双层双向',
    'C50钢筋混凝土', 100.0, 'Φ20@150双层双向',
    2.5, 500.0, 3.0, 0.5,
    100.0, 3.0,
    1
);

-- 插入第2条: 加固型单机掩蔽库
INSERT INTO Shelter_Info (
    ShelterCode, ShelterName, Country, Base, ShelterPicture,
    ShelterWidth, ShelterHeight, ShelterLength, CaveWidth, CaveHeight,
    StructuralForm, DoorMaterial, DoorThick,
    MaskLayerMaterial, MaskLayerThick, SoilLayerMaterial, SoilLayerThick,
    DisperLayerMaterial, DisperLayerThick, DisperLayerReinforcement,
    StructureLayerMaterial, StructureLayerThick, StructureLayerReinforcement,
    ExplosionResistance, AntiKinetic, ResistanceDepth, NuclearBlast,
    RadiationShielding, FireResistance,
    ShelterStatus
) VALUES (
    'SH_TYPE_B_001', 'B型加固单机掩蔽库01', '中国', '某战略空军基地',
    '/images/shelters/sh_b_001.jpg',
    20.0, 10.0, 30.0, 14.0, 7.0,
    '预应力钢筋混凝土拱形', '装甲钢板+复合材料', 35.0,
    '土壤+伪装网', 80.0, '砂土+碎石+粘土', 150.0,
    'C50钢筋混凝土', 120.0, 'Φ18@150双层双向+预应力钢筋',
    'C60钢筋混凝土', 150.0, 'Φ25@120双层双向+钢板加固',
    4.0, 800.0, 5.0, 1.0,
    200.0, 4.0,
    1
);


-- ============================================
-- 4. 地下指挥所表 测试数据
-- ============================================

-- 插入第1条: 战区级地下指挥所
INSERT INTO UCC_Info (
    UCCCode, UCCName, Country, Base, ShelterPicture, Location,
    RockLayerMaterials, RockLayerThick, RockLayerStrength,
    ProtectiveLayerMaterial, ProtectiveLayerThick, ProtectiveLayerStrength,
    LiningLayerMaterial, LiningLayerThick, LiningLayerStrength,
    UCCWallMaterials, UCCWallThick, UCCWallStrength,
    UCCWidth, UCCLength, UCCHeight,
    UCCStatus
) VALUES (
    'UCC_EAST_001', '东部战区地下联合作战指挥中心', '中国', '东部战区',
    '/images/ucc/ucc_east_001.jpg', '某山区地下50米',
    '花岗岩', 15.0, 120.0,
    'C60钢筋混凝土+钢板', 3.0, 60.0,
    'C50钢筋混凝土', 1.5, 50.0,
    'C40钢筋混凝土+防辐射材料', 1.2, 40.0,
    25.0, 60.0, 6.0,
    1
);

-- 插入第2条: 军级地下指挥所
INSERT INTO UCC_Info (
    UCCCode, UCCName, Country, Base, ShelterPicture, Location,
    RockLayerMaterials, RockLayerThick, RockLayerStrength,
    ProtectiveLayerMaterial, ProtectiveLayerThick, ProtectiveLayerStrength,
    LiningLayerMaterial, LiningLayerThick, LiningLayerStrength,
    UCCWallMaterials, UCCWallThick, UCCWallStrength,
    UCCWidth, UCCLength, UCCHeight,
    UCCStatus
) VALUES (
    'UCC_SOUTH_001', '南部战区某集团军地下指挥所', '中国', '南部战区某集团军',
    '/images/ucc/ucc_south_001.jpg', '某丘陵地下30米',
    '石灰岩', 12.0, 80.0,
    'C50钢筋混凝土', 2.5, 50.0,
    'C40钢筋混凝土', 1.2, 40.0,
    'C35钢筋混凝土', 1.0, 35.0,
    18.0, 45.0, 5.0,
    1
);


-- ============================================
-- 5. 毁伤场景表 测试数据
-- ============================================

-- 插入第1条: 机场跑道打击场景
INSERT INTO DamageScene_Info (
    DSCode, DSName, DSOffensive, DSDefensive, DSBattle,
    AMID, AMCode, TargetType, TargetID, TargetCode,
    DSStatus
) VALUES (
    'DS_RUNWAY_001', '东部战区机场跑道打击场景01', '我方空军', '敌方空军',
    '东部海域作战区',
    1, 'GBU-28', 1, 1, 'RW_EAST_001',
    1
);

-- 插入第2条: 地下指挥所打击场景
INSERT INTO DamageScene_Info (
    DSCode, DSName, DSOffensive, DSDefensive, DSBattle,
    AMID, AMCode, TargetType, TargetID, TargetCode,
    DSStatus
) VALUES (
    'DS_UCC_001', '敌方地下指挥所毁伤场景01', '我方战略打击力量', '敌方指挥体系',
    '战略纵深打击',
    1, 'GBU-28', 3, 1, 'UCC_EAST_001',
    1
);


-- ============================================
-- 6. 毁伤参数表 测试数据
-- ============================================

-- 插入第1条: 跑道打击参数
INSERT INTO DamageParameter_Info (
    DSID, DSCode, Carrier, GuidanceMode, WarheadType, ChargeAmount,
    DropHeight, DropSpeed, DropMode, FlightRange,
    ElectroInterference, WeatherConditions, WindSpeed,
    DPStatus
) VALUES (
    1, 'DS_RUNWAY_001', 'F-15E战斗轰炸机', 'GPS/INS制导', '钻地爆破战斗部', 295.0,
    10000.0, 800.0, '水平投弹', 20.0,
    '低', '晴', 5.0,
    1
);

-- 插入第2条: 地下指挥所打击参数
INSERT INTO DamageParameter_Info (
    DSID, DSCode, Carrier, GuidanceMode, WarheadType, ChargeAmount,
    DropHeight, DropSpeed, DropMode, FlightRange,
    ElectroInterference, WeatherConditions, WindSpeed,
    DPStatus
) VALUES (
    2, 'DS_UCC_001', 'B-2隐身轰炸机', 'GPS/INS+惯导', '钻地爆破战斗部', 295.0,
    12000.0, 850.0, '精确投弹', 1000.0,
    '中', '多云', 8.0,
    1
);


-- ============================================
-- 7. 毁伤效能计算评估表 测试数据
-- ============================================

-- 插入第1条: 跑道打击毁伤评估结果
INSERT INTO Assessment_Result (
    DSID, DPID, AMID, TargetType, TargetID,
    DADepth, DADiameter, DAVolume, DAArea, DALength, DAWidth,
    Discturction, DamageDegree
) VALUES (
    1, 1, 1, 1, 1,
    2.8, 6.5, 45.3, 33.2, 8.0, 5.2,
    0.85, '重度毁伤'
);

-- 插入第2条: 地下指挥所打击毁伤评估结果
INSERT INTO Assessment_Result (
    DSID, DPID, AMID, TargetType, TargetID,
    DADepth, DADiameter, DAVolume, DAArea, DALength, DAWidth,
    Discturction, DamageDegree
) VALUES (
    2, 2, 1, 3, 1,
    4.5, 8.0, 120.5, 50.3, 10.0, 8.0,
    0.92, '完全摧毁'
);


-- ============================================
-- 8. 毁伤评估报告表 测试数据
-- ============================================

-- 插入第1条: 跑道毁伤评估报告
INSERT INTO Assessment_Report (
    ReportCode, ReportName, DAID, DSID, DPID, AMID,
    TargetType, TargetID, DamageDegree, Comment,
    Creator, Reviewer
) VALUES (
    'RPT_RUNWAY_20251106_001',
    '东部战区机场跑道GBU-28打击毁伤评估报告',
    1, 1, 1, 1,
    1, 1, '重度毁伤',
    '根据GBU-28钻地炸弹对东部战区机场主跑道的打击效能计算，弹坑深度2.8米，直径6.5米，造成跑道结构破坏程度达85%。评估结果为重度毁伤，预计修复时间超过72小时，严重影响敌方航空作战能力。建议后续持续打击以巩固毁伤效果。',
    1, '李参谋长'
);

-- 插入第2条: 地下指挥所毁伤评估报告
INSERT INTO Assessment_Report (
    ReportCode, ReportName, DAID, DSID, DPID, AMID,
    TargetType, TargetID, DamageDegree, Comment,
    Creator, Reviewer
) VALUES (
    'RPT_UCC_20251106_001',
    '敌方地下联合作战指挥中心毁伤评估报告',
    2, 2, 2, 1,
    3, 1, '完全摧毁',
    '采用B-2隐身轰炸机投放GBU-28钻地炸弹，对敌方东部战区地下联合作战指挥中心实施精确打击。弹坑深度达4.5米，穿透岩层和防护层，直接命中指挥中心主体结构。结构破坏程度达92%，评估为完全摧毁。敌方指挥体系已基本瘫痪，作战指挥能力丧失，战役目标达成。',
    1, '张副司令员'
);


-- ============================================
-- 数据验证
-- ============================================

-- 验证插入的数据
SELECT '弹药数据统计' AS '表名', COUNT(*) AS '记录数' FROM Ammunition
UNION ALL
SELECT '机场跑道数据统计', COUNT(*) FROM Runway_Info
UNION ALL
SELECT '单机掩蔽库数据统计', COUNT(*) FROM Shelter_Info
UNION ALL
SELECT '地下指挥所数据统计', COUNT(*) FROM UCC_Info
UNION ALL
SELECT '毁伤场景数据统计', COUNT(*) FROM DamageScene_Info
UNION ALL
SELECT '毁伤参数数据统计', COUNT(*) FROM DamageParameter_Info
UNION ALL
SELECT '毁伤结果数据统计', COUNT(*) FROM Assessment_Result
UNION ALL
SELECT '毁伤评估报告数据统计', COUNT(*) FROM Assessment_Report;

-- ============================================
-- 脚本执行完成
-- ============================================

