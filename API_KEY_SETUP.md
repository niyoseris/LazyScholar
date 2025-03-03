# Setting Up Your Google API Key for LazyScholar

LazyScholar uses Google's Gemini models to analyze research topics and generate content. To use these features, you'll need to set up a Google API key. This guide will walk you through the process.

## Getting a Google API Key

1. **Visit Google AI Studio**:
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account if you haven't already

2. **Create an API Key**:
   - Click on "Get API key" or "Create API key"
   - Give your key a name (e.g., "LazyScholar Research")
   - Click "Create"

3. **Copy Your API Key**:
   - Your new API key will be displayed
   - Copy this key to your clipboard
   - **Important**: Keep this key secure and don't share it publicly

## Setting Up Your API Key in LazyScholar

1. **Create or Edit the .env File**:
   - Navigate to your LazyScholar project directory
   - Create a file named `.env` if it doesn't exist
   - Open the file in a text editor

2. **Add Your API Key**:
   - Add the following line to the `.env` file:
     ```
     GOOGLE_API_KEY=your_api_key_here
     ```
   - Replace `your_api_key_here` with the API key you copied

3. **Save the File**:
   - Save the `.env` file
   - Make sure it's in the root directory of the LazyScholar project

## Verifying Your API Key

To verify that your API key is working correctly:

1. Run LazyScholar with the `--dry-run` option:
   ```bash
   python lazy_scholar.py "Your research topic" --dry-run
   ```

2. Check the output:
   - If successful, you should see "Gemini models initialized successfully"
   - If there's an error with your API key, you'll see an error message

## Troubleshooting API Key Issues

If you encounter issues with your API key:

1. **Invalid API Key Error**:
   - Double-check that you've copied the entire API key correctly
   - Ensure there are no extra spaces or characters in your `.env` file

2. **API Quota Exceeded**:
   - Google may limit the number of API calls you can make
   - Wait a while before trying again
   - Consider upgrading your API quota if you use LazyScholar frequently

3. **Model Not Available Error**:
   - Ensure you have access to the Gemini models
   - Some models may require additional permissions or be in limited preview

## Using LazyScholar Without an API Key

LazyScholar can still function without a valid API key, but with limited capabilities:

- It will use pre-defined templates for topic generation instead of custom analysis
- The content extraction and final paper generation will use default templates
- You'll still be able to search and download PDFs

To use LazyScholar without an API key, simply run it without setting up the `.env` file or with an invalid key. The program will automatically fall back to using default templates.

## API Usage and Costs

- The Google Gemini API may have usage limits and potential costs beyond the free tier
- Check the [Google AI Studio pricing page](https://ai.google.dev/pricing) for current information
- LazyScholar is designed to be efficient with API calls to minimize costs

## Keeping Your API Key Secure

- Never commit your `.env` file to version control
- Don't share your API key in public forums or repositories
- Consider using environment variables instead of the `.env` file in production environments 