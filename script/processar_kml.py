import geopandas as gpd
import pandas as pd
from lxml import etree
import os

# Caminhos absolutos para evitar erros de diretório
entrada = r"C:\Users\joao.lucas\Desktop\projeto_01\data\entrada.kml" # caminho para pasta do kml
saida = r"C:\Users\joao.lucas\Desktop\projeto_01\results\dados_processados.geojson"   # caminho para o resultado

def extrair_dados_description(description):
    """
    Extrai os dados da tag 'description' removendo HTML e organizando em colunas.
    """
    try:
        # Verifica se a descrição não é nula
        if pd.isna(description):
            return {}

        # Converte a string HTML em um objeto XML
        tree = etree.HTML(description)

        # Extrai todas as linhas da tabela (assumindo que os dados estão dentro de <tr>)
        rows = tree.xpath("//tr")
        dados_extraidos = {}

        for row in rows:
            colunas = row.xpath("./td/text()")  # Pega os textos dentro das <td>
            if len(colunas) == 2:  # Assume que a tabela tem "chave: valor"
                chave = colunas[0].strip().replace(" ", "_").lower()  # Formata a chave
                valor = colunas[1].strip()
                dados_extraidos[chave] = valor

        return dados_extraidos

    except Exception as e:
        print(f"Erro ao processar description: {e}")
        return {}

def processar_kml(arquivo_entrada, arquivo_saida):
    """
    Processa um arquivo KML, extrai dados do campo description e salva um novo arquivo.
    """
    # Verifica se o arquivo existe antes de tentar abrir
    if not os.path.exists(arquivo_entrada):
        print(f"Erro: Arquivo {arquivo_entrada} não encontrado.")
        return

    # Carrega o KML para um GeoDataFrame
    gdf = gpd.read_file(arquivo_entrada, driver='KML')

    # Corrige o nome das colunas para letras minúsculas
    gdf.columns = gdf.columns.str.lower()

    # Exibir as colunas carregadas para verificar se 'description' existe
    print("Colunas disponíveis:", gdf.columns)

    # Verifica se 'description' está presente no arquivo
    if 'description' not in gdf.columns:
        print("Erro: A coluna 'description' não foi encontrada no arquivo KML.")
        return

    # Aplica a função de extração em cada linha do campo 'description'
    dados_extraidos = gdf['description'].apply(extrair_dados_description)

    # Converte os dicionários extraídos em um DataFrame
    df_dados = pd.DataFrame(dados_extraidos.tolist())

    # Concatena o GeoDataFrame original com os novos campos extraídos
    gdf_processado = pd.concat([gdf, df_dados], axis=1)

    # Remove a coluna original 'description' se não for mais necessária
    gdf_processado.drop(columns=['description'], inplace=True)

    # Salva o resultado em um arquivo GeoJSON
    gdf_processado.to_file(arquivo_saida, driver="GeoJSON")

    print(f"Arquivo processado salvo em: {arquivo_saida}")

if __name__ == "__main__":
    processar_kml(entrada, saida)
