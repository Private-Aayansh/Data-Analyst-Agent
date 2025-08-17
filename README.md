# Data Analysis Agent 🤖📊

A powerful AI-driven data analysis service that intelligently processes user questions and uploaded files using multiple large language models (Gemini 2.5 Pro/Flash and OpenAI GPT-4) with integrated web scraping capabilities.

## Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Directory Structure](#directory-structure)
- [Environment Setup](#environment-setup)
- [Local Development](#local-development)
- [API Usage](#api-usage)
- [Cloud Deployment](#cloud-deployment)
  - [AWS Deployment](#aws-deployment)
  - [Google Cloud Platform (GCP)](#google-cloud-platform-gcp)
- [Configuration](#configuration)
- [Supported File Types](#supported-file-types)
- [Error Handling](#error-handling)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

The Data Analysis Agent is a FastAPI-based service that combines the power of multiple AI models to provide comprehensive data analysis. It intelligently determines when web scraping is needed, processes various file formats, and runs parallel AI model inference to deliver robust, accurate results.

### How It Works

1. **Question Analysis**: Determines if web scraping or search is needed based on user queries
2. **Data Collection**: Scrapes web content or searches online when required using Tavily
3. **File Processing**: Handles multiple file formats (CSV, JSON, images, etc.) via Google's Gemini API
4. **Parallel AI Processing**: Runs multiple Gemini models simultaneously for robust analysis
5. **Result Synthesis**: Uses OpenAI to merge and format the final response

## Key Features

- 🧠 **Multi-Model AI Processing**: Parallel execution of Gemini 2.5 Pro, Flash, and GPT-4
- 🌐 **Intelligent Web Scraping**: Automatic detection and execution of web searches/scraping via Tavily
- 📁 **Multi-Format File Support**: CSV, JSON, TXT, images (PNG, JPG), Excel, and more
- ⚡ **Concurrent Processing**: ThreadPoolExecutor for optimal performance
- 🔒 **Secure File Handling**: Temporary file processing with proper cleanup
- 🎯 **Structured Output**: JSON-formatted responses with type validation
- 🐳 **Docker Ready**: Containerized deployment with Docker
- 🚀 **Production Ready**: FastAPI with CORS support and comprehensive error handling

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI       │    │  Gemini Models   │    │   OpenAI GPT-4  │
│   Endpoint      │───▶│  (2.5 Pro/Flash) │───▶│   (Synthesis)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  File Upload    │    │  Code Execution  │    │ Structured JSON │
│  Processing     │    │  & Analysis      │    │    Response     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│ Tavily Search/  │
│ Scraping Engine │
└─────────────────┘
```

## Prerequisites

- **Python**: 3.11 or higher
- **API Keys**:
  - Google Gemini API key
  - OpenAI API key  
  - Tavily API key
- **Docker** (optional, for containerized deployment)
- **Cloud Account** (AWS/GCP for cloud deployment)

## Directory Structure

```
data-analyst-agent/
├── api.py                 # FastAPI main application
├── answer.py              # Core analysis logic with parallel processing
├── scrap.py               # Web scraping decision engine
├── utils/
│   ├── gemini_client.py   # Google Gemini API client
│   ├── openai_client.py   # OpenAI API client
│   └── tavily_client.py   # Tavily search/scraping client
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker container configuration
├── .env.example          # Environment variables template
├── LICENSE               # MIT License
└── README.md            # This file
```

## Environment Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Private-Aayansh/Data-Analyst-Agent.git
   cd Data-Analyst-Agent
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

   Required environment variables:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

## Local Development

1. **Start the development server**:
   ```bash
   uvicorn api:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access the API**:
   - API Endpoint: `http://localhost:8000`
   - Interactive Docs: `http://localhost:8000/docs`
   - OpenAPI Schema: `http://localhost:8000/openapi.json`

3. **Run with Docker**:
   ```bash
   docker build -t data-analyst-agent .
   docker run -p 8000:8000 --env-file .env data-analyst-agent
   ```

## API Usage

### Endpoint: `POST /api`

Send a multipart form request with:
- `questions.txt`: Text file containing your analysis questions
- Additional files: CSV, JSON, images, or other data files

**Example using cURL**:
```bash
curl "http://localhost:8000/api" \
     -F "questions.txt=@questions.txt" \
     -F "data.csv=@sales_data.csv" \
     -F "chart.png=@revenue_chart.png"
```

**Example questions.txt**:
```
Analyze the sales data and answer:
1. What is the total revenue by region?
2. Which product category has the highest growth?
3. Create a summary of key insights from the revenue chart.

Return results in JSON format with keys: total_revenue, top_region, growth_category, insights.
```

**Response Format**:
```json
{
  "total_revenue": 1250000,
  "top_region": "North America",
  "growth_category": "Electronics",
  "insights": [
    "Revenue increased 23% year-over-year",
    "Mobile devices drove 40% of electronics growth"
  ]
}
```

## Cloud Deployment

### AWS Deployment

#### Option 1: AWS App Runner
```bash
# 1. Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker build -t data-analyst-agent .
docker tag data-analyst-agent:latest <account>.dkr.ecr.us-east-1.amazonaws.com/data-analyst-agent:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/data-analyst-agent:latest

# 2. Create App Runner service via AWS Console or CLI
aws apprunner create-service --cli-input-json file://apprunner-config.json
```

#### Option 2: AWS ECS with Fargate
```bash
# 1. Create ECS cluster
aws ecs create-cluster --cluster-name data-analyst-cluster

# 2. Create task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# 3. Create service
aws ecs create-service --cluster data-analyst-cluster --service-name data-analyst-service --task-definition data-analyst-agent:1 --desired-count 1
```

#### Option 3: AWS Lambda (with Mangum)
```bash
# Install additional dependency
pip install mangum

# Deploy with AWS SAM or Serverless Framework
sam build
sam deploy --guided
```

### Google Cloud Platform (GCP)

#### Option 1: Cloud Run
```bash
# 1. Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/data-analyst-agent

# 2. Deploy to Cloud Run
gcloud run deploy data-analyst-agent \
  --image gcr.io/PROJECT_ID/data-analyst-agent \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=$GEMINI_API_KEY,OPENAI_API_KEY=$OPENAI_API_KEY,TAVILY_API_KEY=$TAVILY_API_KEY
```

#### Option 2: Google Kubernetes Engine (GKE)
```bash
# 1. Create GKE cluster
gcloud container clusters create data-analyst-cluster --num-nodes=3

# 2. Deploy with kubectl
kubectl apply -f k8s-deployment.yaml
kubectl apply -f k8s-service.yaml
```

#### Option 3: App Engine
```yaml
# app.yaml
runtime: python311
env: standard

env_variables:
  GEMINI_API_KEY: "your_key_here"
  OPENAI_API_KEY: "your_key_here"
  TAVILY_API_KEY: "your_key_here"

automatic_scaling:
  min_instances: 1
  max_instances: 10
```

```bash
gcloud app deploy
```

## Configuration

### Model Configuration
The system uses multiple AI models for robust analysis:
- **Gemini 2.5 Pro**: Complex reasoning and analysis
- **Gemini 2.5 Flash**: Fast processing and code execution
- **OpenAI GPT-4.1 Nano**: Result synthesis and formatting

### Timeout Settings
- Default processing timeout: 150 seconds
- Individual model timeout: 80 seconds
- Adjustable via environment variables

### File Upload Limits
- Maximum file size: Configurable (default: 10MB per file)
- Supported concurrent uploads: Multiple files per request
- Temporary file cleanup: Automatic

## Supported File Types

| Format | Extensions | Processing Method |
|--------|------------|-------------------|
| **Tabular Data** | `.csv`, `.tsv`, `.xlsx` | Pandas DataFrame |
| **Structured Data** | `.json`, `.jsonl` | JSON parsing |
| **Text Files** | `.txt`, `.md` | Plain text reading |
| **Images** | `.png`, `.jpg`, `.jpeg` | PIL/Computer Vision |
| **Documents** | `.pdf` | Text extraction |

## Error Handling

The system includes comprehensive error handling:
- **API Validation**: Input validation with detailed error messages
- **Timeout Management**: Graceful handling of long-running operations
- **Model Fallbacks**: Continues processing even if individual models fail
- **File Processing**: Safe handling of corrupted or unsupported files
- **Rate Limiting**: Built-in protection against API rate limits

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add type hints for all functions
- Include docstrings for public methods
- Write tests for new features
- Update documentation as needed

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ using FastAPI, Google Gemini, OpenAI, and Tavily**

For questions or support, please open an issue on GitHub.