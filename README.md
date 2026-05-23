# LongevAI Pipeline

A scalable AI pipeline that processes user health profiles and generates personalized health blueprints using Bio_ClinicalBERT embeddings and an LLM via OpenRouter.

## How it works

1. Load user profiles from JSON files in the `data/` folder
2. Use Bio_ClinicalBERT embeddings to match the most relevant actions from the actions library to each user
3. Send the user data and matched actions to an LLM via OpenRouter
4. Generate a personalized health blueprint with an executive summary and prioritized action cards
5. Save the results to `output/report.json`

## Setup & Installation

1. Clone the repository
2. Install dependencies:

conda install -c conda-forge sentence-transformers openai python-dotenv aiohttp numpy

3. Create a `.env` file in the root of the project:

OPENROUTER_API_KEY=your_openrouter_api_key
HF_TOKEN=your_huggingface_token

4. Run the pipeline:

python pipeline.py

## Output

The pipeline generates a structured JSON report at `output/report.json` containing:

- Processing status per user (success or failure)
- Executive summary
- Prioritized action cards with category, priority level, title and description

## Action Categories (Taxonomy)

The pipeline uses a fixed taxonomy of 10 categories:

- Nutrition
- Sleep & Recovery
- Exercise & Movement
- Stress Management
- Cognitive Performance
- Inflammation
- Metabolic Health
- Cardiovascular Health
- Gut Health
- Longevity Protocols

## Project Structure

LongevAI_pipeline/
├── data/                    # Input user profiles (JSON)
├── actions_library/         # Fixed actions library
├── output/                  # Generated reports
├── config.py                # Configuration and settings
├── embeddings.py            # Bio_ClinicalBERT embedding logic
├── llm.py                   # LLM report generation
├── pipeline.py              # Main pipeline engine
├── requirements.txt         # Dependencies
└── README.md

## Appendix: Scalability & Production Documentation

### Scalability Architecture

The pipeline uses Python's `asyncio` with `asyncio.gather()` to process all user profiles concurrently. Each user profile is processed as an independent async task, meaning the pipeline does not wait for one user to finish before starting the next. This pattern scales horizontally — for larger batches, the same approach works with a task queue such as Celery or AWS SQS, with workers processing profiles in parallel.

For very large batches (thousands of users), the recommended production architecture would be:

- A message queue (e.g. AWS SQS or RabbitMQ) receiving profile processing jobs
- Multiple worker instances running the pipeline logic concurrently
- A results database (e.g. PostgreSQL) storing blueprints per user

### Error Handling Strategy

Each user profile is processed inside a try/except block in `process_user()`. If any step fails — whether loading the JSON, generating embeddings, calling the LLM, or parsing the output — the error is caught, logged with the filename and error message, and the pipeline continues to the next user without crashing.

The final report includes a `status` field per user (`success` or `failure`) and an `error` field for failed users. This means the batch always completes, and failures are traceable.

For production, retries would be added using `tenacity` with exponential backoff for transient API errors (e.g. rate limits or timeouts).

### Production Readiness

The LLM provider is fully configurable via `config.py`. Switching from OpenRouter to another provider (e.g. Anthropic, Azure OpenAI, or a self-hosted model) requires changing only two lines in `config.py` — the `base_url` and the model name. No changes to `pipeline.py`, `llm.py` logic, or prompt structure are needed.

The embedding model is similarly configurable. The ideal production model for this use case is `longevity-ai-4432/longevity-finetuned-v1` — a Llama-based model finetuned specifically on longevity data. This model was not used in the current implementation because it lacks Inference Provider support on HuggingFace. However, once deployed (e.g. via HuggingFace Inference Endpoints or a self-hosted vLLM instance), it can be swapped in by updating a single config value.

Prompt logic is centralized in `llm.py` and can be updated independently of the pipeline architecture.

For the LLM, the ideal production choice would be `longevity-ai-4432/longevity-finetuned-v1`, 
a Llama-based model finetuned specifically on longevity and health data. This model was 
researched and identified as the best fit for this use case, but it is not deployed on any 
HuggingFace Inference Provider. As a result, `openai/gpt-oss-120b:free` via OpenRouter was 
used as a production-ready fallback. The architecture is designed so that swapping to the 
longevity model requires only a config change once it becomes available via an inference endpoint.