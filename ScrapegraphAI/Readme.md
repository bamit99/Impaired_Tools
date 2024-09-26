# Intelligent Web Scraper with GUI

This project is an advanced web scraping tool that combines the power of AI-driven content extraction with a user-friendly graphical interface. It allows users to scrape multiple websites simultaneously, guided by custom prompts for targeted information retrieval. The project is based on existing Modules provided @ https://github.com/ScrapeGraphAI/Scrapegraph-ai
Please make sure to install the needed package from the above URL before proceeding to use this Python Code.

## Features

- **AI-Powered Scraping**: Utilizes OpenAI's GPT model for intelligent content extraction.
- **User-Friendly GUI**: Built with Tkinter for easy interaction and visualization of the scraping process.
- **Multi-URL Support**: Scrape multiple websites in one go.
- **Custom Prompts**: Tailor your scraping tasks with custom AI prompts.
- **Real-Time Progress Tracking**: Monitor the scraping progress for each URL.
- **Dark Mode**: Toggle between light and dark themes for comfortable viewing.
- **Export Options**: Save results in JSON and/or CSV formats.
- **Temporary File Handling**: Safely stores intermediate results to prevent data loss.

## Prerequisites

- Python 3.7+
- OpenAI API key

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/intelligent-web-scraper.git
   cd intelligent-web-scraper
   ```

2. Set up your OpenAI API key:
   - Create a `.env` file in the project root.
   - Add your API key: `OPENAI_API_KEY=your_api_key_here`

## Usage

1. Run the main script:
   ```
   python main.py
   ```

2. In the GUI:
   - Enter the URLs you want to scrape (one per line) in the "URL Input" section.
   - Customize the AI prompt in the "LLM Prompt" section if needed.
   - Click "Scrape" to start the process.
   - Monitor progress in the "Scraping Progress" bar and "Console Output".
   - View results in the "Scraping Results" section.
   - Export results using the "Export Results" button.

## Configuration

You can modify the `config.py` file to adjust settings such as:

- AI model selection
- Headless browser mode
- User agent string
- Verbosity of logging

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [OpenAI](https://openai.com/) for providing the GPT model used in this project.
- [Tkinter](https://docs.python.org/3/library/tkinter.html) for the GUI framework.
- [ScrapegrapeAI](https://github.com/scrapegrape/scrapegrape) for the intelligent scraping capabilities.

