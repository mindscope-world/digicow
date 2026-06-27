import pandas as pd
import json
import shap

def run_inference(test_df, predictions, model, features):
    explainer = shap.TreeExplainer(model)
    sample = test_df[features].head(100)
    shap_v = explainer.shap_values(sample)
    if isinstance(shap_v, list): shap_v = shap_v[1]
    
    blueprint = []
    for idx, row in test_df.head(100).iterrows():
        p7, p90, p120 = predictions.iloc[idx]
        blueprint.append({
            "Farmer_ID": str(row['Farmer_ID']),
            "Metrics": {"P_7": round(p7, 3), "P_90": round(p90, 3), "P_120": round(p120, 3)},
            "Segment": "High Trajectory" if (p90-p7) > 0.15 else "Standard"
        })
        
    with open('deployment_blueprint.json', 'w') as f:
        json.dump(blueprint, f, indent=4)
    print("Inference Complete: deployment_blueprint.json generated.")
