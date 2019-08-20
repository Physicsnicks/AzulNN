import React from 'react';
import { Container, Row, Col } from 'reactstrap';
import factdisc from '../imgs/factdisc.png';
import bluetile from "../imgs/bluetile.png";
import yellowtile from "../imgs/yellowtile.png";
import redtile from "../imgs/redtile.png";
import blacktile from "../imgs/blacktile.png";
import snowtile from "../imgs/snowtile.png";
let tiles = [bluetile, yellowtile, redtile, blacktile, snowtile];

class Tile extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            value: null,
            source: tiles[this.props.imgnum],
            opac: "1.0"
        }
    }

    onDragStart = (ev, id) => {
        var sourceLoc = this.state.source
        ev.dataTransfer.setData("source",sourceLoc);

        //this.setState((state, props) => {
        //    return {source: null}
        //})
    }
    onDragOver = (ev) => {
        ev.preventDefault();
    }

    render() {
        return (
            <img
                src={this.state.source}
                className="square"
                onDragStart = {(e) => this.onDragStart(e, this.state.value)}
                draggable
                style={{
                    backgroundColor:this.state.bgColor,
                    height: 24,
                    opacity: this.state.opac,
                }}/>
        )
    }
}

class Disc extends React.Component {
    renderTile(i, j) {
        return <Tile value={i} imgnum={j} />;
    }

    render() {
        return (
            <Container className="disc-container">
                <div className="disc-tile">
                    {this.renderTile(0, 1)}
                    {this.renderTile(1, 2)}
                    {this.renderTile(2, 2)}
                    {this.renderTile(3, 0)}
                </div>
            </Container>
        );
    }
}

export class Factory extends React.Component {

    render() {
        return (
            <Container>
                <Row>
                    <Disc />
                </Row>
                <Row>
                    <Disc />
                </Row>
                <Row>
                    <Disc />
                </Row>
                <Row>
                    <Disc />
                </Row>
                <Row>
                    <Disc />
                </Row>
            </Container>

        );
    }
}