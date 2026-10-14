# BizMind: Руководство по развертыванию на удаленном Linux-сервере (Production Deployment Guide)

> **Версия:** 1.0.0  
> **Целевая среда:** Linux VPS / VDS (Ubuntu 22.04 / 24.04 LTS, Debian 12)  
> **Архитектура:** Docker Compose (Nginx Frontend + FastAPI Backend + Persistent SQLite Volume)

---

## 1. Требования к серверу

- **Операционная система:** Ubuntu 22.04 / 24.04 LTS или Debian 12 (64-bit).
- **Процессор (CPU):** Минимум 1 vCPU (рекомендуется 2 vCPU).
- **Оперативная память (RAM):** Минимум 1 ГБ (рекомендуется 2 ГБ, либо 1 ГБ RAM + 2 ГБ Swap).
- **Дисковое пространство:** Минимум 10 ГБ SSD/NVMe (для Docker-образов, логов и базы данных).
- **Сеть:** Публичный статический IPv4-адрес, открытые входящие порты:
  - `22/tcp` — SSH доступ
  - `80/tcp` — HTTP трафик (Web / Let's Encrypt challenge)
  - `443/tcp` — HTTPS шифрованный трафик

---

## 2. Первоначальная подготовка Linux-сервера

Подключитесь к серверу по SSH под пользователем с правами `sudo`:

```bash
ssh user@your-server-ip
```

### 2.1. Обновление пакетов системы
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git ufw sqlite3 ca-certificates gnupg lsb-release
```

### 2.2. Настройка брандмауэра (UFW)
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'
sudo ufw --force enable
sudo ufw status verbose
```

### 2.3. Настройка файла подкачки (Swap) — критично для серверов с 1 ГБ RAM
```bash
if [ $(free -m | awk '/^Swap:/ {print $2}') -eq 0 ]; then
    echo "Creating 2GB swapfile..."
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi
```

---

## 3. Установка Docker Engine и Docker Compose Plugin

Официальный рекомендованный метод установки Docker для Linux:

```bash
# 1. Скачивание и запуск официального скрипта Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
rm get-docker.sh

# 2. Добавление текущего пользователя в группу docker
sudo usermod -aG docker $USER

# 3. Включение автозапуска службы
sudo systemctl enable docker
sudo systemctl start docker

# 4. Проверка версий (требуется перелогиниться или выполнить newgrp docker)
newgrp docker
docker --version
docker compose version
```

Ожидаемый вывод:
```text
Docker version 27.x.x (или новее)
Docker Compose version v2.x.x (или новее)
```

---

## 4. Передача проекта на сервер

### Вариант A: Клонирование через Git (Рекомендуется)
```bash
cd /opt
sudo git clone https://github.com/your-org/BizMind.git bizmind
sudo chown -R $USER:$USER /opt/bizmind
cd /opt/bizmind
```

### Вариант B: Передача через rsync / scp с локальной машины
```bash
# Выполняется на вашей локальной машине
rsync -avz --exclude 'node_modules' --exclude '.venv' --exclude '__pycache__' \
    /home/disortus/coop-projs/BizMind/ user@your-server-ip:/opt/bizmind/
```

---

## 5. Настройка переменных окружения (`.env`)

Создайте файл `.env` из подготовленного шаблона:

```bash
cd /opt/bizmind
cp .env.example .env
```

Отредактируйте `.env` в редакторе:
```bash
nano .env
```

Пример содержимого для боевого сервера:
```env
# Порт, на котором будет отвечать Nginx frontend
FRONTEND_PORT=80

# Режим окружения
ENVIRONMENT=production

# Путь к SQLite базе внутри контейнера (сохраняется в постоянном томе)
DATABASE_PATH=/app/data/bizmind.db

# Имя сервера или домен (например, app.bizmind.kz)
SERVER_NAME=app.bizmind.kz
```

---

## 6. Сборка и запуск контейнеров

### 6.1. Валидация конфигурации Docker Compose
```bash
docker compose config
```
Команда должна вывести нормализованный YAML без ошибок.

### 6.2. Сборка образов
```bash
docker compose build --pull
```
- Сборка backend компилирует Python-слой с зависимостями через `uv`.
- Сборка frontend выполняет `npm ci` и `npm run build` в Node 20, после чего переносит минифицированный `dist` в легкий образ `nginx:alpine`.

### 6.3. Запуск приложения в фоновом режиме
```bash
docker compose up -d
```

---

## 7. Проверка состояния и диагностика

### 7.1. Проверка запущенных контейнеров
```bash
docker compose ps
```
Ожидаемый статус:
```text
NAME               IMAGE              COMMAND                  SERVICE    CREATED          STATUS                    PORTS
bizmind_backend    bizmind-backend    "/app/.venv/bin/uvic…"   backend    10 seconds ago   Up 10 seconds (healthy)   
bizmind_frontend   bizmind-frontend   "/docker-entrypoint.…"   frontend   10 seconds ago   Up 9 seconds (healthy)    0.0.0.0:80->80/tcp
```

### 7.2. Просмотр журналов (логов)
```bash
# Логи backend
docker compose logs -f backend

# Логи frontend / Nginx
docker compose logs -f frontend

# Все логи вместе
docker compose logs -f --tail=100
```

### 7.3. Проверка доступности через curl
```bash
# 1. Проверка Nginx
curl -I http://localhost/

# 2. Проверка проксирования API через Nginx
curl -s http://localhost/api/ | grep "BizMind Backend API"

# 3. Проверка Healthcheck backend
curl -s http://localhost/api/health
```

---

## 8. Проверка сохранения базы данных (Data Persistence)

База данных SQLite сохраняется в постоянном Docker Volume `bizmind_db_data`.

### Как убедиться, что данные не пропадут при перезапуске:
```bash
# 1. Проверить существование тома
docker volume ls | grep bizmind_db_data

# 2. Остановка и удаление контейнеров (БЕЗ ключа -v!)
docker compose down

# 3. Запуск заново
docker compose up -d

# 4. Проверить, что данные сохранились
curl -s http://localhost/api/auth/organizations
```

> [!CAUTION]
> **Никогда не используйте команду `docker compose down -v` на рабочем сервере!**  
> Флаг `-v` (`--volumes`) безвозвратно удаляет постоянный том `bizmind_db_data` вместе с базой данных `bizmind.db`.

---

## 9. Настройка доменного имени и HTTPS (TLS)

Для доступа по защищенному протоколу HTTPS и привязки домена рекомендуется использовать один из двух вариантов:

### Вариант 1: Использование Caddy в качестве внешнего TLS-прокси (Самый простой)
Caddy автоматически получает и обновляет бесплатные SSL-сертификаты Let's Encrypt.

1. Установите Caddy на хост:
```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update && sudo apt install caddy -y
```

2. В файле `.env` измените `FRONTEND_PORT=8080`, чтобы освободить порт 80 для Caddy:
```bash
sed -i 's/FRONTEND_PORT=80/FRONTEND_PORT=8080/' .env
docker compose up -d
```

3. Настройте `/etc/caddy/Caddyfile`:
```caddy
app.bizmind.kz {
    reverse_proxy 127.0.0.1:8080
}
```

4. Перезапустите Caddy:
```bash
sudo systemctl reload caddy
```

### Вариант 2: Nginx на хосте + Certbot
1. Установите Certbot:
```bash
sudo apt install -y certbot python3-certbot-nginx
```

2. Создайте конфигурацию `/etc/nginx/sites-available/bizmind`:
```nginx
server {
    server_name app.bizmind.kz;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. Выпустите сертификат:
```bash
sudo ln -s /etc/nginx/sites-available/bizmind /etc/nginx/sites-enabled/
sudo certbot --nginx -d app.bizmind.kz
```

---

## 10. Резервное копирование и восстановление SQLite базы

### 10.1. Создание горячего бэкапа без остановки приложения
SQLite поддерживает консистентный онлайн-бэкап через команду `.backup`:

```bash
# Создание директории бэкапов
mkdir -p /opt/bizmind/backups

# Горячий бэкап из работающего контейнера backend
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker compose exec backend python -c "
import sqlite3
src = sqlite3.connect('/app/data/bizmind.db')
dst = sqlite3.connect('/app/data/backup_${TIMESTAMP}.db')
src.backup(dst)
dst.close()
src.close()
"

# Копирование бэкапа на хост
docker compose cp backend:/app/data/backup_${TIMESTAMP}.db /opt/bizmind/backups/bizmind_${TIMESTAMP}.db
docker compose exec backend rm /app/data/backup_${TIMESTAMP}.db

echo "Backup created: /opt/bizmind/backups/bizmind_${TIMESTAMP}.db"
```

### 10.2. Автоматический ежедневный бэкап по Cron
Создайте скрипт `/opt/bizmind/backup.sh`:
```bash
cat << 'EOF' > /opt/bizmind/backup.sh
#!/bin/bash
BACKUP_DIR="/opt/bizmind/backups"
mkdir -p $BACKUP_DIR
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker compose -f /opt/bizmind/docker-compose.yml exec -T backend python -c "
import sqlite3
src = sqlite3.connect('/app/data/bizmind.db')
dst = sqlite3.connect('/app/data/dump.db')
src.backup(dst)
dst.close()
src.close()
"
docker compose -f /opt/bizmind/docker-compose.yml cp backend:/app/data/dump.db "$BACKUP_DIR/bizmind_$TIMESTAMP.db"
docker compose -f /opt/bizmind/docker-compose.yml exec -T backend rm /app/data/dump.db
# Ротация: удалять бэкапы старше 14 дней
find $BACKUP_DIR -name "bizmind_*.db" -mtime +14 -delete
EOF
chmod +x /opt/bizmind/backup.sh
```

Добавьте в crontab (`crontab -e`):
```cron
0 3 * * * /opt/bizmind/backup.sh >> /var/log/bizmind_backup.log 2>&1
```

### 10.3. Восстановление из резервной копии
```bash
# 1. Остановить контейнеры
docker compose down

# 2. Скопировать файл бэкапа поверх базы в томе
# Временный запуск легковесного контейнера для подмены файла в томе
docker run --rm -v bizmind_db_data:/data -v /opt/bizmind/backups:/backups alpine \
    cp /backups/bizmind_TARGET.db /data/bizmind.db

# 3. Запустить контейнеры
docker compose up -d
```

---

## 11. Обновление приложения (Zero-Downtime / Fast Update)

Для обновления BizMind до новой версии без потери данных:

```bash
cd /opt/bizmind

# 1. Получение свежего кода
git pull origin main

# 2. Сборка обновленных образов (данные в томе сохраняются!)
docker compose build

# 3. Бесшовный перезапуск
docker compose up -d --remove-orphans

# 4. Проверка статуса
docker compose ps
docker compose logs -f --tail=30
```

---

## 12. Безопасный сброс и восстановление демонстрационных данных

Если после демонстраций требуется вернуть оба кейса (Cafe Aroma и Daily Cup) к эталонному виду:

```bash
# Выполнить сброс базы внутри работающего контейнера:
docker compose exec backend python -m backend.demo.seed_data
```

Команда детерминированно воссоздаст обе кофейни, историю закупок, финансовые транзакции, каталоги предложений и остатки на складе.
