-- =========================================================
-- IT Application Support & Incident Management Lab
-- Support and Reporting Queries
-- =========================================================


-- 1. View all incidents
SELECT *
FROM tickets
ORDER BY created_at DESC;


-- 2. View all open incidents
SELECT
    id,
    title,
    category,
    priority,
    status,
    assigned_analyst,
    created_at
FROM tickets
WHERE status = 'Open'
ORDER BY created_at DESC;


-- 3. View incidents currently being investigated
SELECT
    id,
    title,
    category,
    priority,
    assigned_analyst,
    created_at
FROM tickets
WHERE status = 'In Progress'
ORDER BY priority DESC, created_at ASC;


-- 4. View high and critical priority incidents
SELECT
    id,
    title,
    category,
    priority,
    status,
    assigned_analyst
FROM tickets
WHERE priority IN ('High', 'Critical')
ORDER BY
    CASE priority
        WHEN 'Critical' THEN 1
        WHEN 'High' THEN 2
        ELSE 3
    END,
    created_at ASC;


-- 5. View escalated incidents
SELECT
    id,
    title,
    category,
    priority,
    status,
    assigned_analyst,
    created_at
FROM tickets
WHERE status = 'Escalated'
ORDER BY created_at ASC;


-- 6. View incidents waiting for user response
SELECT
    id,
    title,
    requester_name,
    email,
    assigned_analyst,
    created_at
FROM tickets
WHERE status = 'Pending User'
ORDER BY created_at ASC;


-- 7. View resolved incidents
SELECT
    id,
    title,
    category,
    priority,
    assigned_analyst,
    created_at,
    resolved_at
FROM tickets
WHERE status = 'Resolved'
ORDER BY resolved_at DESC;


-- 8. Count incidents by category
SELECT
    category,
    COUNT(*) AS incident_count
FROM tickets
GROUP BY category
ORDER BY incident_count DESC;


-- 9. Count incidents by status
SELECT
    status,
    COUNT(*) AS incident_count
FROM tickets
GROUP BY status
ORDER BY incident_count DESC;


-- 10. Count incidents by priority
SELECT
    priority,
    COUNT(*) AS incident_count
FROM tickets
GROUP BY priority
ORDER BY
    CASE priority
        WHEN 'Critical' THEN 1
        WHEN 'High' THEN 2
        WHEN 'Medium' THEN 3
        WHEN 'Low' THEN 4
    END;


-- 11. View incidents assigned to a specific analyst
SELECT
    id,
    title,
    category,
    priority,
    status,
    created_at,
    resolved_at
FROM tickets
WHERE assigned_analyst = 'Kesha Dave'
ORDER BY created_at DESC;


-- 12. Search for Microsoft 365 or identity-related incidents
SELECT
    id,
    title,
    category,
    priority,
    status
FROM tickets
WHERE category IN ('Microsoft 365', 'Identity / Access')
ORDER BY created_at DESC;


-- 13. Search application and API incidents
SELECT
    id,
    title,
    category,
    priority,
    status,
    assigned_analyst
FROM tickets
WHERE category IN ('Application', 'API', 'Database')
ORDER BY created_at DESC;


-- 14. Search incident text for HTTP errors
SELECT
    id,
    title,
    description,
    priority,
    status
FROM tickets
WHERE
    title LIKE '%HTTP%'
    OR description LIKE '%HTTP%'
ORDER BY created_at DESC;


-- 15. View root-cause and resolution history
SELECT
    id,
    title,
    root_cause,
    resolution,
    resolved_at
FROM tickets
WHERE
    root_cause IS NOT NULL
    AND root_cause != ''
ORDER BY resolved_at DESC;


-- 16. View unresolved critical incidents
SELECT
    id,
    title,
    category,
    priority,
    status,
    assigned_analyst
FROM tickets
WHERE priority = 'Critical'
  AND status NOT IN ('Resolved', 'Closed')
ORDER BY created_at ASC;


-- 17. Incident workload by analyst
SELECT
    COALESCE(assigned_analyst, 'Unassigned') AS analyst,
    COUNT(*) AS incident_count
FROM tickets
GROUP BY assigned_analyst
ORDER BY incident_count DESC;


-- 18. Resolved incident count by analyst
SELECT
    assigned_analyst,
    COUNT(*) AS resolved_count
FROM tickets
WHERE status = 'Resolved'
  AND assigned_analyst IS NOT NULL
GROUP BY assigned_analyst
ORDER BY resolved_count DESC;