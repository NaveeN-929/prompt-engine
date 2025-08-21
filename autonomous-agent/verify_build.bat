@echo off
echo 🔍 Verifying Docker Build Changes
echo =================================

echo 1. Building new image...
docker build --target runtime -t paytechneodemo/autonomous-agent:test .

echo 2. Testing environment variable resolution...
docker run --rm -e PROMPT_ENGINE_HOST=prompt-engine -e PROMPT_ENGINE_PORT=5000 -e DOCKER_ENV=true paytechneodemo/autonomous-agent:test python test_env.py

echo 3. Testing config import...
docker run --rm -e PROMPT_ENGINE_HOST=prompt-engine -e PROMPT_ENGINE_PORT=5000 -e DOCKER_ENV=true paytechneodemo/autonomous-agent:test python debug_config.py

echo 🏁 Verification complete
