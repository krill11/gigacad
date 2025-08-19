# CoralMaker - AI-Powered CAD Generation 🤖

CoralMaker is an innovative AI agent that generates CAD parts in Onshape using natural language descriptions. This project represents a significant step toward AI-powered CAD, combining the power of large language models with Onshape's robust API to create 3D parts from simple text prompts.

## 🌟 Features

- **Natural Language CAD Generation**: Describe parts in plain English and watch them come to life
- **Onshape Integration**: Direct API integration with Onshape for professional CAD workflows
- **Flexible LLM Support**: Works with Groq API (Qwen2.5-32B) and local LMStudio endpoints
- **Multiple Interfaces**: Command-line interface and web API for different use cases
- **Tool-Based Architecture**: Extensible system for adding new CAD operations
- **Session Management**: Maintains CAD session state across operations

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Onshape account with API access
- Groq API key (or LMStudio for local use)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/coralmaker.git
   cd coralmaker
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

4. **Configure your API keys**
   ```bash
   # Onshape API Keys (required)
   ONSHAPE_ACCESS_KEY=your_access_key_here
   ONSHAPE_SECRET_KEY=your_secret_key_here
   
   # Groq API Key (required for cloud LLM)
   GROQ_API_KEY=your_groq_api_key_here
   
   # LMStudio (optional, for local LLM)
   LMSTUDIO_BASE_URL=http://localhost:1234/v1
   ```

### Getting Onshape API Keys

1. Go to [Onshape Developer Portal](https://cad.onshape.com/appstore/dev-portal)
2. Click "API keys" in the left pane
3. Click "Create new API key"
4. Select appropriate scopes (OAuth2Read, OAuth2Write recommended)
5. Copy both access key and secret key
6. **Important**: Save the secret key immediately - you won't see it again!

### Usage

#### Command Line Interface

```bash
# Start the CLI
python main.py cli

# Or run directly
python -m src.cli
```

**CLI Commands:**
- `create <description>` - Create a part from description
- `status` - Show current session status
- `reset` - Reset current session
- `help` - Show available commands
- `quit` - Exit the program

**Example:**
```
🤖 CAD Agent > create Create a rectangular box that is 10mm wide, 20mm tall, and 15mm deep
```

#### Web API

```bash
# Start the web server
python main.py web

# Or run directly
python -m src.api
```

The web API will be available at `http://localhost:8000`

**API Endpoints:**
- `POST /create-part` - Create a part from description
- `GET /status` - Get current session status
- `POST /reset` - Reset current session
- `GET /tools` - Get available CAD tools
- `GET /health` - Health check

#### Web Interface

Open `static/index.html` in your browser for a user-friendly web interface.

## 🏗️ Architecture

### Core Components

1. **CADAgent** (`src/ai_agent.py`)
   - Main AI agent coordinating LLM and Onshape operations
   - Manages CAD session state
   - Executes tool calls from LLM

2. **OnshapeClient** (`src/onshape_client.py`)
   - Handles Onshape API authentication and requests
   - Implements HMAC signature generation
   - Provides CAD operation methods

3. **LLM Interface** (`src/llm_interface.py`)
   - Abstract interface for different LLM providers
   - Supports Groq API and local LMStudio
   - Handles tool calling and responses

4. **Configuration** (`src/config.py`)
   - Environment variable management
   - Configuration validation
   - Centralized settings

### Tool System

The AI agent uses a tool-based approach where the LLM can call specific CAD functions:

- **create_document** - Create new Onshape documents
- **create_part_studio** - Create part studios for 3D modeling
- **create_box** - Generate rectangular prism features
- **create_cylinder** - Generate cylindrical features

### Authentication Flow

1. **API Key Generation**: HMAC-SHA256 signatures for each request
2. **Request Signing**: Includes nonce, timestamp, and request details
3. **Secure Communication**: All requests authenticated and signed

## 🔧 Development

### Project Structure

```
coralmaker/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── config.py            # Configuration management
│   ├── onshape_client.py    # Onshape API client
│   ├── llm_interface.py     # LLM provider interfaces
│   ├── ai_agent.py          # Main AI agent logic
│   ├── api.py               # FastAPI web interface
│   └── cli.py               # Command-line interface
├── static/
│   └── index.html           # Web interface
├── main.py                  # Main entry point
├── requirements.txt          # Python dependencies
├── env.example              # Environment variables template
└── README.md                # This file
```

### Adding New CAD Operations

1. **Extend OnshapeClient** with new methods
2. **Add tool definition** to CADAgent.tools
3. **Implement execution logic** in _execute_tool_call
4. **Update system message** with new capabilities

### Testing

```bash
# Run CLI tests
python -m src.cli

# Test web API
python main.py web
# Then visit http://localhost:8000/docs for interactive API docs
```

## 🌐 API Reference

### Onshape API Integration

The system integrates with Onshape's REST API, supporting:
- Document and workspace management
- Part studio creation and management
- Feature creation (extrusions, basic shapes)
- Sketch operations

### LLM Integration

Supports multiple LLM providers:
- **Groq**: Cloud-based, fast inference
- **LMStudio**: Local deployment, privacy-focused

## 🚧 Limitations & Future Work

### Current Limitations
- Basic geometric shapes only (boxes, cylinders)
- Limited to simple operations
- No assembly support yet
- Basic error handling

### Planned Features
- Advanced geometric operations (lofts, sweeps, patterns)
- Assembly creation and management
- Drawing generation
- Export to common formats (STEP, STL)
- More sophisticated LLM prompting
- Batch operations
- Version control integration

## 🤝 Contributing

We welcome contributions! Areas for improvement:
- Additional CAD operations
- Better error handling and validation
- Performance optimizations
- Documentation improvements
- Test coverage
- UI/UX enhancements

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Onshape](https://onshape.com) for their excellent API and CAD platform
- [Groq](https://groq.com) for fast LLM inference
- [LMStudio](https://lmstudio.ai) for local LLM deployment
- The open-source community for inspiration and tools

## 📞 Support

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: GitHub Discussions for questions and ideas
- **Email**: For private inquiries

---

**Note**: This is an experimental project exploring AI-powered CAD. Use at your own risk and always verify generated designs before production use.

**Happy CAD-ing with AI! 🎨🤖** 