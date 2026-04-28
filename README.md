# 📈 Analyste Financier IA
![Aperçu de l'application](image.png)
SIGNAL, Plateforme d'analyse boursière alimentée par IA, SIGNAL combine indicateurs techniques et actualités financières pour produire des recommandations d'investissement structurées.

🔗 **Demo live** : [https://varde11-analyste-financier.hf.space](https://varde11-analyste-financier.hf.space)  

---

## Aperçu

L'utilisateur sélectionne un ticker boursier (parmi 20 disponibles de différent pays — US, France, Europe, Asie) et le système effectue automatiquement :

1. La récupération des **indicateurs techniques** via `yfinance` (RSI, SMA50, SMA200, prix)
2. Une **recherche d'actualités** récentes via DuckDuckGo
3. Une **analyse du sentiment** des news 
4. Le **calcul d'un score pondéré** de −6 à +6 combinant les trois signaux
5. La production d'une **recommandation** BUY / HOLD / SELL avec rapport détaillé

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  Frontend React                  │
│          Vite · CSS Modules · Recharts           │
│   Login · Dashboard · Analyse · Historique       │
└───────────────────┬─────────────────────────────┘
                    │ HTTP / JWT 
┌───────────────────▼─────────────────────────────┐
│               Backend FastAPI                    │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │           Agent LangGraph                │   │
│  │                                          │   │
│  │  get_tech ──► news_llm ──► tools         │   │
│  │      │           │          │            │   │
│  │   yfinance   Qwen3-32b  DuckDuckGo       │   │
│  │      │           │                       │   │
│  │      └────► parse_news ──► decision      │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│              PostgreSQL (SQLAlchemy)              │
└─────────────────────────────────────────────────┘
```

---

## Stack technique

### Backend
| Composant | Technologie |
|---|---|
| Framework API | FastAPI |
| Agent IA | LangGraph + LangChain |
| LLM | Qwen3-32b via Groq API |
| Recherche web | DuckDuckGo Search (LangChain) |
| Données boursières | yfinance |
| Base de données | PostgreSQL + SQLAlchemy |
| Authentification | JWT (python-jose) |
| Conteneurisation | Docker |

### Frontend
| Composant | Technologie |
|---|---|
| Framework | React 18 + Vite |
| Routing | React Router v6 |
| Styles | CSS Modules |
| Graphiques | Recharts (LineChart, PieChart, RadarChart) |
| Déploiement | Docker + Nginx |

---

## Fonctionnement du scoring

La décision finale repose sur un **score pondéré** de −6 à +6 combinant trois signaux indépendants :

### Signal RSI (±2 points)
| Zone | Score | Interprétation |
|---|---|---|
| RSI < 30 | +2 | Survendue — potentiel rebond |
| RSI 30–45 | +1 | Légère sous-pression |
| RSI 45–55 | 0 | Neutre |
| RSI 55–70 | −1 | Légèrement surachetée |
| RSI > 70 | −2 | Surachetée — risque de correction |

### Signal Tendance SMA (±2 points)
| Situation | Score |
|---|---|
| Golden Cross + Prix > SMA50 | +2 |
| Golden Cross + Prix < SMA50 | +1 |
| Death Cross + Prix > SMA50 | −1 |
| Death Cross + Prix < SMA50 | −2 |

### Signal Sentiment news (±2 points)
| Sentiment | Confiance dominante | Score |
|---|---|---|
| POSITIVE | HIGH | +2 |
| POSITIVE | MEDIUM/LOW | +1 |
| NEUTRAL | — | 0 |
| NEGATIVE | MEDIUM/LOW | −1 |
| NEGATIVE | HIGH | −2 |

### Règle de sécurité
Si `sentiment == NEGATIVE HIGH` **et** `Death Cross` → malus supplémentaire de −1 pour forcer un SELL lors d'un krach confirmé.

### Décision finale
```
Score ≥ +3  →  🟢 BUY
Score ≤ −3  →  🔴 SELL
Sinon       →  🟡 HOLD
```

---

## Tickers disponibles

| Symbole | Entreprise | Pays |
|---|---|---|
| TSLA | Tesla | 🇺🇸 |
| AMZN | Amazon | 🇺🇸 |
| GOOG | Alphabet (Google) | 🇺🇸 |
| MSFT | Microsoft | 🇺🇸 |
| AAPL | Apple | 🇺🇸 |
| NVDA | Nvidia | 🇺🇸 |
| META | Meta Platforms | 🇺🇸 |
| NFLX | Netflix | 🇺🇸 |
| BA | Boeing | 🇺🇸 |
| ZS | Zscaler | 🇺🇸 |
| JPM | JPMorgan Chase | 🇺🇸 |
| GLD | SPDR Gold ETF | 🇺🇸 |
| MO | Altria Group | 🇺🇸 |
| MC.PA | LVMH | 🇫🇷 |
| TTE | TotalEnergies | 🇫🇷 |
| AIR.PA | Airbus | 🇫🇷 |
| ASML | ASML Holding | 🇳🇱 |
| SAP | SAP SE | 🇩🇪 |
| SPOT | Spotify | 🇸🇪 |
| 005930.KS | Samsung Electronics | 🇰🇷 |

---

## Structure du projet

```
.
├── app/                         # Backend FastAPI
│   ├── chain.py                 # Point d'entrée FastAPI + routes
│   ├── agents.py                # Graph LangGraph + nodes
│   ├── schema.py                # Schémas Pydantic
│   ├── tools/
│   │   ├── technical_indicator.py  # RSI, SMA, scoring
│   │   └── search.py               # DuckDuckGo tool
│   ├── structure_table.py       # Modèles SQLAlchemy
│   ├── db.py                    # Connexion PostgreSQL
│   ├── helpers.py               # Hash password, JWT
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                    # Frontend React
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx              # Routing React Router v6
│   │   ├── index.css            # Variables CSS globales
│   │   ├── services/
│   │   │   └── api.js           # Appels FastAPI
│   │   ├── context/
│   │   │   └── AuthContext.jsx  # Token JWT global
│   │   ├── hooks/
│   │   │   └── useSessionExpired.js
│   │   ├── components/
│   │   │   ├── layout/          # Sidebar, AppLayout, ProtectedRoute
│   │   │   ├── ui/              # Badge, SessionBanner
│   │   │   └── prediction/      # ScoreBar, ScoreBreakdown
│   │   └── pages/
│   │       ├── Login.jsx
│   │       ├── Register.jsx
│   │       ├── Dashboard.jsx
│   │       ├── NewPrediction.jsx
│   │       ├── History.jsx
│   │       └── PredictionDetail.jsx
│   ├── entrypoint.sh            # Injection runtime API_URL + config nginx
│   ├── Dockerfile
│   └── package.json
│
└── docker-compose.yml
```

---

## Installation locale

### Prérequis
- Docker + Docker Compose
- Clé API Groq ([console.groq.com](https://console.groq.com))

### 1. Cloner le repo
```bash
git clone https://github.com/varde11/analyste-financier.git
cd analyste-financier
```

### 2. Configurer les variables d'environnement
```bash
cp .env.example .env
```

Remplir `.env` :
```env
# Base de données
POSTGRES_USER=user
POSTGRES_PASSWORD=your_password
DATABASE_URL=postgresql://user:your_password@finance_db:5432/finance_database

# Groq
GROQ_API_KEY=gsk_...

# JWT
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS
AUTHORIZED_URL1=http://localhost

# Frontend
API_URL=http://localhost:8000
PORT=80
```

### 3. Lancer
```bash
docker compose up --build
```

L'application est accessible sur `http://localhost`.

---



## Déploiement (Hugging Face Spaces)

Le projet est déployé sur deux Spaces HF distincts :

**Backend** (`Docker` Space) :
```dockerfile
FROM varde11/imagefinance:latest
CMD ["uvicorn", "chain:app", "--host", "0.0.0.0", "--port", "7860"]
```
Variables Secrets HF : `GROQ_API_KEY`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `DATABASE_URL`, `AUTHORIZED_URL1`

**Frontend** (`Docker` Space) :
```dockerfile
FROM varde11/finance_ui:latest
EXPOSE 7860
ENTRYPOINT ["/entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
```
Variables Secrets HF : `API_URL` (URL du backend HF), `PORT=7860`

L'injection de `API_URL` se fait au **runtime** via `entrypoint.sh` dans `window.__ENV__`, ce qui permet de changer l'URL sans rebuild de l'image.

---

## Limitations connues

- Les news récupérées via DuckDuckGo peuvent parfois inclure des articles datant de plusieurs mois — la confiance est automatiquement rétrogradée à LOW pour les articles anciens.
- Le système est calibré pour un horizon d'investissement moyen terme (semaines/mois) — pas adapté au trading intraday.
- Les RSI < 30 ou > 70 sur les grandes capitalisations sont rares en conditions normales de marché, ce qui favorise les décisions HOLD.
- Ce projet est un outil d'aide à la décision à but éducatif — **pas un conseil financier**.

---

## Auteur

**Varde** — Étudiant ingénieur — Spécialisation Data & IA  
GitHub : [@varde11](https://github.com/varde11)
- LinkedIn : [vannel-evrard-feukou-noukatche90092](https://www.linkedin.com/in/vannel-evrard-feukou-noukatche90092)
