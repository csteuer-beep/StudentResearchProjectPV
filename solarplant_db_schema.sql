-- MySQL dump 10.13  Distrib 8.0.39, for Linux (x86_64)
--
-- Host: localhost    Database: solarplant_db
-- ------------------------------------------------------
-- Server version	8.0.39-0ubuntu0.22.04.1

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
-- Table structure for table `Alerts`
--

DROP TABLE IF EXISTS `Alerts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Alerts` (
  `AlertID` varchar(36) NOT NULL,
  `SensorID` varchar(255) DEFAULT NULL,
  `Timestamp` datetime DEFAULT NULL,
  `AlertType` varchar(255) DEFAULT NULL,
  `AlertMessage` text,
  `AlertStatus` varchar(50) DEFAULT NULL,
  `FirstOccurrenceTimestamp` datetime DEFAULT NULL,
  `LastOccurrenceTimestamp` datetime DEFAULT NULL,
  `Parameter` varchar(10) DEFAULT NULL,
  `CurrentValue` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`AlertID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Facilities`
--

DROP TABLE IF EXISTS `Facilities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Facilities` (
  `id` int NOT NULL AUTO_INCREMENT,
  `inst` varchar(255) NOT NULL,
  `eff_coeff` decimal(10,4) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Solarplant_Ag_Data`
--

DROP TABLE IF EXISTS `Solarplant_Ag_Data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Solarplant_Ag_Data` (
  `EntryID` varchar(255) DEFAULT NULL,
  `Inst` varchar(255) DEFAULT NULL,
  `Year` int DEFAULT NULL,
  `Month` int DEFAULT NULL,
  `SumOfP` int DEFAULT NULL,
  `MeanOfP` int DEFAULT NULL,
  `MinOfP` int DEFAULT NULL,
  `MaxOfP` int DEFAULT NULL,
  `MaxOfTc` int DEFAULT NULL,
  `MinOfTc` int DEFAULT NULL,
  `MeanOfTc` int DEFAULT NULL,
  `MaxOfI` int DEFAULT NULL,
  `MinOfI` int DEFAULT NULL,
  `MeanOfI` int DEFAULT NULL,
  `MaxOfV` int DEFAULT NULL,
  `MinOfV` int DEFAULT NULL,
  `MeanOfV` int DEFAULT NULL,
  `MaxOfG` int DEFAULT NULL,
  `MinOfG` int DEFAULT NULL,
  `MeanOfG` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Solarplant_Raw`
--

DROP TABLE IF EXISTS `Solarplant_Raw`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Solarplant_Raw` (
  `FechaHora` datetime DEFAULT NULL,
  `G` float DEFAULT NULL,
  `Tc` float DEFAULT NULL,
  `I` float DEFAULT NULL,
  `V` float DEFAULT NULL,
  `P` float DEFAULT NULL,
  `Inst` varchar(255) DEFAULT NULL,
  `Performance` float DEFAULT NULL,
  `Loss` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-09-30 20:51:17
