SELECT startdate::DATE as date,
    COUNT(*) as mins_active
FROM appleexercisetime
GROUP BY 1