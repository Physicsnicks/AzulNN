import React from 'react';
import './App.css';
import { Board } from './Board/board';
import { Factory } from "./Factory/factory";
import './'
import { Container, Row, Col } from 'reactstrap';


class Game extends React.Component {
    render() {
        return (
            <Container>
                <Row>
                    <Col>
                        <Factory />
                    </Col>
                </Row>
                <Row>
                    <Col>
                        <Board />
                    </Col>
                </Row>
            </Container>
        );
    }
}

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <Game />
      </header>
    </div>
  );
}

export default App;
