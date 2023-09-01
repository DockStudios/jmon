import React, { Component } from "react";

import ReactFlow from 'reactflow';

import 'reactflow/dist/style.css';


class RunConfigGraph extends Component {
  constructor(props) {
    super(props);

  }

  render() {
    return (
      <div style={{ width: '100vh', height: '60%', minHeight: '800px' }}>
        <ReactFlow nodes={this.props.nodes} edges={this.props.edges} />
      </div>
    );
  }
}

export default RunConfigGraph;