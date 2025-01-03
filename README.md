# SharePoint Pipeline

This project is designed to fetch documents from SharePoint, parse them using LlamaParse, and create chunks for further analysis. It consists of several modules that work together to achieve this functionality.

## Project Structure

```
sharepoint-pipeline
├── src
│   ├── main.py          # Entry point for the application
│   ├── parse.py         # Functions to parse documents
│   ├── chunks.py        # Functions to chunk parsed documents
│   └── utils
│       └── __init__.py  # Placeholder for utility functions
├── .env                 # Environment variables for configuration
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd sharepoint-pipeline
   ```

2. **Create a virtual environment (optional but recommended):**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the root directory with the following variables:
   ```
   sharepoint_email=<your-email>
   sharepoint_password=<your-password>
   sharepoint_url_sites=<your-sharepoint-url>
   sharepoint_url_sites_short=<your-short-sharepoint-url>
   sharepoint_site_name=<your-site-name>
   sharepoint_doc_library=<your-document-library>
   ```

## Usage

To run the application, execute the following command:
```
python src/main.py
```

This will connect to SharePoint, fetch the documents, parse them, and create chunks for further analysis.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.