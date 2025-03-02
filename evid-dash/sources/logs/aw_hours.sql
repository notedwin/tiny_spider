SELECT datastr::json->>'title' as title,
    duration,
    timestamp::date as date
FROM eventmodel
WHERE datastr::json->>'app' = 'Code'