
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
        return (self.step_tree_itx * 130) + 20

    def __init__(self, step_data, root_step, step_itx, connecting_node):
        self.step_data = step_data
        self.root_step = root_step
        self.step_itx = step_itx
        self.connecting_node = connecting_node
        self.children = self.get_child_steps()

        # Update graph generator height based on this element's y position
        self.root_step.graph_generator.height = max(self.root_step.graph_generator.height, self.y + 110)

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
            "data": {
                "label": self.step_data.get("description") if len(self.step_data.get("description")) < 70 else f'{self.step_data.get("description")[0:70]}...'
            },
            "position": {
                "x": self.x,
                "y": self.y
            },
            "style": {
                "backgroundColor": self.get_status_color('0.8'),
                # "height": 150,
                # "width": 270
            },
            "className": "light",
            "parentNode": self.root_step.column_id,
            # "extent": "parent"
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

        return {
            "id": f"e{self.connecting_node.id}-{self.id}",
            "source": self.connecting_node.id,
            "target": self.id
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

    @property
    def column_id(self):
        """Return column ID"""
        return str(self.step_itx + 1)

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
            "id": self.column_id,
            "data": {
                "label": self.step_data.get("name")
            },
            "position": {
                "x": self.x,
                "y": self.y
            },
            "className": "light",
            "style": {
                "backgroundColor": self.get_status_color("0.05"),
                "width": self.WIDTH,
                "height": self.graph_generator.height
            }
        }


class GraphGenerator:

    def __init__(self, step_data):
        """Generate graph nodes"""
        previous_root_step = None
        self.column_width = 300
        self.height = 730

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

        return {
            "nodes": column_data + graph_elements,
            "edges": lines
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

    if not step_data:
        return {}, 404

    root_steps = step_data.get("children", [])

    graph_generator = GraphGenerator(root_steps)

    return graph_generator.generate_graph_data()
