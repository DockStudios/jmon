import React, { Component } from "react";

import ReactFlow from 'reactflow';

import 'reactflow/dist/style.css';
import './graph.css';


class RunConfigGraph extends Component {
  constructor(props) {
    super(props);

  }

  render() {
    return (
      <div style={{ width: '100%', height: '60%', minHeight: '800px', backgroundColor: '#eeeeee'}}>
        <ReactFlow
          nodesDraggable={false}
          panOnDrag={true}
          nodes={this.props.nodes}
          edges={this.props.edges}
          fitView={true}
          proOptions={{ hideAttribution: true }} />
      </div>
    );
  }
}

export default RunConfigGraph;