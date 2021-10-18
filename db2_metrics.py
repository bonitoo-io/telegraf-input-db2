import argparse
import ibm_db
import sys
import time
import datetime
import calendar
import os

# print debug messages
debug = False
# metric name prefix
metric = "db2"


def log(log_type, log_msg, host, db):
    msg = "{0}_integration,host={1},database={2},type={3},msg={4} msg=1".format(
        metric,
        host,
        db,
        log_type,
        log_msg.replace(" ", "\\ "))

    if debug == False and msg != None:
        print(msg)
    else:
        print("[debug] {0}".format(msg))


def handle_error(error_message, host, db):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    msg = "{0}|{1}|{2}".format(str(error_message), fname, exc_tb.tb_lineno)
    log("error", msg, host, db)
    sys.exit(1)


def read_last_clock_file(file):
    """Return the clock (Unixtime) from the specified file or current time if the file doesn't exist"""
    last_clock = int(time.time())
    if os.path.isfile(file):
        try:
            last_clock_file = open(file, 'r')
            last_clock = int(last_clock_file.readline())
            last_clock_file.close()
        except IOError:
            sys.stderr.write('Error: failed to read last clock file, ' +
                             file + '\n')
            sys.exit(2)
    return last_clock


def write_last_clock_file(file, clock):
    """Write the supplied clock (Unixtime) to file"""
    try:
        file = open(file, 'w')
        file.write(str(clock))
        file.close()
    except IOError:
        sys.stderr.write('Error writing last clock to file: ' +
                         file + '\n')
        sys.exit(2)


class DB2Metrics:

    def __init__(self, host, db, user, passwd, port=50000):
        self.id = "db2-metrics-1"
        self.db = db
        self.host = host
        self.port = port
        if self.port == None:
            self.port = 50000
        self.user = user
        self.passwd = passwd
        self.connection = None
        try:
            conn_str = ('DATABASE=' + self.db + ';' +
                        'HOSTNAME=' + self.host + ';' +
                        'PORT=' + str(self.port) + ';' +
                        'PROTOCOL=TCPIP;' +
                        'UID=' + self.user + ';' +
                        'PWD=' + self.passwd + ';')
            self.connection = ibm_db.connect(conn_str, '', '')
        except Exception as e:
            handle_error(e, self.host, self.db)

    # function to return query result in rows
    def query(self, sql):
        try:
            from ibm_db import fetch_assoc
            ret = []
            stmt = ibm_db.exec_immediate(self.connection, sql)
            result = fetch_assoc(stmt)
            while result:
                ret.append(result)
                result = fetch_assoc(stmt)
            return ret
        except Exception as e:
            handle_error(e, self.host, self.db)

    # generate and run query using config
    def run_query(self, config):
        cols = []
        sql = ""

        try:
            if config['source_col'] != None:
                cols.append(str(config['source_col']))

            if config['timestamp'] != None:
                cols.append(config['timestamp'])

            if config['metrics'] != None:
                for c in config['metrics']:
                    cols.append(c)
            if config['tags_col'] != None:
                for t in config['tags_col']:
                    cols.append(t)

            if config['sql'] == None:
                # columns
                sql = sql + "SELECT "
                for i, col in enumerate(cols):
                    if i > 0:
                        sql = sql + ", "
                    sql = sql + col

                # table and schema
                if 'schema' in config and config['schema'] != None:
                    sql = sql + \
                        " FROM {0}.{1}".format(
                            config['schema'], config['table'])
                else:
                    sql = sql + " FROM {0}".format(config['table'])

                # where condition (if exists)
                if 'where' in config and config['where'] != None:
                    sql = sql + " WHERE " + config['where']
            else:
                sql = config['sql']

            if debug == True:
                print(config)
                print("[sql]", sql)
            rows = self.query(sql)
            return rows
        except Exception as e:
            handle_error(e, self.host, self.db)

    # run query defined in query config, and send it to the target with appropriate data format
    def report(self, query_config):
        wf_out = []
        rows = self.run_query(query_config)

        try:
            # process the result using query config
            for row in rows:
                source = query_config['source']
                if query_config['source_col'] != None:
                    source = row[query_config['source_col']]

                # get current time first
                epoch = calendar.timegm(time.gmtime())
                # use timestamp, otherwise, use system timestamp
                if "timestamp" in query_config and query_config['timestamp'] != None:
                    time_stamp = row[query_config['timestamp']]
                    epoch = int(
                        (time_stamp - datetime.datetime(1970, 1, 1)).total_seconds())

                data_lines = self.to_influx_format(
                    row, epoch, source, query_config)

                for data_line in data_lines:
                    wf_out.append(data_line)

            if len(wf_out) > 0:
                # send data to telegraf
                for line in wf_out:
                    print(line)

                log("result", "success [{0}] : {1} lines".format(
                    query_config['name'], len(wf_out)), self.host, self.db)
        except Exception as e:
            handle_error(e, self.host, self.db)

    # internal method to convert data into influx db format
    def to_influx_format(self, row, epoch, source, query_config):
        data_lines = []
        data_line = "{0}_{1},host={2}".format(
            metric, query_config['name'].lower().replace("_", "."), source)
        if query_config['tags'] != None:
            for name, value in query_config['tags'].items():
                data_line = data_line + \
                    ",{0}={1}".format(name.lower(), value.replace(" ", "\\ "))
        if query_config['tags_col'] != None:
            for col in query_config['tags_col']:
                val = row[col]
                if val != None and val != "":
                    val = val.strip()
                    data_line = data_line + \
                        ",{0}={1}".format(col.lower(), val.replace(" ", "\\ "))

        data_line = data_line + " "
        i = 0
        for col in query_config['metrics']:
            val = row[col]
            if val != None:
                if i > 0:
                    data_line = data_line + ","
                if type(val) == str:
                    val = '"'+val.replace(" ", "\\ ").replace(",", "\\,")+':'
                elif type(val) == datetime.datetime:
                    val = '"'+val.isoformat()+'"'
                data_line = data_line + "{0}={1}".format(col.lower(), val)
                i = i+1

        if i == 0:
            return data_lines  # no fields available

        data_line = "{0} {1}".format(data_line, epoch * 1000000000)
        data_lines.append(data_line)
        return data_lines

    ####################################
    # query definitions
    ####################################

    def get_db_instance(self):
        # query definition
        query_config = {
            'name': "instance",
            'description': None,
            'metrics': ["TOTAL_CONNECTIONS", "GW_TOTAL_CONS"],
            'tags_col': ["PRODUCT_NAME", "SERVER_PLATFORM"],
            'tags': {"database": self.db},
            'timestamp': None,
            'source_col': None,
            'source': self.host,
            'schema': None,
            'table': "TABLE(MON_GET_INSTANCE(-1))",
            'where': None,
            'sql': None
        }
        self.report(query_config)

    def get_db_database(self):
        # query definition
        query_config = {
            'name': "database",
            'description': None,
            'metrics': ["APPLS_CUR_CONS",
                        "APPLS_IN_DB2",
                        "CONNECTIONS_TOP",
                        "DEADLOCKS",
                        "LAST_BACKUP",
                        "LOCK_LIST_IN_USE",
                        "LOCK_TIMEOUTS",
                        "LOCK_WAIT_TIME",
                        "LOCK_WAITS",
                        "NUM_LOCKS_HELD",
                        "NUM_LOCKS_WAITING",
                        "ROWS_INSERTED",
                        "ROWS_UPDATED",
                        "ROWS_DELETED",
                        "ROWS_MODIFIED",
                        "ROWS_READ",
                        "ROWS_RETURNED",
                        "TOTAL_CONS"
                        ],
            'tags_col': ['DB_STATUS'],
            'tags': {"database": self.db},
            'timestamp': None,
            'source_col': None,
            'source': self.host,
            'schema': None,
            'table': "TABLE(MON_GET_DATABASE(-1))",
            'where': None,
            'sql': None
        }
        self.report(query_config)

    def get_db_buffer_pool(self):
        # query definition
        query_config = {
            'name': "buffer",
            'description': None,
            'metrics': ['POOL_ASYNC_COL_LBP_PAGES_FOUND',
                        'POOL_ASYNC_DATA_LBP_PAGES_FOUND',
                        'POOL_ASYNC_INDEX_LBP_PAGES_FOUND',
                        'POOL_ASYNC_XDA_LBP_PAGES_FOUND',
                        'POOL_COL_GBP_L_READS',
                        'POOL_COL_GBP_P_READS',
                        'POOL_COL_L_READS',
                        'POOL_COL_LBP_PAGES_FOUND',
                        'POOL_COL_P_READS',
                        'POOL_DATA_GBP_L_READS',
                        'POOL_DATA_GBP_P_READS',
                        'POOL_DATA_L_READS',
                        'POOL_DATA_LBP_PAGES_FOUND',
                        'POOL_DATA_P_READS',
                        'POOL_INDEX_GBP_L_READS',
                        'POOL_INDEX_GBP_P_READS',
                        'POOL_INDEX_L_READS',
                        'POOL_INDEX_LBP_PAGES_FOUND',
                        'POOL_INDEX_P_READS',
                        'POOL_TEMP_COL_L_READS',
                        'POOL_TEMP_COL_P_READS',
                        'POOL_TEMP_DATA_L_READS',
                        'POOL_TEMP_DATA_P_READS',
                        'POOL_TEMP_INDEX_L_READS',
                        'POOL_TEMP_INDEX_P_READS',
                        'POOL_TEMP_XDA_L_READS',
                        'POOL_TEMP_XDA_P_READS',
                        'POOL_XDA_GBP_L_READS',
                        'POOL_XDA_GBP_P_READS',
                        'POOL_XDA_L_READS',
                        'POOL_XDA_LBP_PAGES_FOUND',
                        'POOL_XDA_P_READS'
                        ],
            'tags_col': ['BP_NAME'],
            'tags': {"database": self.db},
            'timestamp': None,
            'source_col': None,
            'source': self.host,
            'schema': None,
            'table': "TABLE(MON_GET_BUFFERPOOL(NULL, -1))",
            'where': None,
            'sql': None
        }
        self.report(query_config)

    def get_db_tablespace(self):
        # query definition
        query_config = {
            'name': "tablespace",
            'description': None,
            'metrics': ['TBSP_PAGE_SIZE',
                        'TBSP_TOTAL_PAGES',
                        'TBSP_USABLE_PAGES',
                        'TBSP_USED_PAGES'
                        ],
            'tags_col': ['TBSP_NAME', 'TBSP_STATE'],
            'tags': {"database": self.db},
            'timestamp': None,
            'source_col': None,
            'source': self.host,
            'schema': None,
            'table': "TABLE(MON_GET_TABLESPACE(NULL, -1))",
            'where': None,
            'sql': None
        }
        self.report(query_config)

    def get_db_transaction_log(self):
        # query definition
        query_config = {
            'name': "txlog",
            'description': None,
            'metrics': ['LOG_READS',
                        'LOG_WRITES',
                        'TOTAL_LOG_AVAILABLE',
                        'TOTAL_LOG_USED'
                        ],
            'tags_col': None,
            'tags': {"database": self.db},
            'timestamp': None,
            'source_col': None,
            'source': self.host,
            'schema': None,
            'table': "TABLE(MON_GET_TRANSACTION_LOG(-1))",
            'where': None,
            'sql': None
        }
        self.report(query_config)

    def get_db_table(self):
        # query definition
        query_config = {
            'name': "table",
            'description': None,
            'metrics': ['TOTAL_ROWS_READ',
                        'TOTAL_ROWS_INSERTED',
                        'TOTAL_ROWS_UPDATED',
                        'TOTAL_ROWS_DELETED'
                        ],
            'tags_col': ['TABSCHEMA',
                         'TABNAME'
                         ],
            'tags': {"database": self.db},
            'timestamp': None,
            'source_col': None,
            'source': self.host,
            'schema': None,
            'table': None,
            'where': None,
            'sql': "SELECT varchar(tabschema,20) as tabschema, varchar(tabname,20) as tabname, sum(rows_read) as total_rows_read, sum(rows_inserted) as total_rows_inserted, sum(rows_updated) as total_rows_updated, sum(rows_deleted) as total_rows_deleted FROM TABLE(MON_GET_TABLE('','',-2)) AS t GROUP BY tabschema, tabname ORDER BY total_rows_read DESC"
        }
        self.report(query_config)


if __name__ == "__main__":
    args = None
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-s', '--host', help="database server hostname / IP ", required=True)
        parser.add_argument(
            '-p', '--port', help="database server port", required=False)
        parser.add_argument('-d', '--db', help="database", required=True)
        parser.add_argument('-U', '--user', help="user name", required=True)
        parser.add_argument('-P', '--passwd', help="password", required=True)
        parser.add_argument('-D', '--debug', help="Debug mode",
                            action="store_true", required=False, default=False)
        args = parser.parse_args()
        debug = args.debug

        stats = None
        try:
            stats = DB2Metrics(args.host, args.db,
                               args.user, args.passwd, args.port)
            last_clock = read_last_clock_file(stats.id + ".last_clock")
            # other stats should follow here
            stats.get_db_instance()
            stats.get_db_database()
            stats.get_db_buffer_pool()
            stats.get_db_tablespace()
            stats.get_db_transaction_log()
            stats.get_db_table()
        except Exception as e:
            handle_error(e, args.server, args.db)
        finally:
            if stats != None and stats.connection != None:
                ibm_db.close(stats.connection)
    except Exception as e:
        if args.server != None and args.db != None:
            handle_error(e, args.server, args.db)
