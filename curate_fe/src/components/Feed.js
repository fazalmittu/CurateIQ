import React, { useEffect, useState, PureComponent } from 'react';
import { useLocation } from 'react-router-dom';
import { BeatLoader } from 'react-spinners';
import { FaFilePdf, FaInfoCircle } from 'react-icons/fa';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Sector } from 'recharts';
import Modal from 'react-modal';

// const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];
const COLORS = ['#051e47', '#2e4161', '#2e70db', '#97accf'];

Modal.setAppElement('#root'); // Add this line

const Feed = () => {
    const location = useLocation();
    const { papers = [], authorName = '', keywords = [] } = location.state || {};
    console.log('Received state in Feed:', { papers, authorName, keywords });
    const [loading, setLoading] = useState(true);
    const [modalIsOpen, setModalIsOpen] = useState(false);

    useEffect(() => {
        const timer = setTimeout(() => {
            setLoading(false);
        }, 1000);

        return () => clearTimeout(timer);
    }, []);

    const highlightKeywords = (text, isTitle = false) => {
        if (!text || !keywords || keywords.length === 0 || isTitle) return text;
        const words = text.split(/(\s+)/); // Split by whitespace, preserving whitespace
        const regex = new RegExp(keywords.join('|'), 'gi');
        return words.map((word, index) => 
            regex.test(word) ? <strong key={index}>{word}</strong> : word
        );
    };

    const renderPieChart = (paper) => {
        const data = [
            { name: 'Embedding', value: paper.embedding_score },
            { name: 'Keyword', value: paper.keyword_score },
            { name: 'TF-IDF', value: paper.tfidf_score },
            { name: 'BM25', value: paper.bm25_score },
        ];

        return (
            <ResponsiveContainer width={200} height={200}>
                <PieChart>
                    <Pie
                        data={data}
                        cx="50%"
                        cy="50%"
                        innerRadius={50}  // Adjusted to make segments thicker
                        outerRadius={90}  // Adjusted to make segments thicker
                        fill="#8884d8"
                        paddingAngle={5}
                        dataKey="value"
                    >
                        {data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                    </Pie>
                    <Tooltip formatter={(value, name) => [name]} />
                    <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle" style={{ fontSize: '24px', fontWeight: 'bold' }}>
                        {paper.combined_score.toFixed(2)}
                    </text>
                </PieChart>
            </ResponsiveContainer>
        );
    };

    const openModal = () => {
        setModalIsOpen(true);
    };

    const closeModal = () => {
        setModalIsOpen(false);
    };

    const handleOverlayClick = (event) => {
        if (event.target.className.includes('ReactModal__Overlay')) {
            closeModal();
        }
    };

    const sortedPapers = [...papers].sort((a, b) => b.combined_score - a.combined_score);

    return (
        <div className={modalIsOpen ? 'blur' : ''}> {/* Apply blur class here */}
            <h2 className="sub-header">
                Similar Papers for {authorName}
                <FaInfoCircle onClick={openModal} style={{ cursor: 'pointer', color: '#0056b3', marginLeft: '10px', position: 'relative', top: '3px' }} />
            </h2>
            {loading ? (
                <div className="loading-container">
                    <BeatLoader size={15} color={"#007bff"} loading={loading} />
                </div>
            ) : (
                <div className={`papers`}>
                    {sortedPapers.length === 0 ? (
                        <p>No papers found.</p>
                    ) : (
                        sortedPapers.map((paper) => (
                            <div key={paper.metadata.id} className="paper">
                                <div className="paper-info">
                                    <h2>
                                        <a href={paper.metadata.pdf_url} target="_blank" rel="noopener noreferrer">
                                            {highlightKeywords(paper.metadata.title, true)}
                                        </a>
                                    </h2>
                                    <p>{highlightKeywords(paper.metadata.summary)}</p>
                                    <p><strong>Authors:</strong> {Array.isArray(paper.metadata.authors) ? paper.metadata.authors.join(', ') : paper.metadata.authors}</p>
                                    <p><strong>Published:</strong> {paper.metadata.published}</p>
                                    <a href={paper.metadata.pdf_url} target="_blank" rel="noopener noreferrer">
                                        <FaFilePdf /> Read Paper
                                    </a>
                                </div>
                                <div className="paper-chart">
                                    {renderPieChart(paper)}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            )}
            <Modal
                isOpen={modalIsOpen}
                onRequestClose={closeModal}
                contentLabel="Ranking Algorithm Overview"
                className="Modal"
                overlayClassName="Overlay"
                shouldCloseOnOverlayClick={true}
                onClick={handleOverlayClick}
            >
                <h2>Ranking Algorithm Overview</h2>
                <p>Our ranking algorithm combines multiple methods to determine the relevance of papers. The contributions of each method to the overall ranking are as follows:</p>
                <ul>
                    <li><strong>BM25:</strong> 35%</li>
                    <li><strong>TF-IDF:</strong> 40%</li>
                    <li><strong>Keyword Matching:</strong> 10%</li>
                    <li><strong>Embedding:</strong> 15%</li>
                </ul>
                <div className="chart-container">
                    <RankingAlgorithmChart />
                </div>
                <button onClick={closeModal}>Close</button>
            </Modal>
        </div>
    );
};

const data = [
    // { name: 'BM25', value: 35, fill: '#FF8042' },
    // { name: 'TF-IDF', value: 40, fill: '#FFBB28' },
    // { name: 'Keyword', value: 10, fill: '#00C49F' },
    // { name: 'Embedding', value: 15, fill: '#0088FE' },
    { name: 'BM25', value: 35, fill: '#97accf' },
    { name: 'TF-IDF', value: 40, fill: '#2e70db' },
    { name: 'Keyword', value: 10, fill: '#2e4161' },
    { name: 'Embedding', value: 15, fill: '#051e47' },
];

const renderActiveShape = (props) => {
    const RADIAN = Math.PI / 180;
    const { cx, cy, midAngle, innerRadius, outerRadius, startAngle, endAngle, fill, payload, percent, value } = props;
    const sin = Math.sin(-RADIAN * midAngle);
    const cos = Math.cos(-RADIAN * midAngle);
    const sx = cx + (outerRadius + 10) * cos;
    const sy = cy + (outerRadius + 10) * sin;
    const mx = cx + (outerRadius + 30) * cos;
    const my = cy + (outerRadius + 30) * sin;
    const ex = mx + (cos >= 0 ? 1 : -1) * 22;
    const ey = my;
    const textAnchor = cos >= 0 ? 'start' : 'end';

    return (
        <g>
            <text x={cx} y={cy} dy={8} textAnchor="middle" fill={fill}>
                {payload.name}
            </text>
            <Sector
                cx={cx}
                cy={cy}
                innerRadius={innerRadius}
                outerRadius={outerRadius}
                startAngle={startAngle}
                endAngle={endAngle}
                fill={fill}
            />
            <Sector
                cx={cx}
                cy={cy}
                startAngle={startAngle}
                endAngle={endAngle}
                innerRadius={outerRadius + 6}
                outerRadius={outerRadius + 10}
                fill={fill}
            />
            <path d={`M${sx},${sy}L${mx},${my}L${ex},${ey}`} stroke={fill} fill="none" />
            <circle cx={ex} cy={ey} r={2} fill={fill} stroke="none" />
            <text x={ex + (cos >= 0 ? 1 : -1) * 12} y={ey} textAnchor={textAnchor} fill="#333">{payload.name}</text>
            <text x={ex + (cos >= 0 ? 1 : -1) * 12} y={ey} dy={18} textAnchor={textAnchor} fill="#999">
                {`(${(percent * 100).toFixed(2)}%)`}
            </text>
        </g>
    );
};

class RankingAlgorithmChart extends PureComponent {
    state = {
        activeIndex: 0,
    };

    onPieEnter = (_, index) => {
        this.setState({
            activeIndex: index,
        });
    };

    render() {
        return (
            <ResponsiveContainer width="100%" height={400}>
                <PieChart>
                    <Pie
                        activeIndex={this.state.activeIndex}
                        activeShape={renderActiveShape}
                        data={data}
                        cx="50%"
                        cy="50%"
                        innerRadius={70}
                        outerRadius={100}
                        onMouseEnter={this.onPieEnter}
                        dataKey="value"
                    />
                </PieChart>
            </ResponsiveContainer>
        );
    }
}

export default Feed;