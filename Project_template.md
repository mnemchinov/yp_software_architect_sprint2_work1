## Изучите [README.md](README.md) файл и структуру проекта.

# Задание 1

1. Спроектируйте to be архитектуру КиноБездны, разделив всю систему на отдельные домены и организовав интеграционное взаимодействие и единую точку вызова сервисов.
Результат представьте в виде контейнерной диаграммы в нотации С4.
Добавьте ссылку на файл в этот шаблон
[Ссылка на файл](c4_diagrams/C4_Containers_CinemaAbyss.puml)

## Описание To-Be архитектуры

### Доменная декомпозиция

| Домен            | Сервис           | Ответственность                                        |
|------------------|------------------|--------------------------------------------------------|
| Метаданные       | Movies Service   | Каталог фильмов, жанры, рейтинги, метаданные контента  |
| Пользователи     | Users Service    | Профили, история просмотров, избранное                 |
| Платежи          | Payments Service | Обработка платежей, подписки, скидки                   |
| События          | Events Service   | Kafka Producer/Consumer для User/Payment/Movie событий |
| Шлюз             | Proxy Service    | API Gateway, Strangler Fig, Feature Flags              |

### Стратегия миграции (Strangler Fig)

1. Proxy Service как единая точка входа
2. GRADUAL_MIGRATION - включение/выключение режима миграции
3. MOVIES_MIGRATION_PERCENT - процент трафика (0-100%) к Movies Service
4. Постепенное увеличение процента до полного переключения

### Коммуникация

| Тип         | Технология   | Использование                                 |
|-------------|--------------|-----------------------------------------------|
| Синхронная  | HTTP/REST    | Запросы к API Gateway, межсервисные вызовы    |
| Асинхронная | Apache Kafka | События: User, Payment, Movie                 |
| Внешняя     | HTTPS/REST   | Рекомендательная система, платёжный шлюз, CDN |

### Ключевые компоненты

- Proxy Service (порт 8000) - API Gateway с feature flags
- Movies Service (порт 8081) - выделенный микросервис
- Events Service (порт 8082) - Kafka producer/consumer
- PostgreSQL (порт 5432) - общая БД
- Kafka (порт 9092) - брокер сообщений

# Задание 2

## 1. Proxy

Команда выделила сервис метаданных о фильмах movies. Необходимо реализовать бесшовный переход с применением паттерна Strangler Fig.

Сервис реализован в `./src/microservices/proxy/` на Python.

Конфигурация в docker-compose.yml:
- PORT: 8000
- MONOLITH_URL: http://monolith:8080
- MOVIES_SERVICE_URL: http://movies-service:8081
- EVENTS_SERVICE_URL: http://events-service:8082
- GRADUAL_MIGRATION: "true"
- MOVIES_MIGRATION_PERCENT: "50"

Проверка:
```bash
curl http://localhost:8000/api/mmovies
```

## 2. Kafka

Реализован MVP сервис events в `./src/microservices/events/` на Python.

Функциональность:
- Kafka Producer для создания событий User/Payment/Movie
- Kafka Consumer для обработки событий
- Логирование обработанных событий

Скриншоты результатов:
- [Postman Tests](screenshots/task2-postman-tests.png)
- [Kafka Topics](screenshots/task2-kafka-topics.png)

# Задание 3

## CI/CD

Статус: Выполнено

Workflow: `.github/workflows/docker-build-push.yml`

Триггеры:
- push: branches [main, cinema], paths [src/**, .github/workflows/docker-build-push.yml]
- release: types [published]
- workflow_dispatch

Jobs:
1. build-and-push - сборка и пуш образов в GHCR
2. api-tests - запуск API тестов (опционально)

Образы в GHCR:
| Сервис         | Репозиторий                                              | Тег    |
|----------------|---------------------------------------------------------|--------|
| Monolith       | ghcr.io/mnemchinov/yp_software_architect_sprint2_work1/monolith       | latest |
| Movies Service | ghcr.io/mnemchinov/yp_software_architect_sprint2_work1/movies-service | latest |
| Events Service | ghcr.io/mnemchinov/yp_software_architect_sprint2_work1/events-service | latest |
| Proxy Service  | ghcr.io/mnemchinov/yp_software_architect_sprint2_work1/proxy-service  | latest |

Результат сборки: https://github.com/mnemchinov/yp_software_architect_sprint2_work1/actions/runs/21355017941

## Proxy в Kubernetes

### Шаг 1: Аутентификация в GHCR

1. Создать PAT на https://github.com/settings/tokens (Classic, права: repo, read:packages, write:packages)
2. Авторизоваться: `echo $PAT | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin`
3. Обновить `src/kubernetes/dockerconfigsecret.yaml`:
   ```bash
   cat ~/.docker/config.json | base64
   ```

### Шаг 2: Развёртывание

```bash
kubectl apply -f src/kubernetes/namespace.yaml
kubectl apply -f src/kubernetes/configmap.yaml
kubectl apply -f src/kubernetes/secret.yaml
kubectl apply -f src/kubernetes/dockerconfigsecret.yaml
kubectl apply -f src/kubernetes/postgres-init-configmap.yaml
kubectl apply -f src/kubernetes/postgres.yaml
kubectl apply -f src/kubernetes/kafka/kafka.yaml
kubectl apply -f src/kubernetes/monolith.yaml
kubectl apply -f src/kubernetes/movies-service.yaml
kubectl apply -f src/kubernetes/events-service.yaml
kubectl apply -f src/kubernetes/proxy-service.yaml
kubectl apply -f src/kubernetes/ingress.yaml
```

### Шаг 3: Проверка

```bash
# /etc/hosts
127.0.0.1 cinemaabyss.example.com

minikube addons enable ingress
minikube tunnel

curl https://cinemaabyss.example.com/api/movies
```

Скриншоты:
- [Kubernetes Pods](screenshots/task3-k8s-pods.png)
- [API Response](screenshots/task3-api-response.png)
- [Events Service Logs](screenshots/task3-events-logs.png)

# Задание 4: Helm Charts

Статус: Выполнено

Расположение: `src/kubernetes/helm/`

Обновлённые файлы:
- `src/kubernetes/helm/values.yaml` - настроены пути к образам
- `src/kubernetes/helm/templates/services/proxy-service.yaml` - Deployment + Service
- `src/kubernetes/helm/templates/services/events-service.yaml` - Deployment + Service

Пути к образам в values.yaml:
- monolith: ghcr.io/mnemchinov/yp_software_architect_sprint2_work1/monolith
- proxy-service: ghcr.io/mnemchinov/yp_software_architect_sprint2_work1/proxy-service
- movies-service: ghcr.io/mnemchinov/yp_software_architect_sprint2_work1/movies-service
- events-service: ghcr.io/mnemchinov/yp_software_architect_sprint2_work1/events-service

Установка:
```bash
helm install cinemaabyss ./src/kubernetes/helm --namespace cinemaabyss --create-namespace
```

Скриншоты:
- [Helm Install](screenshots/task4-helm-install.png)
- [API After Helm](screenshots/task4-api-after-helm.png)

---

## Скриншоты результатов

### Задание 2

- [Postman Tests](screenshots/task2-postman-tests.png)
- [Kafka Topics](screenshots/task2-kafka-topics.png)

### Задание 3

- [Kubernetes Pods](screenshots/task3-k8s-pods.png)
- [API Response](screenshots/task3-api-response.png)
- [Events Service Logs](screenshots/task3-events-logs.png)

### Задание 4

- [Helm Install](screenshots/task4-helm-install.png)
- [API After Helm](screenshots/task4-api-after-helm.png)