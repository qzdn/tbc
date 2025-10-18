# tbc - Twitch bot commands

Simple API for Twitch bot commands. Can be running in Docker.


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