# Spring PetClinic: безопасная сборка и развёртывание

Итоговый проект по защите приложения и инфраструктуры. Spring PetClinic запускается с PostgreSQL; проверки исходного кода и образа выполняются в GitLab, образы публикуются в Harbor, развёртывание защищено сетевыми политиками, Kyverno и Falco.

Исходный проект: [spring-projects/spring-petclinic](https://github.com/spring-projects/spring-petclinic), версия исходников `500158f732419217507c7656904b8e6aa1bcc0d6`. История разработки и лицензия Apache 2.0 сохранены. Spring Boot обновлён до 4.1.2 по результатам сканирования зависимостей.

Результаты приведены в [итоговом отчёте](RESULTS.md), соответствие требованиям задания — в [листе проверки](CHECKLIST.md).

## Материалы для проверки

| Часть | Файлы |
|---|---|
| Сборка без инструментов разработки в конечном образе | [Dockerfile](Dockerfile), [.dockerignore](.dockerignore) |
| Запуск приложения с PostgreSQL | [docker-compose.yml](docker-compose.yml), [.env.example](.env.example) |
| Архитектура и пять основных угроз | [SECURITY_DESIGN.md](SECURITY_DESIGN.md) |
| Автоматические проверки и публикация образа | [.gitlab-ci.yml](.gitlab-ci.yml) |
| Приложение, база данных, тома и маршрутизация | [k8s/](k8s/) |
| Сетевая изоляция | [network-policies.yaml](k8s/network-policies.yaml) |
| Контроль системных вызовов | [falco-rules.yaml](k8s/falco-rules.yaml) |
| Запрет небезопасных контейнеров | [kyverno-policy.yaml](k8s/kyverno-policy.yaml) |
| Проверки HTTP-интерфейса и конфигурации узла | [zap-job.yaml](k8s/zap-job.yaml), [kube-bench-job.yaml](k8s/kube-bench-job.yaml) |
| Итог и результаты проверок | [RESULTS.md](RESULTS.md), [reports/](reports/) |

## Локальный запуск

Требуются Docker и Docker Compose. Пароль создаётся локально и не включается в репозиторий:

```bash
umask 077
printf 'APP_PORT=18081\nPOSTGRES_PASSWORD=%s\n' "$(openssl rand -hex 24)" > .env
docker compose up -d --build
docker compose ps
curl --fail http://127.0.0.1:18081/actuator/health
```

Приложение доступно на `http://127.0.0.1:18081`; внутри контейнера используется порт 8080. В `.env` можно задать другой свободный `APP_PORT`. PostgreSQL доступен только во внутренней сети Compose. Обычная остановка: `docker compose down`. Не добавляйте `-v`, если требуется сохранить данные.

Контейнер приложения использует UID 10001, PostgreSQL — UID 70. Корневые файловые системы доступны только для чтения. Запись разрешена во временные тома и том данных PostgreSQL. Пароль обязателен: запуск без него завершается ошибкой.

## Проверки в GitLab

Используется отдельный исполнитель с меткой `project10`, закреплённый за этим проектом и защищёнными ветками. Этап `tests` содержит четыре независимых задания: Gitleaks, Hadolint, Trivy для зависимостей и SonarQube с тестами приложения. Этап `build` собирает образ, выполняет Dockle и Trivy, затем публикует его в Harbor.

Секреты хранятся в защищённых переменных GitLab:

| Переменная | Назначение |
|---|---|
| `SONAR_HOST_URL` | `https://sonarqube.devsecops.education-services.ru` |
| `SONAR_PROJECT_KEY` | Ключ проекта SonarQube |
| `SONAR_TOKEN` | Токен анализа только этого проекта; значение скрыто |
| `HARBOR_REGISTRY` | Адрес реестра с портом |
| `HARBOR_PROJECT` | Имя проекта Harbor |
| `HARBOR_USER`, `HARBOR_PASSWORD` | Учётная запись публикации; пароль скрыт |

Gitleaks блокирует утечки. Trivy блокирует HIGH/CRITICAL; список исключений не используется. SonarQube проверяет проект по установленному порогу качества. Дополнительная проверка запрещает выпуск при уязвимостях и замечаниях BLOCKER/CRITICAL во всём проекте; отсутствие обязательных метрик тоже считается ошибкой. Dockle блокирует FATAL/WARN. Отчёты сохраняются при любом результате задания на 30 дней; итоговые выгрузки дополнительно включены в Git.

Доступ к Docker на исполнителе равнозначен административному доступу к этой ВМ. Поэтому исполнитель выделен только для доверенного проекта, не обслуживает произвольные ветки и не совмещается с рабочим приложением в Kubernetes.

## Развёртывание в Kubernetes

Перед запуском нужны настроенные Calico, Ingress NGINX, StorageClass, Falco, Kyverno и доступ узла к Harbor. Версии и параметры учебных сервисов приведены в [infrastructure/README.md](infrastructure/README.md).

1. Передайте параметры через окружение: `POSTGRES_PASSWORD`, `HARBOR_REGISTRY`, `HARBOR_PULL_USER`, `HARBOR_PULL_PASSWORD`, `TLS_CERT`, `TLS_KEY`. Для кластера используется отдельная учётная запись Harbor только с правом чтения.
2. Выполните `scripts/create-secrets.sh`. Пароли, сертификат и ключ попадут в Secrets; в Git они не записываются.
3. Укажите `APP_IMAGE` в виде `реестр/project10/petclinic@sha256:...` и выполните `scripts/deploy.sh`.
4. Для проверки без настройки имени Ingress выполните `kubectl port-forward service/petclinic 18082:8080` и откройте `http://127.0.0.1:18082`.

Ingress использует имя `petclinic.project10.internal`, HTTPS и сертификат из Secret `petclinic-tls`. Для браузерного доступа через Ingress требуется доверие к выдавшему сертификат центру и разрешение этого имени в адрес Ingress. Проверка сертификата не отключается.

Файл `k8s/harbor-values.yaml` и `k8s/falco-rules.yaml` содержат параметры Helm. Их не следует передавать в `kubectl apply`; прикладные манифесты применяются явно скриптом развёртывания.

## Проверка защитных мер

```bash
python3 scripts/verify-network.py
kubectl run bad-pod --image=nginx --restart=Never
python3 scripts/verify-falco.py
kubectl apply -f k8s/zap-job.yaml
kubectl apply -f k8s/kube-bench-job.yaml
```

Создание `bad-pod` и запись в `/app` должны завершиться отказом. Falco должен зарегистрировать попытку записи. Сетевой тест проверяет разрешённый доступ сканера к приложению, запрет доступа сканера к БД и внешней сети, запрет доступа к приложению для Pod без разрешающей метки.

kube-bench использует набор CIS 1.11 для Kubernetes 1.31. Ему выделено пространство `security-audit` с доступом к процессам и конфигурации узла только на время задания. Подробности этого исключения описаны в модели угроз.

Приложение предназначено для учебной проверки защитных мер. Ограничения одноузловой инфраструктуры и меры, необходимые для обработки реальных персональных данных, описаны в [SECURITY_DESIGN.md](SECURITY_DESIGN.md).
