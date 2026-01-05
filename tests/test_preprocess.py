from app import HeartDiseaseModel, config

def test_preprocess_shape():
    model = HeartDiseaseModel(config.MODEL_DIR)

    sample = {
        "age": 52, "sex": 1, "cp": 0, "trestbps": 130,
        "chol": 250, "fbs": 0, "restecg": 1,
        "thalach": 150, "exang": 0, "oldpeak": 1.0,
        "slope": 2, "ca": 0, "thal": 2
    }

    processed = model.preprocess(sample)
    assert processed.shape[1] == 13
