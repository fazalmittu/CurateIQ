import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useLocation } from 'react-router-dom';
import { BeatLoader } from 'react-spinners';
import { FaFilePdf } from 'react-icons/fa';

const Feed = () => {
    const location = useLocation();
    const { authorName, subjectArea } = location.state;
    const [papers, setPapers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchPapers = async () => {
            try {
                const response = await axios.get(`http://127.0.0.1:5000/api/similar_papers?authorName=${authorName}&category=${subjectArea}`);
                setPapers(response.data);
            } catch (error) {
                console.error('Error fetching papers', error);
            } finally {
                setLoading(false);
            }
        };

        fetchPapers();
    }, [authorName, subjectArea]);

    return (
        <div>
            <h2 className="sub-header">Similar Papers for {authorName}</h2>
            {loading ? (
                <BeatLoader size={15} color={"#007bff"} loading={loading} />
            ) : (
                <div className="papers">
                    {papers.map((paper) => (
                        <div key={paper.id} className="paper">
                            <h2>
                                <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer">
                                    {paper.title}
                                </a>
                            </h2>
                            <p>{paper.summary}</p>
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