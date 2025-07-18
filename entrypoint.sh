#!/bin/bash

ollama serve &

until curl -s http://localhost:11434 > /dev/null; do
  echo "Aguardando o Ollama iniciar..."
  sleep 2
done

if ! ollama list | grep -q "medgemma"; then
  echo "Criando modelo medgemma..."
  ollama create medgemma -f /modelfiles/medgemma-4b-it-Q8_0/Modelfile
else
  echo "Modelo medgemma já existe."
fi

wait