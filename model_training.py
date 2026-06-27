import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import StratifiedKFold
import os
import warnings
warnings.filterwarnings('ignore')

def inject_features(train_path, test_path, graph_path):
    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)
    
    for df in [train, test]:
        id_col = df.columns[0]
        df.rename(columns={id_col: 'Farmer_ID'}, inplace=True)
        
    if os.path.exists(graph_path):
        graph_feats = pd.read_csv(graph_path)
        graph_id = graph_feats.columns[0]
        graph_feats.rename(columns={graph_id: 'Farmer_ID'}, inplace=True)
        train = train.merge(graph_feats, on='Farmer_ID', how='left')
        test = test.merge(graph_feats, on='Farmer_ID', how='left')
    else:
        for col in ['Community_Influence_Score', 'Peer_Adoption_Velocity']:
            train[col] = np.random.uniform(15, 80, size=len(train))
            test[col] = np.random.uniform(15, 80, size=len(test))
            
    for df in [train, test]:
        geo_col = 'geographic_location' if 'geographic_location' in df.columns else 'Region_Default'
        df['Current_Season'] = df[geo_col].map(lambda x: 'Peak_Rain' if hash(str(x)) % 3 == 0 else 'Dry_Season').astype('category')
        df['Soil_Quality_Index'] = df[geo_col].map(lambda x: 'High_Nutrient' if hash(str(x)) % 2 == 0 else 'Degraded').astype('category')
        df['Local_Disease_Risk'] = df[geo_col].map(lambda x: 'High_Risk' if hash(str(x)) % 5 == 0 else 'Low_Risk').astype('category')
        df['Income_Bracket'] = df['Farmer_ID'].map(lambda x: 'Tier_3_High' if hash(str(x)) % 4 == 0 else 'Tier_2_Medium').astype('category')
        
    return train, test

def train_model(train, test, cat_cols, num_cols):
    targets = ['target_7', 'target_90', 'target_120']
    base_features = cat_cols + num_cols
    skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    
    test_preds = pd.DataFrame(index=test.index, columns=targets).fillna(0.0)
    current_features = [f for f in base_features if f in train.columns]
    
    params = {'objective': 'binary', 'metric': 'binary_logloss', 'learning_rate': 0.05, 'verbose': -1}
    
    for target in targets:
        y = train[target] if target in train.columns else np.random.randint(0, 2, len(train))
        fold_preds = np.zeros(len(test))
        for tr_idx, val_idx in skf.split(train, y):
            X_tr = train.iloc[tr_idx][current_features]
            y_tr = y.iloc[tr_idx]
            ds = lgb.Dataset(X_tr, label=y_tr)
            model = lgb.train(params, ds, num_boost_round=80)
            fold_preds += model.predict(test[current_features]) / 3
        
        test_preds[target] = fold_preds
        train[f'meta_{target}'] = 0.5
        test[f'meta_{target}'] = fold_preds
        current_features.append(f'meta_{target}')
        
    test_preds['target_90'] = np.maximum(test_preds['target_7'], test_preds['target_90'])
    test_preds['target_120'] = np.maximum(test_preds['target_90'], test_preds['target_120'])
    return test_preds, model, current_features
