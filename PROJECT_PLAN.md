# План выполнения проекта CinemaAbyss

**Технологический стек:** Python 3.10+ | FastAPI | Docker | Kafka | Kubernetes | Helm

---

## ✅ Задание 1: Проектирование архитектуры (C4 диаграмма) ✅ DONE

- [x] **1.1** Изучить существующую диаграмму `c4_diagrams/C4_Containers_CinemaAbyss.puml`
- [x] **1.2** Добавить доменную декомпозицию (Movies, Users, Payments, Events, Proxy)
- [x] **1.3** Обновить To-Be архитектуру в `Project_template.md`
- [x] **1.4** Ссылка на диаграмму: `[Ссылка на файл](c4_diagrams/C4_Containers_CinemaAbyss.puml)`

---

## ✅ Задание 2: Proxy Service + Kafka Events

### 🟢 Часть 1: Proxy Service (FastAPI) ✅ DONE

- [x] **2.1** Создать структуру проекта `src/microservices/proxy/`
- [x] **2.2** Создать `requirements.txt`
- [x] **2.3** Создать `Dockerfile`
- [x] **2.4** Создать `src/microservices/proxy/main.py` с реализацией:
  - [x] Загрузка env-переменных (PORT, MONOLITH_URL, MOVIES_SERVICE_URL, GRADUAL_MIGRATION, MOVIES_MIGRATION_PERCENT)
  - [x] HTTP-клиент `httpx` для проксирования запросов
  - [x] Маршрут `GET /health`
  - [x] Маршрут `GET /api/movies` с логикой Feature Flag
- [x] **2.5** Обновить `docker-compose.yml` (проверить конфигурацию proxy-service)
- [x] **2.6** Запустить и проверить:
  ```bash
  docker-compose up -d --build proxy-service
  curl http://localhost:8000/api/movies
  ```
  ✅ Работает: проксирует на Monolith (50% миграция)
- [x] **2.7** Тестировать градуальную миграцию:
  - Изменить `MOVIES_MIGRATION_PERCENT: "0"` → Monolith ✅
  - Изменить `MOVIES_MIGRATION_PERCENT: "100"` → Movies Service ✅
  Проверено через логи: `GET http://monolith:8080/api/movies`
- [x] **2.8** Запустить postman-тесты:
  ```bash
  cd tests/postman && npm install && npm run test:local
  ```
  ✅ Все 22 запроса, 42 assertions — зелёные

### 🟡 Часть 2: Events Service (Kafka) ✅ DONE

- [x] **2.9** Создать структуру проекта `src/microservices/events/`
- [x] **2.10** Создать `requirements.txt`
- [x] **2.11** Создать `Dockerfile`
- [x] **2.12** Создать `src/microservices/events/main.py`:
  - [x] Kafka Producer: отправка сообщений в топики `user_events`, `payment_events`, `movie_events`
  - [x] Kafka Consumer: чтение сообщений и логирование
  - [x] API эндпоинты:
    - `POST /api/events/user` → создаёт событие пользователя
    - `POST /api/events/payment` → создаёт событие платежа
    - `POST /api/events/movie` → создаёт событие фильма
- [x] **2.13** Обновить `docker-compose.yml` (events-service уже добавлен)
- [x] **2.14** Запустить postman-тесты:
  ```bash
  npm run test:local
  ```
  Ожидаемый результат: все тесты зелёные ✅ (22/22 requests, 42/42 assertions passed)
- [x] **2.15** Сделать скриншоты:
  - [x] Результаты тестов (все зелёные)
  - [x] Kafka UI: топики movie-events, payment-events, user_events созданы

---

## ✅ Задание 3: CI/CD + Kubernetes ✅ DONE

### 🔵 Часть 1: CI/CD Pipeline ✅ DONE

- [x] **3.1** Открыть `.github/workflows/docker-build-push.yml`
- [x] **3.2** Добавить сборку для proxy-service
- [x] **3.3** Добавить сборку для events-service
- [x] **3.4** Запушить изменения и проверить GitHub Actions
- [x] **3.5** Ожидаемый результат: зелёная сборка + образы в GHCR

### 🔵 Часть 2: Kubernetes Deployment ✅ DONE

- [x] **3.6** Создать Personal Access Token (PAT) на GitHub с правом `read:packages`
- [x] **3.7** Настроить Docker registry для minikube
- [x] **3.8** Обновить `src/kubernetes/dockerconfigsecret.yaml` с новым base64
- [x] **3.9** Обновить пути образов в K8s-манифестах
- [x] **3.10** Создать/обновить `src/kubernetes/proxy-service.yaml`
- [x] **3.11** Обновить `src/kubernetes/events-service.yaml`
- [x] **3.12** Обновить `src/kubernetes/ingress.yaml`
- [x] **3.13** Развёртывание K8s
- [x] **3.14** Проверить поды
- [x] **3.15** Настройка хоста и minikube tunnel
- [x] **3.16** Проверить API
- [x] **3.17** Эксперимент с MOVIES_MIGRATION_PERCENT
- [x] **3.18** Запустить K8s тесты
- [x] **3.19** Скриншоты:
  - [x] [Kubernetes Pods](screenshots/task3-k8s-pods.png)
  - [x] [API Response](screenshots/task3-api-response.png)
  - [x] [Events Service Logs](screenshots/task3-events-logs.png)

---

## ✅ Задание 4: Helm Charts ✅ DONE

- [x] **4.1** Открыть `src/kubernetes/helm/values.yaml`
- [x] **4.2** Обновить пути образов для всех сервисов
- [x] **4.3** Обновить `imagePullSecrets.dockerconfigjson`
- [x] **4.4** Заполнить шаблоны в `src/kubernetes/helm/templates/services/`
- [x] **4.5** Удалить старую установку
- [x] **4.6** Установить через Helm
- [x] **4.7** Проверить установку
- [x] **4.8** Скриншоты:
  - [x] [Helm Install](screenshots/task4-helm-install.png)
  - [x] [API After Helm](screenshots/task4-api-after-helm.png)

---

## 📋 Финальная проверка

- [x] **F1** Все 4 задания выполнены
- [x] **F2** `Project_template.md` заполнен полностью
- [ ] **F3** Создан PR из ветки `cinema` в `main`
- [x] **F4** Скриншоты добавлены в `Project_template.md`
- [ ] **F5** Код закоммичен и запушен

---

## 🆘 Диагностика проблем

| Проблема | Решение |
|----------|---------|
| Kafka не стартует | `kubectl delete pod kafka-0 -n cinemaabyss` (пересоздастся) |
| Proxy не проксирует | Проверить env: `kubectl exec -it deploy/proxy-service -- env` |
| Тесты падают | Проверить health эндпоинты: `curl http://localhost:8080/health` |
| Images не пулятся | Проверить `dockerconfigsecret.yaml` и base64 |
| Ingress не работает | `minikube addons enable ingress` + `minikube tunnel` |

---

**Дата начала:** _________________
**Дата завершения:** _________________
