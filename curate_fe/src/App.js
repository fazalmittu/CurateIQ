import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import ResearcherForm from './components/ResearcherForm';
import Feed from './components/Feed';
import { FaSearch } from 'react-icons/fa';
import './App.css';

function App() {
    return (
        <Router>
            <div className="App">
                <h1>
                    <FaSearch style={{ marginRight: '10px' }} />
                    Curate IQ
                </h1>
                <Routes>
                    <Route path="/" element={<ResearcherForm />} />
                    <Route path="/feed" element={<Feed />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;