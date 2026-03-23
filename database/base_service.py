import psycopg2
import psycopg2.extras
from database.conexao import get_connection

def buscar_enderecos_bases():
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM ponto_base")
        dados = cursor.fetchall()
        cursor.close()
        conn.close()
        return dados
    except psycopg2.Error as err:
        print(f"Erro ao listar pontos base: {err}")
        return []

def excluir_ponto_base(rua, numero, cep):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "DELETE FROM ponto_base WHERE rua = %s AND numero = %s AND cep = %s"
        valores = (rua, numero, cep)
        cursor.execute(sql, valores)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except psycopg2.Error as err:
        print(f"Erro ao excluir ponto base: {err}")
        return False

def cadastrar_ponto_base(rua, numero, cidade, veiculo_id, cep, nome_base, latitude, longitude):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO ponto_base (rua, numero, cidade, veiculo_id, cep, nome_da_base, latitude, longitude) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        valores = (rua, numero, cidade, veiculo_id, cep, nome_base, latitude, longitude)
        cursor.execute(sql, valores)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except psycopg2.Error as err:
        print(f"Erro ao cadastrar ponto base: {err}")
        return False

def buscar_ponto_base_por_veiculo(veiculo_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM ponto_base WHERE veiculo_id = %s", (veiculo_id,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        return resultado
    except psycopg2.Error as err:
        print(f"Erro ao buscar ponto base por veículo: {err}")
        return None
