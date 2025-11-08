# QR Lifecycle Platform

Ứng dụng quản trị vòng đời mã QR cho khách hàng & sản phẩm với khả năng tạo QR nghệ thuật theo mask ảnh. This repository contains both backend (FastAPI) and frontend (React) plus Docker deployment assets.

## Nhanh chóng bắt đầu / Quick start

```bash
cp deploy/.env.example .env
make setup
make dev
```

Hoặc chạy production-like:

```bash
docker compose -f deploy/docker-compose.yml up --build -d
```

Sau khi container chạy:

```bash
docker compose -f deploy/docker-compose.yml exec api alembic upgrade head
docker compose -f deploy/docker-compose.yml exec api python -m app.utils.seed
```

Đăng nhập quản trị: `admin@example.com` / `admin123`.

## Kiến trúc

- **Backend:** FastAPI + SQLAlchemy + Alembic, Redis rate limiting, JSON logging.
- **Frontend:** React + Vite + Tailwind với dark mode.
- **Database:** PostgreSQL (schema hỗ trợ JSONB, UUID) + migrations.
- **Cache/Queue:** Redis cho rate-limit và counters.
- **Tests:** pytest (backend), Vitest + React Testing Library (frontend).

## Thư mục chính

```
/backend   # FastAPI nguồn, tests, Alembic
/frontend  # React admin UI & public scan page
/deploy    # Dockerfiles, docker-compose, nginx
/examples  # Ảnh mask/logo mẫu
/docs      # OpenAPI & Postman collection
```

## Các tính năng nổi bật

- Tạo QR nghệ thuật theo mask ảnh, tự động tăng phiên bản & giãn mask khi mật độ không đủ, hỗ trợ chèn logo với ECC H.
- Lưu trữ vòng đời quét, analytics chi tiết (timeline, heatmap source, CSV export).
- Tái sử dụng QR với chu kỳ, ghi lịch sử và cập nhật owner sản phẩm.
- Trang quét công khai với CTA xác nhận/warranty transfer.
- JWT auth, rate limit cho endpoint scan, logging JSON ẩn PII nhạy cảm.
- Docker Compose chạy full stack (API + Web + Postgres + Redis + Nginx proxy).

## Scripts hữu ích

```bash
make backend-test     # pytest
make frontend-test    # vitest
make migrate          # alembic upgrade head
make seed             # python -m app.utils.seed
```

## Tài liệu API

- OpenAPI: `http://localhost:8000/openapi.json`
- Swagger UI: `http://localhost:8000/docs`
- Postman collection: `docs/postman_collection.json`

## License

MIT
