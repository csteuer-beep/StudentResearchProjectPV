# StudentResearchProjectPV

A student research/study project for photovoltaic (PV) data collection, aggregation, monitoring, and visualization.

## Overview
This project implements a full data pipeline for PV systems, including ingestion via MQTT, raw and aggregated data storage in MySQL, alarm detection, alerting, and real-time web visualization via WebSockets. Grafana dashboards provide insights at both global and operator-specific levels.

## Components & File Descriptions

### Python Modules
-  mqtt_handler.py  – Handles MQTT subscription and incoming data dispatch.  
-  mysql_module.py  – Manages MySQL database interactions.  
-  main_saveraw.py  – Captures and saves raw PV data to the database.  
-  main_month_agg.py  – Creates monthly aggregated summaries.  
-  main_alarms.py  – Detects alarms based on data thresholds.  
-  alerting_module.py  – Formats and dispatches alerts.  
-  websocket_handler.py ,  websocket_server.py  – Provide real-time web interface via WebSockets.

### Shell Scripts
-  startup_mains.sh  – Launches all core services and modules.  
-  stop_mains.sh  – Stops all services gracefully.

### Dashboards
-  grafana_global_view_dashboard  – Grafana dashboard presenting overall system metrics.  
-  grafana_operator_view_dashboard  – Dashboard focused on operator-level detail.

### Miscellaneous
-  .idea/  – IDE-specific configurations (JetBrains). Not essential for project execution.

## Usage Instructions

1. Configure connection parameters for MQTT and MySQL (e.g., in config files or environment variables).  
2. Run `startup_mains.sh` to start all services.  
3. Monitor Grafana dashboards for real-time and historical insight.  
4. Receive alerts as configured when anomalies are detected.  
5. Use `stop_mains.sh` to halt all services cleanly.

## Project Context
This repository supports a student research project aimed at developing a comprehensive PV system monitoring and alerting solution. It demonstrates integration across IoT data ingestion, backend storage, analytics, real-time communication, and visualization tools.

