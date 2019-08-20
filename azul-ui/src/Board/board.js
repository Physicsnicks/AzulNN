import React from 'react';
import { Container, Row, Col } from 'reactstrap';

import redtile from '../imgs/redtile.png';
import bluetile from '../imgs/bluetile.png';
import yellowtile from '../imgs/yellowtile.png';
import snowtile from '../imgs/snowtile.png';
import blacktile from '../imgs/blacktile.png';
import emptytile from '../imgs/empty.png';
import '../index.css';

let tiles = [bluetile, yellowtile, redtile, blacktile, snowtile];
let sqW = 25;
let sqH = 25;
let score = 10;


class Square extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            bgColor: "gray",
            value: null,
            source: null,
        }
    }
    onDragOver = (ev) => {
        ev.preventDefault();
    }

    onDrop = (ev, cat) => {
        let newSource = ev.dataTransfer.getData("source");

        this.setState((state, props) => {

            return {source: newSource}
        })


    }
    render() {
        return (

            <img
                src={this.state.source}
                className="square"
                onDragOver={(e)=>this.onDragOver(e)}
                onDrop={(e)=>this.onDrop(e, "Done")}
                style={{
                    backgroundColor:this.state.bgColor,
                    height: sqH,
                    width: sqW,
                }}/>
        );
    }
}

class WallSquare extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            value: null
        }
    }

    render() {
        return (

            <img
                src={this.props.source}
                className="square"
                style={{
                    height: sqH,
                    width: sqW,
                    opacity: this.props.opac,
                }}/>
        );
    }
}
class EmptySquare extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            value: null
        }
    }

    render() {
        return (
            <img
                src={emptytile}
                className="empty-square"
                style={{
                    height: sqH,
                    width: sqW,
                    borderColor: "red",
                    borderWidth: 0,
                }}/>
        );
    }
}

class FloorSquare extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            bgColor: "gray",
            value: null,
            source: null,
        }
    }
    onDragOver = (ev) => {
        ev.preventDefault();
    }

    onDrop = (ev, cat) => {
        let newSource = ev.dataTransfer.getData("source");

        this.setState((state, props) => {

            return {source: newSource}
        })


    }
    render() {
        return (

            <img
                src={this.state.source}
                className="floor-square"
                onDragOver={(e)=>this.onDragOver(e)}
                onDrop={(e)=>this.onDrop(e, "Done")}
                style={{
                    backgroundColor:this.state.bgColor,
                    height: sqH,
                    width: sqW,
                }}/>
        );
    }
}

class GarageRow extends React.Component {


    renderRow(j) {
        let garageSquares = [];
        for (let i = 0; i < 5-j; i++){
            garageSquares.push(<EmptySquare key={(j-1)*5+i} />);
        }
        for (let i = 0; i < j; i++){
            garageSquares.push(<Square key={(j-1)*5+i+5-j} />);
        }
        return garageSquares;
    }

    render() {
        return (
            this.renderRow(this.props.rowLength)
        );
    }
}

class WallRow extends React.Component {

    renderRow(j) {
        let wallSquares = [];
        for (let i = 0; i < 5; i++){
            wallSquares.push(<WallSquare key={i} source={tiles[(i+j-1)%5]} opac={"0.25"} />);
        }
        return wallSquares;
    }

    render() {
        return (this.renderRow(this.props.rowNum));
    }
}

class Floor extends React.Component {
    renderRow() {
        let floorSquares = [];
        for (let i = 0; i < 7; i++){
            floorSquares.push(<FloorSquare key={i+20} />);
        }
        return floorSquares;
    }

    render() {
        return (this.renderRow())
    }
}

class FloorLabels extends React.Component {
    renderRow() {
        let floorLabels = [];
        let floorLabelNums = ['-1', '-1', '-2', '-2', '-2', '-3', '-3'];
        for (let i = 0; i < 7; i++){
            floorLabels.push(<label className='floor-label' key={i}>{floorLabelNums[i]}</label>);
        }
        return floorLabels;
    }

    render() {
        return (this.renderRow())
    }
}

export class Board extends React.Component {

    render() {
        const status = 'Grab some tiles';

        return (
            <Container className="board-container">
                <Row>
                    <label className="score-board">Score: {score}</label>
                </Row>
                <Row>
                    <GarageRow rowLength={1} className={"ad-right"} />
                    <WallRow rowNum={1} />
                </Row>
                <Row>
                    <GarageRow rowLength={2} className={"ad-right"} />
                    <WallRow rowNum={2} />
                </Row>
                <Row>
                    <GarageRow rowLength={3} className={"ad-right"} />
                    <WallRow rowNum={3} />
                </Row>
                <Row>
                    <GarageRow rowLength={4} className={"ad-right"} />
                    <WallRow rowNum={4} />
                </Row>
                <Row>
                    <GarageRow rowLength={5} className={"ad-right"} />
                    <WallRow rowNum={5} />
                </Row>
                <Row>
                    <FloorLabels />
                </Row>
                <Row>
                    <Floor />
                </Row>
            </Container>
        );
    }
}
