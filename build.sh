#!/usr/bin/env bash

make install && psql -U username -h hostname -p 5432 -d dbname -f database.sql

