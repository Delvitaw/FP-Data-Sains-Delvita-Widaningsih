# -*- coding: utf-8 -*-
"""FP Data Sains.ipynb

Automatically generated by Colab.
"""

# === Bagian 1: Training Model ===

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
import joblib

# Load data
df = pd.read_csv('obesitas.csv')

# Tambah fitur BMI
df['BMI'] = df['Weight'] / np.where(df['Height'] == 0, np.nan, df['Height'] ** 2)

# Cek nilai hilang
missing = df.isna().sum()
print('Missing values per kolom:')
print(missing[missing > 0])

# Visualisasi korelasi
num_cols = ['Age', 'Height', 'Weight', 'BMI']
plt.figure(figsize=(6,4))
sns.heatmap(df[num_cols].corr(), annot=True, cmap='magma')
plt.title('Korelasi Numerik')
plt.tight_layout()
plt.show()

# Distribusi kelas target
plt.figure(figsize=(6,3))
sns.countplot(x='NObeyesdad', data=df, order=df['NObeyesdad'].value_counts().index)
plt.title('Distribusi Kelas')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Split fitur dan target
X = df.drop('NObeyesdad', axis=1)
y = df['NObeyesdad']

# Identifikasi kolom kategorikal dan numerik
cat_cols = X.select_dtypes(include=['object']).columns.tolist()
num_cols = [col for col in X.columns if col not in cat_cols]

# Preprocessor dan pipeline
preprocessor = ColumnTransformer([
    ('num', StandardScaler(), num_cols),
    ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols)
])

model = RandomForestClassifier(random_state=42)

pipe = Pipeline([
    ('prep', preprocessor),
    ('clf', model)
])

# Parameter tuning
param_dist = {
    'clf__n_estimators': [100, 200, 300],
    'clf__max_depth': [None, 10, 20, 30],
    'clf__min_samples_split': [2, 5, 10]
}

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# Training model
rs = RandomizedSearchCV(pipe, param_distributions=param_dist, n_iter=10, cv=5, n_jobs=-1)
rs.fit(X_train, y_train)

# Evaluasi
print('Best params:', rs.best_params_)
y_pred = rs.predict(X_test)
print('Classification Report:')
print(classification_report(y_test, y_pred))

cm = confusion_matrix(y_test, y_pred, labels=rs.classes_)
fig, ax = plt.subplots(figsize=(6,6))
ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=rs.classes_).plot(
    ax=ax, xticks_rotation=45, cmap='Blues'
)
plt.title('Confusion Matrix')
plt.tight_layout()
plt.show()

# Simpan model
joblib.dump(rs.best_estimator_, 'obesity_pipeline.pkl')
print('Model saved as obesity_pipeline.pkl')

# === Bagian 2: Aplikasi Streamlit ===

import streamlit as st
import joblib

st.title('Obesity Category Predictor')

# Load model pipeline
model = joblib.load('obesity_pipeline.pkl')

# Input user
gender = st.selectbox('Gender', ['Male', 'Female'])
age = st.number_input('Age (years)', 10, 90, 25)
height = st.number_input('Height (m)', 1.2, 2.5, 1.70, step=0.01)
weight = st.number_input('Weight (kg)', 30.0, 200.0, 70.0, step=0.1)
family_history = st.selectbox('Family history with overweight', ['yes', 'no'])
favc = st.selectbox('Frequent high-caloric food (FAVC)', ['yes', 'no'])
fcvc = st.slider('Veggies consumption (FCVC)', 1, 3, 2)
ncp  = st.slider('Meals per day (NCP)', 1, 4, 3)
caec = st.selectbox('Snacks (CAEC)', ['no', 'Sometimes', 'Frequently', 'Always'])
smoke = st.selectbox('SMOKE', ['yes', 'no'])
ch2o = st.slider('Water cups / day (CH2O)', 1, 3, 2)
scc = st.selectbox('Calories monitoring (SCC)', ['yes', 'no'])
faf = st.slider('Physical activity (hrs) FAF', 0.0, 3.0, 1.0, step=0.25)
tue = st.slider('Technology use hrs (TUE)', 0.0, 2.0, 1.0, step=0.25)
calc = st.selectbox('Alcohol (CALC)', ['no', 'Sometimes', 'Frequently', 'Always'])
mtrans = st.selectbox('Transportation', ['Public_Transportation','Walking','Automobile','Motorbike','Bike'])

# Tombol prediksi
if st.button('Predict'):
    # Bentuk dataframe
    row = pd.DataFrame([{
        'Gender': gender, 'Age': age, 'Height': height, 'Weight': weight,
        'family_history_with_overweight': family_history,
        'FAVC': favc, 'FCVC': fcvc, 'NCP': ncp, 'CAEC': caec, 'SMOKE': smoke,
        'CH2O': ch2o, 'SCC': scc, 'FAF': faf, 'TUE': tue, 'CALC': calc,
        'MTRANS': mtrans
    }])

    # ✅ Tambahkan kolom BMI
    row['BMI'] = row['Weight'] / (row['Height'] ** 2)

    # Prediksi
    prediction = model.predict(row)[0]
    st.success(f'Predicted category: {prediction}')