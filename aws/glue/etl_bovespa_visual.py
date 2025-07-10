import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from awsglue import DynamicFrame
from pyspark.sql import functions as SqlFuncs

def sparkSqlQuery(glueContext, query, mapping, transformation_ctx) -> DynamicFrame:
    for alias, frame in mapping.items():
        frame.toDF().createOrReplaceTempView(alias)
    result = spark.sql(query)
    return DynamicFrame.fromDF(result, glueContext, transformation_ctx)
def sparkAggregate(glueContext, parentFrame, groups, aggs, transformation_ctx) -> DynamicFrame:
    aggsFuncs = []
    for column, func in aggs:
        aggsFuncs.append(getattr(SqlFuncs, func)(column))
    result = parentFrame.toDF().groupBy(*groups).agg(*aggsFuncs) if len(groups) > 0 else parentFrame.toDF().agg(*aggsFuncs)
    return DynamicFrame.fromDF(result, glueContext, transformation_ctx)

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Script generated for node Amazon S3
AmazonS3_node1749690961519 = glueContext.create_dynamic_frame.from_options(format_options={}, connection_type="s3", format="parquet", connection_options={"paths": ["s3://bck-bovespa/raw/"], "recurse": True}, transformation_ctx="AmazonS3_node1749690961519")

# Script generated for node Drop Duplicates
DropDuplicates_node1749691095632 =  DynamicFrame.fromDF(AmazonS3_node1749690961519.toDF().dropDuplicates(), glueContext, "DropDuplicates_node1749691095632")

# Script generated for node SQL Query
SqlQuery0 = '''
select m.*, 
cast(replace(part,",",".")as decimal(10,3))as part,
cast(replace(partAcum,",",".")as decimal(10,3))as partAcum,
cast(replace(theoricalQty,".","") as bigint)as theoricalQty
from myDataSource m
'''
SQLQuery_node1749692597878 = sparkSqlQuery(glueContext, query = SqlQuery0, mapping = {"myDataSource":DropDuplicates_node1749691095632}, transformation_ctx = "SQLQuery_node1749692597878")

# Script generated for node Change Schema
ChangeSchema_node1749691305107 = ApplyMapping.apply(frame=SQLQuery_node1749692597878, mappings=[("segment", "string", "setor", "string"), ("cod", "string", "codigo", "string"), ("asset", "string", "acao", "string"), ("type", "string", "tipo", "string"), ("part", "decimal", "part", "double"), ("partAcum", "decimal", "part_acum", "double"), ("theoricalQty", "long", "qtd_teorica", "bigint"), ("dt_ref", "string", "dt_ref", "date")], transformation_ctx="ChangeSchema_node1749691305107")

# Script generated for node Aggregate
Aggregate_node1749691185039 = sparkAggregate(glueContext, parentFrame = ChangeSchema_node1749691305107, groups = ["setor", "acao", "dt_ref", "codigo"], aggs = [["qtd_teorica", "sum"]], transformation_ctx = "Aggregate_node1749691185039")

# Script generated for node Rename Field
RenameField_node1749693557003 = RenameField.apply(frame=Aggregate_node1749691185039, old_name="`sum(qtd_teorica)`", new_name="soma_qtd_teorica", transformation_ctx="RenameField_node1749693557003")

# Script generated for node Amazon S3
AmazonS3_node1749691627621 = glueContext.getSink(path="s3://bck-bovespa/refined/", connection_type="s3", updateBehavior="UPDATE_IN_DATABASE", partitionKeys=["dt_ref", "codigo"], enableUpdateCatalog=True, transformation_ctx="AmazonS3_node1749691627621")
AmazonS3_node1749691627621.setCatalogInfo(catalogDatabase="catalog",catalogTableName="bovespa")
AmazonS3_node1749691627621.setFormat("glueparquet", compression="snappy")
AmazonS3_node1749691627621.writeFrame(RenameField_node1749693557003)
job.commit()