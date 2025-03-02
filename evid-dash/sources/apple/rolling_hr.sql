SELECT time,
    AVG(value::FLOAT) OVER (
        ORDER BY time ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as avg_
FROM (
        SELECT startdate::DATE as time,
            AVG(value::FLOAT) as value
        FROM restingheartrate
        GROUP BY 1
    ) as subquery
ORDER BY 1;