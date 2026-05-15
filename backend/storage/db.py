import sqlite3
import json
import os
from pathlib import Path
from typing import List, Dict, Any

DB_PATH = Path("output/history.db")

def init_db():
    """Initialize the SQLite database."""
    os.makedirs(DB_PATH.parent, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        tools_used TEXT NOT NULL,
        total_domains INTEGER DEFAULT 0,
        alive_domains INTEGER DEFAULT 0,
        status TEXT NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scan_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_id INTEGER,
        domain TEXT NOT NULL,
        sources TEXT,
        is_alive BOOLEAN,
        status_code INTEGER,
        title TEXT,
        ip TEXT,
        webserver TEXT,
        FOREIGN KEY (scan_id) REFERENCES scans (id) ON DELETE CASCADE
    )
    ''')
    
    conn.commit()
    conn.close()

def save_scan(target: str, tools: List[str], status: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO scans (target, tools_used, status) VALUES (?, ?, ?)",
        (target, json.dumps(tools), status)
    )
    scan_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return scan_id

def update_scan_status(scan_id: int, status: str, total: int = 0, alive: int = 0):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE scans SET status = ?, total_domains = ?, alive_domains = ? WHERE id = ?",
        (status, total, alive, scan_id)
    )
    conn.commit()
    conn.close()

def save_scan_results(scan_id: int, results: List[Dict[str, Any]]):
    if not results:
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    data = [
        (
            scan_id,
            r["domain"],
            json.dumps(r.get("sources", [])),
            r.get("is_alive"),
            r.get("status_code"),
            r.get("title"),
            r.get("ip"),
            r.get("webserver")
        )
        for r in results
    ]
    
    cursor.executemany('''
    INSERT INTO scan_results 
    (scan_id, domain, sources, is_alive, status_code, title, ip, webserver)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', data)
    
    conn.commit()
    conn.close()

def get_history() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
    
def get_scan_results(scan_id: int) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scan_results WHERE scan_id = ?", (scan_id,))
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        r = dict(row)
        if r["sources"]:
            r["sources"] = json.loads(r["sources"])
        results.append(r)
    return results
