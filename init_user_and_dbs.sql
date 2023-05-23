CREATE DATABASE homepod_data;
create user homepod_data with encrypted password 'homepod_data';
grant all privileges on database homepod_data to homepod_data;
\c homepod_data
GRANT ALL ON SCHEMA "public" TO homepod_data;
