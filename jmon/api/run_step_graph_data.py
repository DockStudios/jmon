
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
        return self.root_step.column_x + 20 + (((self.root_step.WIDTH - 120) / self.root_step.max_child_depth) * (self.depth - 1))

    @property
    def y(self):
        """Return Y co-ordinate"""
        return (self.step_tree_itx * 110) + 110

    def __init__(self, step_data, root_step, step_itx, connecting_node):
        self.step_data = step_data
        self.root_step = root_step
        self.step_itx = step_itx
        self.connecting_node = connecting_node
        self.children = self.get_child_steps()

    def get_status_color(self, opacity):
        """Return CSS color for step status"""
        root_step_colors = {
            StepStatus.INTERNAL_ERROR.value: "rgba(243, 92, 79, {opacity})",
            StepStatus.FAILED.value: "rgba(243, 92, 79, {opacity})",
            StepStatus.TIMEOUT.value: "rgba(155, 96, 248, {opacity})",
            StepStatus.SUCCESS.value: "rgba(60, 201, 122, {opacity})",
            StepStatus.NOT_RUN.value: "rgba(192, 192, 192, {opacity})",
            StepStatus.RUNNING.value: "rgba(255, 160, 0, {opacity})",
        }
        color = ""
        if (status := self.step_data.get("status")) and (color := root_step_colors.get(status, "")):
            color = color.format(opacity=opacity)
        return color

    def get_element_data(self):
        """Return element data"""
        return {
            "id": self.id,
            "type": "rectangle",
            "text": self.step_data.get("description"),
            "fill": self.get_status_color('0.8'),
            "stroke": self.get_status_color('1.0'),
            "fontColor": "#FFF",
            "x": self.x,
            "y": self.y
        }

    def get_child_steps(self):
        """Get child step objects"""
        # Update root max children
        connecting_node = self
        child_nodes = []
        for child_itx, child_data in enumerate(self.step_data.get("children")):
            child_node = ChildStepNode(step_data=child_data, root_step=self.root_step, parent_node=self, step_itx=child_itx, connecting_node=connecting_node)
            child_nodes.append(child_node)
            connecting_node = child_node.get_last_node()
        return child_nodes

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

    def get_all_lines(self):
        """Return all line data"""
        lines = [self.get_connecting_line()]
        for child in self.children:
            lines += child.get_all_lines()
        return [line for line in lines if line]

    def get_last_node(self):
        """Return last node"""
        if self.children:
            return self.children[-1].get_last_node()
        return self

    def get_connecting_line(self):
        """Return connection line from """
        if not self.connecting_node:
            return {}

        # Three types of lines:
        # - parent to child element
        # - child to sibling element
        # - element to new root
        return {
            "id": f"u{self.id}",
            "type": "line",
            "points": [],
            "stroke": "#7D878F",
            "connectType": "elbow",
            "strokeWidth": 2,
            "cornersRadius": "10",
            "from": self.id,
            "to": self.connecting_node.id,
            # Connect to left when connecting to a root, otherwise top
            "fromSide": "left" if isinstance(self, RootGraphData) else "top",
            # Connect from bottom for siblings, otherwise from the right
            "toSide": "bottom" if isinstance(self, ChildStepNode) and self.step_itx > 0 else "right",
            "strokeType": "line",
            "backArrow": "filled",
            "forwardArrow": ""
        }



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
    def WIDTH(self):
        """Return width from graph generator"""
        return self.graph_generator.column_width

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
        return (self.previous_root_step.column_x + self.previous_root_step.WIDTH if self.previous_root_step else 0)

    @property
    def id(self):
        """Return ID"""
        return f"s{self.step_itx + 1}"

    def __init__(self, graph_generator, previous_root_step, *args, **kwargs):
        """Store member variables and setup children"""
        self.max_child_depth = 1
        self.previous_root_step = previous_root_step
        self.graph_generator = graph_generator
        self.parent_node = None
        super(RootGraphData, self).__init__(*args, **kwargs, root_step=self, connecting_node=None)
        # Obtain connecting node from last step of previous node
        if self.previous_root_step is not None:
            self.connecting_node = self.previous_root_step.get_last_node()

        # Set width in graph generator based on max depth of steps
        self.graph_generator.column_width = max(self.graph_generator.column_width, 70 * self.max_child_depth)

    def get_header_data(self):
        """Return header data for root step"""
        return {
            "text": self.step_data.get("name"),
            "fill": self.get_status_color("0.4")
        }

    def get_column_data(self):
        """Return column data"""
        return {
            "id": self.step_itx + 1,
            "type": "$sgroup",
            "groupChildren": self.get_child_step_ids(),
            "style": {
                "fill": self.get_status_color("0.05")
            },
            "x": self.step_itx * (self.WIDTH - 1.25),
            "y": 80,
            "width": self.WIDTH
        }


class GraphGenerator:

    def __init__(self, step_data):
        """Generate graph nodes"""
        previous_root_step = None
        self.column_width = 300

        self.root_step_objects = []
        for root_step_itx, root_step_data in enumerate(step_data):
            root_step_obj = RootGraphData(
                graph_generator=self,
                step_data=root_step_data,
                step_itx=root_step_itx,
                previous_root_step=previous_root_step
            )
            self.root_step_objects.append(root_step_obj)
            previous_root_step = root_step_obj

    def generate_graph_data(self):
        """Return graph data"""
        column_data = []
        column_data = []
        graph_elements = []
        lines = []
        headers = []

        for root_step_obj in self.root_step_objects:
            column_data.append(root_step_obj.get_column_data())
            graph_elements += root_step_obj.get_all_elements()
            lines += root_step_obj.get_all_lines()
            headers.append(root_step_obj.get_header_data())

        width = self.column_width * len(self.root_step_objects)
        layout = [
            [
                step_itx + 1
                for step_itx, _ in enumerate(self.root_step_objects)
            ]
        ]

        return [
            {
                "id": "main",
                "type": "$swimlane",
                "height": 730,
                "width": width,
                "header": {
                    "closable": False,
                    "text": ""
                },
                "layout": layout,
                "subHeaderCols": {
                    "headers": headers
                }
            },
            *column_data,
            *graph_elements,
            *lines
        ]


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

    if not step_data:
        return {}, 404

    root_steps = step_data.get("children", [])

    graph_generator = GraphGenerator(root_steps)

    return graph_generator.generate_graph_data()
