-- Workstation Manager - Sample Data
-- This script populates the database with sample data for testing

-- ============================================
-- Sample Workstations
-- ============================================

INSERT INTO workstations (
    hostname, display_name, os_type, os_version, status,
    ip_address, mac_address, location, description, tags,
    ssh_enabled, ssh_port, ssh_username,
    rdp_enabled, rdp_port, rdp_username,
    agent_version, agent_last_seen
) VALUES
(
    'ws-dev-01',
    'Development Workstation 01',
    'linux',
    'Ubuntu 22.04 LTS',
    'online',
    '192.168.1.101',
    '00:11:22:33:44:01',
    'Seoul Office - Floor 3',
    'Primary development workstation',
    ARRAY['development', 'ubuntu', 'production'],
    true, 22, 'developer',
    false, NULL, NULL,
    '1.0.0',
    CURRENT_TIMESTAMP - INTERVAL '5 minutes'
),
(
    'ws-win-01',
    'Windows Workstation 01',
    'windows',
    'Windows 11 Pro',
    'online',
    '192.168.1.102',
    '00:11:22:33:44:02',
    'Seoul Office - Floor 2',
    'Design and rendering workstation',
    ARRAY['windows', 'design', 'gpu'],
    false, NULL, NULL,
    true, 3389, 'designer',
    '1.0.0',
    CURRENT_TIMESTAMP - INTERVAL '2 minutes'
),
(
    'ws-lab-01',
    'Lab Testing Machine',
    'linux',
    'CentOS 8',
    'online',
    '192.168.1.103',
    '00:11:22:33:44:03',
    'Lab - Testing Area',
    'QA and testing environment',
    ARRAY['testing', 'qa', 'centos'],
    true, 22, 'tester',
    false, NULL, NULL,
    '1.0.0',
    CURRENT_TIMESTAMP - INTERVAL '10 minutes'
),
(
    'ws-db-01',
    'Database Server',
    'linux',
    'Ubuntu 20.04 LTS',
    'offline',
    '192.168.1.104',
    '00:11:22:33:44:04',
    'Server Room - Rack A',
    'PostgreSQL database server',
    ARRAY['database', 'production', 'critical'],
    true, 22, 'dbadmin',
    false, NULL, NULL,
    '1.0.0',
    CURRENT_TIMESTAMP - INTERVAL '1 hour'
),
(
    'ws-offline-01',
    'Offline Workstation',
    'windows',
    'Windows 10 Pro',
    'offline',
    '192.168.1.105',
    '00:11:22:33:44:05',
    'Storage - Floor 1',
    'Temporary offline for maintenance',
    ARRAY['windows', 'storage'],
    false, NULL, NULL,
    true, 3389, 'admin',
    '0.9.5',
    CURRENT_TIMESTAMP - INTERVAL '2 days'
) ON CONFLICT (hostname) DO NOTHING;

-- ============================================
-- Sample System Specs
-- ============================================

INSERT INTO system_specs (
    workstation_id,
    cpu_model, cpu_cores, cpu_threads, cpu_frequency_mhz,
    total_memory_gb,
    gpu_info, storage_info, network_info,
    motherboard, bios_version
)
SELECT
    id,
    'Intel Core i9-13900K',
    24, 32, 3000.0,
    64.0,
    '[{"name": "NVIDIA RTX 4090", "memory_gb": 24, "driver": "535.54.03"}]'::jsonb,
    '[{"device": "/dev/nvme0n1", "size_gb": 2000, "type": "NVMe SSD", "mount": "/"}]'::jsonb,
    '[{"interface": "eth0", "speed_mbps": 10000, "mac": "00:11:22:33:44:01"}]'::jsonb,
    'ASUS ROG MAXIMUS Z790 HERO',
    'Version 2301'
FROM workstations WHERE hostname = 'ws-dev-01'
ON CONFLICT (workstation_id) DO NOTHING;

INSERT INTO system_specs (
    workstation_id,
    cpu_model, cpu_cores, cpu_threads, cpu_frequency_mhz,
    total_memory_gb,
    gpu_info, storage_info, network_info,
    motherboard, bios_version
)
SELECT
    id,
    'AMD Ryzen 9 7950X',
    16, 32, 4500.0,
    128.0,
    '[{"name": "NVIDIA RTX 4080", "memory_gb": 16, "driver": "546.33"}]'::jsonb,
    '[{"device": "C:", "size_gb": 1000, "type": "NVMe SSD"}, {"device": "D:", "size_gb": 4000, "type": "SATA SSD"}]'::jsonb,
    '[{"interface": "Ethernet", "speed_mbps": 2500}]'::jsonb,
    'ASUS ProArt X670E-CREATOR WIFI',
    'Version 1407'
FROM workstations WHERE hostname = 'ws-win-01'
ON CONFLICT (workstation_id) DO NOTHING;

-- ============================================
-- Sample System Metrics
-- ============================================

-- Generate metrics for the last hour (every 5 minutes)
DO $$
DECLARE
    ws_record RECORD;
    time_offset INTEGER;
    random_cpu DECIMAL;
    random_mem DECIMAL;
BEGIN
    FOR ws_record IN SELECT id FROM workstations WHERE status = 'online' LOOP
        FOR time_offset IN 0..12 LOOP
            random_cpu := 10 + (RANDOM() * 70);
            random_mem := 20 + (RANDOM() * 60);

            INSERT INTO system_metrics (
                workstation_id,
                cpu_usage_percent, cpu_frequency_current_mhz, cpu_temperature_celsius,
                memory_used_gb, memory_percent,
                disk_io_read_mbps, disk_io_write_mbps,
                network_sent_mbps, network_recv_mbps,
                gpu_usage_percent, gpu_memory_used_gb, gpu_temperature_celsius,
                process_count, active_users,
                timestamp
            ) VALUES (
                ws_record.id,
                random_cpu, 3000 + (RANDOM() * 1000), 45 + (RANDOM() * 30),
                random_mem * 0.64, random_mem,
                50 + (RANDOM() * 200), 30 + (RANDOM() * 150),
                10 + (RANDOM() * 100), 20 + (RANDOM() * 150),
                20 + (RANDOM() * 60), 4 + (RANDOM() * 12), 50 + (RANDOM() * 20),
                100 + FLOOR(RANDOM() * 200)::INTEGER, 1 + FLOOR(RANDOM() * 3)::INTEGER,
                CURRENT_TIMESTAMP - (time_offset * INTERVAL '5 minutes')
            );
        END LOOP;
    END LOOP;
END $$;

-- ============================================
-- Sample Installed Apps
-- ============================================

INSERT INTO installed_apps (workstation_id, name, version, publisher, install_date, size_mb)
SELECT
    id,
    'Visual Studio Code',
    '1.85.1',
    'Microsoft Corporation',
    CURRENT_DATE - 30,
    350.5
FROM workstations WHERE hostname = 'ws-dev-01'
ON CONFLICT (workstation_id, name, version) DO NOTHING;

INSERT INTO installed_apps (workstation_id, name, version, publisher, install_date, size_mb)
SELECT
    id,
    'Docker Desktop',
    '4.26.1',
    'Docker Inc.',
    CURRENT_DATE - 60,
    1250.0
FROM workstations WHERE hostname = 'ws-dev-01'
ON CONFLICT (workstation_id, name, version) DO NOTHING;

INSERT INTO installed_apps (workstation_id, name, version, publisher, install_date, size_mb)
SELECT
    id,
    'Adobe Photoshop 2024',
    '25.3.1',
    'Adobe Inc.',
    CURRENT_DATE - 90,
    4500.0
FROM workstations WHERE hostname = 'ws-win-01'
ON CONFLICT (workstation_id, name, version) DO NOTHING;

INSERT INTO installed_apps (workstation_id, name, version, publisher, install_date, size_mb)
SELECT
    id,
    'Blender',
    '4.0.2',
    'Blender Foundation',
    CURRENT_DATE - 45,
    780.0
FROM workstations WHERE hostname = 'ws-win-01'
ON CONFLICT (workstation_id, name, version) DO NOTHING;

-- ============================================
-- Sample Usage Sessions
-- ============================================

INSERT INTO usage_sessions (workstation_id, username, login_time, logout_time, session_duration_minutes, is_active)
SELECT
    id,
    'developer',
    CURRENT_TIMESTAMP - INTERVAL '3 hours',
    NULL,
    NULL,
    true
FROM workstations WHERE hostname = 'ws-dev-01';

INSERT INTO usage_sessions (workstation_id, username, login_time, logout_time, session_duration_minutes, is_active)
SELECT
    id,
    'designer',
    CURRENT_TIMESTAMP - INTERVAL '2 hours',
    NULL,
    NULL,
    true
FROM workstations WHERE hostname = 'ws-win-01';

INSERT INTO usage_sessions (workstation_id, username, login_time, logout_time, session_duration_minutes, is_active)
SELECT
    id,
    'developer',
    CURRENT_DATE - 1 + TIME '09:00:00',
    CURRENT_DATE - 1 + TIME '18:30:00',
    570,
    false
FROM workstations WHERE hostname = 'ws-dev-01';

-- ============================================
-- Sample Alerts
-- ============================================

INSERT INTO alerts (
    workstation_id, title, message, severity, status, source, category, created_at
)
SELECT
    id,
    'High CPU Usage',
    'CPU usage exceeded 90% for more than 5 minutes',
    'warning',
    'active',
    'system_monitor',
    'performance',
    CURRENT_TIMESTAMP - INTERVAL '1 hour'
FROM workstations WHERE hostname = 'ws-dev-01';

INSERT INTO alerts (
    workstation_id, title, message, severity, status, source, category, created_at
)
SELECT
    id,
    'Disk Space Low',
    'Available disk space on C: is below 10%',
    'critical',
    'active',
    'system_monitor',
    'storage',
    CURRENT_TIMESTAMP - INTERVAL '30 minutes'
FROM workstations WHERE hostname = 'ws-win-01';

INSERT INTO alerts (
    workstation_id, title, message, severity, status, source, category,
    created_at, acknowledged_at, acknowledged_by
)
SELECT
    w.id,
    'Memory Usage High',
    'Memory usage is at 85%',
    'warning',
    'acknowledged',
    'system_monitor',
    'memory',
    CURRENT_TIMESTAMP - INTERVAL '2 hours',
    CURRENT_TIMESTAMP - INTERVAL '1 hour 30 minutes',
    u.id
FROM workstations w, users u
WHERE w.hostname = 'ws-lab-01' AND u.username = 'admin';

-- ============================================
-- Sample Users
-- ============================================

-- Operator user (password: operator123)
INSERT INTO users (username, email, password_hash, full_name, role)
VALUES (
    'operator',
    'operator@workstation.local',
    '$2b$12$KIXdDxXz0Y6M5kZv8sQ7P.yGJ5rX8LPxJ8sQ7P8LPxJ8sQ7P8LPx',
    'System Operator',
    'operator'
) ON CONFLICT (username) DO NOTHING;

-- Viewer user (password: viewer123)
INSERT INTO users (username, email, password_hash, full_name, role)
VALUES (
    'viewer',
    'viewer@workstation.local',
    '$2b$12$YIXdDxXz0Y6M5kZv8sQ7P.yGJ5rX8LPxJ8sQ7P8LPxJ8sQ7P8LPx',
    'System Viewer',
    'viewer'
) ON CONFLICT (username) DO NOTHING;
