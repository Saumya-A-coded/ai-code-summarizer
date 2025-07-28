 # CodeGenesis- An AI-Code-Summarizer ✒️🤖


<p align="center">
  <em>Your AI-powered partner for automatic code documentation.</em>
  <br/><br/>
  
</p>



Ever felt lost in a massive, unfamiliar GitHub repository? **CodeGenesis** is the revolutionary tool that changes everything. It acts as your personal guide, reading complex code and providing you with simple, human-readable summaries for every component. It's like having an expert developer explain a new project to you, instantly.

Stop wasting hours deciphering complex logic. Start understanding.

## 📋 Table of Contents

- [✨ Features](#-features)
- [🚀 How It Works](#-how-it-works)
- [Getting Started](#-getting-started)
- [Usage](#-usage)
- [🤝 Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

-   **Deep Code Analysis**: Goes beyond syntax to provide summaries of what the code *actually does*.
-   **Broad Language Support**: Out-of-the-box support for **Python, Java, JavaScript, and C++**, making it a versatile tool for any developer.
-   **AI-Powered Summaries**: Built on Microsoft's Autogen framework to leverage powerful, multi-agent AI systems for accurate and concise summaries.
-   **Structured Documentation**: Exports all findings into a clean `summary.json` file, creating a full "Table of Contents" for any codebase.

---

## 🚀 How It Works: Understand Any Repo in 3 Steps

1.  **Provide the Code**: Place the files from any GitHub repository into the `input_code/` folder.
2.  **Run the Analysis**: Execute a single command (`python main.py`) to unleash the AI agents.
3.  **Get Instant Insights**: Open the generated `output/summary.json` to get a full, high-level understanding of the entire project structure and logic.

---

## Getting Started

Follow these steps to get CodeGenesis running on your local machine.

### Prerequisites

-   Python 3.9+
-   A valid OpenAI API key

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Saumya-A-coded/ai-code-summarizer.git](https://github.com/Saumya-A-coded/ai-code-summarizer.git)
    cd ai-code-summarizer
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    # On Windows, use: venv\Scripts\activate
    ```
3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up your API Key:**
    Create a `.env` file in the root directory and add your API key:
    ```
    OPENAI_API_KEY="your-secret-key-here"
    ```
---

## Usage

Running the tool is simple:

1.  Place the code files you want to summarize inside the `input_code/` directory.
2.  Run the main script from the root directory:
    ```bash
    python main.py
    ```
3.  Your new documentation will be ready in the `output/summary.json` file!
4.  You can also see the output being generated in your terminal space before it gets saved 
    to `summary.json`.

### Viewing the Output ✨

The `summary.json` file contains all the rich data, but to see it in a beautiful, readable format, we recommend using an online viewer.

1.  Go to a site like [**Online JSON Viewer and Formatter**](http://jsonviewer.stack.hu/).
2.  Open your local `output/summary.json` file in a text editor and copy its entire content.
3.  Paste the content into the "Text" tab of the online viewer.
4.  Click the "Viewer" tab to see a clean, colorful, and interactive view of your code documentation!

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

### How to Show Support
If this project helps you, please give it a ⭐ **Star** on GitHub!

### How to Contribute
1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## License

Distributed under the MIT License. See `LICENSE` file for more information.


