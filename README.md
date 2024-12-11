# Traffic Data Analysis Web Application

## Deployment Instructions for Vercel

### Prerequisites
- Vercel Account
- Python 3.8+
- Git

### Deployment Steps
1. Clone this repository
2. Create a virtual environment
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```
3. Install dependencies
   ```
   pip install -r requirements.txt
   ```
4. Ensure you have the following files:
   - `app.py`
   - `vercel.json`
   - `requirements.txt`
   - `static/` directory with CSS and JS files
   - `templates/` directory with HTML files

5. Deploy to Vercel
   ```
   vercel
   ```

### Notes
- The application uses `/tmp` directory for temporary file uploads
- Ensure all static files are in the correct directories
- The application is configured to work with Vercel's serverless environment

### License
This project is licensed under the [MIT License](LICENSE).