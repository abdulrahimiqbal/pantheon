# Vercel Deployment Guide

This guide explains how to deploy the Pantheon Physics Swarm project to Vercel with automatic GitHub deployments.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Your project should be in a GitHub repository
3. **Environment Variables**: Set up required API keys (OpenAI, Anthropic, Tavily, etc.)

## Deployment Steps

### 1. Connect GitHub to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository
4. Vercel will automatically detect the `vercel.json` configuration

### 2. Configure Environment Variables

In your Vercel project settings, add these environment variables:

```bash
# Required for Physics Swarm
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
TAVILY_API_KEY=your_tavily_api_key
BRIGHTDATA_API_KEY=your_brightdata_api_key

# Optional
PYTHONPATH=/var/task
NODE_ENV=production
```

### 3. GitHub Actions Setup (Optional)

For additional CI/CD features, add these secrets to your GitHub repository:

1. Go to your GitHub repository
2. Navigate to Settings > Secrets and variables > Actions
3. Add these secrets:
   - `VERCEL_TOKEN`: Your Vercel API token
   - `VERCEL_ORG_ID`: Your Vercel organization ID
   - `VERCEL_PROJECT_ID`: Your Vercel project ID

To get these values:
- **VERCEL_TOKEN**: Go to Vercel Account Settings > Tokens
- **VERCEL_ORG_ID** and **VERCEL_PROJECT_ID**: Found in your project's `.vercel/project.json` after first deployment

### 4. Automatic Deployments

Once configured, Vercel will automatically:
- Deploy on every push to `main` branch
- Create preview deployments for pull requests
- Run the build process using the `vercel.json` configuration

## Project Structure

The deployment configuration includes:

```
├── vercel.json              # Vercel configuration
├── .vercelignore           # Files to exclude from deployment
├── requirements.txt        # Python dependencies
├── orchestration/
│   └── main.py            # FastAPI backend (main entry point)
├── physics_swarm/         # AI agent swarm code
└── .github/workflows/
    └── vercel.yml         # GitHub Actions workflow
```

## API Endpoints

After deployment, your application will have:

- **Frontend**: `https://your-app.vercel.app/`
- **API Health Check**: `https://your-app.vercel.app/api/health`
- **Physics Query**: `https://your-app.vercel.app/api/physics/query`
- **Agent Status**: `https://your-app.vercel.app/api/agents/status`
- **API Documentation**: `https://your-app.vercel.app/api/docs`

## Testing the Deployment

1. Visit your deployed URL
2. Try asking a physics question through the web interface
3. Check the API endpoints directly
4. Monitor the Vercel deployment logs for any issues

## Troubleshooting

### Common Issues

1. **Build Failures**: Check that all dependencies are in `requirements.txt`
2. **Import Errors**: Ensure `PYTHONPATH` is set correctly
3. **API Key Issues**: Verify environment variables are set in Vercel
4. **Function Timeout**: Large AI responses may timeout (increase in vercel.json)

### Debugging

- Check Vercel deployment logs in the dashboard
- Use `vercel logs` CLI command
- Test API endpoints individually
- Monitor function execution time

## Local Development

To run locally:

```bash
# Install dependencies
pip install -r requirements.txt
npm install

# Run the FastAPI server
cd orchestration
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Visit http://localhost:8000
```

## Scaling Considerations

- **Function Limits**: Vercel has execution time limits for serverless functions
- **Memory Usage**: Large AI models may require memory optimization
- **Cold Starts**: First requests may be slower due to serverless cold starts
- **Rate Limits**: Consider implementing rate limiting for API endpoints

## Security

- Never commit API keys to the repository
- Use environment variables for all sensitive data
- Consider implementing authentication for production use
- Monitor API usage and costs

## Support

For issues with:
- **Vercel Platform**: Check [Vercel Documentation](https://vercel.com/docs)
- **GitHub Actions**: See [GitHub Actions Documentation](https://docs.github.com/en/actions)
- **Project Code**: Check the project README and issues 