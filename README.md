# FedRL-Recommendation-Client

Federated Reinforcement Learning client for sustainable food recommendations.
Each client runs as a pair of Docker containers: a **FastAPI backend** (Python) and a **Vue 3 + TypeScript frontend** served by Nginx.

---

## Quick Start - Setup on Raspberry Pi

### 1. Set your Raspberry Pi's LAN IP

```bash
export PI_HOST=<pi-ip>   # replace "<pi-ip>" with your Pi's IP
```

### 2. Create data directories

```bash
mkdir -p data/client_{1,2,3}
```

### 3. Edit server URL in configs

Edit `config/client_1.yaml` (and client_2, client_3) — set `server_url` to your FL server's IP.

### 4. Build and run

```bash
docker compose up --build
```

### Access clients from any device on the LAN

| Client   | UI                            | API                            |
|----------|-------------------------------|--------------------------------|
| client_1 | http://\<pi-ip\>:8001         | http://\<pi-ip\>:9001          |
| client_2 | http://\<pi-ip\>:8002         | http://\<pi-ip\>:9002          |
| client_3 | http://\<pi-ip\>:8003         | http://\<pi-ip\>:9003          |

---

## Project Structure

```
fedrl-client/
├── Dockerfile.api          # Python 3.11 + FastAPI backend
├── Dockerfile.ui           # Vue 3 TS → Nginx static
├── docker-compose.yml      # Multi-client orchestration
├── config/
│   └── client_N.yaml       # Per-client config (mounted read-only)
├── api/
│   ├── main.py             # FastAPI entrypoint (JSON endpoints)
│   ├── rl/
│   │   ├── backbone.py     # Shared backbone (PyTorch, federated)
│   │   ├── local_head.py   # Item/Price/Nudge heads (never leaves device)
│   │   ├── model_manager.py
│   │   ├── context.py      # Context vector builder (16-dim)
│   │   └── reward.py       # Reward function
│   ├── sync/
│   │   └── sync_agent.py   # Background federation upload/download
│   ├── storage/
│   │   ├── interaction_logger.py   # SQLite (on-device only)
│   │   └── catalogue.py      # In-memory + disk cache
│   └── nudges/
│       └── nudge_renderer.py       # N1–N4 framing logic
└── ui/
    ├── src/
    │   ├── api/client.ts       # Axios API layer
    │   ├── types/index.ts      # Shared TypeScript types
    │   ├── stores/
    │   │   ├── cart.ts         # Pinia cart store
    │   │   └── catalogue.ts    # Pinia catalogue store
    │   ├── components/
    │   │   ├── AppNav.vue              # Bottom navigation
    │   │   ├── CartItemCard.vue        # Cart row with rec widget
    │   │   └── RecommendationWidget.vue # N1–N4 nudge display
    │   └── views/
    │       ├── CartView.vue
    │       ├── CatalogueView.vue
    │       └── StatsView.vue
    ├── vite.config.ts
    └── tsconfig.json
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Client status, algorithm, catalogue info |
| GET | `/cart` | Cart items with RL recommendations |
| POST | `/cart/add` | Add item to cart |
| DELETE | `/cart/{id}` | Remove item from cart |
| GET | `/catalogue` | All food items (optional `?category=`) |
| GET | `/catalogue/categories` | All category names |
| POST | `/interact` | Record accept/dismiss, update model |
| GET | `/stats` | Interaction counts, sync status |

---

## Privacy Guarantees

- Raw interaction data is stored in SQLite **inside the container volume** and never transmitted (NFR-4)
- Local head weights (`local_head.json`) have **no export method** in the serialiser — structurally excluded from all uploads (NFR-5)
- Only backbone weights + interaction count `n_k` are sent to the FL server

---

## Adding More Clients

Copy a client block in `docker-compose.yml`, increment port numbers, and create a matching `config/client_N.yaml`.