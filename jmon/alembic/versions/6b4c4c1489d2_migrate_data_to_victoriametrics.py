"""Migrate data to victoriametrics

Revision ID: 6b4c4c1489d2
Revises: e1155219bf75
Create Date: 2024-03-05 06:23:52.646181

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from jmon.timeseries_database import TimeSeriesDatabaseFactory

# revision identifiers, used by Alembic.
revision = '6b4c4c1489d2'
down_revision = 'e1155219bf75'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # ### end Alembic commands ###
    timeseries_db = TimeSeriesDatabaseFactory.get_database()

    c = op.get_bind()
    runs = c.execute(f"""
        SELECT run.timestamp as timestamp,
            run.result_value as result_value,
            "check".name as check_name,
            environment.name as environment_name
        FROM run
        INNER JOIN "check" ON run.check_id="check".id
        INNER JOIN environment ON "check".environment_id=environment.id
    """)
    for run in runs:
        res = timeseries_db.write_metric(
            metric_name="jmon_result",
            properties={"check": run[2], "environment": run[3]},
            fields={"success": run[1]},
            timestamp=run[0]
        )
        if res is False:
            raise Exception("Could not push metric to victoriametrics")


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # ### end Alembic commands ###
    pass
