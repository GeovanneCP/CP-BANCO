import os
import oracledb
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# Configurações de Conexão
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_DSN = os.getenv('DB_DSN')

def get_connection():
    return oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Mestre do Jogo - SQLgard</title>
    <style>
        body { font-family: 'Courier New', monospace; background: #1a1a1a; color: #00ff00; padding: 20px; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; background: #222; }
        th, td { border: 1px solid #444; padding: 12px; text-align: left; }
        th { background: #333; }
        .btn { background: #ff4500; color: white; padding: 10px 20px; border: none; cursor: pointer; font-weight: bold; }
        .btn:hover { background: #ff6347; }
        .status-ATIVO { color: #00ff00; }
        .status-CAÍDO { color: #ff0000; text-decoration: line-through; }
    </style>
</head>
<body>
    <h1>⚔️ O Despertar do Kernel Ancestral</h1>
    <p>A névoa venenosa se espalha por SQLgard...</p>
    
    <form action="/processar" method="post">
        <button type="submit" class="btn">🌀 PRÓXIMO TURNO (Dano de Névoa)</button>
    </form>

    <table>
        <tr>
            <th>ID</th>
            <th>Herói</th>
            <th>Classe</th>
            <th>HP Atual</th>
            <th>Status</th>
        </tr>
        {% for heroi in herois %}
        <tr class="status-{{ heroi[5] }}">
            <td>{{ heroi[0] }}</td>
            <td>{{ heroi[1] }}</td>
            <td>{{ heroi[2] }}</td>
            <td>{{ heroi[3] }} / {{ heroi[4] }}</td>
            <td>{{ heroi[5] }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route('/')
def index():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_heroi, nome, classe, hp_atual, hp_max, status FROM TB_HEROIS ORDER BY id_heroi")
    herois = cursor.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, herois=herois)

@app.route('/processar', method=['POST'])
def processar():
    conn = get_connection()
    cursor = conn.cursor()

    # Bloco PL/SQL
    plsql_block = """
    DECLARE
        v_dano_nevoa NUMBER := 15; -- Dano fixo por turno
        CURSOR c_herois IS 
            SELECT id_heroi, hp_atual 
            FROM TB_HEROIS 
            WHERE status = 'ATIVO' 
            FOR UPDATE;
    BEGIN
        FOR r_heroi IN c_herois LOOP
            -- Cálculo de dano
            IF (r_heroi.hp_atual - v_dano_nevoa) <= 0 THEN
                UPDATE TB_HEROIS 
                SET hp_atual = 0, 
                    status = 'CAÍDO' 
                WHERE id_heroi = r_heroi.id_heroi;
            ELSE
                UPDATE TB_HEROIS 
                SET hp_atual = hp_atual - v_dano_nevoa 
                WHERE id_heroi = r_heroi.id_heroi;
            END IF;
        END LOOP;
        COMMIT;
    END;
    """
    
    cursor.execute(plsql_block)
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)