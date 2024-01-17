import json
import logging
import os
from datetime import datetime
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from mydisk_service.app.common.config import settings

router = APIRouter(prefix="/v1")
logger = logging.getLogger()


def convert_datetime_to_str(obj):
    if isinstance(obj, datetime):
        return obj.strftime("%a, %d %b %Y %H:%M:%S GMT")


def get_s3_client():
    s3 = boto3.client("s3", aws_access_key_id=settings.S3KEY, aws_secret_access_key=settings.S3SECRET, endpoint_url=settings.S3_URL)
    try:
        yield s3
    finally:
        s3.close()


@router.get("/bucket/list")
async def get_bucket_list(s3=Depends(get_s3_client)):
    response = s3.list_buckets()
    logger.debug(f"list bucket :: {response}")
    buckets = json.dumps(response["Buckets"], default=convert_datetime_to_str)
    logger.debug(buckets)
    return JSONResponse(
        status_code=200,
        content={
            "result": 1,
            "errorMessage": "",
            "data": {"body": buckets},
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

        return JSONResponse(status_code=201, content={"result": 1, "errorMessage": ""})
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
async def get_object(
    bucket_name: str,
    download_uuid: str,
    object_path: str = "",
    force: str = False,
    s3=Depends(get_s3_client),
):
    try:
        download_base_dir = os.path.join(settings.MYDISK_INFO.ROOT_DIR, "ADMIN", download_uuid)
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=object_path)
        logger.debug(response.get("Contents", []))
        for obj in response.get("Contents", []):
            s3_key = obj["Key"]
            download_path = os.path.join(download_base_dir, s3_key)
            os.makedirs(os.path.dirname(download_path), exist_ok=True)
            if force or not os.path.exists(download_path):
                s3.download_file(bucket_name, s3_key, download_path)

        logger.debug(f"{object_path} download to :: {download_base_dir}/{object_path}")

        return JSONResponse(status_code=200, content={"result": 1, "errorMessage": ""})
    except ClientError as e:
        logger.error(f"Error getting object: {e}")
        return JSONResponse(status_code=500, content={"result": 0, "errorMessage": str(e)})


@router.post("/object")
async def upload_object(bucket_name: str, object_path: Optional[str] = "", s3=Depends(get_s3_client)):
    try:
        s3.head_bucket(Bucket=bucket_name)
    except ClientError:
        s3.create_bucket(Bucket=bucket_name)
        logger.info(f"Bucket {bucket_name} created successfully (with upload)")

    try:
        local_base_dir = os.path.join(settings.MYDISK_INFO.ROOT_DIR, "ADMIN", bucket_name)
        object_full_path = os.path.join(local_base_dir, object_path)
        logger.debug(object_full_path)
        if os.path.isdir(object_full_path):
            for root, dirs, files in os.walk(object_full_path):
                for file in files:
                    local_path = os.path.join(root, file)
                    s3_path = os.path.relpath(local_path, local_base_dir)
                    await upload_file_one(bucket_name=bucket_name, local_path=local_path, s3_path=s3_path, s3=s3)
                    logger.debug(f"Object {local_path} uploaded to {bucket_name}/{s3_path} successfully")
        else:
            await upload_file_one(bucket_name, object_full_path, object_path, s3)
            logger.debug(f"upload one {object_full_path}/{object_path}")
        return JSONResponse(status_code=200, content={"result": 1, "errorMessage": ""})
    except ClientError as e:
        print(f"Error uploading object: {e}")


async def upload_file_one(bucket_name, local_path, s3_path, s3):
    with open(local_path, "rb") as data:
        s3.upload_fileobj(data, bucket_name, s3_path)
