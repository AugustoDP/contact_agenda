from fastapi import FastAPI, HTTPException
from ariadne import QueryType, MutationType, make_executable_schema, load_schema_from_path, EnumType
from ariadne.graphql import GraphQLError
from ariadne.asgi import GraphQL 
import os 
import requests 
import enum

# Cria a instância da aplicação FastAPI
app = FastAPI(
    title="GraphQL API Gateway",
    description="Gateway que agrega APIs de Contatos e Pedidos."
)

# Carrega o esquema GraphQL 
type_defs = load_schema_from_path("schema.graphql")

# Define as URLs base dos microserviços de Pedidos e Contatos.
# Usa variáveis de ambiente para flexibilidade em diferentes ambientes (produção, desenvolvimento).
# Se as variáveis de ambiente não estiverem definidas, usa URLs de localhost como padrão.
CONTACT_SERVICE_URL = os.getenv("CONTACT_SERVICE_URL", "http://localhost:8002")

# --- Definição dos Resolvers para Queries (Consultas) ---

# Cria um objeto QueryType para agrupar todos os resolvers de consulta
query = QueryType()

# Cria um objeto MutationType para agrupar todos os resolvers de mutação
mutation = MutationType()


class PhoneType(enum.IntEnum):
    PHONE_TYPE_MOBILE = 0
    PHONE_TYPE_FIXED = 1
    PHONE_TYPE_COMERCIAL = 2

class PhoneCategory(enum.IntEnum):
    CATEGORY_FAMILY = 0
    CATEGORY_PERSONAL = 1
    CATEGORY_COMERCIAL = 2

phone_type = EnumType("PhoneType", PhoneType)
phone_category = EnumType("PhoneCategory", PhoneCategory)

# Resolver para a query 'contacts' (busca todos os contatos do Serviço de Contatos)

# mapeia uma consulta a 'contacts' (lista de contatos)
@query.field("contacts")
def resolve_contacts(_, info):
    try:
        # consulta o microsserviço de contatos
        response = requests.get(f"{CONTACT_SERVICE_URL}/contatos")
        response.raise_for_status() # Dispara um HTTPError para status 4xx/5xx
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao consultar serviço de contatos (contacts): {e}")
        return [] # Retorna lista vazia ou um erro mais específico para o cliente GraphQL

# mapeia uma consulta a 'contact' (um contato específico)
@query.field("contact")
def resolve_contact(_, info, id: int):
    try:
        response = requests.get(f"{CONTACT_SERVICE_URL}/contato/{id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return None # Retorna null para contato não encontrado, conforme o esquema
        print(f"Erro HTTP ao consultar serviço de contatos (contact/{id}): {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão ao consultar serviço de contatos (contact/{id}): {e}")
        return None
    

# --- Definição dos Resolvers para Mutations (Operações de Escrita) ---
@mutation.field("addContact")
def resolve_create_contact(_, info, input: dict):
    id = input.get("id")
    name = input.get("name")
    telephones = input.get("telephones")
    category = input.get("category")

    try:
        # faz um POST no microsserviço de contatos
        response = requests.post(
            f"{CONTACT_SERVICE_URL}/contato",
            json={"id": id, "name": name, "telephones": telephones, "category": category}
        )
        response.raise_for_status()
        response_data = response.json()
        return {
            "message": response_data.get("message", "Contato criado com sucesso."),
            "contact": response_data.get("contact")
        }
    except requests.exceptions.HTTPError as e:
        print(f"Erro HTTP ao criar contato: {e}. Resposta: {e.response.text}")
        error_detail = e.response.json().get("detail", "Erro desconhecido ao criar contato.")
        return {
            "message": error_detail,
            "contact": None 
        }
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão ao criar contato: {e}")
        return {
            "message": "Erro de rede ao comunicar com o serviço de contatos.",
            "contact": None
        }



# Cria o esquema executável do GraphQL, combinando as definições de tipo (type_defs)
# com os resolvers (query e mutation).
schema = make_executable_schema(type_defs, query, mutation, phone_category, phone_type)

# Adiciona o Endpoint GraphQL ao FastAPI 
app.mount("/graphql", GraphQL(schema, debug=True)) # debug=True para habilitar o GraphQL IDE