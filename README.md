# tbc - Twitch bot commands

Simple API for Twitch bot commands. Can be running in Docker.

## Local run
Obtain your API keys [[1](https://www.last.fm/api/account/create), [2](https://openweathermap.org/api)]

### With Python and uv:
```bash
$ git clone https://github.com/qzdn/tbc.git
$ cd tbc
$ cp .env.example .env      # Paste your API keys in the .env file
$ uv venv -p 3.13
$ source .venv/bin/activate
$ uv pip install --no-cache -r pyproject.toml
$ uv run fastapi run main.py --host 0.0.0.0 --port 8000
$ firefox 127.0.0.1:8000
```

### With Docker:
```bash
$ git clone https://github.com/qzdn/tbc.git
$ cd tbc
$ cp .env.example .env      # Paste your API keys in the .env file
$ docker build . -t tbc-image
$ docker run --name tbc-container -d -p 80:10000 --env-file=.env tbc-image
$ firefox 127.0.0.1
```

## Render.com
- Open [Dashboard](https://dashboard.render.com/web/new)
- `+ New` -> `Web Service`
- `Public Git Repository` -> https://github.com/qzdn/tbc
- Name your web service
- `Language` -> `Docker`
- Paste `Environment Variables` names from `.env.example` and fill them with your keys [[1](https://www.last.fm/api/account/create), [2](https://openweathermap.org/api)]
- `Deploy Web Service`
- Wait until its build and run the service

## Example 

Add new command `!weather` with this "Response type" field: 
```
${customapi.https://tbc-rksp.onrender.com/weather?city=$(1:)&wind=true&humidity=true&pressure=true&precipitation=true}
```

Now type in your chat: `!weather Moscow`

```
Moscow: 6°C (feels like 6°C), overcast clouds | Wind: 1.27 m/s E | Humidity: 73% | Pressure: 764.4 mmHg 
```

---

Check [docs](https://tbc-rksp.onrender.com/docs) for info. 