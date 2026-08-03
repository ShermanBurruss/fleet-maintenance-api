-- Create the dedicated database used by the automated Pytest suite.
--
-- PostgreSQL executes scripts in /docker-entrypoint-initdb.d when the
-- database volume is initialized for the first time.

CREATE DATABASE fleetdb_test;