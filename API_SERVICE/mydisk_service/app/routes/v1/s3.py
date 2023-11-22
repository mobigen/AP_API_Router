import json
import logging
import os
from datetime import datetime

import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from mydisk_service.app.common.config import settings
from mydisk_service.app.common.const import S3KEY, S3SECRET

router = APIRouter(prefix="/v1")
logger = logging.getLogger()


def convert_datetime_to_str(obj):
    if isinstance(obj, datetime):
        return obj.strftime("%a, %d %b %Y %H:%M:%S GMT")


def get_s3_client():
    s3 = boto3.client("s3", aws_access_key_id=S3KEY, aws_secret_access_key=S3SECRET, endpoint_url=settings.S3_URL)
    try:
        yield s3
    finally:
        s3.close()


@router.get("/bucket/list")
async def get_bucket_list(s3=Depends(get_s3_client)):
    response = s3.list_buckets()
    logger.debug(f"list bucket :: {response}")
    return JSONResponse(
        status_code=200,
        content={
            "result": 1,
            "errorMessage": "",
            "data": {"body": json.dumps(response["Buckets"], default=convert_datetime_to_str)},
        },
    )


@router.get("/bucket/info")
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


@router.post("/bucket")
async def create_bucket(bucket_name: str, s3=Depends(get_s3_client)):
    try:
        s3.create_bucket(Bucket=bucket_name)
        logger.info(f"Bucket {bucket_name} created successfully")

        return JSONResponse(status_code=200, content={"result": 1, "errorMessage": ""})
    except ClientError as e:
        logger.error(f"Error creating bucket: {e}")
        return JSONResponse(status_code=500, content={"result": 0, "errorMessage": str(e)})


@router.post("/bucket/del")
async def delete_bucket(bucket_name: str, s3=Depends(get_s3_client)):
    try:
        s3.delete_bucket(Bucket=bucket_name)
        logger.info(f"Bucket {bucket_name} deleted successfully")

        return JSONResponse(status_code=200, content={"result": 1, "errorMessage": ""})
    except ClientError as e:
        logger.error(f"Error deleting bucket: {e}")
        return JSONResponse(status_code=500, content={"result": 0, "errorMessage": str(e)})


@router.get("/object/list")
async def get_object_list(bucket_name: str, s3=Depends(get_s3_client)):
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)

        return JSONResponse(
            status_code=200,
            content={
                "result": 1,
                "errorMessage": "",
                "data": {"body": json.dumps(response.get("Contents", []), default=convert_datetime_to_str)},
            },
        )
    except ClientError as e:
        logger.error(f"Error listing objects: {e}")
        return JSONResponse(status_code=500, content={"result": 0, "errorMessage": str(e)})


@router.get("/object/download")
async def get_object_one(bucket_name: str, object_name: str, s3=Depends(get_s3_client)):
    try:
        response = s3.get_object(Bucket=bucket_name, Key=object_name)
        data = response["Body"].read().decode("utf-8")
        with open(os.path.join(settings.MYDISK_INFO.ROOT_DIR, bucket_name, object_name), "w") as f:
            f.write(data)

        logger.debug(f"{object_name} object content :: {data}")

        return JSONResponse(status_code=200, content={"result": 1, "errorMessage": ""})
    except ClientError as e:
        logger.error(f"Error getting object: {e}")
        return JSONResponse(status_code=500, content={"result": 0, "errorMessage": str(e)})


@router.post("/object")
async def upload_object_one(bucket_name: str, object_name: str, s3=Depends(get_s3_client)):
    try:
        s3.head_bucket(Bucket=bucket_name)
    except ClientError:
        s3.create_bucket(Bucket=bucket_name)
        logger.info(f"Bucket {bucket_name} created successfully (with upload)")

    try:
        with open(os.path.join(settings.MYDISK_INFO.ROOT_DIR, bucket_name, object_name), "rb") as data:
            s3.upload_fileobj(data, bucket_name, object_name)
        logger.debug(f"Object {object_name} uploaded to {bucket_name} successfully")
    except ClientError as e:
        print(f"Error uploading object: {e}")
