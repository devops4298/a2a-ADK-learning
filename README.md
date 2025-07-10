# Google Agent Development Kit (ADK) - Simple Weather & Time Agent

This project demonstrates how to create a simple AI agent using Google's Agent Development Kit (ADK). The agent can answer questions about weather and time for specific cities.

## Features

- **Weather Information**: Get weather reports for supported cities (New York, Chicago)
- **Time Information**: Get current time for supported cities (New York, Chicago)
- **Interactive CLI**: Chat with the agent via command line
- **Web Interface**: Use the browser-based development UI
- **Function Tools**: Demonstrates how to create and use custom function tools

## Project Structure

```
a2a-ADK-learning/
├── README.md
├── requirements.txt
├── .venv/                    # Python virtual environment
└── multi_tool_agent/
    ├── __init__.py          # Package initialization
    ├── agent.py             # Main agent implementation
    └── .env                 # Environment configuration
```

## Setup Instructions

### 1. Prerequisites

- Python 3.9+ installed
- Terminal access

### 2. Environment Setup

1. **Clone or navigate to this directory**
2. **Create and activate virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Configure API Access

You need to configure access to Google's AI models. Choose one of the following options:

#### Option A: Google AI Studio (Recommended for beginners)

1. Get an API key from [Google AI Studio](https://aistudio.google.com/apikey)
2. Edit `multi_tool_agent/.env` and replace `PASTE_YOUR_ACTUAL_API_KEY_HERE` with your API key:
   ```
   GOOGLE_GENAI_USE_VERTEXAI=FALSE
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

#### Option B: Google Cloud Vertex AI

1. Set up a [Google Cloud project](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-gcp)
2. Install and configure [gcloud CLI](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local)
3. Authenticate: `gcloud auth login`
4. Enable the [Vertex AI API](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com)
5. Edit `multi_tool_agent/.env`:
   ```
   GOOGLE_GENAI_USE_VERTEXAI=TRUE
   GOOGLE_CLOUD_PROJECT=your_project_id
   GOOGLE_CLOUD_LOCATION=us-central1
   ```

## Running the Agent

### Command Line Interface

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the interactive CLI
adk run multi_tool_agent
```

Example conversation:
```
[user]: What is the weather in New York?
[agent]: The weather in New York is sunny with a temperature of 25 degrees Celsius (77 degrees Fahrenheit).

[user]: What time is it in Chicago?
[agent]: The current time in Chicago is 2024-07-10 10:55:13 CDT-0500

[user]: exit
```

### Web Interface

```bash
# Activate virtual environment
source .venv/bin/activate

# Start the web server
adk web
```

Then open http://localhost:8000 in your browser. You can:
- Select "multi_tool_agent" from the dropdown
- Chat with the agent in the web interface
- View function calls and responses in the Events tab
- See trace logs for debugging

## Example Prompts to Try

- "What is the weather in New York?"
- "What is the time in Chicago?"
- "What is the weather in Paris?" (will show error handling)
- "Tell me the time and weather in New York"

## Agent Implementation Details

The agent is implemented in `multi_tool_agent/agent.py` with:

### Function Tools

1. **get_weather(city: str)**: Returns weather information for supported cities
2. **get_current_time(city: str)**: Returns current time for supported cities

### Agent Configuration

- **Model**: `gemini-2.0-flash`
- **Name**: `weather_time_agent`
- **Tools**: Weather and time functions
- **Instructions**: Helpful assistant for weather and time queries

## Extending the Agent

To add more functionality:

1. **Add new cities**: Modify the city checks in `get_weather()` and `get_current_time()`
2. **Add new tools**: Create new functions and add them to the `tools` list
3. **Change the model**: Update the `model` parameter in the Agent configuration
4. **Modify instructions**: Update the `instruction` parameter for different behavior

## Troubleshooting

### Common Issues

1. **API Key Error**: Make sure you've set a valid API key in the `.env` file
2. **Import Error**: Ensure you're in the parent directory when running `adk` commands
3. **Virtual Environment**: Always activate the virtual environment before running commands

### Logs

ADK creates detailed logs in `/tmp/agents_log/`. Check the latest log for debugging:
```bash
tail -F /tmp/agents_log/agent.latest.log
```

## Next Steps

- Explore the [ADK Documentation](https://google.github.io/adk-docs/)
- Try the [ADK Tutorials](https://google.github.io/adk-docs/tutorials/)
- Check out [Sample Agents](https://github.com/google/adk-samples)
- Learn about [Multi-agent Systems](https://google.github.io/adk-docs/agents/multi-agents/)

## License

This project is for educational purposes. Please refer to Google's ADK license for usage terms.