# 🌱 GreenCode Sentinel

**AI-Powered Carbon Footprint Analyzer for Source Code**

GreenCode Sentinel uses Google Gemini 3 Pro with high-level thinking to analyze source code (Python, Java, JavaScript) and identify carbon-heavy patterns. It provides actionable refactoring suggestions to reduce cloud infrastructure energy consumption.

Built for the IBM Dev Day Hackathon 🚀

---

## 🎯 Features

- **🧠 Gemini 3 Pro Integration**: Leverages Google's most advanced AI with "high thinking level" for deep code analysis
- **🌍 Multi-Language Support**: Analyzes Python, Java, and JavaScript code
- **📊 Sustainability Scoring**: 0-100 score with letter grades (A+ to F)
- **💚 CO₂ Estimation**: Calculates potential carbon savings in kg/year
- **🎨 Professional UI**: Clean Flet dashboard with file upload and visual gauges
- **🐳 Docker Ready**: Containerized deployment for easy setup
- **🔒 Secure**: Environment-based credential management

---

## 🏗️ Architecture

```
GreenCode-Sentinel/
├── ai_engine/          # Core AI logic
│   ├── gemini_client.py    # Gemini 3 Pro integration
│   ├── analyzer.py         # Universal code analyzer
│   ├── carbon_scorer.py    # Scoring algorithm
│   └── prompts.py          # Language-specific prompts
├── app/                # Flet UI application
│   ├── main.py            # Entry point
│   ├── ui/                # UI components
│   └── utils/             # Helper utilities
├── data/
│   └── samples/           # Test files (dirty code examples)
├── tests/              # Unit tests
└── Dockerfile          # Container configuration
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Google API Key for Gemini 3 Pro
- pip (Python package manager)

### Step 1: Get Your Google API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the generated API key (you'll need it in Step 3)

> **Note**: The API key is free to use with generous quotas for testing and development.

### Step 2: Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd GreenCode-Sentinel

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy the template
cp .env.template .env

# Edit .env and add your Google API key
# Windows: notepad .env
# macOS/Linux: nano .env
```

Update the `.env` file:
```env
GOOGLE_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-3.1-pro-preview
GEMINI_THINKING_LEVEL=high
```

### Step 4: Test Connection

```bash
# Run the connection test
python test_gemini_connection.py
```

You should see:
```
✅ Gemini 3 Pro connection successful!
✅ ALL TESTS PASSED!
```

### Step 5: Run the Application

```bash
# Start the Flet UI
python app/main.py
```

The dashboard will open in your browser at `http://localhost:8080`

---

## 📖 Usage

### Analyzing Code Files

1. **Upload a File**: Click the upload button or drag-and-drop a `.py`, `.java`, or `.js` file
2. **View Analysis**: The AI will analyze the code using Gemini 3 Pro's high thinking level
3. **Check Score**: See your sustainability score (0-100) and grade
4. **Review Issues**: Examine specific carbon-heavy patterns found
5. **Get Suggestions**: Read actionable refactoring recommendations
6. **Estimate Impact**: See potential CO₂ savings in kg/year

### Testing with Sample Files

Try the included "dirty" code samples:

```bash
# Analyze Python sample
python -c "from ai_engine import CodeAnalyzer; analyzer = CodeAnalyzer(); print(analyzer.analyze_file('data/samples/dirty_python.py'))"

# Analyze Java sample
python -c "from ai_engine import CodeAnalyzer; analyzer = CodeAnalyzer(); print(analyzer.analyze_file('data/samples/dirty_java.java'))"

# Analyze JavaScript sample
python -c "from ai_engine import CodeAnalyzer; analyzer = CodeAnalyzer(); print(analyzer.analyze_file('data/samples/dirty_javascript.js'))"
```

---

## 🧪 Understanding the Scoring

### Sustainability Score (0-100)

The score is calculated based on four categories:

| Category | Weight | Focus Areas |
|----------|--------|-------------|
| **Loops** | 40% | Nested loops, inefficient iterations, O(n²) complexity |
| **Memory** | 30% | Large allocations, memory leaks, unnecessary copies |
| **Network** | 20% | Redundant API calls, inefficient data transfers |
| **Complexity** | 10% | High cyclomatic complexity, code smells |

### Grade Scale

- **A+ (95-100)**: Excellent - Minimal carbon footprint
- **A (90-94)**: Very Good - Minor optimizations possible
- **B (75-89)**: Good - Some improvements recommended
- **C (60-74)**: Fair - Significant optimizations needed
- **D (50-59)**: Poor - Major refactoring required
- **F (0-49)**: Critical - Severe inefficiencies detected

### CO₂ Estimation

The tool estimates annual CO₂ savings based on:
- **CPU Reduction**: Saved processing cycles
- **Memory Reduction**: Lower memory footprint
- **Network Reduction**: Fewer API calls and data transfers
- **Usage Factor**: Estimated executions per year (default: 1000)
- **Cloud Carbon Intensity**: 0.000379 kg CO₂/kWh (AWS average)

---

## 🐳 Docker Deployment

### Build and Run

```bash
# Build the Docker image
docker build -t greencode-sentinel .

# Run the container
docker run -p 8080:8080 --env-file .env greencode-sentinel
```

### Using Docker Compose

```bash
# Start the application
docker-compose up

# Stop the application
docker-compose down
```

Access the dashboard at `http://localhost:8080`

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Your Google Gemini API key | *Required* |
| `GEMINI_MODEL` | Gemini model to use | `gemini-3.1-pro-preview` |
| `GEMINI_THINKING_LEVEL` | AI reasoning depth (low/medium/high) | `high` |
| `GEMINI_TEMPERATURE` | Response randomness (0.0-1.0) | `0.1` |
| `GEMINI_MAX_TOKENS` | Maximum response length | `4096` |
| `APP_PORT` | Application port | `8080` |
| `DEBUG_MODE` | Enable debug logging | `false` |

### Thinking Levels

- **low**: Fast responses, basic analysis
- **medium**: Balanced speed and depth
- **high**: Deep reasoning, comprehensive analysis (recommended)

---

## 🧩 API Usage

### Programmatic Analysis

```python
from ai_engine import CodeAnalyzer

# Initialize analyzer
analyzer = CodeAnalyzer()

# Analyze a file
results = analyzer.analyze_file("path/to/code.py")

# Analyze code string
code = """
def inefficient_function():
    # Your code here
    pass
"""
results = analyzer.analyze_code(code, language="python")

# Access results
print(f"Score: {results['score']}/100")
print(f"Grade: {results['grade']}")
print(f"CO₂ Savings: {results['co2_savings_kg_year']} kg/year")
print(f"Issues: {results['total_issues']}")
```

---

## 📊 Example Output

```
============================================================
GREENCODE SENTINEL - SUSTAINABILITY REPORT
============================================================

Overall Score: 45.3/100 (Grade: F)

Total Issues Found: 8
  - Critical: 2
  - High: 3
  - Medium: 2
  - Low: 1

Category Breakdown:
  - Loops: 32/100
  - Memory: 51/100
  - Network: 68/100
  - Complexity: 55/100

Estimated CO₂ Savings (if optimized):
  - 847.5 kg/year
  - 0.8475 tons/year

Summary: Multiple critical inefficiencies detected including triple
nested loops (O(n³) complexity) and redundant API calls without caching.
Refactoring recommended to reduce energy consumption.
============================================================
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Google Gemini 3 Pro**: For providing advanced AI capabilities
- **IBM Dev Day Hackathon**: For the inspiration and opportunity
- **Flet Framework**: For the beautiful UI components
- **Open Source Community**: For the amazing tools and libraries

---

## 📧 Contact

For questions, issues, or suggestions:
- Open an issue on GitHub
- Email: tmutsvairo18@gmail.com

---

## 🌟 Star This Project

If you find GreenCode Sentinel useful, please give it a ⭐ on GitHub!

**Together, let's make code more sustainable! 🌱**
