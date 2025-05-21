#!/bin/bash

echo "Starting Ollama server..."
ollama serve &

sleep 5

echo "Pulling Mistral"
ollama pull mistral

echo "Pulling TinyLlama"
ollama pull tinyllama

ollama run tinyllama