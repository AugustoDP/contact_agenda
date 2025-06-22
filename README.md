# execute com 
docker compose up --build  

# acesse o gateway graphql em 
http://127.0.0.1:9004/graphql

# acesse docs de APIs
http://127.0.0.1:8002/docs

# resultados de tester podem ser consultados com 
docker logs tester_container

# para rodar os testes novamente basta
docker container start tester_container
# resultados também estarão visíveis no cmd que estiver rodando docker compose up --build

# termine os containers com CTRL+C

# consulte contatos:

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

# crie contatos:

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

# consulte contato:

query {
  contact(id: 1) {
    id
    name
    telephones {
      number
      phone_type
    }
    category
  }
}
