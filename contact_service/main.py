from fastapi import FastAPI, HTTPException, status, Depends 
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, text, Enum
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from enum import IntEnum


app = FastAPI(
    title="Serviço de Contatos",
    description="Gerencia agência de contatos ."
)

class PhoneType(IntEnum):
    PHONE_TYPE_MOBILE = 0
    PHONE_TYPE_FIXED = 1
    PHONE_TYPE_COMERCIAL = 2

class PhoneCategory(IntEnum):
    CATEGORY_FAMILY = 0
    CATEGORY_PERSONAL = 1
    CATEGORY_COMERCIAL = 2

class Telephone(BaseModel):
    number: str
    phone_type: PhoneType

class Contact(BaseModel):
    id: int
    name: str
    telephones: list[Telephone]
    category: PhoneCategory

# Banco de dados simulado em memória
contacts_db = {
    1: Contact(id=1, name="Leandro Wives", telephones=[Telephone(number="+5551912345678", phone_type=PhoneType.PHONE_TYPE_MOBILE)], category=PhoneCategory.CATEGORY_FAMILY),
    2: Contact(id=2, name="Renata Galante", telephones=[Telephone(number="+5551987654321", phone_type=PhoneType.PHONE_TYPE_FIXED)], category=PhoneCategory.CATEGORY_PERSONAL),
    3: Contact(id=3, name="Marcelo Pimenta", telephones=[Telephone(number="+5551956781234", phone_type=PhoneType.PHONE_TYPE_COMERCIAL)], category=PhoneCategory.CATEGORY_COMERCIAL),
}


@app.get("/", tags=["Healthcheck"])
def get_status():
    return {"message": "API is running"}

@app.get("/contato/{contact_id}", response_model=Contact)
def get_contact(contact_id: int):
    """
    Retorna os detalhes de um contato específico.
    """
    contact = contacts_db.get(contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    return contact

@app.get("/contatos", response_model=list[Contact])
def list_contacts():
    """
    Lista todos os contatos disponíveis.
    """
    return list(contacts_db.values())

@app.post("/contato", status_code=201)
def create_contact(contact: Contact):
    """
    Adiciona um novo contato.
    """
    if contact.id in contacts_db:
        raise HTTPException(status_code=400, detail="Contato com este ID já existe")
    contacts_db[contact.id] = contact
    return {"message": "Contato criado com sucesso", "contact": contact}