import os
import oracledb
from flask import Flask, render_template_string, request, redirect, url_for
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASS')
DB_DSN = os.getenv('DB_DSN')

def get_connection():
    return oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Mestre do Jogo - SQLgard</title>
    <style>
        body { font-family: 'Courier New', monospace; background: #1a1a1a; color: #00ff00; padding: 20px; }
        h1 { border-bottom: 2px solid #ff4500; padding-bottom: 10px; }
        .container { max-width: 900px; margin: auto; }
        .controls { display: flex; gap: 10px; margin-bottom: 20px; }
        table { border-collapse: collapse; width: 100%; background: #222; border: 1px solid #444; }
        th, td { border: 1px solid #444; padding: 12px; text-align: left; }
        th { background: #333; color: #ff4500; }
        .btn { color: white; padding: 15px 25px; border: none; cursor: pointer; font-weight: bold; border-radius: 4px; font-size: 16px; }
        .btn-damage { background: #ff4500; }
        .btn-reset { background: #008cba; }
        .btn:hover { opacity: 0.8; transform: scale(1.02); }
        .status-ATIVO { color: #00ff00; }
        .status-CAÍDO { color: #ff0000; text-decoration: line-through; opacity: 0.6; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚔️ O Despertar do Kernel Ancestral</h1>
        <p>Controle o destino dos heróis de SQLgard.</p>
        
        <div class="controls">
            <form action="/processar" method="post">
                <button type="submit" class="btn btn-damage">🌀 PRÓXIMO TURNO (Dano)</button>
            </form>

            <form action="/resetar" method="post">
                <button type="submit" class="btn btn-reset">💖 RESTAURAR TODOS (Reset)</button>
            </form>
        </div>

        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Herói</th>
                    <th>Classe</th>
                    <th>HP Atual / Max</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {% for heroi in herois %}
                <tr class="status-{{ heroi[5] }}">
                    <td>{{ heroi[0] }}</td>
                    <td><strong>{{ heroi[1] }}</strong></td>
                    <td>{{ heroi[2] }}</td>
                    <td>{{ heroi[3] }} / {{ heroi[4] }}</td>
                    <td>{{ heroi[5] }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_heroi, nome, classe, hp_atual, hp_max, status FROM TB_HEROIS ORDER BY id_heroi")
        herois = cursor.fetchall()
        return render_template_string(HTML_TEMPLATE, herois=herois)
    except Exception as e:
        return f"Erro: {str(e)}"
    finally:
        if conn: conn.close()

@app.route('/processar', methods=['POST'])
def processar():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        plsql_block = """
        DECLARE
            v_dano NUMBER := 15;
        BEGIN
            UPDATE TB_HEROIS 
            SET hp_atual = CASE WHEN (hp_atual - v_dano) < 0 THEN 0 ELSE hp_atual - v_dano END,
                status = CASE WHEN (hp_atual - v_dano) <= 0 THEN 'CAÍDO' ELSE 'ATIVO' END
            WHERE status = 'ATIVO';
            COMMIT;
        END;
        """
        cursor.execute(plsql_block)
        return redirect(url_for('index'))
    except Exception as e:
        return f"Erro ao processar: {str(e)}"
    finally:
        if conn: conn.close()

@app.route('/resetar', methods=['POST'])
def resetar():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE TB_HEROIS SET hp_atual = hp_max, status = 'ATIVO'")
        conn.commit()
        return redirect(url_for('index'))
    except Exception as e:
        return f"Erro ao resetar: {str(e)}"
    finally:
        if conn: conn.close()

if __name__ == '__main__':
    app.run(debug=True)