
import json


class RunStepData:
    """Handle generation/interaction with run step data"""

    @property
    def storage_key(self):
        """Return storage key for artifact"""
        return f"{self._run.get_artifact_key()}/step-data.json"

    def __init__(self, artifact_storage, run):
        """Store member variables"""
        self._artifact_storage = artifact_storage
        self._run = run

    def upload_file(self):
        """Generate run step data file and upload"""
        data = self._run.root_step.as_dict()
        self._artifact_storage.upload_file(
            self.storage_key,
            content=json.dumps(data)
        )

    def get_data(self):
        """Obtain run step data from artifact storage"""
        data = self._artifact_storage.get_file(self.storage_key)
        if data:
            return json.loads(data)
