# Учебные сервисы

| Средство | Версия и размещение |
|---|---|
| Сборка и исполнитель GitLab | Debian 12, Docker 28.4.0; отдельная ВМ |
| SonarQube | Учебный сервис, Community Build 26.1.0.118079 |
| Kubernetes | 1.31.2, один узел Ubuntu 22.04; Calico, NGINX Ingress, local-path |
| Harbor | 2.15.4, Helm 1.19.4, пространство `harbor` |
| Falco | 0.45.2, Helm 9.2.2, драйвер eBPF (`modern_ebpf`), пространство `falco` |
| Kyverno | 1.19.2, Helm 3.9.2, пространство `kyverno` |
| kube-bench | 0.16.0, CIS 1.11 |

## SonarQube

Анализ выполняется в [учебном SonarQube](https://sonarqube.devsecops.education-services.ru/dashboard?id=s2417991-project10final), проект `s2417991-project10final`. В GitLab переданы адрес сервиса, ключ проекта и токен анализа этого проекта. Токен хранится как скрытая защищённая переменная. Проверка ожидает результат порога качества и прекращает выпуск при отказе. Скрипт `scripts/check-sonar.py` сохраняет выгрузки и дополнительно проверяет отсутствие уязвимостей и замечаний BLOCKER/CRITICAL во всём проекте.

Для автономного повторения проверки приложен `sonarqube-compose.yml`. Его запуск требует отдельного `SONAR_DB_PASSWORD`; `SONAR_BIND_ADDRESS` по умолчанию ограничивает публикацию адресом 127.0.0.1. Это дополнительная конфигурация; итоговый анализ выполнен на учебном сервисе.

## Harbor

Реестр работает по HTTPS. Закрытый ключ и сертификат передаются в Secret `harbor-tls`; пароль администратора — отдельным закрытым файлом параметров Helm, не включённым в Git.

```bash
helm repo add harbor https://helm.goharbor.io
helm upgrade --install harbor harbor/harbor --version 1.19.4 \
  -n harbor --create-namespace -f k8s/harbor-values.yaml \
  -f /защищённый/каталог/harbor-secret-values.yaml
```

Проект `project10` закрыт. Включено сканирование при публикации и запрещена загрузка образов с HIGH/CRITICAL. Учётная запись `ci` имеет права публикации и чтения, `cluster` — только чтения; срок их действия ограничен семью днями.

Сертификат доверен Docker на ВМ сборки и containerd на узле Kubernetes. Для containerd используется `/etc/containerd/certs.d/harbor.project10.internal:30443/hosts.toml` с `capabilities = ["pull", "resolve"]` и путём к сертификату. Параметры `skip_verify` и небезопасный внешний HTTP не используются.

Учебные ВМ сборки и Kubernetes находятся в отдельных сетях. Соединение между ними организовано через SSH-туннель; адрес реестра для клиента остаётся `harbor.project10.internal:30443`, имя и сертификат проверяются. Снаружи учебного доступа реестр не опубликован. Имя Harbor закреплено в `/etc/hosts`; перезапись этого файла при запуске cloud-init отключена параметром `manage_etc_hosts: false`. После остановки ВМ SSH-соединения необходимо установить заново.

## Falco и Kyverno

```bash
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm repo add kyverno https://kyverno.github.io/kyverno
helm upgrade --install falco falcosecurity/falco --version 9.2.2 \
  -n falco --create-namespace -f k8s/falco-rules.yaml
helm upgrade --install kyverno kyverno/kyverno --version 3.9.2 \
  -n kyverno --create-namespace --set admissionController.replicas=1
kubectl apply -f k8s/kyverno-policy.yaml
```

Одна реплика контроллера допуска выбрана для одноузлового учебного стенда. В отказоустойчивом окружении контроллеры и сервисы должны размещаться на нескольких узлах.

## Восстановление доступа

Доступ к ВМ ограничивается сроком учебного сеанса. Для продолжения работы сеанс продлевается в сервисе учебных окружений. После смены ВМ необходимо заново настроить туннели, доверие к сертификатам, исполнитель GitLab и Secrets кластера. Исходный код, манифесты и отчёты сохраняются в GitLab независимо от срока сеанса.
