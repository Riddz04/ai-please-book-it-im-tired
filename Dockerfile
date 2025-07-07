FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose ports
EXPOSE 8000 8501

# Create startup script that starts both services
RUN echo '#!/bin/bash\n\
echo "Starting AI Calendar Booking Assistant..."\n\
echo "Backend will be available on port 8000"\n\
echo "Frontend will be available on port 8501"\n\
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &\n\
BACKEND_PID=$!\n\
sleep 5\n\
streamlit run frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0 &\n\
FRONTEND_PID=$!\n\
echo "Both services started successfully"\n\
echo "Backend PID: $BACKEND_PID"\n\
echo "Frontend PID: $FRONTEND_PID"\n\
wait $BACKEND_PID $FRONTEND_PID' > start.sh && chmod +x start.sh

CMD ["./start.sh"]