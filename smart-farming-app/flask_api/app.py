# flask_api/app.py
"""
Complete Flask ML API for Smart Farming Application
Handles: Fertility Prediction, Irrigation Prediction, Soil Image Classification
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import os

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ==================== LOAD MODELS ====================
print("🔄 Loading ML models...")

try:
    fertility_model = joblib.load('models/fertility_model.pkl')
    fertility_scaler = joblib.load('models/fertility_scaler.pkl')
    fertility_features = joblib.load('models/fertility_features.pkl')
    try:
        fertility_encoder = joblib.load('models/fertility_label_encoder.pkl')
    except:
        fertility_encoder = None
    print("✅ Fertility model loaded")
    print(f"   Features: {fertility_features}")
except Exception as e:
    print(f"❌ Fertility model error: {e}")
    fertility_model = None

try:
    irrigation_model = joblib.load('models/irrigation_model.pkl')
    irrigation_scaler = joblib.load('models/irrigation_scaler.pkl')
    irrigation_features = joblib.load('models/irrigation_features.pkl')
    print("✅ Irrigation model loaded")
except Exception as e:
    print(f"⚠️  Irrigation model not loaded: {e}")
    irrigation_model = None

try:
    crop_model = joblib.load('models/crop_model.pkl')
    crop_scaler = joblib.load('models/crop_scaler.pkl')
    print("✅ Crop model loaded")
except Exception as e:
    print(f"⚠️  Crop model not loaded: {e}")
    crop_model = None

print("="*70)
print("Starting Flask ML API on http://127.0.0.1:8000")
print("="*70)

# ==================== HELPER FUNCTIONS ====================

def get_fertility_recommendation(pred_label, confidence, nutrient_values):
    """Generate detailed fertility recommendations"""
    
    recommendations = {
        'Low': {
            'message': '⚠️ Your soil fertility is LOW. Immediate action required!',
            'priority': 'High',
            'color': '#dc3545',
            'actions': [
                'Apply organic compost (5-10 tons/hectare)',
                'Use balanced NPK fertilizer (19:19:19) at 200-250 kg/hectare',
                'Add micronutrients: Zinc sulfate (25 kg/ha), Ferrous sulfate (25 kg/ha)',
                'Adjust pH to 6.0-7.0 range using lime if acidic',
                'Incorporate green manure crops (legumes) before main crop'
            ],
            'timeline': 'Implement within 2 weeks before planting'
        },
        'Medium': {
            'message': '👍 Your soil fertility is MEDIUM. Good base, can be optimized.',
            'priority': 'Medium',
            'color': '#ffc107',
            'actions': [
                'Maintain with organic matter (2-3 tons/hectare)',
                'Apply targeted fertilizers based on specific crop needs',
                'Monitor nutrient levels quarterly with soil testing',
                'Practice crop rotation with nitrogen-fixing legumes',
                'Consider vermicompost (1-2 tons/ha) for micronutrient boost'
            ],
            'timeline': 'Implement within 1 month'
        },
        'High': {
            'message': '✅ Excellent! Your soil fertility is HIGH.',
            'priority': 'Low',
            'color': '#28a745',
            'actions': [
                'Maintain current excellent practices',
                'Continue organic matter addition (1-2 tons/hectare annually)',
                'Regular soil testing every 6 months to monitor levels',
                'Watch for over-fertilization symptoms (excessive vegetative growth)',
                'Focus on maintaining soil structure and microbial health'
            ],
            'timeline': 'Maintain current schedule'
        }
    }
    
    return recommendations.get(pred_label, recommendations['Medium'])

def get_irrigation_recommendation(irrigation_needed, confidence, moisture_avg):
    """Generate irrigation recommendations"""
    
    if irrigation_needed:
        if moisture_avg < 20:
            return {
                'urgency': 'Critical',
                'color': '#dc3545',
                'action': '🚨 IRRIGATE IMMEDIATELY - Crops under severe stress!',
                'amount': '50-75mm water depth (deep irrigation)',
                'method': 'Flood or sprinkler irrigation recommended',
                'next_check': '12 hours',
                'timeline': 'Within 2 hours'
            }
        elif moisture_avg < 35:
            return {
                'urgency': 'High',
                'color': '#fd7e14',
                'action': '⚠️ Irrigate within 24 hours to prevent crop stress',
                'amount': '30-50mm water depth',
                'method': 'Drip or sprinkler irrigation',
                'next_check': '24 hours',
                'timeline': 'Within 24 hours'
            }
        else:
            return {
                'urgency': 'Moderate',
                'color': '#ffc107',
                'action': '📅 Schedule irrigation within 48 hours',
                'amount': '20-30mm water depth',
                'method': 'Drip irrigation preferred',
                'next_check': '48 hours',
                'timeline': 'Within 2 days'
            }
    else:
        if moisture_avg > 70:
            return {
                'urgency': 'None',
                'color': '#28a745',
                'action': '✅ Soil moisture is OPTIMAL. No irrigation needed.',
                'amount': 'Monitor only',
                'method': 'Continue current schedule',
                'next_check': '3-4 days',
                'timeline': 'No action required'
            }
        else:
            return {
                'urgency': 'Low',
                'color': '#17a2b8',
                'action': '👍 Soil moisture is adequate. Monitor daily.',
                'amount': 'No irrigation needed yet',
                'method': 'Check sensors daily',
                'next_check': '48-72 hours',
                'timeline': 'Irrigate when below 45%'
            }

# ==================== API ENDPOINTS ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    models_status = {
        'fertility': fertility_model is not None,
        'irrigation': irrigation_model is not None,
        'crop': crop_model is not None
    }
    
    return jsonify({
        'status': 'healthy',
        'message': 'Flask ML API is running',
        'models': models_status,
        'all_models_loaded': all(models_status.values())
    })

@app.route('/predict/fertility', methods=['POST'])
def predict_fertility():
    """Predict soil fertility from nutrient values"""
    
    if not fertility_model:
        return jsonify({'error': 'Fertility model not loaded'}), 503
    
    try:
        data = request.json
        
        print("="*70)
        print("FERTILITY PREDICTION REQUEST")
        print(f"Received data: {data}")
        print("="*70)
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        # Extract features in correct order
        features = []
        missing_features = []
        
        for feature_name in fertility_features:
            if feature_name not in data:
                missing_features.append(feature_name)
            else:
                try:
                    features.append(float(data[feature_name]))
                except (ValueError, TypeError) as e:
                    return jsonify({
                        'error': f'Invalid value for {feature_name}: {data[feature_name]}'
                    }), 400
        
        if missing_features:
            return jsonify({
                'error': f'Missing required features: {missing_features}',
                'received': list(data.keys()),
                'expected': fertility_features
            }), 400
        
        X = np.array([features])
        
        # Scale and predict
        X_scaled = fertility_scaler.transform(X)
        prediction = fertility_model.predict(X_scaled)[0]
        probabilities = fertility_model.predict_proba(X_scaled)[0]
        
        # Map numeric prediction to labels
        fertility_mapping = {
            0: 'Low',
            1: 'Medium', 
            2: 'High'
        }
        
        pred_label = fertility_mapping.get(int(prediction), 'Unknown')
        confidence = float(max(probabilities))
        
        print(f"Prediction: {pred_label}, Confidence: {confidence:.2%}")
        
        # Get detailed recommendation
        recommendation = get_fertility_recommendation(pred_label, confidence, features)
        
        # Analyze individual nutrients (NPK)
        n, p, k = features[0], features[1], features[2]
        
        nutrient_status = {
            'N': {
                'value': float(n),
                'level': 'Low' if n < 280 else 'Medium' if n < 420 else 'High',
                'status': 'Sufficient' if 280 <= n <= 560 else 'Needs attention',
                'optimal_range': '280-560 kg/ha'
            },
            'P': {
                'value': float(p),
                'level': 'Low' if p < 11 else 'Medium' if p < 22 else 'High',
                'status': 'Sufficient' if 11 <= p <= 45 else 'Needs attention',
                'optimal_range': '11-45 kg/ha'
            },
            'K': {
                'value': float(k),
                'level': 'Low' if k < 110 else 'Medium' if k < 280 else 'High',
                'status': 'Sufficient' if 110 <= k <= 560 else 'Needs attention',
                'optimal_range': '110-560 kg/ha'
            }
        }
        
        return jsonify({
            'success': True,
            'prediction': pred_label,
            'confidence': confidence,
            'confidence_percentage': f"{confidence*100:.1f}%",
            'probabilities': {
                'Low': float(probabilities[0]),
                'Medium': float(probabilities[1]),
                'High': float(probabilities[2])
            },
            'recommendation': recommendation,
            'nutrient_analysis': nutrient_status,
            'input_values': {name: val for name, val in zip(fertility_features, features)}
        })
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/predict/irrigation', methods=['POST'])
def predict_irrigation():
    """Predict irrigation need from moisture sensors"""
    
    if not irrigation_model:
        return jsonify({'error': 'Irrigation model not loaded'}), 503
    
    try:
        data = request.json
        
        print("="*70)
        print("IRRIGATION PREDICTION REQUEST")
        print(f"Received data: {data}")
        print("="*70)
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        # Extract features
        features = []
        missing_features = []
        
        for feature_name in irrigation_features:
            if feature_name not in data:
                missing_features.append(feature_name)
            else:
                try:
                    features.append(float(data[feature_name]))
                except (ValueError, TypeError) as e:
                    return jsonify({
                        'error': f'Invalid value for {feature_name}: {data[feature_name]}'
                    }), 400
        
        if missing_features:
            return jsonify({
                'error': f'Missing required features: {missing_features}',
                'received': list(data.keys()),
                'expected': irrigation_features
            }), 400
        
        X = np.array([features])
        
        # Scale and predict
        X_scaled = irrigation_scaler.transform(X)
        prediction = irrigation_model.predict(X_scaled)[0]
        probability = irrigation_model.predict_proba(X_scaled)[0]
        
        confidence = float(max(probability))
        avg_moisture = float(np.mean(features))
        irrigation_needed = bool(prediction == 1)
        
        print(f"Irrigation needed: {irrigation_needed}, Confidence: {confidence:.2%}")
        
        # Get recommendation
        recommendation = get_irrigation_recommendation(irrigation_needed, confidence, avg_moisture)
        
        return jsonify({
            'success': True,
            'irrigationNeeded': irrigation_needed,
            'confidence': confidence,
            'confidence_percentage': f"{confidence*100:.1f}%",
            'average_moisture': avg_moisture,
            'sensor_readings': {
                f'sensor{i+1}': float(val) 
                for i, val in enumerate(features)
            },
            'recommendation': recommendation
        })
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/recommend/crops', methods=['POST'])
def recommend_crops():
    """Recommend crops based on environmental conditions"""
    
    if not crop_model:
        return jsonify({'error': 'Crop model not loaded'}), 503
    
    try:
        data = request.json
        
        print("="*70)
        print("CROP RECOMMENDATION REQUEST")
        print(f"Received data: {data}")
        print("="*70)
        
        # Extract features
        required_features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        features = []
        
        for feature in required_features:
            if feature not in data:
                return jsonify({'error': f'Missing feature: {feature}'}), 400
            features.append(float(data[feature]))
        
        X = np.array([features])
        
        # Scale and predict
        X_scaled = crop_scaler.transform(X)
        probabilities = crop_model.predict_proba(X_scaled)[0]
        
        # Get top 5 recommendations
        top_indices = np.argsort(probabilities)[-5:][::-1]
        
        recommendations = []
        for idx in top_indices:
            crop_name = crop_model.classes_[idx]
            confidence = float(probabilities[idx])
            
            if confidence > 0.01:
                recommendations.append({
                    'crop': crop_name.title(),
                    'confidence': confidence,
                    'confidence_percentage': f"{confidence*100:.1f}%",
                    'suitability': (
                        'Excellent' if confidence > 0.25 else
                        'Good' if confidence > 0.10 else
                        'Fair'
                    )
                })
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'conditions': {
                'nitrogen': float(data['N']),
                'phosphorus': float(data['P']),
                'potassium': float(data['K']),
                'temperature': float(data['temperature']),
                'humidity': float(data['humidity']),
                'ph': float(data['ph']),
                'rainfall': float(data['rainfall'])
            }
        })
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ==================== RUN SERVER ====================
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)