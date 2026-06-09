import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.connection import get_connection


# Projects

def create_project(name: str, color: str = '#4A90D9',
                   pomodoro_enabled: bool = False, afk_enabled: bool = True):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO projects (name, color, pomodoro_enabled, afk_enabled)
                VALUES (%s, %s, %s, %s) RETURNING id
            """, (name, color, pomodoro_enabled, afk_enabled))
            return cur.fetchone()[0]


def get_all_projects():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, color, pomodoro_enabled, afk_enabled
                FROM projects ORDER BY name
            """)
            return cur.fetchall()


def delete_project(project_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM projects WHERE id = %s", (project_id,))


# Processes

def add_process(project_id: int, process_name: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO project_processes (project_id, process_name)
                VALUES (%s, %s)
            """, (project_id, process_name))


def get_processes(project_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT process_name FROM project_processes
                WHERE project_id = %s
            """, (project_id,))
            return [row[0] for row in cur.fetchall()]


def delete_process(project_id: int, process_name: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM project_processes
                WHERE project_id = %s AND process_name = %s
            """, (project_id, process_name))


# Sessions

def start_session(project_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO sessions (project_id, started_at)
                VALUES (%s, NOW()) RETURNING id
            """, (project_id,))
            return cur.fetchone()[0]


def stop_session(session_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE sessions
                SET ended_at = NOW(),
                    duration = EXTRACT(EPOCH FROM (NOW() - started_at))::INTEGER
                WHERE id = %s
            """, (session_id,))


def get_sessions_today():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT s.id, p.name, s.started_at, s.ended_at, s.duration
                FROM sessions s
                JOIN projects p ON s.project_id = p.id
                WHERE s.started_at::DATE = CURRENT_DATE
                ORDER BY s.started_at DESC
            """)
            return cur.fetchall()


def get_stats_by_project(days: int = 7):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.name, p.color, SUM(s.duration) as total_seconds
                FROM sessions s
                JOIN projects p ON s.project_id = p.id
                WHERE s.started_at >= NOW() - INTERVAL '%s days'
                  AND s.duration IS NOT NULL
                GROUP BY p.name, p.color
                ORDER BY total_seconds DESC
            """, (days,))
            return cur.fetchall()


# AFK

def log_afk_start(session_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO afk_events (session_id, afk_start)
                VALUES (%s, NOW()) RETURNING id
            """, (session_id,))
            return cur.fetchone()[0]


def log_afk_end(afk_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE afk_events
                SET afk_end = NOW(),
                    duration = EXTRACT(EPOCH FROM (NOW() - afk_start))::INTEGER
                WHERE id = %s
            """, (afk_id,))