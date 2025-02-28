# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability within LazyScholar, please send an email to [your-email]. All security vulnerabilities will be promptly addressed.

## Data Safety

### API Keys and Credentials
- **Google API Key**: The application uses Google's Generative AI API (Gemini). Store your API key in environment variables using a `.env` file.
- **Never commit API keys**: The `.env` file is included in `.gitignore` to prevent accidental exposure of credentials.

### Data Handling
1. **Academic Content**
   - All academic paper information is processed locally
   - No sensitive research data is stored permanently
   - Search results and analyses are stored temporarily during execution

2. **Logging**
   - Logs are stored locally in `research_assistant.log`
   - Logs contain process information but no sensitive data
   - Regular log rotation is recommended for production use

3. **Browser Automation**
   - Web scraping is done responsibly with appropriate delays
   - No personal user data is collected during web searches
   - Headless browser option available for enhanced privacy

### Safety Measures Implemented

1. **API Safety Settings**
   - Medium and above content filtering for:
     - Harassment
     - Hate speech
     - Sexually explicit content
     - Dangerous content

2. **Error Handling**
   - Graceful handling of API failures
   - Secure error logging without exposing sensitive information
   - Demo mode available when API access is restricted

## Best Practices for Users

1. **API Key Security**
   ```bash
   # Store your API key in .env file
   GOOGLE_API_KEY=your_api_key_here
   ```

2. **Environment Setup**
   - Use virtual environments for isolation
   - Keep dependencies updated
   - Regularly check for security updates

3. **Data Usage**
   - Review generated content before use
   - Respect academic integrity guidelines
   - Properly cite all sources used

## Version Control Safety

1. **Files to Never Commit**
   - `.env` files containing API keys
   - Log files
   - Temporary research data
   - Personal configuration files

2. **Repository Hygiene**
   - Regular security audits
   - Dependency updates
   - Code review practices
