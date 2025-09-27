# **ResuMate (Local Version) 🚀**

**Your personal, offline, and private AI-powered resume toolkit. Analyze your resume, match it against job descriptions, and check its ATS-friendliness without ever sending your data to the cloud.**

ResuMate is a Streamlit web application built to help job seekers optimize their resumes. This local version runs entirely on your machine, ensuring your personal data remains private. It uses powerful local NLP (Natural Language Processing) libraries to provide insightful analysis.

## **✨ Features**

* **🎯 Resume Matcher**: Upload your resume and one or more job descriptions to get an instant match score based on keyword similarity (TF-IDF).  
* **✅ ATS Friendliness Checker**: Get a detailed, rule-based report on how well your resume will be parsed by Applicant Tracking Systems. It checks for:  
  * Contact Information  
  * Standard Section Headings (Experience, Education, etc.)  
  * Use of Action Verbs  
  * Keyword Density  
* **📈 Analytics Dashboard**: Track your progress over time with charts showing your resume match scores and ATS scores from past analyses.  
* **🔒 Completely Private**: No APIs, no data collection. Everything runs 100% on your local machine.  
* **👥 User Authentication**: A simple and secure local user account system to keep your analysis history private.

## **🛠️ Tech Stack**

* **Framework**: [Streamlit](https://streamlit.io/)  
* **Data Analysis**: [Pandas](https://pandas.pydata.org/)  
* **NLP & Matching**: [Scikit-learn](https://scikit-learn.org/), [NLTK](https://www.nltk.org/)  
* **Plotting**: [Plotly](https://plotly.com/)  
* **Database**: [SQLite](https://www.sqlite.org/index.html)  
* **Deployment**: [Docker](https://www.docker.com/) (Optional)

## **⚙️ Installation & Setup**

Follow these steps to get ResuMate running on your local machine.

### **1\. Prerequisites**

* [Python 3.8+](https://www.python.org/downloads/)  
* pip package manager

### **2\. Clone the Repository**

git clone \[https://github.com/YOUR\_USERNAME/resumate.git\](https://github.com/YOUR\_USERNAME/resumate.git)  
cd resumate

### **3\. Install Dependencies**

Install the required Python packages using the requirements.txt file.

pip install \-r requirements.txt

### **4\. Download NLP Data**

The ATS Checker uses the NLTK library. Run the following command to download the necessary data models for it to work offline.

python \-c "import nltk; nltk.download('punkt'); nltk.download('averaged\_perceptron\_tagger'); nltk.download('stopwords')"

### **5\. Run the Application**

Once the setup is complete, you can start the Streamlit application.

streamlit run app.py

Your browser should open a new tab with the ResuMate application running\!

## **🐳 Running with Docker (Optional)**

If you have Docker installed, you can build and run the application in a container for easy setup.

\# 1\. Build the Docker image  
docker build \-t resumate .

\# 2\. Run the Docker container  
docker run \-p 8501:8501 resumate

You can then access the application at http://localhost:8501.

## **🤝 How to Contribute**

We welcome contributions of all kinds\! Whether you're a developer, a designer, or a writer, you can help make ResuMate better.

Please read our [**CONTRIBUTING.md**](https://www.google.com/search?q=CONTRIBUTING.md) file to see how you can get involved. Check out the open issues, especially those labeled good first issue.

## **📜 Code of Conduct**

To ensure a welcoming and inclusive community, we have a [**CODE\_OF\_CONDUCT.md**](https://www.google.com/search?q=CODE_OF_CONDUCT.md) that all contributors are expected to follow.

## **📄 License**

This project is licensed under the MIT License. See the [**LICENSE**](https://www.google.com/search?q=LICENSE) file for details.