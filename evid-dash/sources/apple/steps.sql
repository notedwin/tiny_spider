SELECT startdate::DATE as date,
    SUM(value::int) as steps
FROM stepcount
GROUP BY 1