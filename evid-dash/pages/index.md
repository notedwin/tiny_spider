---
title: How is Edwin?
source: postgres.contributions
---

_how can we understand anything without measuring it?_

<LastRefreshed prefix="Data last updated"/>

## Date Range

<DateInput
name=range_input
defaultValue={'Last 90 Days'}
range
presetRanges={['Last 30 Days', 'Last 90 Days', 'Last 3 Months', 'Last 6 Months', 'Year to Date', 'All Time']}
/>

## rolling steps and hr over range

```sql steps
SELECT
  date,
  AVG(steps::FLOAT) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as rolling_weekly_avg
FROM steps
WHERE date between '${inputs.range_input.start}' and '${inputs.range_input.end}'
```

```sql historical_steps
SELECT
    AVG(steps) as avg_6
FROM steps
```

```sql rolling_hr
SELECT
    *
FROM rolling_hr
where time between '${inputs.range_input.start}' and '${inputs.range_input.end}'
```

```sql avg_hr
SELECT
    AVG(avg_) as avg_
FROM ${rolling_hr}
```

```sql exercise_mins
SELECT
date,
mins_active
FROM exercise
WHERE date between '${inputs.range_input.start}' and '${inputs.range_input.end}'
```

```sql met_goal
SELECT
    COUNT(*) as num_days
FROM ${exercise_mins}
WHERE mins_active > 30
```

```sql sdnn
SELECT
    date,
    sdnn as avg
FROM sdnn
WHERE date between '${inputs.range_input.start}' and '${inputs.range_input.end}'
```

```sql avg_sdnn
SELECT
    AVG(avg) as avg
FROM ${sdnn}
```

<Grid cols=2>
<LineChart data={steps} x=date y=rolling_weekly_avg yAxisTitle="Steps">
    <ReferenceArea yMin=0 yMax=5000 color=negative label="Lame"/>
    <ReferenceArea yMin=5000 yMax=10000 color=warning label="Good"/>
    <ReferenceArea yMin=10000 yMax=20000 color=positive label="Great"/>
    <ReferenceLine data={historical_steps} y=avg_6 label="6 year avg" labelPosition="belowStart" color="purple"/>
</LineChart>

<LineChart data={rolling_hr} x=time y=avg_ yAxisTitle="Heart Rate" yMin=50 yMax=80>
    <ReferenceArea yMin=50 yMax=57 color=positive label="Great"/>
    <ReferenceArea yMin=57 yMax=65 color=warning label="Good"/>
    <ReferenceArea yMin=65 yMax=100 color=negative label="Bad"/>
    <ReferenceLine data={avg_hr} y=avg_ label="avg" labelPosition="belowStart" color="purple"/>
</LineChart>
</Grid>

## daily sdnn + exercise mins

<Grid cols=2>
<LineChart data={sdnn} x=date y=avg yAxisTitle="SDNN" yMin=30 yMax=80>
    <ReferenceArea yMin=50 color=positive label="Great"/>
    <ReferenceArea yMax=50 color=negative label="Bad"/>
    <ReferenceLine data={avg_sdnn} y=avg label="avg sdnn" labelPosition="belowStart" color="purple"/>
</LineChart>

<LineChart data={exercise_mins} x=date y=mins_active yAxisTitle="Exercise mins">
    <ReferenceArea yMin=30 color=positive label="Great"/>
    <ReferenceArea yMax=30 color=negative label="Not reaching goal"/>
</LineChart>

</Grid>

---

### cloudflare stats

```sql cf
SELECT time,
SUM(requests * weight) OVER (ORDER BY time DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) / SUM(weight) OVER (ORDER BY time DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as weighted_rolling_avg
FROM (
    SELECT
    date::date as time,
    SUM(requests) as requests,
    COUNT(*) as weight
    FROM cloudflare
    WHERE date between '${inputs.range_input.start}' and '${inputs.range_input.end}'
    GROUP BY 1
) as cf
```

```sql historical_cf
SELECT
    MIN(requests) as min_,
    AVG(requests) as avg_,
    MAX(requests) as max_
FROM cloudflare
WHERE date between '${inputs.range_input.start}' and '${inputs.range_input.end}'
```

<LineChart data={cf} x=time y=weighted_rolling_avg yAxisTitle="Requests">
    <ReferenceLine data={historical_cf} y=avg_ label="avg" labelPosition="belowStart" color="warning"/>
    <ReferenceLine data={historical_cf} y=min_ label="min" labelPosition="belowStart" color="negative"/>
    <ReferenceLine data={historical_cf} y=max_ label="max" labelPosition="belowStart" color="positive"/>
</LineChart>

---

## time stats

```sql hours_projects
SELECT
    project,
    hours_worked
FROM (
    SELECT split_part(
        split_part(title, '—', 2),
        E'\t',
        1
    ) as project,
    (SUM(duration) / 3600)::int as hours_worked
    FROM aw_hours
    WHERE date between '${inputs.range_input.start}' and '${inputs.range_input.end}'
    GROUP BY 1
)
WHERE hours_worked > 0
```

```sql coding
SELECT * FROM hours
WHERE hours_coding > 0.15
AND date between '${inputs.range_input.start}' and '${inputs.range_input.end}'
```

```sql total_hours
SELECT
    SUM(hours_coding) as total_hours
FROM hours
WHERE date between '${inputs.range_input.start}' and '${inputs.range_input.end}'
```

```sql avg_time
SELECT
    AVG(hours_coding) as time
FROM hours
```

<BigValue
  data={total_hours}
  value=total_hours
  title="Hours Coding in range"
/>

<BigValue
  data={avg_time}
  value=time
  title="avg hours coding alltime"
/>

<BarChart 
    data={hours_projects}
    swapXY=true
    x=project
    y=hours_worked
/>

## screen time

lol, i am tracking this but im not going to embarrass myself by showing it here :p
