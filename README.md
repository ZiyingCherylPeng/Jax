# 📄 Jax

A simple Streamlit app that answers questions about an uploaded document via OpenAI's GPT-3.5.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://document-question-answering-template.streamlit.app/)

## Introduction
Jax is an intelligent knowledge chatbot designed to assist users by retrieving information from Cayenta's internal documents and the Jira database based on their queries. It leverages advanced retrieval technologies to provide fast and accurate responses.

## Key Features

- **Information Retrieval**: Capable of fetching relevant information from Cayenta's internal documents and the Jira database based on user queries.
- **User-Friendly Interface**: Offers an intuitive interface that allows users to easily input questions and receive answers.

## Installation

### Method 1: Using Docker

1. Build the Docker image:
   ```
   docker build -t jax .
   ```
2. Run the Docker container:
   ```
   docker run -p 8501:8501 jax
   ```
3. Access in the browser:
    ```
   http://localhost:8501
   ```


### Method 2: Visit the Web Page

Directly visit the Jax Chatbot at:
[https://jax-api.agreeablesand-7439a19b.canadacentral.azurecontainerapps.io/](https://jax-api.agreeablesand-7439a19b.canadacentral.azurecontainerapps.io/)


## License





   
