dropdb alquiler
createdb   -E utf8 -O alquiler alquiler
createlang plpgsql alquiler
psql -d alquiler -f /usr/share/postgresql/contrib/lwpostgis.sql
psql -d alquiler -f /usr/share/postgresql/contrib/spatial_ref_sys.sql
