from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import glob
import re
import os

app = Flask(__name__)
CORS(app)

# --- CONFIGURAÇÃO DA AWS S3 ---
# Certifique-se que estes valores correspondem ao seu bucket e região
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'curation-images')
S3_REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')

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
    
    df_resultados = df_completo.copy()
    
    # >>> INÍCIO DA ALTERAÇÃO <<<
    # Esta seção foi modificada para gerar a URL pública do S3

    # 1. Extrai a chave do objeto (ex: raw-dataset/0_Amiloidose/...) do caminho local
    df_resultados['S3ObjectKey'] = df_resultados['ImagePath'].apply(
        lambda x: 'raw-dataset' + x.split('raw-dataset', 1)[1] if 'raw-dataset' in x else None
    )
    
    # 2. Constrói a URL pública completa e a atribui a uma nova coluna 'imageUrl'
    df_resultados['imageUrl'] = df_resultados['S3ObjectKey'].apply(
        lambda key: f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{key}" if key else None
    )
    
    # 3. Remove as colunas intermediárias e desnecessárias do resultado final
    df_resultados.dropna(subset=['imageUrl'], inplace=True)
    df_resultados.drop(columns=['ImagePath', 'PublicPath', 'S3ObjectKey'], errors='ignore', inplace=True)
    
    # >>> FIM DA ALTERAÇÃO <<<
    
    return df_resultados.to_dict(orient='records')

@app.route('/api/resultados')
def get_resultados():
    """Endpoint da API que retorna todos os dados de classificação."""
    dados = processar_todos_logs()
    return jsonify(dados)

if __name__ == '__main__':
    print("Servidor de análise iniciado em http://127.0.0.1:5001")
    app.run(debug=True)