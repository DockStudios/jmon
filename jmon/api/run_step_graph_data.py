
from jmon.step_status import StepStatus
from . import FlaskApp
from .utils import get_check_and_environment_by_name
import jmon.models
import jmon.run
from jmon import app
from jmon.run_step_data import RunStepData
from jmon.artifact_storage import ArtifactStorage


@FlaskApp.app.route('/api/v1/checks/<check_name>/environments/<environment_name>/runs/<timestamp>/step-graph-data', methods=["GET"])
def get_run_step_graph_data(check_name, environment_name, timestamp):
    """Obtain run details"""
    check, _, error = get_check_and_environment_by_name(
        check_name=check_name, environment_name=environment_name)
    if error:
        return error, 404

    db_run = jmon.models.Run.get(
        check=check,
        timestamp_id=timestamp
    )
    if not db_run:
        return {
            "error": "Run does not exist"
        }, 400

    run = jmon.run.Run(check=check, db_run=db_run)

    step_data = RunStepData(
        artifact_storage=ArtifactStorage(),
        run=run
    ).get_data()

    root_step_colors = {
        StepStatus.INTERNAL_ERROR.value: "rgba(243, 92, 79, 0.4)",
        StepStatus.FAILED.value: "rgba(243, 92, 79, 0.4)",
        StepStatus.TIMEOUT.value: "rgba(155, 96, 248, 0.4)",
        StepStatus.SUCCESS.value: "rgba(60, 201, 122, 0.4)",
        StepStatus.NOT_RUN.value: "rgba(192, 192, 192, 0.4)",
    }

    if not step_data:
        return {}, 404

    print(step_data)
    root_steps = step_data.get("children", [])

    graph_root_steps = []
    graph_steps = []
    root_x_depths = []

    def process_root_step_children(root_step_children, root_step_itx, parent_name, x, y):
        nonlocal graph_steps
        nonlocal root_x_depths
        child_step_ids = []
        root_x_depths[root_step_itx] = max(root_x_depths[root_step_itx], x)
        
        for child_itx, child in enumerate(root_step_children):
            id_ = f"{parent_name}.{child_itx + 1}"
            child_step_ids.append(id_)
            graph_steps.append({
                "id": id_,
                "type": "end",
                "text": child.get("description"),
                "fill": "#F35C4F",
                "stroke": "#F35C4F",
                "fontColor": "#FFF",
                "x": x,
                "y": y
            })
            child_step_ids += process_root_step_children(child.get("children"), root_step_itx=root_step_itx, parent_name=id_, x=x+65, y=y+20)
        return child_step_ids

    for root_step_itx, root_step in enumerate(root_steps):
        # Copy root depth from previous root step
        root_step_x = 0
        if root_step_itx > 0:
            root_step_x = root_x_depths[root_step_itx - 1]
        previous_step_x = 0
        if root_step_itx > 1:
            previous_step_x = root_x_depths[root_step_itx - 2]

        # Ensure the start of this is at least 300 since previous, if not the first
        # column
        if root_step_itx > 0:
            root_step_x = max(root_step_x, previous_step_x + 300)
        root_x_depths.append(root_step_x)

        # Add element for root step
        graph_steps.append({
            "id": f"s{root_step_itx + 1}",
            "type": "end",
            "text": root_step.get("description"),
            "fill": "#F35C4F",
            "stroke": "#F35C4F",
            "fontColor": "#FFF",
            "x": root_step_x,
            "y": 80
        })
        # Add column data
        graph_root_steps.append({
            "id": root_step_itx + 1,
            "type": "$sgroup",
            "groupChildren": process_root_step_children(
                root_step.get("children"),
                root_step_itx,
                parent_name=f"s{root_step_itx + 1}",
                x=(root_step_x + 85),
                y=50
            ),
            "style": {
                "fill": "rgba(60, 201, 122, 0.05)"
            },
            "x": root_step_x + 20,
            "y": 30
        })

    return [
        {
            "id": "main",
            "type": "$swimlane",
            "height": 730,
            "width": 1195,
            "header": {
                "closable": False,
                "text": ""
            },
            "layout": [
                [
                    step_itx + 1
                    for step_itx, _ in enumerate(root_steps)
                ]
            ],
            "subHeaderCols": {
                "headers": [
                    {
                        "text": first_level_step.get("description"),
                        "fill": root_step_colors.get(first_level_step.get("status"), "")
                    }
                    for step_itx, first_level_step in enumerate(root_steps)
                ]
            }
        },
        *graph_root_steps,
        *graph_steps
    ]
