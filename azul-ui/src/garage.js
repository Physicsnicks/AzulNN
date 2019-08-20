import React from 'react';

export default function GarageSquare({ red, children }) {
    const fill = red ? 'red' : 'gray'
    return <div style={{
        backgroundColor: fill,
        width: '100%',
        height: '100%',
    }} >
        {children}
    </div>
}