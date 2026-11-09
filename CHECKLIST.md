# Проверка по требованиям задания

Проверена опубликованная версия проекта. Результаты инструментов сверены с выводами отчёта, настройками сборки и манифестами Kubernetes.

| Требование | Результат проверки | Подтверждение |
|---|---|---|
| Проект GitLab типа Internal; проверяющий имеет роль Reporter | Подтверждено | [Параметры доступа](reports/gitlab-access.json) |
| Многоэтапная сборка; JDK и Maven отсутствуют в конечном образе | Подтверждено | [Dockerfile](Dockerfile), [проверка контейнера](reports/compose-verification.json) |
| Приложение работает от непривилегированного пользователя | UID 10001 | [Проверка контейнера](reports/compose-verification.json) |
| Compose запускает приложение и PostgreSQL | Оба контейнера исправны; приложение читает данные, HTTP 200 | [Compose](docker-compose.yml), [результат](reports/compose-verification.json) |
| Приложение слушает порт 8080 | Внутри контейнера — 8080; снаружи — свободный порт 18081 | [Compose](docker-compose.yml) |
| Пароли отсутствуют в Compose и прикладных манифестах | Пароль передаётся через окружение; в Kubernetes используются Secrets | [Compose](docker-compose.yml), [создание Secrets](scripts/create-secrets.sh) |
| SonarQube, Gitleaks, Hadolint, Trivy и Dockle выполнены | Результаты сохранены; уязвимостей в проверенном образе и открытых замечаний SonarQube нет | [Сводка проверок](RESULTS.md), [отчёты](reports/) |
| Схема Ingress → приложение → БД и пять угроз | Выполнен анализ STRIDE, указаны защитные меры | [Модель угроз](SECURITY_DESIGN.md) |
| Этап tests содержит независимые проверки | Gitleaks, Hadolint, Trivy и SonarQube | [Настройки GitLab](.gitlab-ci.yml) |
| Этап build собирает, проверяет и публикует образ | Docker, Dockle, Trivy, Harbor | [Настройки GitLab](.gitlab-ci.yml), [выполненные задания](reports/gitlab-jobs.json) |
| Выпуск блокируется при секретах и HIGH/CRITICAL | Проверки останавливают задание; пустой отчёт Trivy тоже считается ошибкой | [Проверка запретов](reports/release-gate-test.json), [проверка SonarQube](reports/sonarqube-release-check.json) |
| Секреты CI хранятся вне кода; отчёты сохраняются | Защищённые переменные GitLab; сохранение отчётов при любом исходе задания | [Настройки GitLab](.gitlab-ci.yml), [описание переменных](README.md) |
| Приложение и PostgreSQL развёрнуты в Kubernetes | Приложение отвечает по HTTPS и читает данные PostgreSQL | [Проверка развёртывания](reports/kubernetes-verification.json) |
| Deployment, StatefulSet с PVC, два ClusterIP Service и Ingress | Все манифесты включены в проект | [Каталог k8s](k8s/) |
| Параметры безопасности приложения и БД | `runAsNonRoot`, `readOnlyRootFilesystem`, `allowPrivilegeEscalation: false`, `drop: [ALL]` | [Приложение](k8s/deployment.yaml), [БД](k8s/postgres-statefulset.yaml) |
| Образ приложения из Harbor закреплён по SHA-256 | Значения в манифесте, развёртывании и отчёте Harbor совпадают | [Адрес образа](reports/image-digest.json), [развёртывание](reports/deployment.json), [Harbor](reports/harbor-artifact.json) |
| Harbor автоматически сканирует публикации | Включено; проверка образа завершена, уязвимостей нет | [Параметры проекта](reports/harbor-project.json), [результат](reports/harbor-artifact.json) |
| Сеть запрещена по умолчанию; разрешены только нужные соединения | Разрешены Ingress и сканер → приложение, приложение → БД, DNS; разрешённые и запрещённые соединения проверены | [Сетевые политики](k8s/network-policies.yaml), [четыре проверки](reports/network-tests.json) |
| Falco выявляет попытки записи вне /tmp | Попытка записи в /app зарегистрирована; файловая система отклонила запись | [Правило](k8s/falco-rules.yaml), [событие](reports/falco-test.json) |
| Kyverno запрещает небезопасные контейнеры в default | Контейнер nginx без обязательных настроек отклонён | [Политика](k8s/kyverno-policy.yaml), [ответ Kubernetes](reports/kyverno-rejection.txt) |
| ZAP выполняется как защищённое задание Kubernetes | Задание завершено; отчёт содержит семь типов замечаний | [Манифест](k8s/zap-job.yaml), [состояние](reports/zap-job.json), [отчёт](reports/zap.json) |
| kube-bench выполняется как задание; перечень FAIL сохранён | 63 проверки пройдены, 12 несоответствий, 58 предупреждений | [Манифест](k8s/kube-bench-job.yaml), [перечень несоответствий](reports/kube-bench-fail.json) |
| Выводы соответствуют исходным отчётам | Количества находок, результаты тестов и SHA-256 сверены | [Контрольные суммы](reports/provenance.json), [проверка комплекта](reports/submission-check.json) |

## Привязка к версиям

Приложенный образ и отчёты его проверки относятся к исходному коду `7d4d3ac71888020b277652fc257ade6d94954654` и [запуску № 16154](https://devsecops.gitlab.yandexcloud.net/s2417991/project10final/-/pipelines/16154). Проверка репозитория с добавленными отчётами и точечными исключениями Gitleaks прошла в [запуске № 16156](https://devsecops.gitlab.yandexcloud.net/s2417991/project10final/-/pipelines/16156). Текущие запуски доступны в [GitLab](https://devsecops.gitlab.yandexcloud.net/s2417991/project10final/-/pipelines).

Завершение задания сканера означает, что проверка выполнена. Замечания ZAP и несоответствия CIS остаются в отчёте с приоритетами и ответственными; их устранение не заявляется. Оценка допуска к промышленной эксплуатации приведена в [заключении](RESULTS.md#решение-по-эксплуатации).
