SELECT zcreationdate::date as date,
    EXTRACT(
        epoch
        FROM sum(zenddate - zstartdate)
    ) / 3600 as hours_coding
FROM apple_screentime
WHERE zvaluestring = 'com.microsoft.VSCode'
    AND zstreamname = '/app/usage'
    AND zcreationdate::date >= '2023-01-01'
GROUP BY 1