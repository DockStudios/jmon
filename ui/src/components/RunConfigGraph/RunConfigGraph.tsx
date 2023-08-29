import React, { Component } from "react";
import '../../Graph/diagramWithEditor.css';


class RunConfigGraph extends Component {
  constructor(props) {
    super(props);

    this.defaults = {
      start: {
        fill: "#F35A4F",
        stroke: "#F35A4F",
        fontColor: "#FFFFFF",
        strokeWidth: 2,
      },
      circle: {
        fill: "#F35A4F",
        stroke: "#F35A4F",
        fontColor: "#FFFFFF",
        strokeWidth: 2,
      },
      rectangle: {
        fill: "#FFFFFF",
        stroke: "#F35A4F",
        fontColor: "#4C4C4C",
        strokeWidth: 2,
      },
    };
  }

  componentDidMount() {
    // eslint-disable-next-line no-undef
    this.diagram = new dhx.Diagram("diagram", {
      type: "default",
      defaults: this.defaults,
    });

    console.log(this.props.graphData);
    
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.graphData) {
      this.diagram.data.parse(nextProps.graphData);
    }
  }

  componentWillUnmount() {
    this.diagram && this.diagram.destructor();
  }

  render() {
    return (
      <div className="dhx-container_inner dhx_sample-container__with-editor">
        <div className="dhx_sample-widget" id="diagram"></div>
      </div>
    );
  }
}

export default RunConfigGraph;