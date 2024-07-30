# PySpark Cannot write file or to database


You reach the end of the script to make the database and you get a warning indicating that pyspark cannot create a file or directory.

You'll see error messages like:

```
...
24/07/24 13:25:19 ERROR FileOutputCommitter: Mkdirs failed to create file:/oops/test_db/_temporary/0
24/07/24 13:25:20 WARN TaskSetManager: Stage 0 contains a task of very large size (1287 KiB). The maximum recommended task size is 1000 KiB.
24/07/24 13:25:22 ERROR Utils: Aborting task                        (0 + 1) / 1]
java.io.IOException: Mkdirs failed to create file:/oops/test_db/_temporary/0/_temporary/attempt_202407241325206051897238596390159_0000_m_000000_0/partition=pdg11_run0000_electron_test (exis
...
```

## Possible solutions

* Check that the output database folder is a place you have write access (or that the path exists).
* Check that when you start the singularity container, you have binded locations you have write access to. Example:
  ```
  -B /tmp:/tmp,/cluster:/cluster
  ```


## Example of getting the error

Example of repeatable error:

```
python3 test_save2petastormdb.py --input-edepsim test.root -ow --petastorm-db-folder /oops/test_db/ --tag electron_test --pdgcode 11 --runid 0
```

Note the intentionally bogus output directory path.


```
********** WRITING TO SPARK DB ***************
WARNING: An illegal reflective access operation has occurred
WARNING: Illegal reflective access by org.apache.spark.unsafe.Platform (file:/usr/local/lib/python3.8/dist-packages/pyspark/jars/spark-unsafe_2.12-3.2.0.jar) to constructor java.nio.DirectByteBuffer(long,int)
WARNING: Please consider reporting this to the maintainers of org.apache.spark.unsafe.Platform
WARNING: Use --illegal-access=warn to enable warnings of further illegal reflective access operations
WARNING: All illegal access operations will be denied in a future release
^[[BUsing Spark's default log4j profile: org/apache/spark/log4j-defaults.properties
Setting default log level to "WARN".
To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).
24/07/24 13:25:12 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
writing  5  entries into the database
store rows to parquet file
24/07/24 13:25:19 ERROR FileOutputCommitter: Mkdirs failed to create file:/oops/test_db/_temporary/0
24/07/24 13:25:20 WARN TaskSetManager: Stage 0 contains a task of very large size (1287 KiB). The maximum recommended task size is 1000 KiB.
24/07/24 13:25:22 ERROR Utils: Aborting task                        (0 + 1) / 1]
java.io.IOException: Mkdirs failed to create file:/oops/test_db/_temporary/0/_temporary/attempt_202407241325206051897238596390159_0000_m_000000_0/partition=pdg11_run0000_electron_test (exists=false, cwd=file:/cluster/tufts/wongjiradlabnu/twongj01/nutufts_edepsim_dataset_maker/simpledet/test)
	at org.apache.hadoop.fs.ChecksumFileSystem.create(ChecksumFileSystem.java:515)
	at org.apache.hadoop.fs.ChecksumFileSystem.create(ChecksumFileSystem.java:500)
	at org.apache.hadoop.fs.FileSystem.create(FileSystem.java:1195)
	at org.apache.hadoop.fs.FileSystem.create(FileSystem.java:1175)
	at org.apache.parquet.hadoop.util.HadoopOutputFile.create(HadoopOutputFile.java:74)
	at org.apache.parquet.hadoop.ParquetFileWriter.<init>(ParquetFileWriter.java:329)
	at org.apache.parquet.hadoop.ParquetOutputFormat.getRecordWriter(ParquetOutputFormat.java:482)
	at org.apache.parquet.hadoop.ParquetOutputFormat.getRecordWriter(ParquetOutputFormat.java:420)
	at org.apache.parquet.hadoop.ParquetOutputFormat.getRecordWriter(ParquetOutputFormat.java:409)
	at org.apache.spark.sql.execution.datasources.parquet.ParquetOutputWriter.<init>(ParquetOutputWriter.scala:36)
	at org.apache.spark.sql.execution.datasources.parquet.ParquetFileFormat$$anon$1.newInstance(ParquetFileFormat.scala:150)
	at org.apache.spark.sql.execution.datasources.BaseDynamicPartitionDataWriter.renewCurrentWriter(FileFormatDataWriter.scala:290)
	at org.apache.spark.sql.execution.datasources.DynamicPartitionDataSingleWriter.write(FileFormatDataWriter.scala:357)
	at org.apache.spark.sql.execution.datasources.FileFormatDataWriter.writeWithMetrics(FileFormatDataWriter.scala:85)
	at org.apache.spark.sql.execution.datasources.FileFormatDataWriter.writeWithIterator(FileFormatDataWriter.scala:92)
	at org.apache.spark.sql.execution.datasources.FileFormatWriter$.$anonfun$executeTask$1(FileFormatWriter.scala:304)
	at org.apache.spark.util.Utils$.tryWithSafeFinallyAndFailureCallbacks(Utils.scala:1496)
	at org.apache.spark.sql.execution.datasources.FileFormatWriter$.executeTask(FileFormatWriter.scala:311)
	at org.apache.spark.sql.execution.datasources.FileFormatWriter$.$anonfun$write$16(FileFormatWriter.scala:229)
	at org.apache.spark.scheduler.ResultTask.runTask(ResultTask.scala:90)
	at org.apache.spark.scheduler.Task.run(Task.scala:131)
	at org.apache.spark.executor.Executor$TaskRunner.$anonfun$run$3(Executor.scala:506)
	at org.apache.spark.util.Utils$.tryWithSafeFinally(Utils.scala:1462)
	at org.apache.spark.executor.Executor$TaskRunner.run(Executor.scala:509)
	at java.base/java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1128)
	at java.base/java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:628)
	at java.base/java.lang.Thread.run(Thread.java:829)
24/07/24 13:25:22 WARN FileOutputCommitter: Could not delete file:/oops/test_db/_temporary/0/_temporary/attempt_202407241325206051897238596390159_0000_m_000000_0
24/07/24 13:25:22 ERROR FileFormatWriter: Job job_202407241325206051897238596390159_0000 aborted.

...
```