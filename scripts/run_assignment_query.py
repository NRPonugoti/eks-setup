#!/usr/bin/env python3
"""
Automated script to run the tbassignment query against Oracle.
Target: Oracle 8.x, WebLogic 8.x environments.
Uses oracledb in Thick mode (Oracle Client) for Oracle 8.x compatibility.
Configure database in db_config.ini (copy from db_config.ini.example).
"""

import configparser
import csv
import sys
from pathlib import Path

try:
    import oracledb
except ImportError:
    print("Install oracledb: pip install oracledb")
    sys.exit(1)

# Default config path (same folder as script)
SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "db_config.ini"


def init_thick_mode(config):
    """Enable Thick mode for Oracle 8.x (and 9/10/11). Required when DB is older than 12.1."""
    section = config["oracle"]
    lib_dir = (section.get("oracle_client_path") or "").strip()
    if lib_dir:
        oracledb.init_oracle_client(lib_dir=lib_dir)
    else:
        # Rely on PATH (Windows) or LD_LIBRARY_PATH / ORACLE_HOME (e.g. WebLogic server box)
        oracledb.init_oracle_client()


def load_config():
    if not CONFIG_PATH.exists():
        print(f"Config not found: {CONFIG_PATH}")
        print("Copy db_config.ini.example to db_config.ini and set your database details.")
        sys.exit(1)
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config


def get_connection(config):
    section = config["oracle"]
    host = section.get("host")
    port = int(section.get("port", 1521))
    user = section.get("user")
    password = section.get("password")
    service_name = section.get("service_name")
    sid = section.get("sid")

    if not all([host, user, password]):
        print("Set host, user, and password in db_config.ini")
        sys.exit(1)
    if not service_name and not sid:
        print("Set either service_name or sid in db_config.ini")
        sys.exit(1)

    if service_name:
        dsn = oracledb.makedsn(host, port, service_name=service_name)
    else:
        dsn = oracledb.makedsn(host, port, sid=sid)

    return oracledb.connect(user=user, password=password, dsn=dsn)


def get_query(config):
    section = config["oracle"]
    date_from = section.get("date_from", "01-NOV-25")
    date_to = section.get("date_to", "30-DEC-25")

    return """
    SELECT /*+ parallel (a,12) */ a.step_instance_id
    FROM tbassignment a
    WHERE a.activity_category = 'AU'
      AND a.state = 'AC'
      AND a.form_id = 'TSAActivities.acActValidationOfCompWork'
      AND a.is_exception = '1'
      AND a.order_action_id IS NOT NULL
      AND a.ctdb_cre_datetime BETWEEN :date_from AND :date_to
    """, {"date_from": date_from, "date_to": date_to}


def main():
    config = load_config()
    init_thick_mode(config)
    conn = get_connection(config)
    query, params = get_query(config)

    output_csv = SCRIPT_DIR / "assignment_results.csv"

    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        columns = [d[0] for d in cursor.description]

        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)

        print(f"Query completed. Rows: {len(rows)}")
        print(f"Output: {output_csv}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
