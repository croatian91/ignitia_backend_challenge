--- create temporary tables used for inserts and updates
CREATE TEMP TABLE tmp_sub_add (
    ts timestamp without time zone,
    msisdn text PRIMARY KEY, 
    service_id integer,
    lat double precision,
    lon double precision
);
CREATE TEMP TABLE tmp_sub_upd (
    ts timestamp without time zone,
    msisdn text PRIMARY KEY, 
    lat double precision,
    lon double precision
);
CREATE TEMP TABLE tmp_sub_del (
    ts timestamp without time zone,
    msisdn text PRIMARY KEY
);

COPY tmp_sub_add
FROM PROGRAM 'awk "(NR == 1) || (FNR > 1)" /var/tmp/*_additions.csv'
WITH (FORMAT CSV, HEADER);

--- process additions
INSERT INTO subscriptions (
    msisdn,
    service_id,
    geom,
    sub_date,
    lid
)
SELECT msisdn, 
    service_id, 
    ST_SetSRID(ST_MakePoint(lon, lat), 4326) AS geom, 
    ts AS sub_date,
    (
        SELECT gid 
        FROM forecasts 
        ORDER BY ST_DistanceSphere(geom, ST_SetSRID(ST_MakePoint(lon, lat), 4326)) ASC 
        LIMIT 1
    ) as lid
FROM tmp_sub_add;

COPY tmp_sub_upd
FROM PROGRAM 'awk "(NR == 1) || (FNR > 1)" /var/tmp/*_locupdates.csv'
WITH (FORMAT CSV, HEADER);

--- process locupdates
--- the lid field is updated using a trigger defined in create_tables.sql
UPDATE subscriptions
SET geom = tmp.geom
FROM (SELECT msisdn, ST_SetSRID(ST_MakePoint(lon, lat), 4326) AS geom FROM tmp_sub_upd) as tmp
INNER JOIN subscriptions sub
ON sub.msisdn = tmp.msisdn;

COPY tmp_sub_del
FROM PROGRAM 'awk "(NR == 1) || (FNR > 1)" /var/tmp/*_deletions.csv'
WITH (FORMAT CSV, HEADER);

--- process deletions (unsubscribe)
UPDATE subscriptions
SET service_id = 0, unsub_date = CURRENT_TIMESTAMP
FROM tmp_sub_del
WHERE tmp_sub_del.msisdn = subscriptions.msisdn;

--- clean temporary tables
DROP TABLE tmp_sub_add;
DROP TABLE tmp_sub_upd;
DROP TABLE tmp_sub_del;

SELECT * FROM subscriptions LIMIT 15;