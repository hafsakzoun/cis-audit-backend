-- === Rule PGSQL_9 ===  -- 3.1.6 Ensure the log file permissions are set correctly (Automated)
-- 3.1.6 Ensure the log file permissions are set correctly (Automated)

DO $$
DECLARE
    current_mode TEXT;
    expected_mode TEXT := '0600';
BEGIN
    SELECT setting INTO current_mode
    FROM pg_settings
    WHERE name = 'log_file_mode';

    IF current_mode = expected_mode THEN
        RAISE NOTICE 'Control 3.1.6 Ensure the log file permissions are set correctly (Automated): PASS - log_file_mode is set to %', current_mode;
    ELSE
        RAISE NOTICE 'Control 3.1.6 Ensure the log file permissions are set correctly (Automated): FAIL - log_file_mode is set to %, expected: %', current_mode, expected_mode;
    END IF;
END
$$;


-- === Rule PGSQL_10 ===  -- 3.1.7 Ensure 'log_truncate_on_rotation' is enabled (Automated)
-- 3.1.7 Ensure 'log_truncate_on_rotation' is enabled (Automated)

DO $$
DECLARE
    current_setting TEXT;
    expected_setting TEXT := 'on';
BEGIN
    SELECT setting INTO current_setting
    FROM pg_settings
    WHERE name = 'log_truncate_on_rotation';
    IF current_setting = expected_setting THEN
        RAISE NOTICE 'Control 3.1.7: PASS - log_truncate_on_rotation is set to %', current_setting;
    ELSE
        RAISE NOTICE 'Control 3.1.7: FAIL - log_truncate_on_rotation is set to %, expected: %', current_setting, expected_setting;
    END IF;
END
$$;


-- === Rule PGSQL_11 ===  -- 3.1.8 Ensure the maximum log file lifetime is set correctly (Automated)
-- 3.1.8 Ensure the maximum log file lifetime is set correctly (Automated)

DO $$
DECLARE
    current_setting TEXT;
    expected_setting TEXT := '1d';
BEGIN
    SELECT setting INTO current_setting
    FROM pg_settings
    WHERE name = 'log_rotation_age';

    IF current_setting = expected_setting THEN
        RAISE NOTICE 'Control 3.1.8: PASS - log_rotation_age is set to %', current_setting;
    ELSE
        RAISE NOTICE 'Control 3.1.8: FAIL - log_rotation_age is set to %, expected: %', current_setting, expected_setting;
    END IF;
END
$$;


-- === Rule PGSQL_12 ===  -- 3.1.9 Ensure the maximum log file size is set correctly (Automated)
-- 3.1.9 Ensure the maximum log file size is set correctly (Automated)

DO $$
DECLARE
    current_setting TEXT;
    expected_setting TEXT := '0';  -- Change to organization policy if different
BEGIN
    SELECT setting INTO current_setting
    FROM pg_settings
    WHERE name = 'log_rotation_size';
    IF current_setting = expected_setting THEN
        RAISE NOTICE 'Control 3.1.9: PASS - log_rotation_size is set to %', current_setting;
    ELSE
        RAISE NOTICE 'Control 3.1.9: FAIL - log_rotation_size is set to %, expected: %', current_setting, expected_setting;
    END IF;
END
$$;


-- === Rule PGSQL_13 ===  -- 3.1.10 Ensure the correct syslog facility is selected (Manual)
-- 3.1.10 Ensure the correct syslog facility is selected (Manual)

DO $$
DECLARE
    current_setting TEXT;
    expected_setting TEXT := 'local0';  -- Adjust if your org uses a different facility
BEGIN
    SELECT setting INTO current_setting
    FROM pg_settings
    WHERE name = 'syslog_facility';

    IF current_setting = expected_setting THEN
        RAISE NOTICE 'Control 3.1.10: PASS - syslog_facility is set to %', current_setting;
    ELSE
        RAISE NOTICE 'Control 3.1.10: FAIL - syslog_facility is set to %, expected: %', current_setting, expected_setting;
    END IF;
END
$$;

-- === Rule PGSQL_14 ===
-- 3.1.11 Ensure syslog messages are not suppressed (Automated)
DO $$
DECLARE
    current_setting TEXT;
    expected_setting TEXT := 'on';
BEGIN
    SELECT setting INTO current_setting
    FROM pg_settings
    WHERE name = 'syslog_sequence_numbers';
    IF current_setting = expected_setting THEN
        RAISE NOTICE 'Control 3.1.11: PASS - syslog_sequence_numbers is set to %', current_setting;
    ELSE
        RAISE NOTICE 'Control 3.1.11: FAIL - syslog_sequence_numbers is set to %, expected: %', current_setting, expected_setting;
    END IF;
END
$$;

-- === Rule PGSQL_15 ===
-- 3.1.12 Ensure syslog messages are not lost due to size (Automated)

DO $$
DECLARE
    current_setting TEXT;
    expected_setting TEXT := 'on';
BEGIN
    SELECT setting INTO current_setting
    FROM pg_settings
    WHERE name = 'syslog_split_messages';

    IF current_setting = expected_setting THEN
        RAISE NOTICE 'Control 3.1.12: PASS - syslog_split_messages is set to %', current_setting;
    ELSE
        RAISE NOTICE 'Control 3.1.12: FAIL - syslog_split_messages is set to %, expected: %', current_setting, expected_setting;
    END IF;
END
$$;

-- === Rule PGSQL_16 ===
-- 3.1.13 Ensure the program name for PostgreSQL syslog messages is correct (Automated)
DO $$
DECLARE
    current_setting TEXT;
    expected_setting TEXT := 'postgres';
BEGIN
    SELECT setting INTO current_setting
    FROM pg_settings
    WHERE name = 'syslog_ident';
    IF current_setting = expected_setting THEN
        RAISE NOTICE 'Control 3.1.13 Ensure the program name for PostgreSQL syslog messages is correct (Automated): PASS - syslog_ident is set to %', current_setting;
    ELSE
        RAISE NOTICE 'Control 3.1.13 Ensure the program name for PostgreSQL syslog messages is correct (Automated): FAIL - syslog_ident is set to %, expected: %', current_setting, expected_setting;
    END IF;
END
$$;

-- === Rule PGSQL_17 ===
-- 3.1.14 Ensure the correct messages are written to the server log

DO $$
DECLARE
    current_setting TEXT;
    level_order CONSTANT TEXT[] := ARRAY[
        'debug5', 'debug4', 'debug3', 'debug2', 'debug1',
        'log', 'exception', 'info', 'warning', 'error', 'fatal', 'panic'
    ];
    required_min_level TEXT := 'warning';
    current_index INT;
    required_index INT;
BEGIN
    SELECT setting INTO current_setting
    FROM pg_settings
    WHERE name = 'log_min_messages';

    SELECT i INTO current_index
    FROM generate_subscripts(level_order, 1) AS i
    WHERE level_order[i] = current_setting;

    SELECT i INTO required_index
    FROM generate_subscripts(level_order, 1) AS i
    WHERE level_order[i] = required_min_level;

    IF current_index >= required_index THEN
        RAISE NOTICE 'Control 3.1.14 Ensure the correct messages are written to the server log: PASS - log_min_messages is set to %', current_setting;
    ELSE
        RAISE NOTICE 'Control 3.1.14 Ensure the correct messages are written to the server log: FAIL - log_min_messages is set to %, expected at least: %', current_setting, required_min_level;
    END IF;
END
$$;

-- === Rule PGSQL_18 ===
-- 3.1.15 Ensure the correct SQL statements generating errors are recorded (Automated)
DO $$
DECLARE
    current_setting TEXT;
    level_order CONSTANT TEXT[] := ARRAY[
        'debug5', 'debug4', 'debug3', 'debug2', 'debug1',
        'info', 'exception', 'warning', 'error', 'log', 'fatal', 'panic'
    ];
    required_min_level TEXT := 'error';
    current_index INT;
    required_index INT;
BEGIN
    SELECT setting INTO current_setting
    FROM pg_settings
    WHERE name = 'log_min_error_statement';
    SELECT i INTO current_index
    FROM generate_subscripts(level_order, 1) AS i
    WHERE level_order[i] = current_setting;
    SELECT i INTO required_index
    FROM generate_subscripts(level_order, 1) AS i
    WHERE level_order[i] = required_min_level;
    IF current_index >= required_index THEN
        RAISE NOTICE 'Control 3.1.15 Ensure the correct SQL statements generating errors are recorded (Automated): PASS - log_min_error_statement is set to %', current_setting;
    ELSE
        RAISE NOTICE 'Control 3.1.15 Ensure the correct SQL statements generating errors are recorded (Automated): FAIL - log_min_error_statement is set to %, expected at least %', current_setting, required_min_level;
    END IF;
END
$$;

-- === Rule PGSQL_19 ===
-- 3.1.16 Ensure 'debug_print_parse' is disabled
DO $$
DECLARE
    current_setting TEXT;
BEGIN
    SELECT setting INTO current_setting
    FROM pg_settings
    WHERE name = 'debug_print_parse';

    IF current_setting = 'off' THEN
        RAISE NOTICE 'Control 3.1.16 Ensure ''debug_print_parse'' is disabled: PASS - debug_print_parse is set to off';
    ELSE
        RAISE NOTICE 'Control 3.1.16 Ensure ''debug_print_parse'' is disabled: FAIL - debug_print_parse is set to %, expected off', current_setting;
    END IF;
END
$$;

-- === Rule PGSQL_20 ===
-- 3.1.17 Ensure 'debug_print_rewritten' is disabled (Automated)
DO $$
DECLARE
    current_setting TEXT;
BEGIN
    SELECT s.setting INTO current_setting
    FROM pg_settings s
    WHERE s.name = 'debug_print_rewritten';

    IF current_setting = 'off' THEN
        RAISE NOTICE 'Control 3.1.17 Ensure ''debug_print_rewritten'' is disabled (Automated): PASS - debug_print_rewritten is set to off';
    ELSE
        RAISE NOTICE 'Control 3.1.17 Ensure ''debug_print_rewritten'' is disabled (Automated): FAIL - debug_print_rewritten is set to %, expected off', current_setting;
    END IF;
END
$$;

-- === Rule PGSQL_21 ===
-- 3.1.18 Ensure 'debug_print_plan' is disabled
DO $$
DECLARE
    current_setting TEXT;
BEGIN
    SELECT setting INTO current_setting
    FROM pg_settings
    WHERE name = 'debug_print_plan';

    IF current_setting = 'off' THEN
        RAISE NOTICE 'Control 3.1.19 Ensure ''debug_pretty_print'' is enabled (Automated): PASS - debug_print_plan is set to off';
    ELSE
        RAISE NOTICE 'Control 3.1.19 Ensure ''debug_pretty_print'' is enabled (Automated): FAIL - debug_print_plan is set to %, expected off', current_setting;
    END IF;
END
$$;


-- === Rule PGSQL_22 ===
-- 3.1.19 Ensure 'debug_pretty_print' is enabled (Automated)
DO $$
DECLARE
    current_setting TEXT;
BEGIN
    SELECT setting INTO current_setting
    FROM pg_settings
    WHERE name = 'debug_pretty_print';
    IF current_setting = 'on' THEN
        RAISE NOTICE 'Control 3.1.19 Ensure ''debug_pretty_print'' is enabled (Automated): PASS - debug_pretty_print is enabled';
    ELSE
        RAISE NOTICE 'Control 3.1.19 Ensure ''debug_pretty_print'' is enabled (Automated): FAIL - debug_pretty_print is %, expected on', current_setting;
    END IF;
END
$$;

-- === Rule PGSQL_23 ===
-- 3.1.20 Ensure 'log_connections' is enabled
DO $$
DECLARE
    current_setting TEXT;
BEGIN
    SELECT s.setting INTO current_setting
    FROM pg_settings s
    WHERE s.name = 'log_connections';

    IF current_setting = 'on' THEN
        RAISE NOTICE 'Control 3.1.20 Ensure ''log_connections'' is enabled: PASS - log_connections is enabled';
    ELSE
        RAISE NOTICE 'Control 3.1.20 Ensure ''log_connections'' is enabled: FAIL - log_connections is %, expected on', current_setting;
    END IF;
END
$$;



-- === Rule PGSQL_24 ===
-- 3.1.21 Ensure 'log_disconnections' is enabled (Automated)
DO $$
DECLARE
    current_setting TEXT;
BEGIN
    SELECT s.setting INTO current_setting
    FROM pg_settings s
    WHERE s.name = 'log_disconnections';

    IF current_setting = 'on' THEN
        RAISE NOTICE 'Control 3.1.21 Ensure ''log_disconnections'' is enabled (Automated): PASS - log_disconnections is enabled';
    ELSE
        RAISE NOTICE 'Control 3.1.21 Ensure ''log_disconnections'' is enabled (Automated): FAIL - log_disconnections is %, expected on', current_setting;
    END IF;
END
$$;


-- === Rule PGSQL_25 ===
-- 3.1.22 Ensure 'log_error_verbosity' is set correctly
DO $$
DECLARE
    verbosity TEXT;
BEGIN
    SELECT setting INTO verbosity
    FROM pg_settings
    WHERE name = 'log_error_verbosity';

    IF verbosity = 'verbose' THEN
        RAISE NOTICE 'Control 3.1.22 Ensure ''log_error_verbosity'' is set correctly: PASS - log_error_verbosity is set to verbose';
    ELSE
        RAISE NOTICE 'Control 3.1.22 Ensure ''log_error_verbosity'' is set correctly: FAIL - log_error_verbosity is set to %, expected "verbose"', verbosity;
    END IF;
END
$$;

-- === Rule PGSQL_26 ===
-- 3.1.23 Ensure 'log_hostname' is set correctly (Automated)
DO $$
DECLARE
    current_setting TEXT;
    expected_setting TEXT := 'off';
BEGIN
    SELECT setting INTO current_setting
    FROM pg_settings
    WHERE name = 'log_hostname';
    IF current_setting = expected_setting THEN
        RAISE NOTICE 'Control 3.1.23 Ensure ''log_hostname'' is set correctly (Automated): PASS - log_hostname is set to %', current_setting;
    ELSE
        RAISE NOTICE 'Control 3.1.23 Ensure ''log_hostname'' is set correctly (Automated): FAIL - log_hostname is set to %, expected: %', current_setting, expected_setting;
    END IF;
END
$$;

-- === Rule PGSQL_27 ===
-- 3.1.24 Ensure 'log_line_prefix' is set correctly (Automated)

DO $$
DECLARE
    current_setting TEXT;
    expected_prefix TEXT := '%m [%p]';
BEGIN
    SELECT setting INTO current_setting
    FROM pg_settings
    WHERE name = 'log_line_prefix';

    IF current_setting LIKE '%' || expected_prefix || '%' THEN
        RAISE NOTICE 'Control 3.1.24 Ensure ''log_line_prefix'' is set correctly (Automated): PASS - log_line_prefix contains %', expected_prefix;
    ELSE
        RAISE NOTICE 'Control 3.1.24 Ensure ''log_line_prefix'' is set correctly (Automated): FAIL - log_line_prefix is set to %, expected to contain: %', current_setting, expected_prefix;
    END IF;
END
$$;

-- === Rule PGSQL_28 ===
-- 3.1.25 Ensure 'log_statement' is set correctly (Automated)
DO $$
DECLARE
    current_setting TEXT;
    invalid_setting TEXT := 'none';
BEGIN
    SELECT setting INTO current_setting
    FROM pg_settings
    WHERE name = 'log_statement';
    IF current_setting = invalid_setting THEN
        RAISE NOTICE 'Control 3.1.25 Ensure ''log_statement'' is set correctly (Automated): FAIL - log_statement is set to %, expected: ddl, mod, or all', current_setting;
    ELSE
        RAISE NOTICE 'Control 3.1.25 Ensure ''log_statement'' is set correctly (Automated): PASS - log_statement is set to %', current_setting;
    END IF;
END
$$;

-- === Rule PGSQL_29 ===
-- 3.1.26 Ensure 'log_timezone' is set correctly (Automated)

DO $$
DECLARE
    current_setting TEXT;
    valid_setting TEXT := 'UTC';
BEGIN
    SELECT setting INTO current_setting
    FROM pg_settings
    WHERE name = 'log_timezone';

    IF current_setting = valid_setting THEN
        RAISE NOTICE 'Control 3.1.26 Ensure ''log_timezone'' is set correctly (Automated): PASS - log_timezone is set to %', current_setting;
    ELSE
        RAISE NOTICE 'Control 3.1.26 Ensure ''log_timezone'' is set correctly (Automated): FAIL - log_timezone is set to %, expected: % (or organization-defined equivalent)', current_setting, valid_setting;
    END IF;
END
$$;

-- === Rule PGSQL_30 ===
-- 3.2 Ensure the PostgreSQL Audit Extension (pgAudit) is enabled (Automated)
DO $$
DECLARE
    preload_libs TEXT;
    audit_setting TEXT;
BEGIN
    SELECT setting INTO preload_libs
    FROM pg_settings
    WHERE name = 'shared_preload_libraries';

    IF position('pgaudit' IN preload_libs) > 0 THEN
        RAISE NOTICE 'Control 3.2 Ensure the PostgreSQL Audit Extension (pgAudit) is enabled (Automated): PASS - pgaudit is included in shared_preload_libraries (%).', preload_libs;
    ELSE
        RAISE NOTICE 'Control 3.2 Ensure the PostgreSQL Audit Extension (pgAudit) is enabled (Automated): FAIL - pgaudit is NOT included in shared_preload_libraries (%).', preload_libs;
        -- Don't RETURN here, so script continues even if missing
    END IF;

    BEGIN
        SELECT setting INTO audit_setting
        FROM pg_settings
        WHERE name = 'pgaudit.log';

        IF audit_setting IS NOT NULL AND audit_setting <> '' THEN
            RAISE NOTICE 'Control 3.2 Ensure the PostgreSQL Audit Extension (pgAudit) is enabled (Automated): PASS - pgaudit.log is set to "%".', audit_setting;
        ELSE
            RAISE NOTICE 'Control 3.2 Ensure the PostgreSQL Audit Extension (pgAudit) is enabled (Automated): FAIL - pgaudit.log is empty or not properly configured.';
        END IF;

    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Control 3.2 Ensure the PostgreSQL Audit Extension (pgAudit) is enabled (Automated): FAIL - pgaudit.log parameter not found. pgAudit may not be fully loaded.';
            -- Exception handled, continue normally
    END;
END
$$;

-- === Rule PGSQL_32 ===
-- 4.2 Ensure excessive administrative privileges are revoked (Manual)

DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT rolname, rolsuper, rolcreaterole, rolcreatedb, rolreplication, rolbypassrls
        FROM pg_roles
        WHERE rolname <> 'postgres'
    LOOP
        IF r.rolsuper OR r.rolcreaterole OR r.rolcreatedb OR r.rolreplication OR r.rolbypassrls THEN
            RAISE NOTICE 'Control 4.2 Ensure excessive administrative privileges are revoked (Manual): FAIL - Role "%" has elevated privileges: superuser=%, createrole=%, createdb=%, replication=%, bypass_rls=%',
                r.rolname, r.rolsuper, r.rolcreaterole, r.rolcreatedb, r.rolreplication, r.rolbypassrls;
        ELSE
            RAISE NOTICE 'Control 4.2 Ensure excessive administrative privileges are revoked (Manual): PASS - Role "%" does not have elevated privileges.', r.rolname;
        END IF;
    END LOOP;
END $$;

-- === Rule PGSQL_33 ===
-- 4.3 Ensure excessive function privileges are revoked (Automated)
DO $$
DECLARE
    rec RECORD;
BEGIN
    FOR rec IN
        SELECT n.nspname, p.proname, p.prosecdef, a.rolname
        FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace = n.oid
        JOIN pg_authid a ON a.oid = p.proowner
        WHERE p.prosecdef = true AND p.proname NOT LIKE 'pgaudit%'
    LOOP
        RAISE NOTICE 'Control 4.3 Ensure excessive function privileges are revoked (Automated): FAIL - Function %.% is SECURITY DEFINER owned by role "%"', rec.nspname, rec.proname, rec.rolname;
    END LOOP;

    IF NOT FOUND THEN
        RAISE NOTICE 'Control 4.3 Ensure excessive function privileges are revoked (Automated): PASS - No unauthorized SECURITY DEFINER functions found.';
    END IF;
END
$$;

-- === Rule PGSQL_36 ===
-- 4.6 Ensure the set_user extension is installed (Automated)
DO $$
DECLARE
    result TEXT;
BEGIN
    SELECT CASE 
        WHEN EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'set_user') 
            THEN 'Pass: set_user extension is installed.'
        ELSE 
            'Fail: set_user extension not installed.'
    END INTO result;
    
    RAISE NOTICE 'Control 4.6.1 Ensure the set_user extension is installed (Automated): %', result;
END
$$;

DO $$
DECLARE
    result TEXT;
BEGIN
    SELECT CASE 
        WHEN COUNT(*) > 0 THEN 
            'Fail: Superuser roles that can login: ' || string_agg(rolname, ', ')
        ELSE 
            'Pass: No superuser roles can login.'
    END INTO result
    FROM pg_authid
    WHERE rolsuper = TRUE AND rolcanlogin = TRUE;

    RAISE NOTICE 'Control 4.6.2 Ensure the set_user extension is installed (Automated): %', result;
END
$$;

DO $$
DECLARE
    result TEXT;
BEGIN
    WITH RECURSIVE role_hierarchy AS (
        SELECT oid, rolname, rolsuper, ARRAY[oid] AS path
        FROM pg_authid
        WHERE rolcanlogin = TRUE
        UNION ALL
        SELECT p.oid, p.rolname, p.rolsuper, rh.path || p.oid
        FROM pg_authid p
        JOIN pg_auth_members m ON p.oid = m.roleid
        JOIN role_hierarchy rh ON m.member = rh.oid
        WHERE NOT p.oid = ANY(rh.path)
    )
    SELECT CASE 
        WHEN EXISTS (
            SELECT 1 FROM role_hierarchy 
            WHERE rolsuper = TRUE 
              AND oid <> (SELECT oid FROM pg_authid WHERE rolname = 'postgres')
        ) THEN
            'Fail: There are roles with superuser privileges through membership (besides postgres).'
        ELSE
            'Pass: No unprivileged roles have superuser privileges via membership.'
    END INTO result;

    RAISE NOTICE 'Control 4.6.3 Ensure the set_user extension is installed (Automated): %', result;
END
$$;

-- === Rule PGSQL_42 ===
-- 6.2 Ensure 'backend' runtime parameters are configured correctly (Automated)

DO $$
DECLARE
    ignore_system_indexes TEXT;
    jit_debugging_support TEXT;
    jit_profiling_support TEXT;
    log_connections TEXT;
    log_disconnections TEXT;
    post_auth_delay TEXT;
BEGIN
    -- Fetch current values
    SELECT setting INTO ignore_system_indexes FROM pg_settings WHERE name = 'ignore_system_indexes';
    SELECT setting INTO jit_debugging_support FROM pg_settings WHERE name = 'jit_debugging_support';
    SELECT setting INTO jit_profiling_support FROM pg_settings WHERE name = 'jit_profiling_support';
    SELECT setting INTO log_connections FROM pg_settings WHERE name = 'log_connections';
    SELECT setting INTO log_disconnections FROM pg_settings WHERE name = 'log_disconnections';
    SELECT setting INTO post_auth_delay FROM pg_settings WHERE name = 'post_auth_delay';

    -- Check each parameter
    IF ignore_system_indexes != 'off' THEN
        RAISE NOTICE 'Control 6.2 Ensure ''backend'' runtime parameters are configured correctly (Automated): FAIL - ignore_system_indexes is %, expected "off"', ignore_system_indexes;
    END IF;

    IF jit_debugging_support != 'off' THEN
        RAISE NOTICE 'Control 6.2 Ensure ''backend'' runtime parameters are configured correctly (Automated): FAIL - jit_debugging_support is %, expected "off"', jit_debugging_support;
    END IF;

    IF jit_profiling_support != 'off' THEN
        RAISE NOTICE 'Control 6.2 Ensure ''backend'' runtime parameters are configured correctly (Automated): FAIL - jit_profiling_support is %, expected "off"', jit_profiling_support;
    END IF;

    IF log_connections != 'on' THEN
        RAISE NOTICE 'Control 6.2 Ensure ''backend'' runtime parameters are configured correctly (Automated): FAIL - log_connections is %, expected "on"', log_connections;
    END IF;

    IF log_disconnections != 'on' THEN
        RAISE NOTICE 'Control 6.2 Ensure ''backend'' runtime parameters are configured correctly (Automated): FAIL - log_disconnections is %, expected "on"', log_disconnections;
    END IF;

    IF post_auth_delay != '0' THEN
        RAISE NOTICE 'Control 6.2 Ensure ''backend'' runtime parameters are configured correctly (Automated): FAIL - post_auth_delay is %, expected "0"', post_auth_delay;
    END IF;

    -- If all checks pass
    RAISE NOTICE 'Control 6.2 Ensure ''backend'' runtime parameters are configured correctly (Automated): PASS - All backend runtime parameters are correctly set';

END
$$;

-- === Rule PGSQL_48 ===
-- 6.8 Ensure TLS is enabled and configured correctly

DO $$
DECLARE
    ssl_enabled TEXT;
    ssl_cert_file TEXT;
    ssl_key_file TEXT;
BEGIN
    -- Check if SSL is enabled
    SELECT setting INTO ssl_enabled
    FROM pg_settings
    WHERE name = 'ssl';

    IF ssl_enabled <> 'on' THEN
        RAISE NOTICE 'Control 6.8 Ensure TLS is enabled and configured correctly: FAIL - TLS/SSL is not enabled (ssl = %)', ssl_enabled;
    END IF;

    -- Check if server certificate and key are configured
    SELECT setting INTO ssl_cert_file
    FROM pg_settings
    WHERE name = 'ssl_cert_file';

    SELECT setting INTO ssl_key_file
    FROM pg_settings
    WHERE name = 'ssl_key_file';

    IF ssl_cert_file IS NULL OR ssl_cert_file = '' THEN
        RAISE NOTICE 'Control 6.8 Ensure TLS is enabled and configured correctly: FAIL - ssl_cert_file is not configured';
    ELSIF ssl_key_file IS NULL OR ssl_key_file = '' THEN
        RAISE NOTICE 'Control 6.8 Ensure TLS is enabled and configured correctly: FAIL - ssl_key_file is not configured';
    ELSE
        RAISE NOTICE 'Control 6.8 Ensure TLS is enabled and configured correctly: PASS - TLS/SSL is enabled and certificate/key are configured properly';
    END IF;
END
$$;



-- === Rule PGSQL_49 ===
-- 6.9 Ensure the pgcrypto extension is installed and configured correctly (Manual)
DO $$
DECLARE
    ext_available TEXT;
    ext_installed TEXT;
BEGIN
    SELECT installed_version INTO ext_installed
    FROM pg_available_extensions
    WHERE name = 'pgcrypto';
    IF ext_installed IS NULL THEN
        RAISE NOTICE 'Control 6.9 Ensure the pgcrypto extension is installed and configured correctly (Manual): FAIL - pgcrypto extension is not installed or available in the cluster';
    ELSIF ext_installed = '' THEN
        RAISE NOTICE 'Control 6.9 Ensure the pgcrypto extension is installed and configured correctly (Manual): FAIL - pgcrypto extension is available but not installed';
    ELSE
        RAISE NOTICE 'Control 6.9 Ensure the pgcrypto extension is installed and configured correctly (Manual): PASS - pgcrypto extension is installed (version %)', ext_installed;
    END IF;
END
$$;

-- === Rule PGSQL_50 ===
-- 7.1 Ensure a replication-only user is created and used for streaming replication

DO $$
DECLARE
    replication_users INT;
    postgres_has_replication BOOLEAN;
BEGIN
    -- Count how many users have replication privileges
    SELECT COUNT(*) INTO replication_users
    FROM pg_roles
    WHERE rolreplication = true;

    -- Check if only 'postgres' has replication privileges
    SELECT EXISTS (
        SELECT 1 FROM pg_roles WHERE rolname = 'postgres' AND rolreplication = true
    ) INTO postgres_has_replication;

    IF replication_users = 1 AND postgres_has_replication THEN
        RAISE NOTICE 'Control 7.1 Ensure a replication-only user is created and used for streaming replication: FAIL - Only the default "postgres" user has replication privileges. Create a dedicated replication-only user.';
    ELSIF replication_users >= 1 AND NOT postgres_has_replication THEN
        RAISE NOTICE 'Control 7.1 Ensure a replication-only user is created and used for streaming replication: PASS - A dedicated replication-only user exists and is used.';
    ELSE
        RAISE NOTICE 'Control 7.1 Ensure a replication-only user is created and used for streaming replication: REVIEW - Multiple users have replication privileges. Manual validation needed to confirm correct usage.';
    END IF;
END
$$;

-- === Rule PGSQL_51 ===
-- 7.2 Ensure logging of replication commands is configured (Manual)

DO $$
DECLARE
    log_replication_value TEXT;
BEGIN
    SELECT setting INTO log_replication_value
    FROM pg_settings
    WHERE name = 'log_replication_commands';
    IF log_replication_value = 'on' THEN
        RAISE NOTICE 'Control 7.2 Ensure logging of replication commands is configured (Manual): PASS - log_replication_commands is set to "on"';
    ELSE
        RAISE NOTICE 'Control 7.2 Ensure logging of replication commands is configured (Manual): FAIL - log_replication_commands is set to %, expected "on"', log_replication_value;
    END IF;
END
$$;

-- === Rule PGSQL_53 ===
-- 7.4 Ensure WAL archiving is configured and functional

DO $$
DECLARE
    archive_mode TEXT;
    archive_cmd TEXT;
    archive_lib TEXT;
    archived BIGINT;
    failed BIGINT;
BEGIN
    -- Check WAL archiving settings
    SELECT setting INTO archive_mode 
    FROM pg_settings 
    WHERE name = 'archive_mode';

    SELECT setting INTO archive_cmd 
    FROM pg_settings 
    WHERE name = 'archive_command';

    SELECT setting INTO archive_lib 
    FROM pg_settings 
    WHERE name = 'archive_library';

    -- Step 1: Check archive_mode
    IF archive_mode != 'on' THEN
        RAISE NOTICE 'Control 7.4 Ensure WAL archiving is configured and functional: FAIL - archive_mode is not set to "on"';
    END IF;

    -- Step 2: Check if archiving method is set
    IF archive_cmd = '' AND archive_lib = '' THEN
        RAISE NOTICE 'Control 7.4 Ensure WAL archiving is configured and functional: FAIL - Neither archive_command nor archive_library is configured';
    END IF;

    -- Step 3: Check if archiving is working
    SELECT a.archived_count, a.failed_count
    INTO archived, failed
    FROM pg_stat_archiver a;

    IF archived = 0 THEN
        RAISE NOTICE 'Control 7.4 Ensure WAL archiving is configured and functional: FAIL - No WAL files have been archived yet (archived_count = 0)';
    ELSIF failed > 0 THEN
        RAISE NOTICE 'Control 7.4 Ensure WAL archiving is configured and functional: FAIL - Some WAL files failed to archive (failed_count = %)', failed;
    ELSE
        RAISE NOTICE 'Control 7.4 Ensure WAL archiving is configured and functional: PASS - WAL archiving is enabled and functioning';
    END IF;
END
$$;


-- === Rule PGSQL_55 ===
-- 8.1 Ensure PostgreSQL subdirectory locations are outside the data cluster (Manual)

DO $$
DECLARE
    rec RECORD;
    fail_count INT := 0;
BEGIN
    FOR rec IN
        SELECT name, setting
        FROM pg_settings
        WHERE name ~ '_directory$' OR name ~ '_tablespace'
    LOOP
        -- Adjust this check to your actual outside path if needed
        IF rec.setting LIKE 'outside_data_cluster%' THEN
            RAISE NOTICE 'Control 8.1 Ensure PostgreSQL subdirectory locations are outside the data cluster (Manual): PASS - % is outside the data cluster (%).', rec.name, rec.setting;
        ELSE
            RAISE NOTICE 'Control 8.1 Ensure PostgreSQL subdirectory locations are outside the data cluster (Manual): FAIL - % is NOT outside the data cluster (%).', rec.name, rec.setting;
            fail_count := fail_count + 1;
        END IF;
    END LOOP;

    IF fail_count = 0 THEN
        RAISE NOTICE 'Control 8.1 Ensure PostgreSQL subdirectory locations are outside the data cluster (Manual): PASS - All relevant directories are configured outside the data cluster.';
    ELSE
        RAISE NOTICE 'Control 8.1 Ensure PostgreSQL subdirectory locations are outside the data cluster (Manual): FAIL - % setting(s) are still inside the data cluster.', fail_count;
    END IF;
END
$$;