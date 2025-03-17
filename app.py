import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.utils import resample
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.preprocessing import StandardScaler

# Define the categorical columns and their mapping
CATEGORICAL_COLS = {
    'Gender': {'options': ["Female", "Male"], 'map': {"Female": 0, "Male": 1}},
    'Smoking/Alcohol Consumption Status': {'options': ["No", "Yes"], 'map': {"No": 0, "Yes": 1}},
    'Family History of Disease': {'options': ["No", "Yes"], 'map': {"No": 0, "Yes": 1}}
}

# ---------------------------
# Helper Functions
# ---------------------------
@st.cache_data
def load_and_preprocess_data():
    # Load dataset
    df = pd.read_csv('heart_disease_prediction.csv')
    
    # Fill missing numerical values with median
    num_cols = ['Age', 'Blood Pressure', 'Cholesterol Levels', 'Glucose Levels', 'BMI']
    for col in num_cols:
        df[col] = df[col].fillna(df[col].median())
    
    # Fill missing target variable if necessary
    if df["Target Variable"].isnull().any():
        df["Target Variable"] = df["Target Variable"].fillna(df["Target Variable"].first_valid_index())
    
    # Process categorical columns.
    for col in CATEGORICAL_COLS.keys():
        df[col] = df[col].fillna(method='ffill')
        # If the column is not numeric, convert common text values to 0/1.
        if df[col].dtype == object:
            df[col] = df[col].map(CATEGORICAL_COLS[col]['map'])
    
    return df

@st.cache_resource
def train_models(df):
    # Separate features and target
    X = df.drop(columns=['Target Variable'])
    y = df['Target Variable']
    
    # Balance the dataset via random under-sampling (if necessary)
    df_balanced = pd.concat([X, y], axis=1)
    majority_class = df_balanced[df_balanced['Target Variable'] == 0]
    minority_class = df_balanced[df_balanced['Target Variable'] == 1]
    
    if len(minority_class) > 0 and len(majority_class) > len(minority_class):
        majority_downsampled = resample(majority_class,
                                        replace=False,
                                        n_samples=len(minority_class),
                                        random_state=42)
        df_resampled = pd.concat([majority_downsampled, minority_class])
    else:
        df_resampled = df_balanced.copy()
    
    X_resampled = df_resampled.drop(columns=['Target Variable'])
    y_resampled = df_resampled['Target Variable']
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_resampled)
    X_scaled = pd.DataFrame(X_scaled, columns=X_resampled.columns)
    
    # Split into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_resampled, test_size=0.2, random_state=42)
    
    # Train Logistic Regression model
    log_model = LogisticRegression()
    log_model.fit(X_train, y_train)
    y_pred_log = log_model.predict(X_test)
    log_accuracy = accuracy_score(y_test, y_pred_log)
    log_conf_matrix = confusion_matrix(y_test, y_pred_log)
    
    # Train Random Forest model
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    rf_model.fit(X_train, y_train)
    y_pred_rf = rf_model.predict(X_test)
    rf_accuracy = accuracy_score(y_test, y_pred_rf)
    rf_conf_matrix = confusion_matrix(y_test, y_pred_rf)
    
    models = {
        'scaler': scaler,
        'logistic': log_model,
        'rf': rf_model,
        'log_accuracy': log_accuracy,
        'log_conf_matrix': log_conf_matrix,
        'rf_accuracy': rf_accuracy,
        'rf_conf_matrix': rf_conf_matrix,
        'features': X_resampled.columns
    }
    return models

# ---------------------------
# Main App
# ---------------------------
st.title("Heart Disease Prediction App")

# Sidebar for navigation
page = st.sidebar.selectbox("Navigation", ["Exploratory Data Analysis", "Logistic Regression Prediction", "Random Forest Prediction"])

# Load and preprocess data
df = load_and_preprocess_data()
st.write("### Data Preview")
st.dataframe(df.head())

if page == "Exploratory Data Analysis":
    st.header("Exploratory Data Analysis")
    
    st.subheader("Feature Visualizations")
    plot_choice = st.selectbox("Select a feature to visualize", df.columns)
    
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    # Boxplot
    sns.boxplot(x=df[plot_choice], ax=ax[0])
    ax[0].set_title(f"Box Plot of {plot_choice}")
    
    # Histogram with KDE
    sns.histplot(df[plot_choice], bins=30, kde=True, ax=ax[1])
    ax[1].set_title(f"Histogram of {plot_choice}")
    
    st.pyplot(fig)
    
    st.subheader("Correlation Matrix")
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    sns.heatmap(df.corr(), annot=True, cmap="coolwarm", fmt=".2f", ax=ax2)
    st.pyplot(fig2)
    
elif page == "Logistic Regression Prediction":
    st.header("Logistic Regression Prediction")
    
    # Train models if not already trained
    models = train_models(df)
    scaler = models['scaler']
    log_model = models['logistic']
    
    st.subheader("Model Performance")
    st.write(f"**Accuracy:** {models['log_accuracy'] * 100:.2f}%")
    st.write("**Confusion Matrix:**")
    st.write(models['log_conf_matrix'])
    
    st.subheader("Enter Patient Data")
    input_data = {}
    # For each feature, present a selectbox for categorical features or a number_input for numeric features.
    for feature in models['features']:
        if feature in CATEGORICAL_COLS:
            # Use selectbox for categorical input
            option = st.selectbox(f"{feature}", options=CATEGORICAL_COLS[feature]['options'])
            # Map the option to numeric
            input_data[feature] = CATEGORICAL_COLS[feature]['map'][option]
        else:
            input_data[feature] = st.number_input(f"{feature}", value=float(50))
    
    user_df = pd.DataFrame([input_data])
    user_scaled = scaler.transform(user_df)
    
    if st.button("Predict with Logistic Regression"):
        prediction = log_model.predict(user_scaled)[0]
        prediction_proba = log_model.predict_proba(user_scaled)[0]
        if prediction == 1:
            st.error(f"High Risk of Heart Disease! (Probability: {prediction_proba[1] * 100:.2f}%)")
        else:
            st.success(f"Low Risk of Heart Disease (Probability: {prediction_proba[0] * 100:.2f}%)")
    
elif page == "Random Forest Prediction":
    st.header("Random Forest Prediction")
    
    # Train models if not already trained
    models = train_models(df)
    scaler = models['scaler']
    rf_model = models['rf']
    
    st.subheader("Model Performance")
    st.write(f"**Accuracy:** {models['rf_accuracy'] * 100:.2f}%")
    st.write("**Confusion Matrix:**")
    st.write(models['rf_conf_matrix'])
    
    st.subheader("Enter Patient Data")
    input_data = {}
    for feature in models['features']:
        if feature in CATEGORICAL_COLS:
            option = st.selectbox(f"{feature}", options=CATEGORICAL_COLS[feature]['options'])
            input_data[feature] = CATEGORICAL_COLS[feature]['map'][option]
        else:
            input_data[feature] = st.number_input(f"{feature}", value=float(50))
    
    user_df = pd.DataFrame([input_data])
    user_scaled = scaler.transform(user_df)
    
    if st.button("Predict with Random Forest"):
        prediction = rf_model.predict(user_scaled)[0]
        prediction_proba = rf_model.predict_proba(user_scaled)[0]
        if prediction == 1:
            st.error(f"High Risk of Heart Disease! (Probability: {prediction_proba[1] * 100:.2f}%)")
        else:
            st.success(f"Low Risk of Heart Disease (Probability: {prediction_proba[0] * 100:.2f}%)")
