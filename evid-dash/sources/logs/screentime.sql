SELECT zcreationdate::date as date,
    EXTRACT(
        epoch
        FROM SUM(zenddate - zstartdate)
    ) / 3600 as usage
FROM apple_screentime
WHERE zstreamname = '/app/usage'
GROUP BY 1
ORDER BY 2 DESC
LIMIT 30