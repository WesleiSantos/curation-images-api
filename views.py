from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import glob
import re

app = Flask(__name__)
CORS(app)

def processar_todos_logs():
    """
    Lê todos os logs e retorna a lista COMPLETA de amostras, sem filtrar.
    """
    print("Processando todos os arquivos de log...")
    # Ajuste o caminho se seus arquivos estiverem em um subdiretório
    todos_arquivos = glob.glob('baseline/prediction_log_uni_*.csv') 
    if not todos_arquivos:
        return []

    lista_dfs = []
    for arquivo in todos_arquivos:
        df = pd.read_csv(arquivo)
        match = re.search(r'prediction_log_uni_(\d+_[A-Za-z_]+)_fold', arquivo)
        df['Modelo'] = match.group(1) if match else 'N/A'
        lista_dfs.append(df)
    
    df_completo = pd.concat(lista_dfs, ignore_index=True)
    
    # --- MUDANÇA PRINCIPAL AQUI ---
    # REMOVEMOS O FILTRO para incluir TP, TN, FP, e FN.
    # A variável foi renomeada de df_erros para df_resultados.
    df_resultados = df_completo.copy()
    
    # Cria o caminho relativo para a pasta 'public' do Quasar
    df_resultados['PublicPath'] = df_resultados['ImagePath'].apply(
        lambda x: 'raw-dataset' + x.split('raw-dataset', 1)[1] if 'raw-dataset' in x else None
    )
    
    df_resultados.dropna(subset=['PublicPath'], inplace=True)
    
    return df_resultados.to_dict(orient='records')

@app.route('/api/resultados') # Rota renomeada para refletir que retorna todos os resultados
def get_resultados():
    """Endpoint da API que retorna todos os dados de classificação."""
    dados = processar_todos_logs()
    return jsonify(dados)

if __name__ == '__main__':
    print("Servidor de análise iniciado em http://127.0.0.1:5001")
    app.run(debug=True)