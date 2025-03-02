SELECT startdate::DATE as date,
    AVG(value::float) as sdnn
FROM heartratevariabilitysdnn
GROUP BY 1