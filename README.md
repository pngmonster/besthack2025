# 3DOM x BEST_HACK

![Логотип](./frontend/logo.jpg)


# Запуск
```
docker build -t backend ./backend
docker-compose up --build
```

# API

SWAGGER: http://localhost:8000/docs#/search/search_api_search_get

GET http://localhost:8000/api/search?address=<address>

# Response
```json
{
  "searched_address": "string",
  "objects": [
    {
      "locality": "string",
      "street": "string",
      "number": "string",
      "lon": 0,
      "lat": 0,
      "score": 0
    }
  ]
}
```

# FRONT

local: file:///<PATH_TO_PROJECT>/frontend/index.html

online: http://5.129.246.225:8080/