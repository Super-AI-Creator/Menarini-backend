/*
 Navicat MySQL Dump SQL

 Source Server         : connection
 Source Server Type    : MySQL
 Source Server Version : 100432 (10.4.32-MariaDB)
 Source Host           : localhost:3306
 Source Schema         : menarini

 Target Server Type    : MySQL
 Target Server Version : 100432 (10.4.32-MariaDB)
 File Encoding         : 65001

 Date: 06/05/2025 22:46:12
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for admin_table
-- ----------------------------
DROP TABLE IF EXISTS `admin_table`;
CREATE TABLE `admin_table`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `domain` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `password` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `role` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `imap_server` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of admin_table
-- ----------------------------
INSERT INTO `admin_table` VALUES (1, 'robertedyoung@gmail.com', 'RO', 'reva gpan ieaa eujj', '2', 'imap.gmail.com');
INSERT INTO `admin_table` VALUES (2, 'test@arkinno-ai.com', 'RO', 'test123!@#', '1', 'arkinno-ai.com');

-- ----------------------------
-- Table structure for attachment_table
-- ----------------------------
DROP TABLE IF EXISTS `attachment_table`;
CREATE TABLE `attachment_table`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `supplier` char(120) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `DN#` char(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `DN` tinyint(1) NULL DEFAULT 0,
  `INV` tinyint(1) NULL DEFAULT 0,
  `Bill of Lading` tinyint(1) NULL DEFAULT 0,
  `Air Waybill` tinyint(1) NULL DEFAULT 0,
  `COA` tinyint(1) NULL DEFAULT 0,
  `complete` tinyint(1) NULL DEFAULT 0,
  `Supplier ID` char(120) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Item Count` int NULL DEFAULT 0,
  `COA Count` int NULL DEFAULT 0,
  `admin_email` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `date` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `final_complete` int NULL DEFAULT 0,
  `date_format` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `incoterms` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 565 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of attachment_table
-- ----------------------------

-- ----------------------------
-- Table structure for bol_table
-- ----------------------------
DROP TABLE IF EXISTS `bol_table`;
CREATE TABLE `bol_table`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `DN#` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Incoterms` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Posting Date` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Document` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 81 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of bol_table
-- ----------------------------

-- ----------------------------
-- Table structure for coa_table
-- ----------------------------
DROP TABLE IF EXISTS `coa_table`;
CREATE TABLE `coa_table`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `DN#` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Item Description` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Manufacturing Date` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Expiry Date` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Document` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Batch#` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `flag` int NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 120 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of coa_table
-- ----------------------------

-- ----------------------------
-- Table structure for dn_table
-- ----------------------------
DROP TABLE IF EXISTS `dn_table`;
CREATE TABLE `dn_table`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `DN#` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `PO#` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Item Code` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Packing Slip#` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Quantity` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Batch#` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Manufacturing Date` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Expiry Date` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Document Date` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Incoterms` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Item Description` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Document` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `percent` float NULL DEFAULT 0.1,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 260 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of dn_table
-- ----------------------------

-- ----------------------------
-- Table structure for domain_table
-- ----------------------------
DROP TABLE IF EXISTS `domain_table`;
CREATE TABLE `domain_table`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `domain` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `country` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 18 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of domain_table
-- ----------------------------
INSERT INTO `domain_table` VALUES (1, 'AU82', 'AU');
INSERT INTO `domain_table` VALUES (2, 'C307', 'CN');
INSERT INTO `domain_table` VALUES (3, 'C335', 'CN');
INSERT INTO `domain_table` VALUES (4, 'H92H', 'HK');
INSERT INTO `domain_table` VALUES (5, 'ID30', 'ID');
INSERT INTO `domain_table` VALUES (6, 'ID32', 'ID');
INSERT INTO `domain_table` VALUES (7, 'IN82', 'IN');
INSERT INTO `domain_table` VALUES (8, 'KR82', 'KR');
INSERT INTO `domain_table` VALUES (9, 'N334', 'NZ');
INSERT INTO `domain_table` VALUES (10, 'PH91', 'PH');
INSERT INTO `domain_table` VALUES (11, 'S304', 'AMAPH');
INSERT INTO `domain_table` VALUES (12, 'S302', 'AMAPP');
INSERT INTO `domain_table` VALUES (13, 'S93M', 'MY');
INSERT INTO `domain_table` VALUES (14, 'S93S', 'SG');
INSERT INTO `domain_table` VALUES (15, 'S93T', 'TW');
INSERT INTO `domain_table` VALUES (16, 'TH91', 'TH');
INSERT INTO `domain_table` VALUES (17, 'VN93', 'VN');

-- ----------------------------
-- Table structure for duplicated_attachment
-- ----------------------------
DROP TABLE IF EXISTS `duplicated_attachment`;
CREATE TABLE `duplicated_attachment`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `DN#` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `doc_type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `source` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `drive_file_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 205 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of duplicated_attachment
-- ----------------------------

-- ----------------------------
-- Table structure for email_attachment
-- ----------------------------
DROP TABLE IF EXISTS `email_attachment`;
CREATE TABLE `email_attachment`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `email_id` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `DN#` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `DN` int NULL DEFAULT NULL,
  `INV` int NULL DEFAULT NULL,
  `COA` int NULL DEFAULT NULL,
  `Bill of Lading` int NULL DEFAULT NULL,
  `Air Waybill` int NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 333 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of email_attachment
-- ----------------------------

-- ----------------------------
-- Table structure for email_check
-- ----------------------------
DROP TABLE IF EXISTS `email_check`;
CREATE TABLE `email_check`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `email_id` char(100) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `new_flag` tinyint(1) NULL DEFAULT 0,
  `extra` char(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `DN#` char(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `sender` char(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `subject` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `body` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `attachments` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `admin_email` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `date` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1459 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of email_check
-- ----------------------------

-- ----------------------------
-- Table structure for email_domain
-- ----------------------------
DROP TABLE IF EXISTS `email_domain`;
CREATE TABLE `email_domain`  (
  `id` int NOT NULL,
  `domain` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `vendor_domain` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `vendor_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of email_domain
-- ----------------------------
INSERT INTO `email_domain` VALUES (1, 'kki.com', 'S304', 'Kyowa Kirin International Limited Services');
INSERT INTO `email_domain` VALUES (2, 'pardiag.com', 'S93T', 'PHARDIAG LTD');
INSERT INTO `email_domain` VALUES (3, 'thg.sg', 'abc', 'Tabernacle');
INSERT INTO `email_domain` VALUES (4, 'menariniapac.com', 'Men', 'Menarini');

-- ----------------------------
-- Table structure for email_error_table
-- ----------------------------
DROP TABLE IF EXISTS `email_error_table`;
CREATE TABLE `email_error_table`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `email_id` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `error` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `type` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `DN#` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 843 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of email_error_table
-- ----------------------------

-- ----------------------------
-- Table structure for error_table
-- ----------------------------
DROP TABLE IF EXISTS `error_table`;
CREATE TABLE `error_table`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `message` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `DN#` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `email_id` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `attachment_error` int NULL DEFAULT NULL,
  `reference` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 56 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of error_table
-- ----------------------------

-- ----------------------------
-- Table structure for google_drive_change
-- ----------------------------
DROP TABLE IF EXISTS `google_drive_change`;
CREATE TABLE `google_drive_change`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `supplier_domain` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `supplier_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `dn` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 151 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of google_drive_change
-- ----------------------------

-- ----------------------------
-- Table structure for inv_table
-- ----------------------------
DROP TABLE IF EXISTS `inv_table`;
CREATE TABLE `inv_table`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `DN#` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `PO#` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Packing Slip#` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Quantity` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Batch#` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Manufacturing Date` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Item Code` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Expiry Date` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Document Date` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `INV NO#` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Incoterms` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Item Description` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Document` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 134 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of inv_table
-- ----------------------------

-- ----------------------------
-- Table structure for logo_table
-- ----------------------------
DROP TABLE IF EXISTS `logo_table`;
CREATE TABLE `logo_table`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `email_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `logo` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `img` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `DN#` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 251 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of logo_table
-- ----------------------------

-- ----------------------------
-- Table structure for logsheet
-- ----------------------------
DROP TABLE IF EXISTS `logsheet`;
CREATE TABLE `logsheet`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `log` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `email` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `color` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `date` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `detail` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 246 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of logsheet
-- ----------------------------

-- ----------------------------
-- Table structure for multi_doc_intervention
-- ----------------------------
DROP TABLE IF EXISTS `multi_doc_intervention`;
CREATE TABLE `multi_doc_intervention`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `email_id` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `vendor_id` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `DN#` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `doc_list` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `file_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 32 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of multi_doc_intervention
-- ----------------------------

-- ----------------------------
-- Table structure for notification_table
-- ----------------------------
DROP TABLE IF EXISTS `notification_table`;
CREATE TABLE `notification_table`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `header` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `message` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `key` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `date` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 47 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of notification_table
-- ----------------------------

-- ----------------------------
-- Table structure for ocr_table
-- ----------------------------
DROP TABLE IF EXISTS `ocr_table`;
CREATE TABLE `ocr_table`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `DN#` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `doc_type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `page` int NULL DEFAULT NULL,
  `page_width` double NULL DEFAULT NULL,
  `page_height` double NULL DEFAULT NULL,
  `pdf_path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `index` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `key` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `x` double NULL DEFAULT NULL,
  `y` double NULL DEFAULT NULL,
  `width` double NULL DEFAULT NULL,
  `height` double NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 964 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of ocr_table
-- ----------------------------

-- ----------------------------
-- Table structure for po_list
-- ----------------------------
DROP TABLE IF EXISTS `po_list`;
CREATE TABLE `po_list`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `Entity Code` char(150) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `PO Number` char(150) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Menarini PO` int NULL DEFAULT NULL,
  `Item Code` char(150) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Item Name` char(150) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Open PO Quantity` int NULL DEFAULT NULL,
  `Unit Price` decimal(10, 0) NULL DEFAULT NULL,
  `Packing Slip` char(150) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Invoice No` char(150) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Posting Date` date NULL DEFAULT NULL,
  `Shipped Quantity` int NULL DEFAULT NULL,
  `Batch Number` char(150) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Manufacturing Date` date NULL DEFAULT NULL,
  `Expiry Date` date NULL DEFAULT NULL,
  `Vendor Code` char(150) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Vendor` char(150) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Incoterms` char(150) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Document Date` date NULL DEFAULT NULL,
  `Prepare By` char(150) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of po_list
-- ----------------------------

-- ----------------------------
-- Table structure for staging_table
-- ----------------------------
DROP TABLE IF EXISTS `staging_table`;
CREATE TABLE `staging_table`  (
  `id` int NOT NULL,
  `PO#` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of staging_table
-- ----------------------------

-- ----------------------------
-- Table structure for supplier_name_intervention
-- ----------------------------
DROP TABLE IF EXISTS `supplier_name_intervention`;
CREATE TABLE `supplier_name_intervention`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `email_id` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `vendor_id` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `DN#` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 28 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of supplier_name_intervention
-- ----------------------------

-- ----------------------------
-- Table structure for supplier_table
-- ----------------------------
DROP TABLE IF EXISTS `supplier_table`;
CREATE TABLE `supplier_table`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `domain` char(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `vendor_account` char(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `vendor_name` char(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `currency` char(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `group` char(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 75 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of supplier_table
-- ----------------------------
INSERT INTO `supplier_table` VALUES (2, 'S304', 'SUP0009643', 'FINE FOODS E PHARMACEUTICALS NTMSPA', 'EUR', 'TRTP');
INSERT INTO `supplier_table` VALUES (3, 'S302', 'SUP0009643', 'FINE FOODS E PHARMACEUTICALS NTMSPA', 'EUR', 'TRTP');
INSERT INTO `supplier_table` VALUES (4, 's304', 'SUP0010515', 'A. MENARINI PHARM. IRELAND LTD', 'EUR', 'TRRC');
INSERT INTO `supplier_table` VALUES (5, 'S93T', 'SUP0011819', 'PHARDIAG LTD.', 'EUR', 'TRRC');
INSERT INTO `supplier_table` VALUES (6, 'S302', 'SUP0049856', 'RELIFE S.r.l.', 'EUR', 'TRRC');
INSERT INTO `supplier_table` VALUES (7, 'kr82', 'SUP0065299', 'AMDIPHARM LIMITED', 'KRW', 'TRTP');
INSERT INTO `supplier_table` VALUES (8, 'VN93', 'SUP0065300', 'GE Healthcare AS', 'USD', 'TRTP');
INSERT INTO `supplier_table` VALUES (9, 'id32', 'SUP0065491', 'GRANT INDUSTRIES INC.', 'USD', 'TRTP');
INSERT INTO `supplier_table` VALUES (10, 'id32', 'SUP0065493', 'MEGACHEM LIMITED', 'USD', 'TRTP');
INSERT INTO `supplier_table` VALUES (11, 'S302', 'SUP0069242', 'PT. MENARINI INDRIA LABORATORIES', 'IDR', 'TRFS');
INSERT INTO `supplier_table` VALUES (12, 's304', 'SUP0070245', 'PHARMACOSMOS A/S', 'EUR', 'TRTP');
INSERT INTO `supplier_table` VALUES (13, 'au82', 'SUP0070245', 'PHARMACOSMOS A/S', 'EUR', 'TRTP');
INSERT INTO `supplier_table` VALUES (14, 'id32', 'SUP0070759', 'PT. INTILAND MANDIRI KEMASINDO', 'IDR', 'TRTP');
INSERT INTO `supplier_table` VALUES (15, 'id32', 'SUP0071075', 'TASTEPOINT BY IFF', 'USD', 'TRTP');
INSERT INTO `supplier_table` VALUES (16, 'au82', 'SUP0071100', 'Sandoz AG', 'EUR', 'TRTP');
INSERT INTO `supplier_table` VALUES (17, 'id32', 'SUP0071288', 'PT CIPTA PERKASA TUNGGAL', 'IDR', 'TRTP');
INSERT INTO `supplier_table` VALUES (18, 'id32', 'SUP0071754', 'MEDA MANUFACTURING, a Viatris Company', 'EUR', 'TRTP');
INSERT INTO `supplier_table` VALUES (19, 'id32', 'SUP0072066', 'PT DIBLESTARI DJAUHARI', 'IDR', 'TRTP');
INSERT INTO `supplier_table` VALUES (20, 'id32', 'SUP0072200', 'PT SINERGI MULTI LESTARINDO', 'IDR', 'TRTP');
INSERT INTO `supplier_table` VALUES (21, 'S304', 'SUP0076612', 'Kyowa Kirin International UK NewCo Ltd', 'EUR', 'TRTP');
INSERT INTO `supplier_table` VALUES (26, 'S93T', 'SUP0072123', 'F.I.S. - FABBRICA ITALIANA SINTETICI S.p.A.', 'EUR', 'TRTP');
INSERT INTO `supplier_table` VALUES (64, 'AU82', 'SUP0072066', 'ZUELLIG PHARMA PTE LTD', 'EUR', 'TRTP');
INSERT INTO `supplier_table` VALUES (65, 'AU82', 'SUP0070759', 'ZUELLIG PHARMA VIETNAM LTD', 'EUR', 'TRTP');
INSERT INTO `supplier_table` VALUES (66, 'AU82', 'SUP0070759', 'F.I.S. - FABBRICA ITALIANA SINTETICI S.p.A.', 'IDR', 'TRTP');
INSERT INTO `supplier_table` VALUES (67, 'RO', 'SUP0065299', 'ZUELLIG PHARMA VIETNAM LTD', 'IDR', 'TRTP');
INSERT INTO `supplier_table` VALUES (68, 'RO', 'SUP0065493', 'ZUELLIG PHARMA PTE LTD', 'USD', 'TRTP');
INSERT INTO `supplier_table` VALUES (69, 'RO', 'SUP0010515', 'BERLIN-CHEMIE AG', 'USD', 'TRTP');
INSERT INTO `supplier_table` VALUES (73, 'RO', NULL, 'MENARINI AUSTRALIA PTY LTD', NULL, NULL);
INSERT INTO `supplier_table` VALUES (74, 'RO', NULL, 'ZUBELLIG PHARMA VIETNAM LTD', NULL, NULL);

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` char(120) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `username` char(80) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `password` char(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `domain` char(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `role` int NULL DEFAULT NULL,
  `gmail_password` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `admin_email` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 26 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of user
-- ----------------------------
INSERT INTO `user` VALUES (7, 'robertedyoung@gmail.com', 'Admin', 'scrypt:32768:8:1$QJjm7TTEtrwHCVD5$3c81763261d53c2da21634edb716d1c6e07678658f7ac2134a97db14bf7920320446065294e366ae416294ffe96a48bc88e67bca053997253be1fda8c257f58f', 'AU82', 1, 'reva gpan ieaa eujj', 'robertedyoung@gmail.com');
INSERT INTO `user` VALUES (8, 'venusdev42@gmail.com', 'supplier', 'scrypt:32768:8:1$PJHOwpusQxPVMWcR$23d6d5e37b85e9ae08a5a8697063d501322a4dca7c888cb8868fdd86652b654336f086d6969249d5a6a4c93f868a872c4bf4840c597d213a2f9f66f6689d664f', 'RO', 2, 'arxy nebl rodd xnbq', NULL);
INSERT INTO `user` VALUES (18, 'jc3247329@gmail.com', 'JohnCena', 'scrypt:32768:8:1$pj7YZski7HWw4wNy$62f215719c670401479132597b0979dd4182e2c60c95012ab9cc433f4753f82f6c99cfbd29ba3d7b63f05d38a34e02cba810d05c78af2a2ce25c7575fe72480c', 'AU82', 2, '123456', NULL);
INSERT INTO `user` VALUES (19, 'joshua.freeman.passion@gmail.com', 'JoshuaFreeman', NULL, 'AU82', 2, NULL, NULL);
INSERT INTO `user` VALUES (20, 'test@arkinno-ai.com', 'SupperAdmin', 'scrypt:32768:8:1$BIbwEKYuTf02WBjr$9812ae94b4fa5c4ac24a2ca9e0be215a5ca29185a3952dd48377cae19ac994296ad2df43b1598fe7dc334bfac2e251b9f01978d2f91630d5a68c690e95077b6a', 'RO', 1, 'zvte afst rhpy hcls', 'robertedyoung@gmail.com');
INSERT INTO `user` VALUES (21, 'Cynthia.chong@menariniapac.com', 'Cynthia.chong', 'scrypt:32768:8:1$1jRWp9HZ77TtujqF$caae1399e35f72678bfa8e8507203f5afa6a45e6df0949810bb09f44f295094c6be85932b223a6035e8ef3364677979a6f66f781cc5f1e31342845d85cdc2edf', 'RO', 1, NULL, 'test@arkinno-ai.com');
INSERT INTO `user` VALUES (22, 'eve.ong@menariniapac.com', 'Eve Ong', 'scrypt:32768:8:1$BIbwEKYuTf02WBjr$9812ae94b4fa5c4ac24a2ca9e0be215a5ca29185a3952dd48377cae19ac994296ad2df43b1598fe7dc334bfac2e251b9f01978d2f91630d5a68c690e95077b6a', 'RO', 1, NULL, 'test@arkinno-ai.com');
INSERT INTO `user` VALUES (23, 'zec.h@arkinno-ai.com Zec Cheng', 'Zec H', 'scrypt:32768:8:1$BIbwEKYuTf02WBjr$9812ae94b4fa5c4ac24a2ca9e0be215a5ca29185a3952dd48377cae19ac994296ad2df43b1598fe7dc334bfac2e251b9f01978d2f91630d5a68c690e95077b6a', 'RO', 1, NULL, 'test@arkinno-ai.com');
INSERT INTO `user` VALUES (24, 'hadi.g@arkinno-ai.com', 'Hadi G', 'scrypt:32768:8:1$BIbwEKYuTf02WBjr$9812ae94b4fa5c4ac24a2ca9e0be215a5ca29185a3952dd48377cae19ac994296ad2df43b1598fe7dc334bfac2e251b9f01978d2f91630d5a68c690e95077b6a', 'RO', 1, NULL, 'robertedyoung@gmail.com');
INSERT INTO `user` VALUES (25, 'founder@thg.sg', 'Founder', 'scrypt:32768:8:1$BIbwEKYuTf02WBjr$9812ae94b4fa5c4ac24a2ca9e0be215a5ca29185a3952dd48377cae19ac994296ad2df43b1598fe7dc334bfac2e251b9f01978d2f91630d5a68c690e95077b6a', 'RO', 1, NULL, 'robertedyoung@gmail.com');

SET FOREIGN_KEY_CHECKS = 1;
