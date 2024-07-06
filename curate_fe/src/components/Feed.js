import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { BeatLoader } from 'react-spinners';
import { FaFilePdf } from 'react-icons/fa';

const Feed = () => {
    const location = useLocation();
    const { papers = [], authorName, keywords = [] } = location.state || {};
    console.log('Received state in Feed:', { papers, authorName, keywords });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Simulate loading delay
        const timer = setTimeout(() => {
            setLoading(false);
        }, 1000);

        return () => clearTimeout(timer);
    }, []);

    const highlightKeywords = (text) => {
        if (!keywords || keywords.length === 0) return text;
        const regex = new RegExp(`(${keywords.join('|')})`, 'gi');
        return text.split(regex).map((part, index) =>
            regex.test(part) ? <strong key={index}>{part}</strong> : part
        );
    };

    return (
        <div>
            <h2 className="sub-header">Similar Papers for {authorName}</h2>
            {loading ? (
                <div className="loading-container">
                    <BeatLoader size={15} color={"#007bff"} loading={loading} />
                </div>
            ) : (
                <div className="papers">
                    {papers.map((paper) => (
                        <div key={paper.id} className="paper">
                            <h2>
                                <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer">
                                    {highlightKeywords(paper.title)}
                                </a>
                            </h2>
                            <p>{highlightKeywords(paper.summary)}</p>
                            <p><strong>Authors:</strong> {Array.isArray(paper.authors) ? paper.authors.join(', ') : paper.authors}</p>
                            <p><strong>Published:</strong> {paper.published}</p>
                            <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer">
                                <FaFilePdf /> Read Paper
                            </a>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Feed;