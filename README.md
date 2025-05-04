# Python Chatbot Service - Hoàng Tú Pickleball Shop

Dịch vụ chatbot đa agent cho cửa hàng Hoàng Tú Pickleball Shop, sử dụng OpenAI Assistant API và RAG (Retrieval Augmented Generation).

## Tính năng

- Kiến trúc đa agent chuyên biệt:
  - **Product Agent**: Tư vấn và cung cấp thông tin về sản phẩm pickleball
  - **Cart Agent**: Quản lý giỏ hàng và thanh toán
  - **Shop Agent**: Thông tin cửa hàng, chính sách và đơn hàng
  - **Checkout Agent**: Xử lý quá trình thanh toán và đặt hàng
  - **Manager Agent**: Điều phối giữa các agent

- RAG (Retrieval Augmented Generation) cho thông tin sản phẩm
- Tích hợp đầy đủ với Spring Boot backend thông qua API
- Hỗ trợ quản lý giỏ hàng và xử lý đơn hàng
- Hỗ trợ tiếng Việt hoàn toàn

## Kiến trúc tổng thể

```
[Frontend] <--> [Spring Boot Backend] <--> [Python Chatbot Service]
                      |                             |
                [MySQL Database]              [Milvus Vector DB]
```

## Yêu cầu hệ thống

- Python 3.10+
- FastAPI
- OpenAI API Key
- Milvus Vector Database
- MySQL Database
- Spring Boot Backend (Hiện có)

## Cài đặt

### Bước 1: Clone repository

```bash
git clone https://github.com/username/HoangTuChatbot.git
cd HoangTuChatbot
```

### Bước 2: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Bước 3: Cấu hình môi trường

Tạo file `.env` từ mẫu `.env.example`:

```bash
cp .env.example .env
```

Sửa file `.env` với các thông tin cấu hình của bạn:
- `OPENAI_API_KEY`: API key của OpenAI
- `SPRING_BOOT_API_URL`: URL của Spring Boot Backend
- `DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME`: Thông tin kết nối MySQL
- `MILVUS_HOST, MILVUS_PORT`: Thông tin kết nối Milvus

### Bước 4: Cài đặt Milvus Vector Database

#### Sử dụng Docker
```bash
wget https://github.com/milvus-io/milvus/releases/download/v2.3.2/milvus-standalone-docker-compose.yml -O docker-compose.yml
docker-compose up -d
```

#### Cài đặt PyMilvus
```bash
pip install pymilvus
```

### Bước 5: Khởi động ứng dụng

```bash
uvicorn app.main:app --reload
```

Ứng dụng sẽ chạy tại `http://localhost:8000`

## Cấu trúc dự án

```
HoangTuChatbot/
├── app/
│   ├── api/              # API endpoints
│   ├── agents/           # Các agent xử lý
│   │   ├── product_agent.py
│   │   ├── cart_agent.py
│   │   ├── shop_agent.py
│   │   ├── checkout_agent.py
│   │   └── manager_agent.py
│   ├── rag/              # RAG components
│   │   ├── embeddings.py
│   │   ├── retriever.py
│   │   └── vector_store.py
│   ├── tools/            # Tool functions
│   │   ├── product_tools.py
│   │   ├── cart_tools.py
│   │   ├── checkout_tools.py
│   │   ├── shop_tools.py
│   │   └── manager_tools.py
│   ├── client/           # Spring Boot API clients
│   │   └── spring_client.py
│   ├── core/             # Core configurations
│   │   ├── config.py
│   │   ├── hooks.py
│   │   └── security.py
│   ├── db/               # Database models và kết nối
│   │   └── services.py
│   └── prompts/          # Agent prompts
├── logs/                 # Log files
├── tests/                # Unit tests
└── main.py               # Entry point
```

## API Endpoints

### Chat API

```
POST /api/chat
```

Request:
```json
{
  "message": "Tôi muốn tìm vợt pickleball cho người mới chơi",
  "thread_id": "thread_123",
  "user_id": "user_456",
  "auth_token": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Response:
```json
{
  "message": "Chúng tôi có nhiều loại vợt pickleball phù hợp cho người mới chơi. Một số lựa chọn tốt là vợt Niupipo hoặc Head với mức giá từ 1-2 triệu đồng. Bạn quan tâm đến mức giá nào?",
  "source_documents": [...],
  "thread_id": "thread_123",
  "products": [...]
}
```

### Sync API

```
POST /api/sync
```

Request:
```json
{
  "type": "products",
  "data": [...]
}
```

Response:
```json
{
  "status": "success",
  "count": 10,
  "message": "Đã đồng bộ 10 sản phẩm"
}
```

## Tích hợp với Spring Boot

### API được sử dụng từ Spring Boot Backend

#### API Sản phẩm
- **GET /api/products**: Lấy danh sách sản phẩm (phân trang)
- **GET /api/products/{id}**: Lấy thông tin sản phẩm theo ID
- **GET /api/products/category/{categoryId}**: Lấy sản phẩm theo danh mục

#### API Giỏ hàng
- **POST /api/cart/add**: Thêm sản phẩm vào giỏ hàng
- **PUT /api/cart/update**: Cập nhật số lượng sản phẩm
- **DELETE /api/cart/remove/{productId}**: Xóa sản phẩm khỏi giỏ hàng
- **GET /api/cart**: Lấy thông tin giỏ hàng
- **DELETE /api/cart/clear**: Xóa tất cả sản phẩm trong giỏ hàng

#### API Đơn hàng
- **POST /api/orders**: Tạo đơn hàng mới
- **GET /api/orders/my-orders**: Lấy danh sách đơn hàng của người dùng
- **GET /api/orders/{id}**: Lấy chi tiết đơn hàng

## Các Agent và Công cụ

### Product Agent
- Tìm kiếm và cung cấp thông tin sản phẩm pickleball
- So sánh vợt pickleball
- Đề xuất sản phẩm theo trình độ và nhu cầu

### Cart Agent
- Quản lý giỏ hàng (thêm, cập nhật, xóa sản phẩm)
- Xem thông tin giỏ hàng

### Checkout Agent
- Hướng dẫn quá trình thanh toán
- Tạo đơn hàng
- Hỗ trợ thanh toán COD và TRANSFER

### Shop Agent
- Cung cấp thông tin cửa hàng
- Thông tin về chính sách bán hàng
- Tra cứu thông tin đơn hàng

### Manager Agent
- Điều phối yêu cầu đến đúng agent chuyên biệt
- Xử lý đa dạng loại truy vấn

## Vector Database

Dự án sử dụng Milvus làm vector database để:
- Lưu trữ embeddings của thông tin sản phẩm
- Thực hiện tìm kiếm ngữ nghĩa (semantic search) với hiệu suất cao
- Hỗ trợ RAG để cung cấp thông tin chính xác về sản phẩm

Milvus là giải pháp Vector Database mã nguồn mở, mạnh mẽ với khả năng mở rộng cao, hỗ trợ:
- ANN (Approximate Nearest Neighbor) search với độ chính xác cao
- Quản lý hàng triệu vectors
- Xử lý truy vấn với độ trễ thấp

## Cách chạy với Docker

### Bước 1: Build Docker image

```bash
docker build -t hoangtu-chatbot .
```

### Bước 2: Chạy container

```bash
docker run -d -p 8000:8000 --env-file .env --name hoangtu-chatbot hoangtu-chatbot
```

### Bước 3: Docker Compose (Tùy chọn)

Tạo file `docker-compose.yml`:

```yaml
version: '3'
services:
  chatbot:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - milvus

  milvus:
    image: milvusdb/milvus:v2.3.2
    ports:
      - "19530:19530"
      - "19531:19531"
    environment:
      - ETCD_HOST=etcd
      - ETCD_PORT=2379
      - MINIO_ADDRESS=minio:9000
    volumes:
      - milvus_data:/var/lib/milvus
    depends_on:
      - etcd
      - minio

  etcd:
    image: quay.io/coreos/etcd:v3.5.0
    environment:
      - ETCD_AUTO_COMPACTION_MODE=revision
      - ETCD_AUTO_COMPACTION_RETENTION=1000
      - ETCD_QUOTA_BACKEND_BYTES=4294967296
    volumes:
      - etcd_data:/etcd

  minio:
    image: minio/minio:RELEASE.2023-03-20T20-16-18Z
    environment:
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin
    volumes:
      - minio_data:/data
    command: minio server /data

volumes:
  milvus_data:
  etcd_data:
  minio_data:
```

Chạy với Docker Compose:
```bash
docker-compose up -d
```

## Đóng góp

Vui lòng tạo issue hoặc pull request nếu bạn muốn đóng góp cho dự án.