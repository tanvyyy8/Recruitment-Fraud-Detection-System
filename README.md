# Recruitment Fraud Detection System

## Description

The Recruitment Fraud Detection System is an AI-powered web application developed to identify fraudulent job postings and help job seekers avoid recruitment scams. Users can enter job details such as the job title, company information, location, salary, employment type, and job description. The system preprocesses the input text using Natural Language Processing (NLP), analyzes the content using a deep learning model, and classifies the job posting as **Legitimate** or **Fraudulent**. To ensure transparency, the application also provides explanations for its predictions using Explainable AI techniques, enabling users to understand the factors influencing the decision.

## Models and Algorithms Used

* **DistilBERT**

  * Used as the primary deep learning model for fraud classification.
  * Generates contextual embeddings by understanding the meaning and relationships between words in a job posting.
  * Provides faster inference with lower computational cost while maintaining high classification accuracy

* **LIME (Local Interpretable Model-agnostic Explanations)**

  * Explains individual predictions by identifying the words and features that contributed most to the classification.
  * Helps users understand why a job posting was marked as legitimate or fraudulent.

* **SHAP (SHapley Additive exPlanations)**

  * Measures the contribution of each feature to the model's prediction using Shapley values.
  * Provides both local and global interpretability, making the AI model more transparent and trustworthy.

## Technologies Used

* **Frontend:** HTML, CSS, Bootstrap, JavaScript
* **Backend:** Python, Django
* **Deep Learning:** DistilBERT (Transformers)
* **NLP:** NLTK
* **Explainable AI:** SHAP, LIME
* **Database:** MySQL

