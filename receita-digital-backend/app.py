from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import jwt
from datetime import datetime, timedelta
from functools import wraps
import os
from notifications import NotificationManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'  # Mude para uma chave mais segura em produção
CORS(app)

# Configuração do banco de dados
DATABASE = 'database.db'

notification_manager = NotificationManager()

def init_db():
    """Inicializa o banco de dados com as tabelas necessárias"""
    with sqlite3.connect(DATABASE) as conn:
        with open('sqlite_backend_script.sql', 'r', encoding='utf-8') as f:
            conn.executescript(f.read())

def get_db():
    """Conecta ao banco de dados"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Decorator para verificar token JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token é obrigatório'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
            
            # Verificar se o usuário ainda existe
            conn = get_db()
            user = conn.execute(
                'SELECT * FROM Usuario WHERE id_usuario = ?', 
                (current_user_id,)
            ).fetchone()
            conn.close()
            
            if not user:
                return jsonify({'message': 'Token inválido'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido'}), 401
            
        return f(current_user_id, *args, **kwargs)
    
    return decorated

# ROTAS DE AUTENTICAÇÃO

@app.route('/api/register', methods=['POST'])
def register():
    """Cadastro de novos usuários"""
    try:
        data = request.get_json()
        
        # Validação dos dados obrigatórios
        required_fields = ['nome', 'email', 'senha', 'tipo']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Campo {field} é obrigatório'}), 400
        
        # Validar tipo de usuário
        if data['tipo'] not in ['paciente', 'medico', 'admin']:
            return jsonify({'message': 'Tipo de usuário inválido'}), 400
        
        conn = get_db()
        
        # Verificar se email já existe
        existing_user = conn.execute(
            'SELECT id_usuario FROM Usuario WHERE email = ?', 
            (data['email'],)
        ).fetchone()
        
        if existing_user:
            conn.close()
            return jsonify({'message': 'Email já cadastrado'}), 409
        
        # Hash da senha
        hashed_password = generate_password_hash(data['senha'])
        
        # Inserir usuário
        cursor = conn.execute(
            'INSERT INTO Usuario (nome, email, senha, tipo) VALUES (?, ?, ?, ?)',
            (data['nome'], data['email'], hashed_password, data['tipo'])
        )
        user_id = cursor.lastrowid
        
        # Inserir dados específicos baseado no tipo
        if data['tipo'] == 'paciente':
            conn.execute(
                'INSERT INTO Paciente (id_paciente, cpf, telefone, endereco) VALUES (?, ?, ?, ?)',
                (user_id, data.get('cpf'), data.get('telefone'), data.get('endereco'))
            )
        elif data['tipo'] == 'medico':
            if not data.get('crm') or not data.get('especialidade'):
                conn.close()
                return jsonify({'message': 'CRM e especialidade são obrigatórios para médicos'}), 400
            
            conn.execute(
                'INSERT INTO Medico (id_medico, crm, especialidade) VALUES (?, ?, ?)',
                (user_id, data['crm'], data['especialidade'])
            )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Usuário cadastrado com sucesso',
            'user_id': user_id
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Login de usuários"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('senha'):
            return jsonify({'message': 'Email e senha são obrigatórios'}), 400
        
        conn = get_db()
        user = conn.execute(
            'SELECT * FROM Usuario WHERE email = ?', 
            (data['email'],)
        ).fetchone()
        conn.close()
        
        if not user or not check_password_hash(user['senha'], data['senha']):
            return jsonify({'message': 'Credenciais inválidas'}), 401
        
        # Gerar token JWT
        token = jwt.encode({
            'user_id': user['id_usuario'],
            'email': user['email'],
            'tipo': user['tipo'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'token': token,
            'user': {
                'id': user['id_usuario'],
                'nome': user['nome'],
                'email': user['email'],
                'tipo': user['tipo']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/profile', methods=['GET'])
@token_required
def get_profile(current_user_id):
    """Obter perfil do usuário logado"""
    try:
        conn = get_db()
        
        # Buscar dados do usuário
        user = conn.execute(
            'SELECT id_usuario, nome, email, tipo FROM Usuario WHERE id_usuario = ?',
            (current_user_id,)
        ).fetchone()
        
        if not user:
            conn.close()
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        profile_data = dict(user)
        
        # Buscar dados específicos baseado no tipo
        if user['tipo'] == 'paciente':
            paciente = conn.execute(
                'SELECT cpf, telefone, endereco FROM Paciente WHERE id_paciente = ?',
                (current_user_id,)
            ).fetchone()
            if paciente:
                profile_data.update(dict(paciente))
        
        elif user['tipo'] == 'medico':
            medico = conn.execute(
                'SELECT crm, especialidade FROM Medico WHERE id_medico = ?',
                (current_user_id,)
            ).fetchone()
            if medico:
                profile_data.update(dict(medico))
        
        conn.close()
        return jsonify(profile_data), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500

# ROTAS DE CRUD

@app.route('/api/usuarios', methods=['GET'])
@token_required
def get_usuarios(current_user_id):
    """Listar todos os usuários (apenas admins)"""
    try:
        conn = get_db()
        
        # Verificar se é admin
        current_user = conn.execute(
            'SELECT tipo FROM Usuario WHERE id_usuario = ?',
            (current_user_id,)
        ).fetchone()
        
        if current_user['tipo'] != 'admin':
            conn.close()
            return jsonify({'message': 'Acesso negado'}), 403
        
        usuarios = conn.execute(
            'SELECT id_usuario, nome, email, tipo FROM Usuario ORDER BY nome'
        ).fetchall()
        
        conn.close()
        
        return jsonify([dict(user) for user in usuarios]), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/medicamentos', methods=['GET'])
@token_required
def get_medicamentos(current_user_id):
    """Listar medicamentos"""
    try:
        conn = get_db()
        medicamentos = conn.execute(
            'SELECT * FROM Medicamento ORDER BY nome'
        ).fetchall()
        conn.close()
        
        return jsonify([dict(med) for med in medicamentos]), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/medicamentos', methods=['POST'])
@token_required
def create_medicamento(current_user_id):
    """Criar novo medicamento"""
    try:
        data = request.get_json()
        
        required_fields = ['nome', 'principio_ativo', 'fabricante']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Campo {field} é obrigatório'}), 400
        
        conn = get_db()
        cursor = conn.execute(
            '''INSERT INTO Medicamento 
               (nome, principio_ativo, fabricante, codigo_barras, prescricao_obrigatoria) 
               VALUES (?, ?, ?, ?, ?)''',
            (data['nome'], data['principio_ativo'], data['fabricante'], 
             data.get('codigo_barras'), data.get('prescricao_obrigatoria', 0))
        )
        
        medicamento_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Medicamento criado com sucesso',
            'id': medicamento_id
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/farmacias', methods=['GET'])
@token_required
def get_farmacias(current_user_id):
    """Listar farmácias"""
    try:
        conn = get_db()
        farmacias = conn.execute(
            'SELECT * FROM Farmacia ORDER BY nome_fantasia'
        ).fetchall()
        conn.close()
        
        return jsonify([dict(farm) for farm in farmacias]), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/farmacias', methods=['POST'])
@token_required
def create_farmacia(current_user_id):
    """Criar nova farmácia"""
    try:
        data = request.get_json()
        
        # Campos obrigatórios
        required_fields = ['cnpj', 'nome_fantasia', 'endereco']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Campo {field} é obrigatório'}), 400
        
        # Validação de latitude e longitude (opcional, mas se fornecido deve ser válido)
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if latitude is not None:
            try:
                latitude = float(latitude)
                if not (-90 <= latitude <= 90):
                    return jsonify({'message': 'Latitude deve estar entre -90 e 90'}), 400
            except (ValueError, TypeError):
                return jsonify({'message': 'Latitude deve ser um número válido'}), 400
        
        if longitude is not None:
            try:
                longitude = float(longitude)
                if not (-180 <= longitude <= 180):
                    return jsonify({'message': 'Longitude deve estar entre -180 e 180'}), 400
            except (ValueError, TypeError):
                return jsonify({'message': 'Longitude deve ser um número válido'}), 400
        
        # Validação: se uma coordenada for fornecida, ambas devem ser fornecidas
        if (latitude is not None and longitude is None) or (latitude is None and longitude is not None):
            return jsonify({'message': 'Latitude e longitude devem ser fornecidas juntas'}), 400
        
        conn = get_db()
        cursor = conn.execute(
            '''INSERT INTO Farmacia 
               (cnpj, nome_fantasia, endereco, telefone, responsavel_tecnico, latitude, longitude) 
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (data['cnpj'], data['nome_fantasia'], data['endereco'],
             data.get('telefone'), data.get('responsavel_tecnico'), 
             latitude, longitude)
        )
        
        farmacia_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        response_data = {
            'message': 'Farmácia criada com sucesso',
            'id': farmacia_id
        }
        
        # Incluir coordenadas na resposta se foram fornecidas
        if latitude is not None and longitude is not None:
            response_data['coordenadas'] = {
                'latitude': latitude,
                'longitude': longitude
            }
        
        return jsonify(response_data), 201
        
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/receitas', methods=['POST'])
@token_required
def create_receita(current_user_id):
    """Criar nova receita (apenas médicos)"""
    try:
        data = request.get_json()
        
        conn = get_db()
        
        # Verificar se o usuário atual é médico
        current_user = conn.execute(
            'SELECT tipo FROM Usuario WHERE id_usuario = ?',
            (current_user_id,)
        ).fetchone()
        
        if current_user['tipo'] != 'medico':
            conn.close()
            return jsonify({'message': 'Apenas médicos podem criar receitas'}), 403
        
        # Validação dos dados obrigatórios
        required_fields = ['id_paciente', 'medicamentos', 'diagnostico']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Campo {field} é obrigatório'}), 400
        
        # Validar se paciente existe
        paciente = conn.execute(
            'SELECT id_paciente FROM Paciente WHERE id_paciente = ?',
            (data['id_paciente'],)
        ).fetchone()
        
        if not paciente:
            conn.close()
            return jsonify({'message': 'Paciente não encontrado'}), 404
        
        # Validar medicamentos
        medicamentos = data['medicamentos']
        if not isinstance(medicamentos, list) or len(medicamentos) == 0:
            conn.close()
            return jsonify({'message': 'Deve haver pelo menos um medicamento na receita'}), 400
        
        # Validar cada medicamento
        for i, med in enumerate(medicamentos):
            required_med_fields = ['id_medicamento', 'dosagem', 'quantidade', 'posologia']
            for field in required_med_fields:
                if not med.get(field):
                    conn.close()
                    return jsonify({'message': f'Campo {field} é obrigatório no medicamento {i+1}'}), 400
            
            # Verificar se medicamento existe
            medicamento_exists = conn.execute(
                'SELECT id_medicamento FROM Medicamento WHERE id_medicamento = ?',
                (med['id_medicamento'],)
            ).fetchone()
            
            if not medicamento_exists:
                conn.close()
                return jsonify({'message': f'Medicamento {med["id_medicamento"]} não encontrado'}), 404
        
        # Inserir receita
        validade_dias = data.get('validade_dias', 30)  # Padrão 30 dias
        data_emissao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data_validade = (datetime.now() + timedelta(days=validade_dias)).strftime('%Y-%m-%d')
        
        cursor = conn.execute(
            '''INSERT INTO Receita 
               (id_medico, id_paciente, data_emissao, data_validade, diagnostico, observacoes, status) 
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (current_user_id, data['id_paciente'], data_emissao, data_validade, 
             data['diagnostico'], data.get('observacoes_gerais'), 'ativa')
        )
        
        receita_id = cursor.lastrowid
        
        # Inserir medicamentos da receita
        for medicamento in medicamentos:
            conn.execute(
                '''INSERT INTO ReceitaMedicamento 
                   (id_receita, id_medicamento, dosagem, quantidade, posologia, observacoes) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (receita_id, medicamento['id_medicamento'], medicamento['dosagem'],
                 medicamento['quantidade'], medicamento['posologia'], 
                 medicamento.get('observacoes'))
            )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Receita criada com sucesso',
            'id_receita': receita_id,
            'data_emissao': data_emissao,
            'data_validade': data_validade,
            'total_medicamentos': len(medicamentos)
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500


@app.route('/api/receitas/<int:receita_id>', methods=['GET'])
@token_required
def get_receita_detalhes(current_user_id, receita_id):
    """Obter detalhes de uma receita específica"""
    try:
        conn = get_db()
        
        # Verificar tipo do usuário
        user = conn.execute(
            'SELECT tipo FROM Usuario WHERE id_usuario = ?',
            (current_user_id,)
        ).fetchone()
        
        # Montar query baseada no tipo de usuário
        if user['tipo'] == 'paciente':
            # Paciente só vê suas próprias receitas
            receita = conn.execute(
                '''SELECT r.*, um.nome as nome_medico, m.especialidade, m.crm
                   FROM Receita r 
                   JOIN Medico m ON r.id_medico = m.id_medico
                   JOIN Usuario um ON m.id_medico = um.id_usuario
                   WHERE r.id_receita = ? AND r.id_paciente = ?''',
                (receita_id, current_user_id)
            ).fetchone()
        elif user['tipo'] == 'medico':
            # Médico só vê receitas que prescreveu
            receita = conn.execute(
                '''SELECT r.*, up.nome as nome_paciente
                   FROM Receita r 
                   JOIN Paciente p ON r.id_paciente = p.id_paciente
                   JOIN Usuario up ON p.id_paciente = up.id_usuario
                   WHERE r.id_receita = ? AND r.id_medico = ?''',
                (receita_id, current_user_id)
            ).fetchone()
        else:  # admin
            # Admin vê todas as receitas
            receita = conn.execute(
                '''SELECT r.*, up.nome as nome_paciente, um.nome as nome_medico, m.especialidade, m.crm
                   FROM Receita r 
                   JOIN Paciente p ON r.id_paciente = p.id_paciente
                   JOIN Usuario up ON p.id_paciente = up.id_usuario
                   JOIN Medico m ON r.id_medico = m.id_medico
                   JOIN Usuario um ON m.id_medico = um.id_usuario
                   WHERE r.id_receita = ?''',
                (receita_id,)
            ).fetchone()
        
        if not receita:
            conn.close()
            return jsonify({'message': 'Receita não encontrada'}), 404
        
        # Buscar medicamentos da receita
        medicamentos = conn.execute(
            '''SELECT rm.*, med.nome, med.principio_ativo, med.fabricante
               FROM ReceitaMedicamento rm
               JOIN Medicamento med ON rm.id_medicamento = med.id_medicamento
               WHERE rm.id_receita = ?''',
            (receita_id,)
        ).fetchall()
        
        conn.close()
        
        # Montar resposta
        receita_dict = dict(receita)
        receita_dict['medicamentos'] = [dict(med) for med in medicamentos]
        
        return jsonify(receita_dict), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500


@app.route('/api/receitas/<int:receita_id>/status', methods=['PUT'])
@token_required
def update_receita_status(current_user_id, receita_id):
    """Atualizar status da receita (usar/cancelar)"""
    try:
        data = request.get_json()
        
        if not data.get('status'):
            return jsonify({'message': 'Campo status é obrigatório'}), 400
        
        status_validos = ['ativa', 'utilizada', 'cancelada', 'expirada']
        if data['status'] not in status_validos:
            return jsonify({'message': f'Status deve ser um de: {", ".join(status_validos)}'}), 400
        
        conn = get_db()
        
        # Verificar se a receita existe e se o usuário tem permissão
        user = conn.execute(
            'SELECT tipo FROM Usuario WHERE id_usuario = ?',
            (current_user_id,)
        ).fetchone()
        
        if user['tipo'] == 'medico':
            # Médico só pode alterar suas próprias receitas
            receita = conn.execute(
                'SELECT id_receita FROM Receita WHERE id_receita = ? AND id_medico = ?',
                (receita_id, current_user_id)
            ).fetchone()
        elif user['tipo'] == 'admin':
            # Admin pode alterar qualquer receita
            receita = conn.execute(
                'SELECT id_receita FROM Receita WHERE id_receita = ?',
                (receita_id,)
            ).fetchone()
        else:
            # Pacientes não podem alterar status
            conn.close()
            return jsonify({'message': 'Pacientes não podem alterar status de receitas'}), 403
        
        if not receita:
            conn.close()
            return jsonify({'message': 'Receita não encontrada ou sem permissão'}), 404
        
        # Atualizar status
        conn.execute(
            'UPDATE Receita SET status = ? WHERE id_receita = ?',
            (data['status'], receita_id)
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Status da receita atualizado com sucesso',
            'novo_status': data['status']
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500   

# Adicione estas rotas ao seu arquivo app.py

@app.route('/api/receitas', methods=['GET'])
@token_required
def get_receitas_usuario(current_user_id):
    """Listar receitas baseado no tipo de usuário"""
    try:
        conn = get_db()
        
        # Verificar tipo do usuário
        user = conn.execute(
            'SELECT tipo FROM Usuario WHERE id_usuario = ?',
            (current_user_id,)
        ).fetchone()
        
        if not user:
            conn.close()
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        # Buscar receitas baseado no tipo de usuário
        if user['tipo'] == 'paciente':
            # Paciente vê apenas suas receitas
            receitas = conn.execute(
                '''SELECT r.*, 
                          um.nome as nome_medico, 
                          m.especialidade, 
                          m.crm,
                          up.nome as nome_paciente
                   FROM Receita r 
                   JOIN Medico m ON r.id_medico = m.id_medico
                   JOIN Usuario um ON m.id_medico = um.id_usuario
                   JOIN Paciente p ON r.id_paciente = p.id_paciente
                   JOIN Usuario up ON p.id_paciente = up.id_usuario
                   WHERE r.id_paciente = ?
                   ORDER BY r.data_emissao DESC''',
                (current_user_id,)
            ).fetchall()
            
        elif user['tipo'] == 'medico':
            # Médico vê receitas que prescreveu
            receitas = conn.execute(
                '''SELECT r.*, 
                          um.nome as nome_medico, 
                          m.especialidade, 
                          m.crm,
                          up.nome as nome_paciente
                   FROM Receita r 
                   JOIN Medico m ON r.id_medico = m.id_medico
                   JOIN Usuario um ON m.id_medico = um.id_usuario
                   JOIN Paciente p ON r.id_paciente = p.id_paciente
                   JOIN Usuario up ON p.id_paciente = up.id_usuario
                   WHERE r.id_medico = ?
                   ORDER BY r.data_emissao DESC''',
                (current_user_id,)
            ).fetchall()
            
        else:  # admin
            # Admin vê todas as receitas
            receitas = conn.execute(
                '''SELECT r.*, 
                          um.nome as nome_medico, 
                          m.especialidade, 
                          m.crm,
                          up.nome as nome_paciente
                   FROM Receita r 
                   JOIN Medico m ON r.id_medico = m.id_medico
                   JOIN Usuario um ON m.id_medico = um.id_usuario
                   JOIN Paciente p ON r.id_paciente = p.id_paciente
                   JOIN Usuario up ON p.id_paciente = up.id_usuario
                   ORDER BY r.data_emissao DESC'''
            ).fetchall()
        
        # Para cada receita, buscar os medicamentos
        receitas_completas = []
        for receita in receitas:
            receita_dict = dict(receita)
            
            # Buscar medicamentos da receita
            medicamentos = conn.execute(
                '''SELECT rm.*, med.nome, med.principio_ativo, med.fabricante
                   FROM ReceitaMedicamento rm
                   JOIN Medicamento med ON rm.id_medicamento = med.id_medicamento
                   WHERE rm.id_receita = ?''',
                (receita['id_receita'],)
            ).fetchall()
            
            receita_dict['medicamentos'] = [dict(med) for med in medicamentos]
            receitas_completas.append(receita_dict)
        
        conn.close()
        return jsonify(receitas_completas), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500


@app.route('/api/receitas/paciente/<int:paciente_id>', methods=['GET'])
@token_required
def get_receitas_paciente(current_user_id, paciente_id):
    """Buscar receitas de um paciente específico (apenas médicos e admins)"""
    try:
        conn = get_db()
        
        # Verificar permissões
        current_user = conn.execute(
            'SELECT tipo FROM Usuario WHERE id_usuario = ?',
            (current_user_id,)
        ).fetchone()
        
        if current_user['tipo'] not in ['medico', 'admin']:
            conn.close()
            return jsonify({'message': 'Acesso negado'}), 403
        
        # Buscar receitas do paciente
        receitas = conn.execute(
            '''SELECT r.*, 
                      um.nome as nome_medico, 
                      m.especialidade, 
                      m.crm,
                      up.nome as nome_paciente
               FROM Receita r 
               JOIN Medico m ON r.id_medico = m.id_medico
               JOIN Usuario um ON m.id_medico = um.id_usuario
               JOIN Paciente p ON r.id_paciente = p.id_paciente
               JOIN Usuario up ON p.id_paciente = up.id_usuario
               WHERE r.id_paciente = ?
               ORDER BY r.data_emissao DESC''',
            (paciente_id,)
        ).fetchall()
        
        # Para cada receita, buscar os medicamentos
        receitas_completas = []
        for receita in receitas:
            receita_dict = dict(receita)
            
            # Buscar medicamentos da receita
            medicamentos = conn.execute(
                '''SELECT rm.*, med.nome, med.principio_ativo, med.fabricante
                   FROM ReceitaMedicamento rm
                   JOIN Medicamento med ON rm.id_medicamento = med.id_medicamento
                   WHERE rm.id_receita = ?''',
                (receita['id_receita'],)
            ).fetchall()
            
            receita_dict['medicamentos'] = [dict(med) for med in medicamentos]
            receitas_completas.append(receita_dict)
        
        conn.close()
        return jsonify(receitas_completas), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500


@app.route('/api/receitas/medico/<int:medico_id>', methods=['GET'])
@token_required
def get_receitas_medico(current_user_id, medico_id):
    """Buscar receitas de um médico específico (apenas admins)"""
    try:
        conn = get_db()
        
        # Verificar se é admin
        current_user = conn.execute(
            'SELECT tipo FROM Usuario WHERE id_usuario = ?',
            (current_user_id,)
        ).fetchone()
        
        if current_user['tipo'] != 'admin':
            conn.close()
            return jsonify({'message': 'Acesso negado'}), 403
        
        # Buscar receitas do médico
        receitas = conn.execute(
            '''SELECT r.*, 
                      um.nome as nome_medico, 
                      m.especialidade, 
                      m.crm,
                      up.nome as nome_paciente
               FROM Receita r 
               JOIN Medico m ON r.id_medico = m.id_medico
               JOIN Usuario um ON m.id_medico = um.id_usuario
               JOIN Paciente p ON r.id_paciente = p.id_paciente
               JOIN Usuario up ON p.id_paciente = up.id_usuario
               WHERE r.id_medico = ?
               ORDER BY r.data_emissao DESC''',
            (medico_id,)
        ).fetchall()
        
        # Para cada receita, buscar os medicamentos
        receitas_completas = []
        for receita in receitas:
            receita_dict = dict(receita)
            
            # Buscar medicamentos da receita
            medicamentos = conn.execute(
                '''SELECT rm.*, med.nome, med.principio_ativo, med.fabricante
                   FROM ReceitaMedicamento rm
                   JOIN Medicamento med ON rm.id_medicamento = med.id_medicamento
                   WHERE rm.id_receita = ?''',
                (receita['id_receita'],)
            ).fetchall()
            
            receita_dict['medicamentos'] = [dict(med) for med in medicamentos]
            receitas_completas.append(receita_dict)
        
        conn.close()
        return jsonify(receitas_completas), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500


@app.route('/api/receitas/stats', methods=['GET'])
@token_required
def get_receitas_stats(current_user_id):
    """Estatísticas de receitas baseado no tipo de usuário"""
    try:
        conn = get_db()
        
        # Verificar tipo do usuário
        user = conn.execute(
            'SELECT tipo FROM Usuario WHERE id_usuario = ?',
            (current_user_id,)
        ).fetchone()
        
        stats = {}
        
        if user['tipo'] == 'paciente':
            # Estatísticas do paciente
            total = conn.execute(
                'SELECT COUNT(*) as total FROM Receita WHERE id_paciente = ?',
                (current_user_id,)
            ).fetchone()
            
            ativas = conn.execute(
                'SELECT COUNT(*) as ativas FROM Receita WHERE id_paciente = ? AND status = ?',
                (current_user_id, 'ativa')
            ).fetchone()
            
            utilizadas = conn.execute(
                'SELECT COUNT(*) as utilizadas FROM Receita WHERE id_paciente = ? AND status = ?',
                (current_user_id, 'utilizada')
            ).fetchone()
            
            stats = {
                'total_receitas': total['total'],
                'receitas_ativas': ativas['ativas'],
                'receitas_utilizadas': utilizadas['utilizadas']
            }
            
        elif user['tipo'] == 'medico':
            # Estatísticas do médico
            total = conn.execute(
                'SELECT COUNT(*) as total FROM Receita WHERE id_medico = ?',
                (current_user_id,)
            ).fetchone()
            
            ativas = conn.execute(
                'SELECT COUNT(*) as ativas FROM Receita WHERE id_medico = ? AND status = ?',
                (current_user_id, 'ativa')
            ).fetchone()
            
            pacientes_atendidos = conn.execute(
                'SELECT COUNT(DISTINCT id_paciente) as pacientes FROM Receita WHERE id_medico = ?',
                (current_user_id,)
            ).fetchone()
            
            stats = {
                'total_receitas_prescritas': total['total'],
                'receitas_ativas': ativas['ativas'],
                'pacientes_atendidos': pacientes_atendidos['pacientes']
            }
            
        else:  # admin
            # Estatísticas gerais
            total_receitas = conn.execute('SELECT COUNT(*) as total FROM Receita').fetchone()
            total_usuarios = conn.execute('SELECT COUNT(*) as total FROM Usuario').fetchone()
            total_medicamentos = conn.execute('SELECT COUNT(*) as total FROM Medicamento').fetchone()
            total_farmacias = conn.execute('SELECT COUNT(*) as total FROM Farmacia').fetchone()
            
            stats = {
                'total_receitas': total_receitas['total'],
                'total_usuarios': total_usuarios['total'],
                'total_medicamentos': total_medicamentos['total'],
                'total_farmacias': total_farmacias['total']
            }
        
        conn.close()
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500


# Atualizar a rota existente de detalhes da receita para incluir número da receita
@app.route('/api/receitas/<int:receita_id>', methods=['GET'])
@token_required
def get_receita_detalhes_updated(current_user_id, receita_id):
    """Obter detalhes de uma receita específica com número formatado"""
    try:
        conn = get_db()
        
        # Verificar tipo do usuário
        user = conn.execute(
            'SELECT tipo FROM Usuario WHERE id_usuario = ?',
            (current_user_id,)
        ).fetchone()
        
        # Montar query baseada no tipo de usuário
        if user['tipo'] == 'paciente':
            # Paciente só vê suas próprias receitas
            receita = conn.execute(
                '''SELECT r.*, um.nome as nome_medico, m.especialidade, m.crm
                   FROM Receita r 
                   JOIN Medico m ON r.id_medico = m.id_medico
                   JOIN Usuario um ON m.id_medico = um.id_usuario
                   WHERE r.id_receita = ? AND r.id_paciente = ?''',
                (receita_id, current_user_id)
            ).fetchone()
        elif user['tipo'] == 'medico':
            # Médico só vê receitas que prescreveu
            receita = conn.execute(
                '''SELECT r.*, up.nome as nome_paciente
                   FROM Receita r 
                   JOIN Paciente p ON r.id_paciente = p.id_paciente
                   JOIN Usuario up ON p.id_paciente = up.id_usuario
                   WHERE r.id_receita = ? AND r.id_medico = ?''',
                (receita_id, current_user_id)
            ).fetchone()
        else:  # admin
            # Admin vê todas as receitas
            receita = conn.execute(
                '''SELECT r.*, up.nome as nome_paciente, um.nome as nome_medico, m.especialidade, m.crm
                   FROM Receita r 
                   JOIN Paciente p ON r.id_paciente = p.id_paciente
                   JOIN Usuario up ON p.id_paciente = up.id_usuario
                   JOIN Medico m ON r.id_medico = m.id_medico
                   JOIN Usuario um ON m.id_medico = um.id_usuario
                   WHERE r.id_receita = ?''',
                (receita_id,)
            ).fetchone()
        
        if not receita:
            conn.close()
            return jsonify({'message': 'Receita não encontrada'}), 404
        
        # Buscar medicamentos da receita
        medicamentos = conn.execute(
            '''SELECT rm.*, med.nome, med.principio_ativo, med.fabricante
               FROM ReceitaMedicamento rm
               JOIN Medicamento med ON rm.id_medicamento = med.id_medicamento
               WHERE rm.id_receita = ?''',
            (receita_id,)
        ).fetchall()
        
        conn.close()
        
        # Montar resposta
        receita_dict = dict(receita)
        receita_dict['medicamentos'] = [dict(med) for med in medicamentos]
        
        # Adicionar número formatado da receita
        receita_dict['numero'] = f"#{receita_dict['id_receita']:08d}"
        
        return jsonify(receita_dict), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500        

# ROTA DE SAÚDE
@app.route('/api/health', methods=['GET'])
def health_check():
    """Verificar se a API está funcionando"""
    return jsonify({'status': 'API funcionando!', 'timestamp': datetime.now().isoformat()}), 200

@app.route('/api/notifications/register', methods=['POST'])
def register_notification_token():
    data = request.get_json()
    token = data.get('token')
    platform = data.get('platform')
    
    if not token:
        return jsonify({'error': 'Token não fornecido'}), 400
    
    # Aqui você pode salvar o token no banco de dados
    # Por exemplo:
    # cursor = get_db().cursor()
    # cursor.execute('INSERT INTO notification_tokens (token, platform) VALUES (?, ?)',
    #                (token, platform))
    # get_db().commit()
    
    return jsonify({'message': 'Token registrado com sucesso'}), 200

@app.route('/api/notifications/send', methods=['POST'])
def send_notification():
    data = request.get_json()
    token = data.get('token')
    title = data.get('title')
    body = data.get('body')
    notification_data = data.get('data')
    
    if not all([token, title, body]):
        return jsonify({'error': 'Dados incompletos'}), 400
    
    response = notification_manager.send_push_notification(
        token,
        title,
        body,
        notification_data
    )
    
    if response:
        return jsonify({'message': 'Notificação enviada com sucesso'}), 200
    else:
        return jsonify({'error': 'Falha ao enviar notificação'}), 500

# Inicialização
if __name__ == '__main__':
    # Criar banco de dados se não existir
    if not os.path.exists(DATABASE):
        init_db()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
