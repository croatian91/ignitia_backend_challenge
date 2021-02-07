CREATE TABLE forecasts (
    gid integer PRIMARY KEY,
    geom geometry(POINT, 4326),
    fcat24 double precision,
    fcat48 double precision
);
CREATE TABLE subscriptions (
    msisdn text PRIMARY KEY,
    service_id integer NOT NULL,
    current_service_id integer NOT NULL DEFAULT 0,
    geom geometry(POINT, 4326),
    lid integer,
    sub_date timestamp without time zone NOT NULL,
    unsub_date timestamp without time zone,
    next_billing_date date NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT subscriptions_lid_fkey FOREIGN KEY (lid) REFERENCES forecasts(gid)
);

CREATE FUNCTION update_lid() RETURNS trigger AS $update_lid$
    BEGIN
        IF NEW.geom IS NULL THEN
            RAISE EXCEPTION 'geom cannot be null';
        END IF;
        IF NEW.geom::text <> OLD.geom::text THEN
            UPDATE subscriptions
            SET lid = f.gid
            FROM (
                SELECT gid 
                FROM forecasts
                ORDER BY ST_DistanceSphere(NEW.geom, geom) ASC 
                LIMIT 1
            ) as f;
        END IF;
        RETURN NEW;
    END;
$update_lid$ LANGUAGE plpgsql;

CREATE TRIGGER geom_changes
  AFTER UPDATE
  ON subscriptions
  FOR EACH ROW
  EXECUTE PROCEDURE update_lid();