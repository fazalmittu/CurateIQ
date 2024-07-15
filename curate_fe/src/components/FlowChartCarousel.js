// src/components/FlowChartCarousel.js

import React from 'react';
import { Carousel } from 'react-responsive-carousel';
import "react-responsive-carousel/lib/styles/carousel.min.css"; // requires a loader
// import './FlowChartCarousel.css';

const FlowChartCarousel = ({ steps }) => {
    return (
        <Carousel showThumbs={false} showStatus={false} infiniteLoop useKeyboardArrows>
            {steps.map((step, index) => (
                <div key={index} className="carousel-slide">
                    <h3>{step.title}</h3>
                    <p>{step.description}</p>
                    <img src={step.img} alt={step.title} className="step-image" />
                </div>
            ))}
        </Carousel>
    );
};

export default FlowChartCarousel;
