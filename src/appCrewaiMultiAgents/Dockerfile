FROM python:3.10-slim

WORKDIR /appCrewaiMultiAgents

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables to disable telemetry
ENV CREWAI_DISABLE_TELEMETRY=true
ENV OTEL_SDK_DISABLED=true
ENV OPENAI_API_KEY = none

COPY . .

ENV PYTHONPATH="${PYTHONPATH}:/appCrewaiMultiAgents"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
