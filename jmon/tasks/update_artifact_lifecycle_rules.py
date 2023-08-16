
import jmon.artifact_storage

def update_artifact_lifecycle_rules():
    """Update the bucket lifecycle rules for artifact storage"""
    jmon.artifact_storage.ArtifactStorage().set_bucket_lifecycle_rules()
