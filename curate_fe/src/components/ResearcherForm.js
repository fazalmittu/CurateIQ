import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './ResearcherForm.css';

const arxivCategories = [
    "cs.AI", "cs.AR", "cs.CC", "cs.CE", "cs.CG", "cs.CL", "cs.CR", "cs.CV", "cs.CY", "cs.DB",
    "cs.DC", "cs.DL", "cs.DM", "cs.DS", "cs.ET", "cs.FL", "cs.GL", "cs.GR", "cs.GT", "cs.HC",
    "cs.IR", "cs.IT", "cs.LG", "cs.LO", "cs.MA", "cs.MM", "cs.MS", "cs.NA", "cs.NE", "cs.NI",
    "cs.OH", "cs.OS", "cs.PF", "cs.PL", "cs.RO", "cs.SC", "cs.SD", "cs.SE", "cs.SI", "cs.SY",
    "econ.EM", "econ.GN", "econ.TH", "eess.AS", "eess.IV", "eess.SP", "eess.SY", "math.AC",
    "math.AG", "math.AP", "math.AT", "math.CA", "math.CO", "math.CT", "math.CV", "math.DG",
    "math.DS", "math.FA", "math.GM", "math.GN", "math.GR", "math.GT", "math.HO", "math.IT",
    "math.KT", "math.LO", "math.MG", "math.MP", "math.NA", "math.NT", "math.OA", "math.OC",
    "math.PR", "math.QA", "math.RA", "math.RT", "math.SG", "math.SP", "math.ST", "astro-ph.CO",
    "astro-ph.EP", "astro-ph.GA", "astro-ph.HE", "astro-ph.IM", "astro-ph.SR", "cond-mat.dis-nn",
    "cond-mat.mes-hall", "cond-mat.mtrl-sci", "cond-mat.other", "cond-mat.quant-gas",
    "cond-mat.soft", "cond-mat.stat-mech", "cond-mat.str-el", "cond-mat.supr-con", "gr-qc",
    "hep-ex", "hep-lat", "hep-ph", "hep-th", "math-ph", "nlin.AO", "nlin.CD", "nlin.CG", "nlin.PS",
    "nlin.SI", "nucl-ex", "nucl-th", "physics.acc-ph", "physics.ao-ph", "physics.app-ph",
    "physics.atm-clus", "physics.atom-ph", "physics.bio-ph", "physics.chem-ph", "physics.class-ph",
    "physics.comp-ph", "physics.data-an", "physics.ed-ph", "physics.flu-dyn", "physics.gen-ph",
    "physics.geo-ph", "physics.hist-ph", "physics.ins-det", "physics.med-ph", "physics.optics",
    "physics.plasm-ph", "physics.pop-ph", "physics.soc-ph", "physics.space-ph", "quant-ph",
    "q-bio.BM", "q-bio.CB", "q-bio.GN", "q-bio.MN", "q-bio.NC", "q-bio.OT", "q-bio.PE", "q-bio.QM",
    "q-bio.SC", "q-bio.TO", "q-fin.CP", "q-fin.EC", "q-fin.GN", "q-fin.MF", "q-fin.PM", "q-fin.PR",
    "q-fin.RM", "q-fin.ST", "q-fin.TR", "stat.AP", "stat.CO", "stat.ME", "stat.ML", "stat.OT",
    "stat.TH"
];

const ResearcherForm = () => {
    const [formData, setFormData] = useState({
        fullName: '',
        subjectArea: ''
    });
    const [loading, setLoading] = useState(false);

    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!arxivCategories.includes(formData.subjectArea)) {
            alert('Invalid subject area. Please select a valid arXiv subject area.');
            return;
        }
        setLoading(true);
        try {
            await axios.post('http://127.0.0.1:5000/api/researcher', formData, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            navigate('/author_papers', { state: { authorName: formData.fullName, subjectArea: formData.subjectArea } });
        } catch (error) {
            console.error('Error submitting data', error);
            alert('Error submitting data: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="form-container">
            {loading ? (
                <h2 className="loading-text">Loading your papers...</h2>
            ) : (
                <>
                    <h2 className="loading-text">Enter Researcher Details</h2>
                    <form onSubmit={handleSubmit}>
                        <input type="text" name="fullName" placeholder="Full Name" onChange={handleChange} required />
                        <input type="text" name="subjectArea" placeholder="Subject Area" onChange={handleChange} required />
                        <button type="submit">Submit</button>
                    </form>
                </>
            )}
        </div>
    );
};

export default ResearcherForm;