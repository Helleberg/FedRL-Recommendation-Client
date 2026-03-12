## FedRL-Recommendation-Client

Federated Reinforcement Learning client for sustainable food recommendations.
Each client runs as a pair of Docker containers: a **FastAPI backend** (Python) and a **Vue 3 + TypeScript frontend** served by Nginx.

---

## Quick Start - Setup on Raspberry Pi

### 1. Set your Raspberry Pi's LAN IP

```bash
export PI_HOST=<pi-ip>   # replace "<pi-ip>" with your Pi's IP
```

### 2. Edit per‑client config

Edit `config/client_1.yaml` (and `client_2.yaml`, `client_3.yaml`) and set:
- **`server_url`**: base URL of your FL server (no `/api/...` suffix).
- **`api_version`**: API version path segment (e.g. `v1`), used to build `SERVER_URL = server_url + "/api/" + api_version` inside the client.
- Optional model/sync settings as documented in the config files.

### 3. Build and run

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

```text
FedRL-Recommendation-Client/
├── Dockerfile.api          # Python 3.11 + FastAPI backend
├── Dockerfile.ui           # Vue 3 TS → Nginx static
├── docker-compose.yml      # Multi-client orchestration
├── config/
│   └── client_N.yaml       # Per-client config (mounted read-only)
├── api/
│   ├── main.py             # FastAPI entrypoint (JSON endpoints)
│   ├── rl/
│   │   ├── backbone.py         # Shared backbone (PyTorch, federated)
│   │   ├── local_head.py       # Item/Price/Nudge heads (never leaves device)
│   │   ├── model_manager.py    # Backbone + local heads, save/load
│   │   ├── context.py          # Context vector builder (16-dim)
│   │   └── reward.py           # Reward function
│   ├── sync/
│   │   └── sync_agent.py       # Background federation upload/download
│   ├── storage/
│   │   ├── models.py           # FoodItem / FoodCategory / SubstitutionGroup dataclasses
│   │   ├── interaction_logger.py   # SQLite (on-device only)
│   │   └── catalogue.py            # Catalogue cache + versioned snapshot sync
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

All endpoints are exposed by the client API container (per client) and are versioned via the `SERVER_URL` constructed from `config/client_N.yaml` (`server_url + "/api/" + api_version`).

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Client status, algorithm, catalogue info |
| GET | `/cart` | Cart items with RL recommendations |
| POST | `/cart/add` | Add item to cart |
| DELETE | `/cart/{id}` | Remove item from cart |
| GET | `/catalogue` | All food items (optional `?category=`) |
| GET | `/catalogue/categories` | All category objects (`id`, `code`, `name`) |
| POST | `/interact` | Record accept/dismiss, update model and log interaction |
| GET | `/stats` | Interaction counts, sync status, backbone version |

---

## Privacy Guarantees

- Raw interaction data is stored in SQLite **inside the container volume** and never transmitted (NFR-4)
- Local head weights (`local_head.json`) have **no export method** in the serialiser — structurally excluded from all uploads (NFR-5)
- Only backbone weights + interaction count `n_k` are sent to the FL server

---

## Adding More Clients

Copy a client block in `docker-compose.yml`, increment port numbers, and create a matching `config/client_N.yaml`.
