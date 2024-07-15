// src/components/LandingPage.js

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FaUser, FaListAlt, FaSearch, FaChartPie } from 'react-icons/fa';
import RankingAlgorithmChart from './RankingAlgorithmChart';
import './LandingPage.css';

const LandingPage = () => {
    const navigate = useNavigate();
    const steps = [
        {
            img: '/form.png',
            title: 'Step 1: Enter Researcher Information',
            description: 'Provide your name and subject area to get started.',
            icon: <FaUser size={50} color="#007bff" />,
        },
        {
            img: '/get_curated_feed.png',
            title: 'Step 2: Personalize Your Feed',
            description: 'The system finds your papers and asks which ones you want the feed to be based on.',
            icon: <FaListAlt size={50} color="#007bff" />,
        },
        {
            img: '/curated_feed.png',
            title: 'Step 3: Discover and Explore',
            description: 'Our powerful AI ranking system curates the best, latest papers for you.',
            icon: <FaSearch size={50} color="#007bff" />,
        },
        {
            img: <RankingAlgorithmChart />,
            title: 'Ranking Algorithm Overview',
            description: 'Our ranking algorithm combines multiple methods to determine the relevance of papers. The contributions of each method to the overall ranking are as follows: BM25: 35%, TF-IDF: 40%, Keyword Matching: 10%, Embedding: 15%.',
            icon: <FaChartPie size={50} color="#007bff" />,
        },
    ];

    return (
        <div className="landing-page">
            <main className="main-content">
                <h1>Curate IQ is the new way to discover research papers.</h1>
                <p>Beautifully designed, intelligent curation powered by advanced algorithms and machine learning.</p>
                <button className="get-started-button" onClick={() => navigate('/researcher_form')}>Get Started With Curate IQ for Free →</button>
            </main>
            <div className="steps-section">
                {steps.map((step, index) => (
                    <div className={`step-block ${index % 2 === 0 ? 'image-left' : 'image-right'}`} key={index}>
                        <div className="step-content">
                            {step.icon && <div className="icon">{step.icon}</div>}
                            <h2>{step.title}</h2>
                            <p>{step.description}</p>
                        </div>
                        <div className="step-image">
                            {typeof step.img === 'string' ? <img src={step.img} alt={step.title} /> : step.img}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default LandingPage;
