#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para gerar dados mock para o sistema de receitas médicas
Baseado na estrutura do backend Flask fornecido
"""

import sqlite3
import json
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

DATABASE = 'database.db'

def clear_database():
    """Limpa todas as tabelas para inserir dados frescos"""
    conn = sqlite3.connect(DATABASE)
    
    # Desabilitar foreign keys temporariamente
    conn.execute('PRAGMA foreign_keys = OFF')
    
    tables = [
        'ReceitaMedicamento',
        'Receita', 
        'Medicamento',
        'Farmacia',
        'Paciente',
        'Medico',
        'Usuario'
    ]
    
    for table in tables:
        try:
            conn.execute(f'DELETE FROM {table}')
            print(f"Tabela {table} limpa")
        except sqlite3.OperationalError:
            print(f"Tabela {table} não existe")
    
    # Reabilitar foreign keys
    conn.execute('PRAGMA foreign_keys = ON')
    conn.commit()
    conn.close()

def insert_mock_users():
    """Inserir usuários mock (admins, médicos e pacientes)"""
    conn = sqlite3.connect(DATABASE)
    
    # Admin
    admin_data = {
        'nome': 'Administrador Sistema',
        'email': 'admin@sistema.com',
        'senha': generate_password_hash('admin123'),
        'tipo': 'admin'
    }
    
    cursor = conn.execute(
        'INSERT INTO Usuario (nome, email, senha, tipo) VALUES (?, ?, ?, ?)',
        (admin_data['nome'], admin_data['email'], admin_data['senha'], admin_data['tipo'])
    )
    admin_id = cursor.lastrowid
    
    # Médicos
    medicos_data = [
        {
            'nome': 'Dr. João Silva',
            'email': 'joao.silva@clinica.com',
            'senha': generate_password_hash('medico123'),
            'tipo': 'medico',
            'crm': 'CRM-SP 123456',
            'especialidade': 'Cardiologia'
        },
        {
            'nome': 'Dra. Maria Santos',
            'email': 'maria.santos@hospital.com',
            'senha': generate_password_hash('medico123'),
            'tipo': 'medico',
            'crm': 'CRM-RJ 789012',
            'especialidade': 'Clínica Geral'
        },
        {
            'nome': 'Dr. Carlos Oliveira',
            'email': 'carlos.oliveira@clinica.com',
            'senha': generate_password_hash('medico123'),
            'tipo': 'medico',
            'crm': 'CRM-MG 345678',
            'especialidade': 'Endocrinologia'
        },
        {
            'nome': 'Dra. Ana Costa',
            'email': 'ana.costa@hospital.com',
            'senha': generate_password_hash('medico123'),
            'tipo': 'medico',
            'crm': 'CRM-SP 901234',
            'especialidade': 'Pediatria'
        },
        {
            'nome': 'Dr. Ricardo Ferreira',
            'email': 'ricardo.ferreira@clinica.com',
            'senha': generate_password_hash('medico123'),
            'tipo': 'medico',
            'crm': 'CRM-RS 567890',
            'especialidade': 'Neurologia'
        }
    ]
    
    medico_ids = []
    for medico in medicos_data:
        cursor = conn.execute(
            'INSERT INTO Usuario (nome, email, senha, tipo) VALUES (?, ?, ?, ?)',
            (medico['nome'], medico['email'], medico['senha'], medico['tipo'])
        )
        medico_id = cursor.lastrowid
        medico_ids.append(medico_id)
        
        # Inserir dados específicos do médico
        conn.execute(
            'INSERT INTO Medico (id_medico, crm, especialidade) VALUES (?, ?, ?)',
            (medico_id, medico['crm'], medico['especialidade'])
        )
    
    # Pacientes
    pacientes_data = [
        {
            'nome': 'José da Silva',
            'email': 'jose.silva@email.com',
            'senha': generate_password_hash('paciente123'),
            'tipo': 'paciente',
            'cpf': '123.456.789-01',
            'telefone': '(11) 98765-4321',
            'endereco': 'Rua das Flores, 123 - São Paulo/SP'
        },
        {
            'nome': 'Maria Oliveira',
            'email': 'maria.oliveira@email.com',
            'senha': generate_password_hash('paciente123'),
            'tipo': 'paciente',
            'cpf': '987.654.321-09',
            'telefone': '(21) 91234-5678',
            'endereco': 'Av. Copacabana, 456 - Rio de Janeiro/RJ'
        },
        {
            'nome': 'Carlos Santos',
            'email': 'carlos.santos@email.com',
            'senha': generate_password_hash('paciente123'),
            'tipo': 'paciente',
            'cpf': '456.789.123-45',
            'telefone': '(31) 99876-5432',
            'endereco': 'Rua Minas Gerais, 789 - Belo Horizonte/MG'
        },
        {
            'nome': 'Ana Paula Costa',
            'email': 'ana.costa@email.com',
            'senha': generate_password_hash('paciente123'),
            'tipo': 'paciente',
            'cpf': '321.654.987-12',
            'telefone': '(85) 98765-1234',
            'endereco': 'Rua do Sol, 321 - Fortaleza/CE'
        },
        {
            'nome': 'Pedro Almeida',
            'email': 'pedro.almeida@email.com',
            'senha': generate_password_hash('paciente123'),
            'tipo': 'paciente',
            'cpf': '159.753.486-20',
            'telefone': '(51) 97654-3210',
            'endereco': 'Av. Brasil, 654 - Porto Alegre/RS'
        },
        {
            'nome': 'Lucia Ferreira',
            'email': 'lucia.ferreira@email.com',
            'senha': generate_password_hash('paciente123'),
            'tipo': 'paciente',
            'cpf': '753.159.642-85',
            'telefone': '(62) 96543-2109',
            'endereco': 'Rua Goiás, 987 - Goiânia/GO'
        },
        {
            'nome': 'Roberto Lima',
            'email': 'roberto.lima@email.com',
            'senha': generate_password_hash('paciente123'),
            'tipo': 'paciente',
            'cpf': '852.963.741-96',
            'telefone': '(81) 95432-1098',
            'endereco': 'Av. Boa Viagem, 147 - Recife/PE'
        }
    ]
    
    paciente_ids = []
    for paciente in pacientes_data:
        cursor = conn.execute(
            'INSERT INTO Usuario (nome, email, senha, tipo) VALUES (?, ?, ?, ?)',
            (paciente['nome'], paciente['email'], paciente['senha'], paciente['tipo'])
        )
        paciente_id = cursor.lastrowid
        paciente_ids.append(paciente_id)
        
        # Inserir dados específicos do paciente
        conn.execute(
            'INSERT INTO Paciente (id_paciente, cpf, telefone, endereco) VALUES (?, ?, ?, ?)',
            (paciente_id, paciente['cpf'], paciente['telefone'], paciente['endereco'])
        )
    
    conn.commit()
    conn.close()
    
    print(f"Usuários inseridos:")
    print(f"- 1 Admin (ID: {admin_id})")
    print(f"- {len(medico_ids)} Médicos (IDs: {medico_ids})")
    print(f"- {len(paciente_ids)} Pacientes (IDs: {paciente_ids})")
    
    return admin_id, medico_ids, paciente_ids

def insert_mock_medicamentos():
    """Inserir medicamentos mock"""
    conn = sqlite3.connect(DATABASE)
    
    medicamentos_data = [
        {
            'nome': 'Losartana 50mg',
            'principio_ativo': 'Losartana Potássica',
            'fabricante': 'EMS',
            'codigo_barras': '7891234567890',
            'prescricao_obrigatoria': 1
        },
        {
            'nome': 'Paracetamol 500mg',
            'principio_ativo': 'Paracetamol',
            'fabricante': 'Medley',
            'codigo_barras': '7891234567891',
            'prescricao_obrigatoria': 0
        },
        {
            'nome': 'Omeprazol 20mg',
            'principio_ativo': 'Omeprazol',
            'fabricante': 'Eurofarma',
            'codigo_barras': '7891234567892',
            'prescricao_obrigatoria': 1
        },
        {
            'nome': 'Metformina 850mg',
            'principio_ativo': 'Cloridrato de Metformina',
            'fabricante': 'Sandoz',
            'codigo_barras': '7891234567893',
            'prescricao_obrigatoria': 1
        },
        {
            'nome': 'Ibuprofeno 600mg',
            'principio_ativo': 'Ibuprofeno',
            'fabricante': 'Sanofi',
            'codigo_barras': '7891234567894',
            'prescricao_obrigatoria': 0
        },
        {
            'nome': 'Atenolol 25mg',
            'principio_ativo': 'Atenolol',
            'fabricante': 'Germed',
            'codigo_barras': '7891234567895',
            'prescricao_obrigatoria': 1
        },
        {
            'nome': 'Dipirona 500mg',
            'principio_ativo': 'Dipirona Sódica',
            'fabricante': 'Neo Química',
            'codigo_barras': '7891234567896',
            'prescricao_obrigatoria': 0
        },
        {
            'nome': 'Sinvastatina 20mg',
            'principio_ativo': 'Sinvastatina',
            'fabricante': 'Ranbaxy',
            'codigo_barras': '7891234567897',
            'prescricao_obrigatoria': 1
        },
        {
            'nome': 'Captopril 25mg',
            'principio_ativo': 'Captopril',
            'fabricante': 'Medquímica',
            'codigo_barras': '7891234567898',
            'prescricao_obrigatoria': 1
        },
        {
            'nome': 'Amoxicilina 500mg',
            'principio_ativo': 'Amoxicilina',
            'fabricante': 'Novartis',
            'codigo_barras': '7891234567899',
            'prescricao_obrigatoria': 1
        }
    ]
    
    medicamento_ids = []
    for medicamento in medicamentos_data:
        cursor = conn.execute(
            '''INSERT INTO Medicamento 
               (nome, principio_ativo, fabricante, codigo_barras, prescricao_obrigatoria) 
               VALUES (?, ?, ?, ?, ?)''',
            (medicamento['nome'], medicamento['principio_ativo'], 
             medicamento['fabricante'], medicamento['codigo_barras'], 
             medicamento['prescricao_obrigatoria'])
        )
        medicamento_ids.append(cursor.lastrowid)
    
    conn.commit()
    conn.close()
    
    print(f"Medicamentos inseridos: {len(medicamento_ids)} (IDs: {medicamento_ids})")
    return medicamento_ids

def insert_mock_farmacias():
    """Inserir farmácias mock"""
    conn = sqlite3.connect(DATABASE)
    
    farmacias_data = [
        {
            'cnpj': '12.345.678/0001-90',
            'nome_fantasia': 'Farmácia Central',
            'endereco': 'Av. Paulista, 1000 - São Paulo/SP',
            'telefone': '(11) 3333-4444',
            'responsavel_tecnico': 'Farmacêutico João Pedro - CRF-SP 12345',
            'latitude': -23.5613,
            'longitude': -46.6560
        },
        {
            'cnpj': '98.765.432/0001-10',
            'nome_fantasia': 'Drogaria Popular',
            'endereco': 'Rua das Palmeiras, 250 - Rio de Janeiro/RJ',
            'telefone': '(21) 2222-3333',
            'responsavel_tecnico': 'Farmacêutica Maria Clara - CRF-RJ 67890',
            'latitude': -22.9068,
            'longitude': -43.1729
        },
        {
            'cnpj': '11.222.333/0001-44',
            'nome_fantasia': 'Farmácia Saúde Total',
            'endereco': 'Av. Afonso Pena, 500 - Belo Horizonte/MG',
            'telefone': '(31) 1111-2222',
            'responsavel_tecnico': 'Farmacêutico Carlos Eduardo - CRF-MG 11111',
            'latitude': -19.9191,
            'longitude': -43.9378
        },
        {
            'cnpj': '55.666.777/0001-88',
            'nome_fantasia': 'Drogaria Vida Nova',
            'endereco': 'Rua José de Alencar, 800 - Fortaleza/CE',
            'telefone': '(85) 9999-8888',
            'responsavel_tecnico': 'Farmacêutica Ana Beatriz - CRF-CE 22222',
            'latitude': -3.7319,
            'longitude': -38.5267
        },
        {
            'cnpj': '33.444.555/0001-66',
            'nome_fantasia': 'Farmácia Bem Estar',
            'endereco': 'Av. Borges de Medeiros, 1200 - Porto Alegre/RS',
            'telefone': '(51) 7777-6666',
            'responsavel_tecnico': 'Farmacêutico Ricardo Silva - CRF-RS 33333',
            'latitude': -30.0346,
            'longitude': -51.2177
        }
    ]
    
    farmacia_ids = []
    for farmacia in farmacias_data:
        cursor = conn.execute(
            '''INSERT INTO Farmacia 
               (cnpj, nome_fantasia, endereco, telefone, responsavel_tecnico, latitude, longitude) 
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (farmacia['cnpj'], farmacia['nome_fantasia'], farmacia['endereco'],
             farmacia['telefone'], farmacia['responsavel_tecnico'], 
             farmacia['latitude'], farmacia['longitude'])
        )
        farmacia_ids.append(cursor.lastrowid)
    
    conn.commit()
    conn.close()
    
    print(f"Farmácias inseridas: {len(farmacia_ids)} (IDs: {farmacia_ids})")
    return farmacia_ids

def insert_mock_receitas(medico_ids, paciente_ids, medicamento_ids):
    """Inserir receitas mock"""
    conn = sqlite3.connect(DATABASE)
    
    # Status possíveis para receitas
    status_opcoes = ['ativa', 'utilizada', 'cancelada']
    
    # Diagnósticos comuns
    diagnosticos = [
        'Hipertensão Arterial',
        'Diabetes Mellitus Tipo 2',
        'Infecção Respiratória',
        'Gastrite',
        'Cefaleia',
        'Artralgia',
        'Síndrome Gripal',
        'Dislipidemia',
        'Ansiedade',
        'Lombalgia'
    ]
    
    # Dosagens comuns
    dosagens = ['1 comprimido', '2 comprimidos', '1/2 comprimido', '1 cápsula', '2 cápsulas']
    
    # Posologias comuns
    posologias = [
        '1 vez ao dia',
        '2 vezes ao dia',
        '3 vezes ao dia',
        'De 8 em 8 horas',
        'De 12 em 12 horas',
        'A cada 6 horas',
        'Antes das refeições',
        'Após as refeições',
        'Em jejum',
        'Ao deitar'
    ]
    
    receita_ids = []
    
    # Gerar 25 receitas mock
    for i in range(25):
        medico_id = random.choice(medico_ids)
        paciente_id = random.choice(paciente_ids)
        diagnostico = random.choice(diagnosticos)
        status = random.choice(status_opcoes)
        
        # Data de emissão (últimos 60 dias)
        dias_atras = random.randint(0, 60)
        data_emissao = datetime.now() - timedelta(days=dias_atras)
        
        # Data de validade (30 dias após emissão)
        validade_dias = random.randint(15, 45)
        data_validade = data_emissao + timedelta(days=validade_dias)
        
        # Observações opcionais
        observacoes_gerais = None
        if random.random() < 0.3:  # 30% das receitas têm observações
            observacoes_gerais = random.choice([
                'Paciente alérgico a dipirona',
                'Tomar com bastante água',
                'Evitar exposição ao sol',
                'Retornar em 15 dias',
                'Monitorar pressão arterial'
            ])
        
        # Inserir receita
        cursor = conn.execute(
            '''INSERT INTO Receita 
               (id_medico, id_paciente, data_emissao, data_validade, diagnostico, observacoes, status) 
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (medico_id, paciente_id, data_emissao.strftime('%Y-%m-%d %H:%M:%S'), 
             data_validade.strftime('%Y-%m-%d'), diagnostico, observacoes_gerais, status)
        )
        
        receita_id = cursor.lastrowid
        receita_ids.append(receita_id)
        
        # Inserir 1-4 medicamentos por receita
        num_medicamentos = random.randint(1, 4)
        medicamentos_selecionados = random.sample(medicamento_ids, num_medicamentos)
        
        for medicamento_id in medicamentos_selecionados:
            dosagem = random.choice(dosagens)
            quantidade = random.randint(1, 3)
            posologia = random.choice(posologias)
            
            # Observações específicas do medicamento (opcional)
            observacoes_med = None
            if random.random() < 0.2:  # 20% dos medicamentos têm observações
                observacoes_med = random.choice([
                    'Tomar longe das refeições',
                    'Não partir ou mastigar',
                    'Pode causar sonolência',
                    'Tomar com alimentos',
                    'Interromper se houver efeitos colaterais'
                ])
            
            conn.execute(
                '''INSERT INTO ReceitaMedicamento 
                   (id_receita, id_medicamento, dosagem, quantidade, posologia, observacoes) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (receita_id, medicamento_id, dosagem, quantidade, posologia, observacoes_med)
            )
    
    conn.commit()
    conn.close()
    
    print(f"Receitas inseridas: {len(receita_ids)} (IDs: {receita_ids[:5]}...)")
    return receita_ids

def generate_login_credentials():
    """Gerar arquivo com credenciais de login para teste"""
    credentials = {
        "admin": {
            "email": "admin@sistema.com",
            "senha": "admin123",
            "tipo": "admin",
            "descricao": "Administrador do sistema - acesso total"
        },
        "medicos": [
            {
                "email": "joao.silva@clinica.com",
                "senha": "medico123",
                "nome": "Dr. João Silva",
                "especialidade": "Cardiologia",
                "crm": "CRM-SP 123456"
            },
            {
                "email": "maria.santos@hospital.com",
                "senha": "medico123",
                "nome": "Dra. Maria Santos",
                "especialidade": "Clínica Geral",
                "crm": "CRM-RJ 789012"
            },
            {
                "email": "carlos.oliveira@clinica.com",
                "senha": "medico123",
                "nome": "Dr. Carlos Oliveira",
                "especialidade": "Endocrinologia",
                "crm": "CRM-MG 345678"
            }
        ],
        "pacientes": [
            {
                "email": "jose.silva@email.com",
                "senha": "paciente123",
                "nome": "José da Silva",
                "cpf": "123.456.789-01"
            },
            {
                "email": "maria.oliveira@email.com",
                "senha": "paciente123",
                "nome": "Maria Oliveira",
                "cpf": "987.654.321-09"
            },
            {
                "email": "carlos.santos@email.com",
                "senha": "paciente123",
                "nome": "Carlos Santos",
                "cpf": "456.789.123-45"
            }
        ]
    }
    
    with open('credenciais_teste.json', 'w', encoding='utf-8') as f:
        json.dump(credentials, f, indent=2, ensure_ascii=False)
    
    print("\nArquivo 'credenciais_teste.json' criado com as credenciais de login!")

def main():
    """Função principal para executar a geração de dados mock"""
    print("=== Gerador de Dados Mock - Sistema de Receitas Médicas ===\n")
    
    print("1. Limpando banco de dados...")
    clear_database()
    
    print("\n2. Inserindo usuários...")
    admin_id, medico_ids, paciente_ids = insert_mock_users()
    
    print("\n3. Inserindo medicamentos...")
    medicamento_ids = insert_mock_medicamentos()
    
    print("\n4. Inserindo farmácias...")
    farmacia_ids = insert_mock_farmacias()
    
    print("\n5. Inserindo receitas...")
    receita_ids = insert_mock_receitas(medico_ids, paciente_ids, medicamento_ids)
    
    print("\n6. Gerando credenciais de teste...")
    generate_login_credentials()
    
    print(f"\n=== RESUMO ===")
    print(f"✅ Dados mock inseridos com sucesso!")
    print(f"📊 Total de registros criados:")
    print(f"   - Usuários: {1 + len(medico_ids) + len(paciente_ids)} (1 admin, {len(medico_ids)} médicos, {len(paciente_ids)} pacientes)")
    print(f"   - Medicamentos: {len(medicamento_ids)}")
    print(f"   - Farmácias: {len(farmacia_ids)}")
    print(f"   - Receitas: {len(receita_ids)}")
    print(f"\n🔑 Credenciais salvas em 'credenciais_teste.json'")
    print(f"\n🚀 O sistema está pronto para testes!")

if __name__ == '__main__':
    main()
