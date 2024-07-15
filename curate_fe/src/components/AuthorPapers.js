import React, { useEffect, useState, useLayoutEffect, useRef } from 'react';
import axios from 'axios';
import { useNavigate, useLocation } from 'react-router-dom';
import { BeatLoader } from 'react-spinners';

const AuthorPapers = () => {
    const location = useLocation();
    const { authorName, subjectArea } = location.state;
    const [papers, setPapers] = useState([]);
    const [selectedPapers, setSelectedPapers] = useState([]);
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [selectAll, setSelectAll] = useState(false);
    const buttonContainerRef = useRef(null);

    useEffect(() => {
        const fetchPapers = async () => {
            setLoading(true);
            try {
                const response = await axios.get(`https://sheltered-shore-45178-a9d722462cf3.herokuapp.com/api/author_papers?authorName=${authorName}`);
                // const response = await axios.get(`http://127.0.0.1:5000/api/author_papers?authorName=${authorName}`);
                setPapers(response.data);
            } catch (error) {
                console.error('Error fetching papers', error);
            } finally {
                setLoading(false);
                setSelectAll(false);
            }
        };

        fetchPapers();
    }, [authorName]);

    useLayoutEffect(() => {
        if (buttonContainerRef.current) {
            const buttons = buttonContainerRef.current.querySelectorAll('.curate-button');
            buttons.forEach(button => {
                button.style.width = '150px';
                button.style.marginRight = '15px';
            });
        }
    }, [loading]);

    const handleCheckboxChange = (paperId) => {
        setSelectedPapers(prevSelectedPapers =>
            prevSelectedPapers.includes(paperId)
                ? prevSelectedPapers.filter(id => id !== paperId)
                : [...prevSelectedPapers, paperId]
        );
    };

    const handleSelectAll = () => {
        setSelectAll(!selectAll);
        if (!selectAll) {
            setSelectedPapers(papers.map(paper => paper.id));
        } else {
            setSelectedPapers([]);
        }
    };

    const handleSubmit = async () => {
        setLoading(true);
        try {
            const response = await axios.get('https://sheltered-shore-45178-a9d722462cf3.herokuapp.com/api/similar_papers', {
                params: {
                    authorName,
                    category: subjectArea,
                    selectedPaperIds: selectedPapers.join(',')
                }
            });
            // const response = await axios.get('http://127.0.0.1:5000/api/similar_papers', {
            //     params: {
            //         authorName,
            //         category: subjectArea,
            //         selectedPaperIds: selectedPapers.join(',')
            //     }
            // });
            console.log('Navigating to feed with state:', { papers: response.data.papers, authorName, keywords: response.data.keywords });
            navigate('/feed', { state: { papers: response.data.papers, authorName, keywords: response.data.keywords } });
        } catch (error) {
            console.error('Error fetching similar papers', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="loading-container">
                <BeatLoader size={15} color={"#007bff"} loading={loading} />
            </div>
        );
    }

    if (papers.length === 0) {
        return (
            <div className="no-papers-container">
                <h2>No papers found for '{authorName}'</h2>
                <button onClick={() => navigate('/')}>Go Back</button>
            </div>
        );
    }

    return (
        <div>
            <h2 className="loading-text">{loading ? 'Loading your papers...' : 'Select Papers for Curated Feed'}</h2>
            {!loading && (
                <div className="button-container" ref={buttonContainerRef}>
                    <button className="curate-button" onClick={handleSubmit}>Get Curated Feed</button>
                    <button className="curate-button" onClick={handleSelectAll}>
                        {selectAll ? 'Deselect All' : 'Select All'}
                    </button>
                </div>
            )}
            <div className="papers">
                {papers.map((paper) => (
                    <div key={paper.id} className="paper">
                        <div className="paper-info">
                            <h2>
                                <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer">
                                    {paper.title}
                                </a>
                            </h2>
                            <p>{paper.summary}</p>
                            <p><strong>Authors:</strong> {Array.isArray(paper.authors) ? paper.authors.join(', ') : paper.authors}</p>
                        </div>
                        <div className="paper-actions">
                            <label htmlFor={`checkbox-${paper.id}`} style={{ cursor: 'pointer' }}>
                                <input
                                    id={`checkbox-${paper.id}`}
                                    type="checkbox"
                                    checked={selectedPapers.includes(paper.id)}
                                    onChange={() => handleCheckboxChange(paper.id)}
                                    style={{ cursor: 'pointer' }}
                                />
                            </label>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default AuthorPapers;
