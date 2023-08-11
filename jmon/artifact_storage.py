
from io import BytesIO

import boto3
import boto3.session
import botocore.exceptions

import jmon.config
from jmon.logger import logger


class ArtifactStorage:

    _INSTANCE = None

    @classmethod
    def get_instance(cls):
        """Return singleton instance of class"""
        if cls._INSTANCE is None:
            cls._INSTANCE = cls()
        return cls._INSTANCE

    def __init__(self):
        """Create client"""
        s3_kwargs = {}
        if endpoint := jmon.config.Config.get().AWS_ENDPOINT:
            s3_kwargs['endpoint_url'] = endpoint
            s3_kwargs['config'] = boto3.session.Config(signature_version='s3v4')
        self._s3_client = boto3.client('s3', **s3_kwargs)
        self._s3_resource = boto3.resource('s3', **s3_kwargs)

    def _get_bucket(self):
        """Get bucket object"""
        return self._s3_resource.Bucket(
            jmon.config.Config.get().AWS_BUCKET_NAME
        )

    def set_bucket_lifecycle_rules(self):
        """Set bucket lifecycle rules"""
        if expiration := jmon.config.Config.get().RESULT_ARTIFACT_RETENTION_DAYS:
            logger.info(f"Setting bucket expiration to {expiration} days")
            bucket_lifecycle_configuration = self._s3_resource.BucketLifecycleConfiguration(
                jmon.config.Config.get().AWS_BUCKET_NAME)

            response = bucket_lifecycle_configuration.put(
                LifecycleConfiguration={
                    'Rules': [
                        {
                            'Expiration': {
                                'Days': expiration
                            },
                            'Filter': {
                                'Prefix': ''
                            },
                            'ID': 'DeleteExpiredArtifacts',
                            'Status': 'Enabled'
                        }
                    ]
                }
            )
            logger.debug(f"Got response: {response}")
        else:
            logger.info(f"Bucket expiration not set... skipping")

    def upload_file(self, path, content=None, source_path=None):
        """Upload log to s3"""
        # If a source path is provided, read content from file
        if source_path:
            with open(source_path, 'rb') as fh:
                content = fh.read()

        self._get_bucket().put_object(
            Key=path,
            Body=content
        )

    def list_files(self, path_prefix):
        """List files in path prefix"""
        return [
            file.key
            for file in self._get_bucket().objects.filter(Prefix=path_prefix)
        ]

    def get_file(self, path):
        """Get content for artifact"""
        content = BytesIO()
        try:
            self._get_bucket().download_fileobj(Key=path, Fileobj=content)
        except botocore.exceptions.ClientError:
            return None
        content.seek(0)
        return content.read()
