#!/bin/bash
# Database server host name  or IP
HOST=localhost
# Database server port
PORT=50000
# Database name
DB=testdb
# Database user
USERNAME=db2inst1
PASSWORD=changeit

SCRIPT=`dirname $0`/db2_metrics.py

## You can possibly export Oracle Client environment variables herein. 
## The recommended approach is to export then before running telegraf.
# export LD_LIBRARY_PATH=/opt/oracle/client

python3 "$SCRIPT" --host "$HOST" --port "$PORT" --db "$DB" --user "$USERNAME" --passwd "$PASSWORD"