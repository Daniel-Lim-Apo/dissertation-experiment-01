# Dockerfile.ollama

FROM ollama/ollama

# Add Fortigate corporate CA certificate (if required for network interception)
COPY ./fortigate.crt /usr/local/share/ca-certificates/fortigate-ca.crt
RUN update-ca-certificates

# Copy the startup script (which now only starts the server)
# COPY ./start.ollama.sh /start.ollama.sh
# RUN chmod +x /start.ollama.sh

# ENTRYPOINT ["/start.ollama.sh"]
