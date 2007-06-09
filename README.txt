Autor: Juan F. Codagnone (Zauber S.A.)

Esta aplicaci�n ayuda a recopilar informaci�n para analizar posibles
alquileres. Es una peque�a prueba de conceptos como una peque�a herramienta
puede agregar bastante valor.


Requerimientos:
   * postgresql 8.x
   * postgis
   * python >= 2.4
   * dev-python/psycopg

   
Instalaci�n de la base de datos:
   1. Crear la base de datos
       createuser alquiler
       createdb   -E utf8 -O alquiler alquiler
       createlang plpgsql alquiler
       psql -d alquiler -f /usr/share/postgresql/contrib/lwpostgis.sql
       psql -d alquiler -f /usr/share/postgresql/contrib/spatial_ref_sys.sqla
   2. Popular la base de datos
       correr los sql en orden alfabetico del directorio dbscript (psql -d
       alquiler -U alquiler -f dbscripts/1.sql ...)

