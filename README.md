# DB2 Input Plugin

This repository contains a telegraf external plugin that collects metrics from DB2 RDBMS using performance monitor tables. 

### Installation

The plugin executes a python script to gather metrics. It requires proper installation of [python3](https://www.python.org/downloads/) with [ibm_db](https://github.com/ibmdb/python-ibmdb) extension module. The extension module might require extra environment variables, which must be set. 

__Setting up the appropriate privileges in DB2__
This integration needs to execute queries on DB2 performance resources. Switch to the instance master user (e.g. DB2INST1) and run these commands in `db2` CLI. You should start the database and attach to the database before running these, see [test setup example](./dev/test-db2-setup.txt).

```sh
db2 "update dbm cfg using HEALTH_MON on"
db2 "update dbm cfg using DFT_MON_STMT on"
db2 "update dbm cfg using DFT_MON_LOCK on"
db2 "update dbm cfg using DFT_MON_TABLE on"
db2 "update dbm cfg using DFT_MON_BUFPOOL on"
```
Validate whether the settings are correctly applied by running the following command:
```sh
db2 "get dbm cfg"
```
Among the configurations being output'ed, you should see the following settings:
```
Default database monitor switches  
  Buffer pool                         (DFT_MON_BUFPOOL) = ON  
  Lock                                   (DFT_MON_LOCK) = ON  
  Sort                                   (DFT_MON_SORT) = OFF  
  Statement                              (DFT_MON_STMT) = ON  
  Table                                 (DFT_MON_TABLE) = ON  
  Timestamp                         (DFT_MON_TIMESTAMP) = ON  
  Unit of work                            (DFT_MON_UOW) = OFF  
Monitor health of instance and databases   (HEALTH_MON) = ON
```

__Clone the repository__

```
git clone git@github.com:bonitoo-io/telegraf-input-db2.git
```

__Modify telegraf configuration__

```toml
[[inputs.execd]]
  command = ["/path/to/telegraf-input-db2/db2_metrics.sh"]
  signal = "none"
```
Replace `/path/to/telegraf-input-db2` with a directory of your clone. The 
`db2_metrics.sh` executes the python script and also ensures that DB2
user password is not printed in telegraf logs.

__Modify /path/to/telegraf-input-db2/db2_metrics.sh__

- Modify `hostname`, `port` and `database` or your DB2 connection.
- Modify `username` and `password` of your DB2 user.

### Metrics

```
$ telegraf --config ./dev/telegraf.conf --input-filter execd --test
> db2_instance,database=testdb,host=localhost,product_name=DB2\ v11.5.6.0,server_platform=Linux/X8664 gw_total_cons=0,total_connections=2 1634580099000000000
> db2_database,database=testdb,db_status=ACTIVE,host=localhost appls_cur_cons=1,appls_in_db2=1,connections_top=20,deadlocks=0,last_backup="2021-10-18T14:40:12",lock_list_in_use=38400,lock_timeouts=0,lock_wait_time=0,lock_waits=0,num_locks_held=3,num_locks_waiting=0,rows_deleted=0,rows_inserted=0,rows_modified=0,rows_read=728,rows_returned=1,rows_updated=0,total_cons=2 1634580099000000000
> db2_buffer,bp_name=IBMDEFAULTBP,database=testdb,host=localhost pool_async_col_lbp_pages_found=0,pool_async_data_lbp_pages_found=27,pool_async_index_lbp_pages_found=0,pool_async_xda_lbp_pages_found=0,pool_col_gbp_l_reads=0,pool_col_gbp_p_reads=0,pool_col_l_reads=0,pool_col_lbp_pages_found=0,pool_col_p_reads=0,pool_data_gbp_l_reads=0,pool_data_gbp_p_reads=0,pool_data_l_reads=1000,pool_data_lbp_pages_found=897,pool_data_p_reads=168,pool_index_gbp_l_reads=0,pool_index_gbp_p_reads=0,pool_index_l_reads=912,pool_index_lbp_pages_found=699,pool_index_p_reads=213,pool_temp_col_l_reads=0,pool_temp_col_p_reads=0,pool_temp_data_l_reads=0,pool_temp_data_p_reads=0,pool_temp_index_l_reads=0,pool_temp_index_p_reads=0,pool_temp_xda_l_reads=0,pool_temp_xda_p_reads=0,pool_xda_gbp_l_reads=0,pool_xda_gbp_p_reads=0,pool_xda_l_reads=0,pool_xda_lbp_pages_found=0,pool_xda_p_reads=0 1634580099000000000
> db2_buffer,bp_name=IBMSYSTEMBP4K,database=testdb,host=localhost pool_async_col_lbp_pages_found=0,pool_async_data_lbp_pages_found=0,pool_async_index_lbp_pages_found=0,pool_async_xda_lbp_pages_found=0,pool_col_gbp_l_reads=0,pool_col_gbp_p_reads=0,pool_col_l_reads=0,pool_col_lbp_pages_found=0,pool_col_p_reads=0,pool_data_gbp_l_reads=0,pool_data_gbp_p_reads=0,pool_data_l_reads=0,pool_data_lbp_pages_found=0,pool_data_p_reads=0,pool_index_gbp_l_reads=0,pool_index_gbp_p_reads=0,pool_index_l_reads=0,pool_index_lbp_pages_found=0,pool_index_p_reads=0,pool_temp_col_l_reads=0,pool_temp_col_p_reads=0,pool_temp_data_l_reads=0,pool_temp_data_p_reads=0,pool_temp_index_l_reads=0,pool_temp_index_p_reads=0,pool_temp_xda_l_reads=0,pool_temp_xda_p_reads=0,pool_xda_gbp_l_reads=0,pool_xda_gbp_p_reads=0,pool_xda_l_reads=0,pool_xda_lbp_pages_found=0,pool_xda_p_reads=0 1634580099000000000
> db2_buffer,bp_name=IBMSYSTEMBP8K,database=testdb,host=localhost pool_async_col_lbp_pages_found=0,pool_async_data_lbp_pages_found=0,pool_async_index_lbp_pages_found=0,pool_async_xda_lbp_pages_found=0,pool_col_gbp_l_reads=0,pool_col_gbp_p_reads=0,pool_col_l_reads=0,pool_col_lbp_pages_found=0,pool_col_p_reads=0,pool_data_gbp_l_reads=0,pool_data_gbp_p_reads=0,pool_data_l_reads=0,pool_data_lbp_pages_found=0,pool_data_p_reads=0,pool_index_gbp_l_reads=0,pool_index_gbp_p_reads=0,pool_index_l_reads=0,pool_index_lbp_pages_found=0,pool_index_p_reads=0,pool_temp_col_l_reads=0,pool_temp_col_p_reads=0,pool_temp_data_l_reads=0,pool_temp_data_p_reads=0,pool_temp_index_l_reads=0,pool_temp_index_p_reads=0,pool_temp_xda_l_reads=0,pool_temp_xda_p_reads=0,pool_xda_gbp_l_reads=0,pool_xda_gbp_p_reads=0,pool_xda_l_reads=0,pool_xda_lbp_pages_found=0,pool_xda_p_reads=0 1634580099000000000
> db2_buffer,bp_name=IBMSYSTEMBP16K,database=testdb,host=localhost pool_async_col_lbp_pages_found=0,pool_async_data_lbp_pages_found=0,pool_async_index_lbp_pages_found=0,pool_async_xda_lbp_pages_found=0,pool_col_gbp_l_reads=0,pool_col_gbp_p_reads=0,pool_col_l_reads=0,pool_col_lbp_pages_found=0,pool_col_p_reads=0,pool_data_gbp_l_reads=0,pool_data_gbp_p_reads=0,pool_data_l_reads=0,pool_data_lbp_pages_found=0,pool_data_p_reads=0,pool_index_gbp_l_reads=0,pool_index_gbp_p_reads=0,pool_index_l_reads=0,pool_index_lbp_pages_found=0,pool_index_p_reads=0,pool_temp_col_l_reads=0,pool_temp_col_p_reads=0,pool_temp_data_l_reads=0,pool_temp_data_p_reads=0,pool_temp_index_l_reads=0,pool_temp_index_p_reads=0,pool_temp_xda_l_reads=0,pool_temp_xda_p_reads=0,pool_xda_gbp_l_reads=0,pool_xda_gbp_p_reads=0,pool_xda_l_reads=0,pool_xda_lbp_pages_found=0,pool_xda_p_reads=0 1634580099000000000
> db2_buffer,bp_name=IBMSYSTEMBP32K,database=testdb,host=localhost pool_async_col_lbp_pages_found=0,pool_async_data_lbp_pages_found=0,pool_async_index_lbp_pages_found=0,pool_async_xda_lbp_pages_found=0,pool_col_gbp_l_reads=0,pool_col_gbp_p_reads=0,pool_col_l_reads=0,pool_col_lbp_pages_found=0,pool_col_p_reads=0,pool_data_gbp_l_reads=0,pool_data_gbp_p_reads=0,pool_data_l_reads=0,pool_data_lbp_pages_found=0,pool_data_p_reads=0,pool_index_gbp_l_reads=0,pool_index_gbp_p_reads=0,pool_index_l_reads=0,pool_index_lbp_pages_found=0,pool_index_p_reads=0,pool_temp_col_l_reads=0,pool_temp_col_p_reads=0,pool_temp_data_l_reads=0,pool_temp_data_p_reads=0,pool_temp_index_l_reads=0,pool_temp_index_p_reads=0,pool_temp_xda_l_reads=0,pool_temp_xda_p_reads=0,pool_xda_gbp_l_reads=0,pool_xda_gbp_p_reads=0,pool_xda_l_reads=0,pool_xda_lbp_pages_found=0,pool_xda_p_reads=0 1634580099000000000
> db2_tablespace,database=testdb,host=localhost,tbsp_name=SYSCATSPACE,tbsp_state=NORMAL tbsp_page_size=4096,tbsp_total_pages=32768,tbsp_usable_pages=32764,tbsp_used_pages=28956 1634580099000000000
> db2_tablespace,database=testdb,host=localhost,tbsp_name=TEMPSPACE1,tbsp_state=NORMAL tbsp_page_size=4096,tbsp_total_pages=1,tbsp_usable_pages=1,tbsp_used_pages=1 1634580099000000000
> db2_tablespace,database=testdb,host=localhost,tbsp_name=USERSPACE1,tbsp_state=NORMAL tbsp_page_size=4096,tbsp_total_pages=8192,tbsp_usable_pages=8160,tbsp_used_pages=96 1634580099000000000
> db2_tablespace,database=testdb,host=localhost,tbsp_name=SYSTOOLSPACE,tbsp_state=NORMAL tbsp_page_size=4096,tbsp_total_pages=8192,tbsp_usable_pages=8188,tbsp_used_pages=144 1634580099000000000
> db2_txlog,database=testdb,host=localhost log_reads=0,log_writes=0,total_log_available=158605312,total_log_used=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSPLAN,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=699,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSHISTOGRAMTEMPLATE,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=73,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSHISTOGRAMTEMPLATE,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=40,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSSERVICECLASSES,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=14,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSROUTINES,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=12,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSSCHEMATA,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=12,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSROLEAUTH,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=10,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSVARIABLES,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=5,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSWORKLOADS,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=4,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSSTOGROUPS,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=3,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSTABLESPACES,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=3,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSDBAUTH,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=2,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSNODEGROUPS,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=2,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSWORKCLASSATTRIBUT,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=2,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSWORKLOADAUTH,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=2,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSCONTEXTATTRIBUTES,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=1,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSCONTEXTS,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=1,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSEVENTMONITORS,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=1,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSHISTOGRAMTEMPLATE,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=1,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSSURROGATEAUTHIDS,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=1,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSTHRESHOLDS,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=1,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSVERSIONS,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=1,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSWORKACTIONS,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=1,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSWORKACTIONSETS,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=1,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSWORKCLASSES,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=1,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSAUDITPOLICIES,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=0,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSMEMBERSUBSETS,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=0,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSTASKS,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=0,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSUSAGELISTS,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=0,total_rows_updated=0 1634580099000000000
> db2_table,database=testdb,host=localhost,tabname=SYSWORKLOADCONNATTR,tabschema=SYSIBM total_rows_deleted=0,total_rows_inserted=0,total_rows_read=0,total_rows_updated=0 1634580099000000000
```

### Credits
[https://github.com/wavefrontHQ/integrations/db2](https://github.com/wavefrontHQ/integrations/tree/12c631f/db2) was initially used to create this plugin. 
