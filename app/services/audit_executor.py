import psycopg2
import psycopg2.extensions

def execute_audit_script(dbname, user, password, host, port, script_path):
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    with open(script_path, 'r') as f:
        sql = f.read()
        cur.execute(sql)

    notices = conn.notices
    cur.close()
    conn.close()
    return notices
