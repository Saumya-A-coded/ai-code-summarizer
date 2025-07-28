# CodeGenesis- An AI-Code-Summarizer ✒️🤖


<p align="center">
  <em>Your AI-powered partner for automatic code documentation.</em>
  <br/><br/>
  
</p>

---

CodeGenesis AI uses multi-agent systems powered by Microsoft Autogen to read your codebase, understand the logic within functions and classes, and generate clear, natural-language summaries. Stop writing boilerplate documentation and let your AI partner do it for you.

## 📋 Table of Contents

- [ Features](#-features)
- [ Getting Started](#-getting-started)
- [ Usage](#-usage)
- [ Contributing](#-contributing)
- [ License](#-license)

---

## ✨ Features

-   **Multi-Language Parser**: Extracts functions and classes from Python and Java files.
-   **AI-Powered Summaries**: Leverages powerful LLMs to generate concise, accurate summaries.
-   **Structured Output**: Saves all documentation into a clean, easy-to-use `summary.json` file.
-   **Agent-Based System**: Built with Microsoft Autogen for robust, conversational AI interaction.

---

## 🚀 Getting Started

Follow these steps to get CodeGenesis AI running on your local machine.

### Prerequisites

-   Python 3.9+
-   A valid OpenAI API key

### Installation

1.  **Clone the repository:**
    ```bash
    git clone (git clone https://github.com/Saumya-A-coded/ai-code-summarizer.git)
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

Once installed, running the tool is simple:

1.  Place the code files you want to summarize inside the `input_code/` directory.
2.  Run the main script from the root directory:
    ```bash
    python main.py
    ```
3.  Find your generated documentation in the `output/summary.json` file!
4.  You will also see the output being generated in your terminal space.

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

### How to Show Support
If you like this project, please consider giving it a ⭐ **Star** on GitHub! It helps a lot.

### How to Contribute
1.  **Fork the Project**: Create your own copy of the repository.
2.  **Create your Feature Branch**: (`git checkout -b feature/AmazingFeature`)
3.  **Commit your Changes**: (`git commit -m 'Add some AmazingFeature'`)
4.  **Push to the Branch**: (`git push origin feature/AmazingFeature`)
5.  **Open a Pull Request**: Submit your changes for review.

Please feel free to open an **issue** if you have a suggestion or find a bug.

---

## License

Distributed under the MIT License. See `LICENSE` file for more information.
