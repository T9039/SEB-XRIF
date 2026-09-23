-- Runs once, on first initialisation of the Postgres data directory.
-- Creates the dedicated database that the SQL LRS (lrsql) owns.
CREATE DATABASE lrsql_db OWNER sebxrif;
