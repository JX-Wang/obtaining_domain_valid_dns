-- MySQL dump 10.13  Distrib 5.5.62, for debian-linux-gnu (x86_64)
--
-- Host: 127.0.0.1    Database: domain_valid_dns
-- ------------------------------------------------------
-- Server version	5.7.10-log

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
-- Table structure for table `domain_tld`
--

DROP TABLE IF EXISTS `domain_tld`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `domain_tld` (
  `tld` varchar(255) CHARACTER SET utf8mb4 NOT NULL,
  `domain_num` int(11) DEFAULT NULL,
  `insert_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`tld`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='focused_domain中域名的顶级域名';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `domain_valid_ns`
--

DROP TABLE IF EXISTS `domain_valid_ns`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `domain_valid_ns` (
  `domain` varchar(255) CHARACTER SET utf8mb4 NOT NULL,
  `domain_ns` varchar(700) CHARACTER SET utf8mb4 DEFAULT NULL,
  `ns_md5` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL,
  `tld_ns` varchar(700) CHARACTER SET utf8mb4 DEFAULT NULL,
  `ns_ns` varchar(700) CHARACTER SET utf8mb4 DEFAULT NULL,
  `unknown_ns` varchar(700) CHARACTER SET utf8mb4 DEFAULT NULL,
  `invalid_ns` varchar(700) CHARACTER SET utf8mb4 DEFAULT NULL,
  `verify_strategy` int(10) DEFAULT NULL,
  `task_id` varchar(100) DEFAULT NULL,
  `insert_time` datetime DEFAULT NULL,
  PRIMARY KEY (`domain`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_AUTO_VALUE_ON_ZERO,STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `update2insert` BEFORE UPDATE ON `domain_valid_ns` FOR EACH ROW begin
 insert into domain_valid_ns_history (domain,ns_md5,domain_ns,tld_ns,ns_ns,invalid_ns,unknown_ns,insert_time,task_id,verify_strategy) values (old.domain,old.ns_md5,old.domain_ns,old.tld_ns,old.ns_ns,old.invalid_ns,old.unknown_ns,old.insert_time,old.task_id,old.verify_strategy);
end */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `domain_valid_ns_history`
--

DROP TABLE IF EXISTS `domain_valid_ns_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `domain_valid_ns_history` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `domain` varchar(255) CHARACTER SET utf8mb4 NOT NULL,
  `domain_ns` varchar(700) CHARACTER SET utf8mb4 DEFAULT NULL,
  `ns_md5` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL,
  `tld_ns` varchar(700) CHARACTER SET utf8mb4 DEFAULT NULL,
  `ns_ns` varchar(700) CHARACTER SET utf8mb4 DEFAULT NULL,
  `unknown_ns` varchar(700) CHARACTER SET utf8mb4 DEFAULT NULL,
  `invalid_ns` varchar(700) CHARACTER SET utf8mb4 DEFAULT NULL,
  `verify_strategy` int(10) DEFAULT NULL,
  `task_id` varchar(100) DEFAULT NULL,
  `insert_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=86046 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_AUTO_VALUE_ON_ZERO,STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `update2insert_copy1` BEFORE UPDATE ON `domain_valid_ns_history` FOR EACH ROW begin
 insert into domain_valid_ns_history (domain,ns_md5,domain_ns,tld_ns,ns_ns,invalid_ns,unknown_ns,was_insert_time) values (old.domain,old.ns_md5,old.domain_ns,old.tld_ns,old.ns_ns,old.invalid_ns,old.unknown_ns,old.insert_time);
end */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `domain_valid_ns_periodic`
--

DROP TABLE IF EXISTS `domain_valid_ns_periodic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `domain_valid_ns_periodic` (
  `domain` varchar(255) CHARACTER SET utf8mb4 NOT NULL,
  `domain_ns` varchar(700) CHARACTER SET utf8mb4 DEFAULT NULL,
  `ns_md5` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL,
  `tld_ns` varchar(700) CHARACTER SET utf8mb4 DEFAULT NULL,
  `ns_ns` varchar(700) CHARACTER SET utf8mb4 DEFAULT NULL,
  `unknown_ns` varchar(700) CHARACTER SET utf8mb4 DEFAULT NULL,
  `invalid_ns` varchar(700) CHARACTER SET utf8mb4 DEFAULT NULL,
  `verify_strategy` int(10) DEFAULT NULL,
  `task_id` varchar(100) DEFAULT NULL,
  `insert_time` datetime DEFAULT NULL,
  PRIMARY KEY (`domain`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_AUTO_VALUE_ON_ZERO,STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `update2insert_copy2` BEFORE UPDATE ON `domain_valid_ns_periodic` FOR EACH ROW begin
 insert into domain_valid_ns_periodic_history (domain,ns_md5,domain_ns,tld_ns,ns_ns,invalid_ns,unknown_ns,insert_time,task_id,verify_strategy) values (old.domain,old.ns_md5,old.domain_ns,old.tld_ns,old.ns_ns,old.invalid_ns,old.unknown_ns,old.insert_time,old.task_id,old.verify_strategy);
end */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `domain_valid_ns_periodic_history`
--

DROP TABLE IF EXISTS `domain_valid_ns_periodic_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `domain_valid_ns_periodic_history` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `domain` varchar(255) CHARACTER SET utf8mb4 NOT NULL,
  `domain_ns` varchar(700) CHARACTER SET utf8mb4 DEFAULT NULL,
  `ns_md5` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL,
  `tld_ns` varchar(700) CHARACTER SET utf8mb4 DEFAULT NULL,
  `ns_ns` varchar(700) CHARACTER SET utf8mb4 DEFAULT NULL,
  `unknown_ns` varchar(700) CHARACTER SET utf8mb4 DEFAULT NULL,
  `invalid_ns` varchar(700) CHARACTER SET utf8mb4 DEFAULT NULL,
  `verify_strategy` int(10) DEFAULT NULL,
  `task_id` varchar(100) DEFAULT NULL,
  `insert_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=230692 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_AUTO_VALUE_ON_ZERO,STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `update2insert_copy1_copy1` BEFORE UPDATE ON `domain_valid_ns_periodic_history` FOR EACH ROW begin
 insert into domain_valid_ns_history (domain,ns_md5,domain_ns,tld_ns,ns_ns,invalid_ns,unknown_ns,was_insert_time) values (old.domain,old.ns_md5,old.domain_ns,old.tld_ns,old.ns_ns,old.invalid_ns,old.unknown_ns,old.insert_time);
end */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `focused_domain`
--

DROP TABLE IF EXISTS `focused_domain`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `focused_domain` (
  `domain` varchar(255) CHARACTER SET utf8mb4 NOT NULL,
  `insert_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`domain`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `root_server`
--

DROP TABLE IF EXISTS `root_server`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `root_server` (
  `server_name` varchar(255) CHARACTER SET utf8mb4 NOT NULL,
  `server_ipv4` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL,
  `server_ipv6` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL,
  `insert_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`server_name`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tld_ns_root`
--

DROP TABLE IF EXISTS `tld_ns_root`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tld_ns_root` (
  `tld` varchar(255) CHARACTER SET utf8mb4 NOT NULL,
  `root_name` varchar(255) CHARACTER SET utf8mb4 NOT NULL,
  `server_name` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL,
  `server_ipv4` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL,
  `server_ipv6` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL,
  `tld_status` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL,
  `insert_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`tld`,`root_name`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tld_ns_zone`
--

DROP TABLE IF EXISTS `tld_ns_zone`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tld_ns_zone` (
  `tld` varchar(255) CHARACTER SET utf8mb4 NOT NULL,
  `server_name` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL,
  `server_ipv4` varchar(700) CHARACTER SET utf8mb4 DEFAULT NULL,
  `server_ipv6` varchar(700) CHARACTER SET utf8mb4 DEFAULT NULL,
  `insert_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`tld`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tld_server`
--

DROP TABLE IF EXISTS `tld_server`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tld_server` (
  `tld` varchar(255) CHARACTER SET utf8mb4 NOT NULL,
  `server_name` varchar(255) CHARACTER SET utf8mb4 NOT NULL,
  `server_ipv4` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL,
  `server_ipv6` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL,
  `insert_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`tld`,`server_name`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-07-02 10:47:21
