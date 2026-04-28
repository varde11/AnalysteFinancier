from agents import make_agent, load_agent_artificats
from langchain_core.messages import HumanMessage
from fastapi import FastAPI, HTTPException, Depends
from schema import enumTicket,enumDecision, Client_Out, Client_In,Client_Login, PredictionSchema,TokenOut
from structure_table import Client, Prediction, Base
from db import get_db, engine
from sqlalchemy.orm import Session
from datetime import datetime,timedelta,timezone
from contextlib import asynccontextmanager
from sqlalchemy import exists


from helpers import verify_password,hash_password
from jose import jwt
from contextlib import asynccontextmanager

from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os


agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent
    print("Préparation des ressources....")
    load_agent_artificats()
    if agent is None:
        agent = make_agent()
    Base.metadata.create_all(bind=engine)
    print("Préparation terminé")
    yield
    print("Fermeture de l'application, merci de l'avoir essayer ;)")


app = FastAPI(title="Stock Decision Agent", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("AUTHORIZED_URL1"),os.getenv("AUTHORIZED_URL2")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)



SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))



def create_access_token(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


security = HTTPBearer()

def get_current_client(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_client = payload.get("sub")
        if not id_client:
            raise HTTPException(status_code=401, detail="Token invalide")
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")

    client = db.query(Client).filter(Client.id_client == id_client).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client introuvable")

    return client



@app.post("/login", response_model=TokenOut)
def login(client_data: Client_Login, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id_client == client_data.id_client).first()

    if not client or not verify_password(client_data.password, client.password_hash):
        raise HTTPException(status_code=401, detail="Identifiants invalides")

    token = create_access_token({"sub": client.id_client})

    return TokenOut(access_token=token)





@app.get("/healthy")
def healthy():
    return {"status": "okay"}


@app.get("/Me")
def get_client_by_id_client(current_client:Client=Depends(get_current_client),db:Session=Depends(get_db)):
    client = db.query(Client).filter(Client.id_client==current_client.id_client).first()
    if not client:
        raise HTTPException(status_code=404,detail=f"Le client d'identifiant {current_client.id_client} n'existe pas.")
    return client


@app.get("/GetPredictionByIdPrediction/{id_prediction}", response_model=PredictionSchema)
def get_prediction_by_idprediction(id_prediction: int, db: Session = Depends(get_db)):
    prediction = db.query(Prediction).filter(Prediction.id_prediction == id_prediction).first()
    if not prediction:
        raise HTTPException(status_code=404, detail=f"Prédiction {id_prediction} introuvable.")
    return prediction


@app.get("/GetPredictionByIdClient",response_model=list[PredictionSchema])
def get_prediction_by_idclient(current_client:Client=Depends(get_current_client),db:Session=Depends(get_db)):
    client = db.query(Client).filter(current_client.id_client==Client.id_client).first()
    if not client:
        raise HTTPException(status_code=404,detail=f"Le client d'identifiant {current_client.id_client} n'existe pas.")
    
    predictions = db.query(Prediction).filter(current_client.id_client==Prediction.id_client).order_by(Prediction.time_stamp).all()
    if not predictions:
        return []
    
    return predictions


def get_current_ticket(id_client:str,db:Session=Depends(get_db)):
    prediction_raw = db.query(Prediction).filter(Prediction.id_client==id_client)
    if not prediction_raw:
        return []
    
    tickets_set = set ( [PredictionSchema.model_validate(p).model_dump().get("ticket") for p in prediction_raw] )
    
    return list(tickets_set)


@app.get("/GetPredictionByTicket",response_model=list[PredictionSchema])
def get_prediction_by_ticket(ticket:enumTicket,current_client:Client=Depends(get_current_client),db:Session=Depends(get_db)):
    predictions = db.query(Prediction).filter(Prediction.id_client==current_client.id_client).filter(Prediction.ticket==ticket).all()

    if not predictions:
        return []
    print(f"here's your current ticket: {get_current_ticket(current_client.id_client,db)}")
    return predictions



@app.get("/GetPredictionByDecision",response_model=list[PredictionSchema])
def get_prediction_by_decision(decision:enumDecision,current_client:Client=Depends(get_current_client),db:Session=Depends(get_db)):
    predictions = db.query(Prediction).filter(current_client.id_client==Prediction.id_client).filter(Prediction.decision==decision).all()

    if not predictions:
        return []
    
    return predictions


@app.post("/Prediction", response_model=PredictionSchema)
def make_prediction( ticket: enumTicket,current_client:Client=Depends(get_current_client), db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id_client == current_client.id_client).first()
    if not client:
        raise HTTPException(status_code=404, detail=f"Client {current_client.id_client} introuvable.")

    events = agent.stream(
        {"messages": [HumanMessage(content=ticket)]},
        stream_mode="values"
    )

    result = None
    for event in events:
        if "final" in event and event["final"]:
            result = event["final"]
            break

    if result is None:
        raise HTTPException(status_code=500, detail="Une erreur s'est produite lors de l'analyse, merci de rééssayer dans quelques secondes.")

    time_stamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prediction = Prediction(
        id_client=current_client.id_client,
        ticket=ticket,
        time_stamp=datetime.strptime(time_stamp_str, "%Y-%m-%d %H:%M:%S"),
        key_news=result["news"]["key_news"],
        sentiment=result["news"]["sentiment"],
        notes=result["news"].get("notes"),
        step_by_step_check=result["step_by_step_check"],
        decision=result["decision"],
        reasoning=result["reasoning"],
        report_detail=result["report_detail"],    # ← structure JSON
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return prediction



@app.post("/AddClient", response_model=Client_Out)
def add_client(client: Client_In, db: Session = Depends(get_db)):
    if db.query(exists().where(Client.id_client == client.id_client)).scalar():
        raise HTTPException(
            status_code=422,
            detail=f"Il existe déjà un client avec l'id {client.id_client}"
        )

    new_client = Client(
        id_client=client.id_client,
        nom=client.nom,
        password_hash=hash_password(client.password),

    )

    db.add(new_client)
    db.commit()
    db.refresh(new_client)

    return new_client



def delete_prediction_for_client(id_client,db):
    db.query(Prediction).filter(Prediction.id_client==id_client).delete(synchronize_session=False)
    db.commit()


@app.delete("/DeletePredictionByIdClient",response_model=list[PredictionSchema])
def delete_prediction_by_idclient(current_client:Client=Depends(get_current_client),db:Session=Depends(get_db)):
    client = db.query(Client).filter(Client.id_client==current_client.id_client).first()
    if not client:
        raise HTTPException(status_code=404,detail=f"Le client d'identifiant {current_client.id_client} est introuvable.")
    
    prediction_raw = db.query(Prediction).filter(Prediction.id_client==current_client.id_client).all()
    if not prediction_raw:
        return []

    deleted = [PredictionSchema.model_validate(p).model_dump() for p in prediction_raw]
    delete_prediction_for_client(id_client=current_client.id_client,db=db)

    return deleted


@app.delete("/DeletePredictionByIdPrediction",response_model=PredictionSchema)
def delete_prediction_by_idprediction(id_prediction:int,db:Session=Depends(get_db)):
    prediction = db.query(Prediction).filter(Prediction.id_prediction==id_prediction).first()
    if not prediction:
        raise HTTPException(status_code=404,detail=f"Il n'existe aucune prédiction avec l'identifiant {id_prediction}")
    
    deleted = PredictionSchema.model_validate(prediction).model_dump()
    db.query(Prediction).filter(Prediction.id_prediction==id_prediction).delete(synchronize_session=False)
    db.commit()
    db.refresh(prediction)

    return deleted