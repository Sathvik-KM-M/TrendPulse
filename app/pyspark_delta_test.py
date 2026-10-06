from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip

builder = (SparkSession.builder
    .appName('delta-test')
    .config('spark.sql.extensions', 'io.delta.sql.DeltaSparkSessionExtension')
    .config('spark.sql.catalog.spark_catalog', 'org.apache.spark.sql.delta.catalog.DeltaCatalog'))

spark = configure_spark_with_delta_pip(builder).getOrCreate()

df = spark.createDataFrame([(1, 'hello'), (2, 'world')], ['id', 'word'])
df.write.format('delta').mode('overwrite').save('/tmp/delta-test')

df2 = spark.read.format('delta').load('/tmp/delta-test')
df2.show()
spark.stop()
print('Delta works properly!')