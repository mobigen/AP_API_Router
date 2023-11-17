import logging
import os

import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from mydisk_service.app.common.config import settings
from mydisk_service.app.common.const import S3KEY, S3SECRET

router = APIRouter(prefix="/v1")
logger = logging.getLogger()


def get_s3_client():
    s3 = boto3.client("s3", aws_access_key_id=S3KEY, aws_secret_access_key=S3SECRET, endpoint_url=settings.S3_URL)
    try:
        yield s3
    finally:
        s3.close()


@router.get("/buckets")
async def get_bucket_list(s3=Depends(get_s3_client)):
    response = s3.list_buckets()
    return JSONResponse(
        status_code=200, content={"result": 1, "errorMessage": "", "data": {"body": list(response["Buckets"])}}
    )


@router.get("/buckets/one")
async def bucket_info(bucket_name: str, s3=Depends(get_s3_client)):
    try:
        res = s3.head_bucket(Bucket=bucket_name)
        return JSONResponse(status_code=200, content={"result": 1, "errorMessage": "", "data": {"body": res}})
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "404":
            logger.debug(f"Bucket {bucket_name} does not exist")
            return JSONResponse(
                status_code=error_code, content={"result": 1, "errorMessage": f"{bucket_name} not found"}
            )
        else:
            logger.error(f"Error checking bucket existence: {e}")
            return JSONResponse(status_code=500, content={"result": 0, "errorMessage": str(e)})


@router.post("/buckets/{bucket_name}/p")
async def create_bucket(bucket_name: str, s3=Depends(get_s3_client)):
    try:
        s3.create_bucket(Bucket=bucket_name)
        logger.info(f"Bucket {bucket_name} created successfully")

        return JSONResponse(status_code=200, content={"result": 1, "errorMessage": ""})
    except ClientError as e:
        logger.error(f"Error creating bucket: {e}")
        return JSONResponse(status_code=500, content={"result": 0, "errorMessage": str(e)})


@router.post("/buckets/{bucket_name}/d")
async def delete_bucket(bucket_name: str, s3=Depends(get_s3_client)):
    try:
        s3.delete_bucket(Bucket=bucket_name)
        logger.info(f"Bucket {bucket_name} deleted successfully")

        return JSONResponse(status_code=200, content={"result": 1, "errorMessage": ""})
    except ClientError as e:
        logger.error(f"Error deleting bucket: {e}")
        return JSONResponse(status_code=500, content={"result": 0, "errorMessage": str(e)})


@router.get("/buckets/{bucket_name}/objects")
async def get_object_list(bucket_name: str, s3=Depends(get_s3_client)):
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)

        return JSONResponse(
            status_code=200, content={"result": 1, "errorMessage": "", "data": {"body": response.get("Contents", [])}}
        )
    except ClientError as e:
        logger.error(f"Error listing objects: {e}")
        return JSONResponse(status_code=500, content={"result": 0, "errorMessage": str(e)})


@router.get("/buckets/{bucket_name}/objects/{object_name}")
async def get_object_one(bucket_name: str, object_name: str, s3=Depends(get_s3_client)):
    try:
        response = s3.get_object(Bucket=bucket_name, Key=object_name)
        data = response["Body"].read().decode("utf-8")
        # with open("path", "w") as f:
        #     f.write(data)

        logger.debug(f"{object_name} object content :: {data}")

        return JSONResponse(status_code=200, content={"result": 1, "errorMessage": "", "data": {"body": data}})
    except ClientError as e:
        logger.error(f"Error getting object: {e}")
        return JSONResponse(status_code=500, content={"result": 0, "errorMessage": str(e)})


@router.post("/buckets/{bucket_name}/objects/{object_name}")
async def upload_object_one(bucket_name: str, object_name: str, s3=Depends(get_s3_client)):
    try:
        s3.head_bucket(Bucket=bucket_name)
    except ClientError:
        s3.create_bucket(Bucket=bucket_name)
        logger.info(f"Bucket {bucket_name} created successfully (with upload)")

    try:
        with open(os.path.join("", object_name), "rb") as data:
            s3.upload_fileobj(data, bucket_name, object_name)
        logger.debug(f"Object {object_name} uploaded to {bucket_name} successfully")
    except ClientError as e:
        print(f"Error uploading object: {e}")


# create_new_bucket("test-bucket-1020")
# print_bucket_list()
# # delete_bucket('test-buecket-1020')
# # print_bucket_list()
# upload_object_to_bucket("./upload_example.txt", "upload_example.txt", "test-bucket-1020")
# print_object_list("test-bucket-1020")