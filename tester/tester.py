import os 
import requests
import time

CONTACT_SERVICE_URL = "http://contact_service_container:8002"
GRAPHQL_SERVICE_URL = "http://graphql_api_gateway_container:9004"

def check_api_status(attempts=10, delay=3):
    for i in range(attempts):
        try:
            response = requests.get(f"{CONTACT_SERVICE_URL}/")
            if response.status_code == 200:
                print("API is up. Ready for use.")
                return
        except requests.exceptions.ConnectionError:
            print("Failed connection, retrying...")
            
        print(f"Attempting connection to API... ({i+1}/{attempts})")


        time.sleep(delay)
    raise Exception("Exceeded max attempts. Could not get API status")

def test_list_contacts():
    try:
        # consulta o microsserviço de contatos
        response = requests.get(f"{CONTACT_SERVICE_URL}/contatos")
        response.raise_for_status() # Dispara um HTTPError para status 4xx/5xx
        print(response.json())
        
    except requests.exceptions.RequestException as e:
        print(f"Erro ao consultar serviço de contatos (contacts): {e}")
        print([]) # Retorna lista vazia ou um erro mais específico para o cliente GraphQL
        

def test_find_contact_by_id(id: int):
    try:
        response = requests.get(f"{CONTACT_SERVICE_URL}/contato/{id}")
        response.raise_for_status()
        print(response.json())
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return None # Retorna null para contato não encontrado, conforme o esquema
        print(f"Erro HTTP ao consultar serviço de contatos (contact/{id}): {e}")
        print(None)
        
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão ao consultar serviço de contatos (contact/{id}): {e}")
        print(None)
        
    
    
def test_add_contact():
    contact = {"id": "47",
               "name":"Agente",
                "telephones": [{"number":"+5551999999999",
                                "phone_type": "0"},
                                {"number":"+555188888888",
                                 "phone_type": "1"},
                                 ], 
                "category": "2"
                }
    try:
        # faz um POST no microsserviço de contatos
        response = requests.post(
            f"{CONTACT_SERVICE_URL}/contato",
            json=contact
        )
        response.raise_for_status()
        response_data = response.json()
        print(response_data)
        
    except requests.exceptions.HTTPError as e:
        print(f"Erro HTTP ao criar contato: {e}. Resposta: {e.response.text}")
        error_detail = e.response.json().get("detail", "Erro desconhecido ao criar contato.")
        print(error_detail)
        
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão ao criar contato: {e}")
        print("Erro de rede ao comunicar com o serviço de contatos.")
        


def test_list_contacts_graphql():
    query = """
        query {
            contacts {
                id
                name
                telephones {
                    number
                    phone_type
                }
                category
            }
        }
        """
    
    response = requests.post(f"{GRAPHQL_SERVICE_URL}/graphql", json={"query": query})
    print(response.status_code)
    print(response.json())

        


def test_add_contact_graphql():
    mutation = """
        mutation {
            addContact(
                input: {id: 99, name: "Augusto Dalcin Peiter", telephones: [{number: "+5551955554444", phone_type: PHONE_TYPE_MOBILE}, {number: "+5551944445555", phone_type: PHONE_TYPE_FIXED}], category: CATEGORY_PERSONAL}
            ) {
                message
                contact {
                name
                telephones {
                    number
                    phone_type
                }
                category
                }
            }
        }
        """
    response = requests.post(f"{GRAPHQL_SERVICE_URL}/graphql", json={"query": mutation})
    print(response.status_code)
    print(response.json())

        

def test_find_contact_by_id_graphql():
    query = """
        query {
            contact(id:1) {
                id
                name
                telephones {
                number
                phone_type
                }
                category
            }
        }
        """
    
    response = requests.post(f"{GRAPHQL_SERVICE_URL}/graphql", json={"query": query})
    print(response.status_code)
    print(response.json())

        


if __name__ == "__main__":
    check_api_status()
    print("TESTING REST API CALLS")
    print("TEST LIST CONTACTS")
    print(test_list_contacts())
    print("TEST FIND CONTACT BY ID")
    print(test_find_contact_by_id(1))
    print("TEST ADD CONTACT")
    print(test_add_contact())
    print("TESTING GRAPHQL CALLS")
    print("TEST LIST CONTACTS")
    test_list_contacts_graphql()
    print("TEST FIND CONTACT BY ID")
    test_find_contact_by_id_graphql()
    print("TEST ADD CONTACT")
    test_add_contact_graphql()
