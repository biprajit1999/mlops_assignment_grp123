from app import HeartDiseaseModel, config

def test_prediction_output():
    model = HeartDiseaseModel(config.MODEL_DIR)

    sample = {
        "age": 60, "sex": 1, "cp": 2, "trestbps": 140,
        "chol": 260, "fbs": 0, "restecg": 1,
        "thalach": 120, "exang": 1, "oldpeak": 2.3,
        "slope": 1, "ca": 2, "thal": 3
    }

    result = model.predict(sample)

    assert "prediction" in result
    assert "confidence" in result
    assert result["confidence"] >= 0.0 and result["confidence"] <= 1.0
