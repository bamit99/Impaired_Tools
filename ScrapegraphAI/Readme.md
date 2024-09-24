# ScrapegraphAI

ScrapegraphAI is a powerful web scraping tool with a user-friendly graphical interface. It uses AI-powered scraping to extract specific information from websites based on user-defined prompts.

## Features

- Easy-to-use graphical user interface
- AI-powered web scraping using GPT models
- Supports scraping multiple URLs in batch
- Customizable LLM prompts for targeted information extraction
- Dark mode for comfortable viewing
- Export results in JSON and CSV formats
- Real-time console output and progress tracking
- Temporary file storage for large scraping tasks

## Requirements

- Python 3.7+
- tkinter
- scrapegraphai
- python-dotenv
- openai

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/Impaired_Tools/scrapegraphai.git
   cd scrapegraphai
   ```

2. Install the required packages:
   ```
   pip install scrapegraphai python-dotenv openai
   ```

3. Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

1. Run the script:
   ```
   python scrapegraphai.py
   ```

2. In the GUI:
   - Enter the URLs you want to scrape in the "URL Input" section (one per line)
   - Customize the LLM prompt in the "LLM Prompt" section
   - Click "Scrape" to start the scraping process
   - Monitor progress in the console output and progress bar
   - View results in the "Scraping Results" section
   - Export results in JSON and/or CSV format using the "Export Results" button

## Configuration

You can modify the `create_scraper_config()` function to customize the scraper settings:

- `model`: Choose the OpenAI model to use (default: "openai/gpt-4o-mini")
- `verbose`: Set to `True` for detailed logging (default: `True`)
- `headless`: Set to `True` for headless browser scraping (default: `False`)
- `user_agent`: Customize the user agent string (default: "CustomWebScraper v1.0")

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
