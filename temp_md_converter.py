import json
import sys
import html
from datetime import datetime

def formatar_nome_autor(autor: str) -> str:
    """Formata o nome do autor no padrão ABNT (SOBRENOME, Nome)"""
    partes = autor.split()
    if len(partes) > 1:
        return f"{partes[-1].upper()}, {' '.join(partes[:-1])}"
    return autor

def formatar_referencia_abnt(ref: str) -> str:
    """Formata referências no estilo ABNT básico"""
    if "Acesso em" in ref:
        return ref
    if "http" in ref:
        return f"Disponível em: <{ref}>. Acesso em: [data]."
    return f"{ref}."

try:
    with open('artigos-gerados-exemplo/json/artigo_Meio Ambiente.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Processar data no formato ABNT (dia/mês/ano)
    data_criacao = data.get("data_criacao", "")
    if data_criacao:
        try:
            dt = datetime.strptime(data_criacao.split('T')[0], "%Y-%m-%d")
            data_criacao = dt.strftime("%d/%m/%Y")
        except ValueError:
            data_criacao = ""

    # Cabeçalho ABNT
    md_content = f'# {html.unescape(data.get("titulo", "Artigo")).upper()}\n\n'
    md_content += f'**Autor:** {formatar_nome_autor(html.unescape(data.get("autor", "Artigo Multiagente IA")))}\n\n'
    md_content += f'**Data:** {data_criacao}\n\n'
    md_content += "---\n\n"

    # Processar seções do artigo
    secoes_abnt = {
        "resumo": "RESUMO",
        "introdução": "1 INTRODUÇÃO",
        "desenvolvimento": "2 DESENVOLVIMENTO",
        "conclusão": "3 CONSIDERAÇÕES FINAIS"
    }

    for p in data.get("paragrafos", []):
        titulo = html.unescape(p.get("titulo", "")).lower()
        conteudo = html.unescape(p.get("conteudo", ""))
        
        # Formatar seções especiais
        if titulo in secoes_abnt:
            if titulo == "resumo":
                md_content += f'## {secoes_abnt[titulo]}\n\n{conteudo}\n\n'
                md_content += '**Palavras-chave:** [adicione 3-5 palavras-chave separadas por vírgula].\n\n'
                md_content += "---\n\n"
            else:
                md_content += f'## {secoes_abnt[titulo]}\n\n{conteudo}\n\n'
        else:
            md_content += f'### {html.unescape(p.get("titulo", ""))}\n\n{conteudo}\n\n'

    # Referências ABNT
    if data.get("referencias"):
        md_content += '## REFERÊNCIAS\n\n'
        for ref in data.get("referencias", []):
            md_content += f'- {formatar_referencia_abnt(html.unescape(ref))}\n'

    # Rodapé
    md_content += '\n\n---\n'
    # md_content += '\n*Documento formatado conforme normas ABNT básicas*\n'

    # Salvar arquivo
    base_filename = html.unescape(data.get("titulo", "artigo"))
    base_filename = ''.join(c for c in base_filename if c.isalnum() or c in ' _-')
    output_filename = f"artigos-gerados-exemplo/{base_filename}_ABNT.md"
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(md_content)
        
    print(f"Arquivo ABNT gerado com sucesso: {output_filename}")
    
except Exception as e:
    print(f"Erro ao converter para Markdown ABNT: {str(e)}")
    sys.exit(1)