import React, { useState } from 'react';
import axios from 'axios';
import Navbar from './Navbar';
import Footer from './Footer';

const SoilMoistureForm = () => {
  const [formData, setFormData] = useState({
    moisture0: '', moisture1: '', moisture2: '', moisture3: '', moisture4: ''
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
      const response = await axios.post('http://localhost:5000/api/crops/moisture', formData);
      setResult(response.data);
    } catch (err) {
      console.error(err);
      setResult({ error: 'Prediction failed. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const moistureFields = [
    { name: 'moisture0', label: 'Sensor 1 (%)', placeholder: 'e.g., 45' },
    { name: 'moisture1', label: 'Sensor 2 (%)', placeholder: 'e.g., 50' },
    { name: 'moisture2', label: 'Sensor 3 (%)', placeholder: 'e.g., 55' },
    { name: 'moisture3', label: 'Sensor 4 (%)', placeholder: 'e.g., 60' },
    { name: 'moisture4', label: 'Sensor 5 (%)', placeholder: 'e.g., 65' },
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
                  <h2 className="card-title text-center mb-4 fw-bold text-primary">Soil Moisture Check</h2>
                  <p className="text-center text-muted mb-5">Enter moisture sensor readings to get an irrigation prediction.</p>
                  
                  <form onSubmit={handleSubmit}>
                    <div className="row g-4">
                      {moistureFields.map(field => (
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
                          'Predict Irrigation'
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
                            <span className="fw-bold">Irrigation Needed:</span> {result.irrigationNeeded ? 'Yes' : 'No'}
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

export default SoilMoistureForm;
