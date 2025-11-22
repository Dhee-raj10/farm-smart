import React, { useState } from 'react';
import axios from 'axios';
import Navbar from './Navbar';
import Footer from './Footer';

const SoilFertilityForm = () => {
  const [formData, setFormData] = useState({
    N: '', P: '', K: '', pH: '', EC: '', OC: '',
    S: '', Zn: '', Fe: '', Cu: '', Mn: '', B: ''
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = e => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const response = await axios.post('http://localhost:5000/api/crops/fertility', formData);
      setResult(response.data);
    } catch (err) {
      console.error(err);
      setResult({ error: 'Prediction failed. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const nutrientFields = [
    { name: 'N', label: 'Nitrogen (N)', placeholder: 'e.g., 20' },
    { name: 'P', label: 'Phosphorus (P)', placeholder: 'e.g., 15' },
    { name: 'K', label: 'Potassium (K)', placeholder: 'e.g., 30' },
    { name: 'pH', label: 'pH Value', placeholder: 'e.g., 6.5' },
    { name: 'EC', label: 'Electrical Conductivity (EC)', placeholder: 'e.g., 1.2' },
    { name: 'OC', label: 'Organic Carbon (OC)', placeholder: 'e.g., 0.8' },
    { name: 'S', label: 'Sulfur (S)', placeholder: 'e.g., 10' },
    { name: 'Zn', label: 'Zinc (Zn)', placeholder: 'e.g., 5' },
    { name: 'Fe', label: 'Iron (Fe)', placeholder: 'e.g., 12' },
    { name: 'Cu', label: 'Copper (Cu)', placeholder: 'e.g., 3' },
    { name: 'Mn', label: 'Manganese (Mn)', placeholder: 'e.g., 8' },
    { name: 'B', label: 'Boron (B)', placeholder: 'e.g., 1.5' },
  ];

  return (
    <>
      <Navbar />
      <section className="py-5 bg-light">
        <div className="container">
          <div className="row justify-content-center">
            <div className="col-lg-8">
              <div className="card shadow-lg rounded-3">
                <div className="card-body p-4 p-md-5">
                  <h2 className="card-title text-center mb-4 fw-bold text-primary">Soil Fertility Check</h2>
                  <p className="text-center text-muted mb-5">Enter your soil nutrient data to get a fertility prediction and recommendations.</p>
                  
                  <form onSubmit={handleSubmit}>
                    <div className="row g-4">
                      {nutrientFields.map(field => (
                        <div className="col-md-6" key={field.name}>
                          <div className="form-floating">
                            <input
                              type="number"
                              className="form-control"
                              id={field.name}
                              name={field.name}
                              placeholder={field.placeholder}
                              value={formData[field.name]}
                              onChange={handleChange}
                              required
                              step="any"
                            />
                            <label htmlFor={field.name}>{field.label}</label>
                          </div>
                        </div>
                      ))}
                    </div>
                    
                    <div className="d-grid mt-5">
                      <button type="submit" className="btn btn-primary btn-lg rounded-pill" disabled={loading}>
                        {loading ? (
                          <>
                            <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                            <span className="ms-2">Predicting...</span>
                          </>
                        ) : (
                          'Predict Fertility'
                        )}
                      </button>
                    </div>
                  </form>

                  {result && (
                    <div className="mt-5 p-4 rounded-3 text-center" style={{ backgroundColor: '#e9f5ee' }}>
                      {result.error ? (
                        <p className="text-danger fw-bold">{result.error}</p>
                      ) : (
                        <>
                          <h4 className="text-success fw-bold mb-3">Prediction Result</h4>
                          <p className="lead">
                            <span className="fw-bold">Fertility Class:</span> {result.prediction}
                          </p>
                          <p className="mt-3 text-muted">
                            <span className="fw-bold">Recommendation:</span> {result.recommendation}
                          </p>
                        </>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
      <Footer />
    </>
  );
};

export default SoilFertilityForm;
