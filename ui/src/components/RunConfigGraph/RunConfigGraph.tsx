import React, { Component } from "react";

import ReactFlow from 'reactflow';

import 'reactflow/dist/style.css';


class RunConfigGraph extends Component {
  constructor(props) {
    super(props);

  }

  render() {
    return (
      <div style={{ width: '100%', height: '60%', minHeight: '800px' }}>
        <ReactFlow
          nodesDraggable={false}
          panOnDrag={true}
          nodes={this.props.nodes}
          edges={this.props.edges}
          proOptions={{ hideAttribution: true }} />
      </div>
    );
  }
}

export default RunConfigGraph;