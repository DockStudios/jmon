
from jmon.step_status import StepStatus
from . import FlaskApp
from .utils import get_check_and_environment_by_name
import jmon.models
import jmon.run
from jmon import app
from jmon.run_step_data import RunStepData
from jmon.artifact_storage import ArtifactStorage


class BaseGraphNode:

    @property
    def id(self):
        """Return ID"""
        raise NotImplementedError

    @property
    def depth(self):
        """Depth of child nesting"""
        raise NotImplementedError

    @property
    def step_tree_itx(self):
        """Depth of child nesting"""
        raise NotImplementedError

    @property
    def x(self):
        """Return X co-ordinate"""
        return self.root_step.column_x + 20 + ((180 / self.root_step.max_child_depth) * (self.depth - 1))

    @property
    def y(self):
        """Return Y co-ordinate"""
        return (self.step_tree_itx * 65) + 110

    def __init__(self, step_data, root_step, step_itx):
        self.step_data = step_data
        self.root_step = root_step
        self.step_itx = step_itx
        self.children = self.get_child_steps()

    def get_element_data(self):
        """Return element data"""
        return {
            "id": self.id,
            "type": "end",
            "text": self.step_data.get("description"),
            "fill": "#F35C4F",
            "stroke": "#F35C4F",
            "fontColor": "#FFF",
            "x": self.x,
            "y": self.y
        }

    def get_child_steps(self):
        """Get child step objects"""
        # Update root max children
        return [
            ChildStepNode(step_data=child_data, root_step=self.root_step, parent_node=self, step_itx=child_itx)
            for child_itx, child_data in enumerate(self.step_data.get("children"))
        ]

    def get_child_step_ids(self):
        """Return list of child step IDs"""
        child_ids = [self.id]
        for child in self.children:
            child_ids += child.get_child_step_ids()
        return child_ids

    def get_all_elements(self):
        """Return all data"""
        elements = [self.get_element_data()]
        for child in self.children:
            elements += child.get_all_elements()
        return elements


class ChildStepNode(BaseGraphNode):
    
    @property
    def depth(self):
        """Depth of child nesting"""
        return self.parent_node.depth + 1

    @property
    def step_tree_itx(self):
        """Depth of child nesting"""
        return self.parent_node.step_tree_itx + (self.step_itx + 1)

    @property
    def id(self):
        """Return ID"""
        return f"{self.parent_node.id}.{self.step_itx + 1}"

    def __init__(self, parent_node, root_step, *args, **kwargs):
        self.parent_node = parent_node
        self.previous_root_step = root_step.previous_root_step
        super(ChildStepNode, self).__init__(*args, **kwargs, root_step=root_step)
        self.root_step.max_child_depth = max(self.root_step.max_child_depth, self.depth)


class RootGraphData(BaseGraphNode):

    @property
    def depth(self):
        """Depth of child nesting"""
        return 1

    @property
    def step_tree_itx(self):
        return 1

    @property
    def column_x(self):
        """Return X cordinate for start of column"""
        return self.step_itx * 300

    @property
    def id(self):
        """Return ID"""
        return f"s{self.step_itx + 1}"

    def __init__(self, previous_root_step, *args, **kwargs):
        self.max_child_depth = 1
        self.previous_root_step = previous_root_step
        self.parent_node = None
        super(RootGraphData, self).__init__(*args, **kwargs, root_step=self)

    def get_column_data(self):
        """Return column data"""
        return {
            "id": self.step_itx + 1,
            "type": "$sgroup",
            "groupChildren": self.get_child_step_ids(),
            "style": {
                "fill": "rgba(60, 201, 122, 0.05)"
            },
            "x": self.step_itx * 298.75,
            "y": 80
        }


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

    root_steps = step_data.get("children", [])


    column_data = []
    graph_elements = []
    previous_root_step = None
    root_step_count = 0
    for root_step_itx, root_step_data in enumerate(root_steps):
        root_step_count += 1

        root_step_obj = RootGraphData(step_data=root_step_data, step_itx=root_step_itx, previous_root_step=previous_root_step)

        column_data.append(root_step_obj.get_column_data())
        graph_elements += root_step_obj.get_all_elements()

        previous_root_step = root_step_obj


    return [
        {
            "id": "main",
            "type": "$swimlane",
            "height": 730,
            "width": 300 * root_step_count,
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
        *column_data,
        *graph_elements
    ]
