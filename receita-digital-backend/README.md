# 🏥 Sistema de Receitas Médicas - Backend

API REST para gerenciamento de receitas médicas digitais, desenvolvida com Flask e SQLite.

## ✨ Características

- 🔐 **Autenticação JWT** - Login seguro com tokens
- 👥 **Múltiplos perfis** - Admin, Médicos e Pacientes
- 📋 **Gestão de receitas** - CRUD completo de receitas médicas
- 💊 **Catálogo de medicamentos** - Base de dados de medicamentos
- 🏪 **Rede de farmácias** - Cadastro com geolocalização
- 🔒 **Controle de acesso** - Permissões baseadas em perfil
- 📱 **CORS habilitado** - Pronto para frontend
- 🗄️ **SQLite** - Banco leve e portátil

## 🛠️ Tecnologias

- **Python 3.8+**
- **Flask** - Framework web
- **SQLite** - Banco de dados
- **JWT** - Autenticação
- **Werkzeug** - Segurança de senhas
- **Flask-CORS** - Cross-Origin Resource Sharing

## 📁 Estrutura do Projeto

```
backend/
├── app.py                      # Aplicação principal Flask
├── database.db                 # Banco SQLite (criado automaticamente)
├── sqlite_backend_script.sql   # Script de criação das tabelas
├── generate_mock_data.py       # Gerador de dados mock
├── credenciais_teste.json      # Credenciais para teste (gerado)
├── requirements.txt            # Dependências Python
├── test_api.sh                # Script de testes automatizados
└── README.md                  # Este arquivo
```

## 🚀 Instalação

### 1. Clone o repositório
```bash
git clone <repository-url>
cd sistema-receitas-backend
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados
```bash
# O banco será criado automaticamente na primeira execução
# Ou execute o script SQL manualmente se necessário
```

### 5. Execute a aplicação
```bash
python app.py
```

A API estará disponível em: `http://localhost:5000`

### 6. (Opcional) Gere dados mock
```bash
python generate_mock_data.py
```

## 🗄️ Estrutura do Banco de Dados

### Tabelas Principais

#### **Usuario**
```sql
- id_usuario (PK)
- nome
- email (unique)
- senha (hash)
- tipo (admin/medico/paciente)
```

#### **Medico**
```sql
- id_medico (PK, FK -> Usuario)
- crm
- especialidade
```

#### **Paciente**
```sql
- id_paciente (PK, FK -> Usuario)
- cpf
- telefone
- endereco
```

#### **Medicamento**
```sql
- id_medicamento (PK)
- nome
- principio_ativo
- fabricante
- codigo_barras
- prescricao_obrigatoria
```

#### **Farmacia**
```sql
- id_farmacia (PK)
- cnpj
- nome_fantasia
- endereco
- telefone
- responsavel_tecnico
- latitude
- longitude
```

#### **Receita**
```sql
- id_receita (PK)
- id_medico (FK)
- id_paciente (FK)
- data_emissao
- data_validade
- diagnostico
- observacoes
- status (ativa/utilizada/cancelada/expirada)
```

#### **ReceitaMedicamento**
```sql
- id_receita_medicamento (PK)
- id_receita (FK)
- id_medicamento (FK)
- dosagem
- quantidade
- posologia
- observacoes
```

## 🔐 Autenticação

### Sistema JWT
- **Login**: `POST /api/login`
- **Token**: Válido por 24 horas
- **Header**: `Authorization: Bearer <token>`

### Perfis de Usuário

| Perfil | Permissões |
|--------|------------|
| **Admin** | ✅ Tudo: usuários, medicamentos, farmácias, receitas |
| **Médico** | ✅ Criar receitas, ver próprias receitas, medicamentos, farmácias |
| **Paciente** | ✅ Ver próprias receitas, medicamentos, farmácias |

## 🛣️ Endpoints da API

### 🔓 Públicos
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/health` | Status da API |
| `POST` | `/api/register` | Cadastro de usuários |
| `POST` | `/api/login` | Login de usuários |

### 🔒 Protegidos (Requer Token)

#### **Usuários**
| Método | Endpoint | Permissão | Descrição |
|--------|----------|-----------|-----------|
| `GET` | `/api/profile` | Todos | Perfil do usuário logado |
| `GET` | `/api/usuarios` | Admin | Listar todos os usuários |

#### **Medicamentos**
| Método | Endpoint | Permissão | Descrição |
|--------|----------|-----------|-----------|
| `GET` | `/api/medicamentos` | Todos | Listar medicamentos |
| `POST` | `/api/medicamentos` | Admin | Criar medicamento |

#### **Farmácias**
| Método | Endpoint | Permissão | Descrição |
|--------|----------|-----------|-----------|
| `GET` | `/api/farmacias` | Todos | Listar farmácias |
| `POST` | `/api/farmacias` | Admin | Criar farmácia |

#### **Receitas**
| Método | Endpoint | Permissão | Descrição |
|--------|----------|-----------|-----------|
| `POST` | `/api/receitas` | Médico | Criar receita |
| `GET` | `/api/receitas/<id>` | Dono/Admin | Ver receita específica |
| `PUT` | `/api/receitas/<id>/status` | Médico/Admin | Alterar status |

## 💡 Exemplos de Uso

### Login
```bash
# Admin
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@sistema.com", "senha": "admin123"}'

# Médico
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "joao.silva@clinica.com", "senha": "medico123"}'
```

### Criar Receita
```bash
curl -X POST http://localhost:5000/api/receitas \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "id_paciente": 8,
    "diagnostico": "Hipertensão Arterial",
    "observacoes_gerais": "Controlar pressão diariamente",
    "medicamentos": [
      {
        "id_medicamento": 1,
        "dosagem": "1 comprimido",
        "quantidade": 2,
        "posologia": "1 vez ao dia",
        "observacoes": "Tomar em jejum"
      }
    ]
  }'
```

### Ver Perfil
```bash
curl -X GET http://localhost:5000/api/profile \
  -H "Authorization: Bearer <token>"
```

## 🎭 Dados Mock

Execute o script para popular o banco com dados de teste:

```bash
python generate_mock_data.py
```

### Credenciais de Teste

**Admin:**
- Email: `admin@sistema.com`
- Senha: `admin123`

**Médicos:**
- Email: `joao.silva@clinica.com` | Senha: `medico123`
- Email: `maria.santos@hospital.com` | Senha: `medico123`

**Pacientes:**
- Email: `jose.silva@email.com` | Senha: `paciente123`
- Email: `maria.oliveira@email.com` | Senha: `paciente123`

## 🧪 Testes

### Manual com HTTPie
```bash
# Instalar HTTPie
pip install httpie

# Teste básico
http GET localhost:5000/api/health

# Login
http POST localhost:5000/api/login email=admin@sistema.com senha=admin123
```

### Script Automatizado
```bash
chmod +x test_api.sh
./test_api.sh
```

### Teste de Endpoints
```bash
# Saúde da API
curl http://localhost:5000/api/health

# Login e obter token
TOKEN=$(curl -s -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sistema.com","senha":"admin123"}' | \
  python -c "import sys, json; print(json.load(sys.stdin)['token'])")

# Usar token
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/profile
```

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.


**Desenvolvido com ❤️ para facilitar o gerenciamento de receitas médicas digitais**