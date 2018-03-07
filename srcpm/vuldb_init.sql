-- MySQL dump 10.13  Distrib 5.6.27, for osx10.8 (x86_64)
--
-- Host: 127.0.0.1    Database: vuldb
-- ------------------------------------------------------
-- Server version	5.7.13

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('974f738bb748');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `assets`
--

DROP TABLE IF EXISTS `assets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `assets` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sysname` varchar(64) DEFAULT NULL,
  `domain` varchar(64) DEFAULT NULL,
  `back_domain` varchar(100) DEFAULT NULL,
  `web_or_int` varchar(64) DEFAULT NULL,
  `is_http` tinyint(1) DEFAULT NULL,
  `is_https` tinyint(1) DEFAULT NULL,
  `in_or_out` varchar(64) DEFAULT NULL,
  `level` varchar(64) DEFAULT NULL,
  `business_cata` varchar(64) DEFAULT NULL,
  `department` varchar(64) DEFAULT NULL,
  `owner` varchar(600) DEFAULT NULL,
  `sec_owner` varchar(600) DEFAULT NULL,
  `status` varchar(64) DEFAULT NULL,
  `chkdate` date DEFAULT NULL,
  `create_date` date DEFAULT NULL,
  `update_date` date DEFAULT NULL,
  `ps` varchar(200) DEFAULT NULL,
  `private_data` text,
  `count_private_data` varchar(100) DEFAULT NULL,
  `down_time` varchar(100) DEFAULT NULL,
  `secure_level` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_assets_domain` (`domain`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assets`
--

LOCK TABLES `assets` WRITE;
/*!40000 ALTER TABLE `assets` DISABLE KEYS */;
/*!40000 ALTER TABLE `assets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categorys`
--

DROP TABLE IF EXISTS `categorys`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `categorys` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `category_name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `category_name` (`category_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categorys`
--

LOCK TABLES `categorys` WRITE;
/*!40000 ALTER TABLE `categorys` DISABLE KEYS */;
/*!40000 ALTER TABLE `categorys` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `comment`
--

DROP TABLE IF EXISTS `comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `comment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comt_id` int(11) DEFAULT NULL,
  `author_name` varchar(50) DEFAULT NULL,
  `author_email` varchar(100) DEFAULT NULL,
  `author_ip` varchar(20) DEFAULT NULL,
  `comment_create_time` datetime DEFAULT NULL,
  `content` text,
  `content_html` text,
  `isvisible` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `comt_id` (`comt_id`),
  CONSTRAINT `comment_ibfk_1` FOREIGN KEY (`comt_id`) REFERENCES `postdrops` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comment`
--

LOCK TABLES `comment` WRITE;
/*!40000 ALTER TABLE `comment` DISABLE KEYS */;
/*!40000 ALTER TABLE `comment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `departs`
--

DROP TABLE IF EXISTS `departs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `departs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `department` varchar(64) DEFAULT NULL,
  `leader` varchar(64) DEFAULT NULL,
  `email` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_departs_department` (`department`),
  KEY `ix_departs_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `departs`
--

LOCK TABLES `departs` WRITE;
/*!40000 ALTER TABLE `departs` DISABLE KEYS */;
/*!40000 ALTER TABLE `departs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `login_users`
--

DROP TABLE IF EXISTS `login_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `login_users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(64) DEFAULT NULL,
  `username` varchar(64) DEFAULT NULL,
  `password_hash` varchar(128) DEFAULT NULL,
  `role_name` varchar(64) DEFAULT NULL,
  `confirmed` tinyint(1) DEFAULT NULL,
  `related_name` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_login_users_email` (`email`),
  UNIQUE KEY `ix_login_users_username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `login_users`
--

LOCK TABLES `login_users` WRITE;
/*!40000 ALTER TABLE `login_users` DISABLE KEYS */;
INSERT INTO `login_users` VALUES (5,'admin@admin.com','admin','pbkdf2:sha1:1000$bLXlzNNn$6f8a286571a361ca99ede2ca3b9163e346f8a3ca','超级管理员',1,NULL);
/*!40000 ALTER TABLE `login_users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permissions`
--

DROP TABLE IF EXISTS `permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `role_name` varchar(64) DEFAULT NULL,
  `have_perm` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permissions`
--

LOCK TABLES `permissions` WRITE;
/*!40000 ALTER TABLE `permissions` DISABLE KEYS */;
INSERT INTO `permissions` VALUES (1,'安全管理员','admin.index'),(2,'安全管理员','admin.depart_add'),(3,'安全管理员','admin.depart_read'),(4,'安全管理员','admin.depart_modify'),(5,'安全管理员','admin.depart_delete'),(6,'安全管理员','admin.user_add'),(7,'安全管理员','admin.user_read'),(8,'安全管理员','admin.user_modify'),(9,'安全管理员','admin.user_delete'),(10,'安全管理员','admin.assets_add'),(11,'安全管理员','admin.assets_add_ajax'),(12,'安全管理员','admin.assets_read'),(13,'安全管理员','admin.assets_modify'),(14,'安全管理员','admin.assets_delete'),(15,'安全管理员','admin.vul_type_add'),(16,'安全管理员','admin.vul_type_read'),(17,'安全管理员','admin.vul_type_modify'),(18,'安全管理员','admin.vul_type_delete'),(19,'安全管理员','src.vul_report_delete'),(20,'安全管理员','src.vul_report_review'),(21,'安全管理员','src.vul_report_review_ajax'),(22,'安全管理员','src.vul_report_send_email'),(23,'安全管理员','src.vul_report_known'),(24,'安全管理员','src.vul_report_dev_finish'),(25,'安全管理员','src.vul_report_vul_cata'),(26,'安全管理员','src.vul_report_attack_check'),(27,'安全管理员','src.vul_report_retest_result'),(28,'安全管理员','src.vul_report_retest_ajax'),(29,'安全管理员','src.vul_report_add'),(30,'安全管理员','src.upload_img'),(31,'安全管理员','src.vul_review_list'),(32,'安全管理员','src.assets_read'),(33,'安全管理员','src.assets_add'),(34,'安全管理员','src.assets_add_ajax'),(35,'安全管理员','src.assets_modify'),(36,'安全管理员','drops.manager'),(37,'安全人员','admin.index'),(38,'安全人员','admin.assets_add'),(39,'安全人员','admin.assets_add_ajax'),(40,'安全人员','admin.assets_read'),(41,'安全人员','admin.assets_modify'),(42,'安全人员','src.vul_report_vul_cata'),(43,'安全人员','src.vul_report_attack_check'),(44,'安全人员','src.vul_report_retest_result'),(45,'安全人员','src.vul_report_retest_ajax'),(46,'安全人员','src.vul_report_add'),(47,'安全人员','src.upload_img'),(48,'安全人员','src.vul_review_list'),(49,'安全人员','src.assets_read'),(50,'安全人员','src.assets_add'),(51,'安全人员','src.assets_add_ajax'),(52,'安全人员','src.assets_modify'),(53,'安全人员','drops.manager'),(54,'普通用户','src.vul_report_known'),(55,'普通用户','src.vul_report_dev_finish'),(56,'普通用户','src.assets_read');
/*!40000 ALTER TABLE `permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `postdrops`
--

DROP TABLE IF EXISTS `postdrops`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `postdrops` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `drop_content` text,
  `drop_content_html` text,
  `drop_title` varchar(50) DEFAULT NULL,
  `drop_name` varchar(50) DEFAULT NULL,
  `drop_create_time` datetime DEFAULT NULL,
  `view_num` int(11) DEFAULT NULL,
  `comment_count` int(11) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `author_id` int(11) DEFAULT NULL,
  `drop_modified_time` datetime DEFAULT NULL,
  `category_id` int(11) DEFAULT NULL,
  `tags_name` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `drop_name` (`drop_name`),
  KEY `author_id` (`author_id`),
  KEY `category_id` (`category_id`),
  CONSTRAINT `postdrops_ibfk_1` FOREIGN KEY (`author_id`) REFERENCES `login_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `postdrops_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `categorys` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `postdrops`
--

LOCK TABLES `postdrops` WRITE;
/*!40000 ALTER TABLE `postdrops` DISABLE KEYS */;
/*!40000 ALTER TABLE `postdrops` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `relationships`
--

DROP TABLE IF EXISTS `relationships`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `relationships` (
  `tag_id` int(11) DEFAULT NULL,
  `postdrop_id` int(11) DEFAULT NULL,
  KEY `postdrop_id` (`postdrop_id`),
  KEY `tag_id` (`tag_id`),
  CONSTRAINT `relationships_ibfk_1` FOREIGN KEY (`postdrop_id`) REFERENCES `postdrops` (`id`),
  CONSTRAINT `relationships_ibfk_2` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `relationships`
--

LOCK TABLES `relationships` WRITE;
/*!40000 ALTER TABLE `relationships` DISABLE KEYS */;
/*!40000 ALTER TABLE `relationships` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `role_name` varchar(64) DEFAULT NULL,
  `default` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `role_name` (`role_name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'安全管理员',0),(2,'安全人员',0),(3,'普通用户',1);
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tags`
--

DROP TABLE IF EXISTS `tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tags` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tags`
--

LOCK TABLES `tags` WRITE;
/*!40000 ALTER TABLE `tags` DISABLE KEYS */;
/*!40000 ALTER TABLE `tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `email` varchar(64) DEFAULT NULL,
  `department` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_email` (`email`),
  KEY `ix_users_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vul_logs`
--

DROP TABLE IF EXISTS `vul_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vul_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `related_vul_id` int(11) DEFAULT NULL,
  `time` datetime DEFAULT NULL,
  `related_user_email` varchar(64) DEFAULT NULL,
  `action` varchar(64) DEFAULT NULL,
  `content` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vul_logs`
--

LOCK TABLES `vul_logs` WRITE;
/*!40000 ALTER TABLE `vul_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `vul_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vul_reports`
--

DROP TABLE IF EXISTS `vul_reports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vul_reports` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `author` varchar(64) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `title` varchar(128) DEFAULT NULL,
  `related_asset` varchar(64) DEFAULT NULL,
  `related_asset_inout` varchar(64) DEFAULT NULL,
  `related_asset_status` varchar(64) DEFAULT NULL,
  `related_vul_cata` varchar(64) DEFAULT NULL,
  `related_vul_type` varchar(64) DEFAULT NULL,
  `vul_self_rank` int(11) DEFAULT NULL,
  `vul_source` varchar(64) DEFAULT NULL,
  `vul_poc` text,
  `vul_poc_html` text,
  `vul_solution` text,
  `vul_solution_html` text,
  `grant_rank` int(11) DEFAULT NULL,
  `vul_type_level` varchar(64) DEFAULT NULL,
  `risk_score` float DEFAULT NULL,
  `person_score` int(11) DEFAULT NULL,
  `done_solution` text,
  `done_rank` int(11) DEFAULT NULL,
  `residual_risk_score` float DEFAULT NULL,
  `vul_status` varchar(64) DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `fix_date` date DEFAULT NULL,
  `attack_check` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_vul_reports_author` (`author`),
  KEY `ix_vul_reports_timestamp` (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vul_reports`
--

LOCK TABLES `vul_reports` WRITE;
/*!40000 ALTER TABLE `vul_reports` DISABLE KEYS */;
/*!40000 ALTER TABLE `vul_reports` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vul_types`
--

DROP TABLE IF EXISTS `vul_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vul_types` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `vul_type` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_vul_types_vul_type` (`vul_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vul_types`
--

LOCK TABLES `vul_types` WRITE;
/*!40000 ALTER TABLE `vul_types` DISABLE KEYS */;
/*!40000 ALTER TABLE `vul_types` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-03-07 15:46:29
