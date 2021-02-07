COPY forecasts (gid, geom, fcat24, fcat48)
FROM PROGRAM 'cut -d "," -f 1,2,5,6 /var/tmp/forecasts.csv'
WITH (FORMAT CSV, HEADER);