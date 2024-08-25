from dataclasses import dataclass

import boto3
from typing_extensions import override

from pfl.serverless.stores.base import ConfigParams, DataStoreConfig, ServerlessPFLStore


@dataclass
class S3ConfigParams(ConfigParams):
    bucket_name: str
    aws_access_key_id: str
    aws_secret_access_key: str
    region_name: str


@dataclass
class S3StoreConfig(DataStoreConfig):
    name = "s3"
    params: S3ConfigParams

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(self.name, *args, **kwargs)


class S3Store(ServerlessPFLStore):
    def __init__(self, config: S3StoreConfig) -> None:
        super().__init__(config)
        self._s3 = boto3.client(
            "s3",
            aws_access_key_id=config.params.aws_access_key_id,
            aws_secret_access_key=config.params.aws_secret_access_key,
            region_name=config.params.region_name,
        )

    @override
    def _get_data_for_key(self, key):
        return self._s3.get_object(Bucket=self.config.params.bucket_name, Key=key)["Body"].read()

    @override
    def _save_data_for_key(self, key, data) -> None:
        self._s3.put_object(Bucket=self.config.params.bucket_name, Key=key, Body=data)
