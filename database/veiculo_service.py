import psycopg2
import psycopg2.extras
from database.conexao import get_connection


def capacidade_disponivel_veiculo(placa):
    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT capacidade_disponivel FROM veiculo WHERE placa = %s", (placa,))
        dado = cursor.fetchone()
        return dado['capacidade_disponivel'] if dado else None
    except psycopg2.Error as err:
        print(f"Erro ao buscar capacidade disponível do veículo: {err}")
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def atualizar_capacidade_veiculo(placa, nova_capacidade):
    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "UPDATE veiculo SET capacidade_disponivel = %s WHERE placa = %s"
        valores = (nova_capacidade, placa)
        cursor.execute(sql, valores)
        conn.commit()
        return True
    except psycopg2.Error as err:
        print(f"Erro ao atualizar capacidade do veículo: {err}")
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def buscar_veiculos():
    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM veiculo")
        dados = cursor.fetchall()
        return dados
    except psycopg2.Error as err:
        print(f"Erro ao listar veículos: {err}")
        return []
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def buscar_veiculo_por_id(veiculo_id):
    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM veiculo WHERE veiculo_id = %s", (veiculo_id,))
        dado = cursor.fetchone()
        return dado
    except psycopg2.Error as err:
        print(f"Erro ao buscar veículo por ID: {err}")
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def buscar_veiculo_por_placa(placa):
    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM veiculo WHERE placa = %s", (placa,))
        dado = cursor.fetchone()
        return dado
    except psycopg2.Error as err:
        print(f"Erro ao buscar veículo por placa: {err}")
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def cadastrar_veiculo(modelo, placa, capacidade, capacidade_disponivel, autonomia):
    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """INSERT INTO veiculo
                 (modelo_caminhao, placa, capacidade_maxima, capacidade_disponivel, autonomia_total)
                 VALUES (%s, %s, %s, %s, %s)"""
        valores = (modelo, placa, capacidade, capacidade_disponivel, autonomia)
        cursor.execute(sql, valores)
        conn.commit()
        return True
    except psycopg2.Error as err:
        print(f"Erro ao cadastrar veículo: {err}")
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def excluir_veiculo(veiculo_id):
    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM rota WHERE veiculo_designado_rota = %s", (veiculo_id,))
        cursor.execute("DELETE FROM veiculo WHERE veiculo_id = %s", (veiculo_id,))
        conn.commit()
        return True
    except psycopg2.Error as err:
        print(f"Erro ao deletar veículo: {err}")
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
