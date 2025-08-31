import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from collections import Counter
import calendar
import sys

# --- Configurações de Design ---
TEMA = 'clam'
FONTE_PADRAO = ('Helvetica', 10)
FONTE_LABEL = ('Helvetica', 12)
FONTE_TITULO = ('Helvetica', 14, 'bold')
# -----------------------------

# Adicionar a versão do aplicativo
VERSAO = "4.5.0"

# Lista de despesas predefinidas (CORRIGIDA)
CATEGORIAS_DESPESAS_PREDEFINIDAS = [
    'Aluguel',
    'Financiamento Imobibiario',
    'Estacionamento',
    'Fatura de Energia',
    'Fatura de Água',
    'Fatura Tv / Internet',
    'Despesas Reforma',
    'Contabilidade',
    'INSS',
    'Simples Nacional',
    'Parcelamento 1',
    'Parcelamento 2',
    'Despesa Supermercado',
    'Despesa Padaria',
    'Despesa Refeição Trabalho',
    'Despesa Fast Food/Restaurante',
    'Plano de Saúde Familiar',
    'Plano de Saúde Contribuição',
    'Cartão de crédito XP',
    'Cartão de crédito BVI',
    'Cartão de crédito Itaú',
    'Cartão RCHLO',
    'Cartão credito ML',
    'Medicamentos',
    'Pet Shop',
    'Cabeleireiro',
    'Dentista',
    'Diversão Heitor',
    'pagamento condominio',
    'outros'
]

# Nova lista de receitas predefinidas
CATEGORIAS_ENTRADAS_PREDEFINIDAS = [
    'Salário',
    'Aluguel',
    'Dividendos',
    'Outros'
]

# Variáveis globais para o mês e ano atuais
MES_ATUAL = datetime.now().month
ANO_ATUAL = datetime.now().year

# --- Criação do diretório de dados ---
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Função para obter o nome do arquivo JSON com base no mês e ano
def get_json_file(ano, mes):
    return os.path.join(DATA_DIR, f'data_orcamento_{ano}_{mes:02d}.json')

# Função para carregar dados do arquivo JSON
def carregar_dados(ano, mes):
    json_file = get_json_file(ano, mes)
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            try:
                data = json.load(f)
                # Ensure all keys exist
                if 'entradas' not in data:
                    data['entradas'] = []
                if 'despesas' not in data:
                    data['despesas'] = []
                if 'investimentos' not in data:
                    data['investimentos'] = []
                if 'cartoes_parcelados' not in data:
                    data['cartoes_parcelados'] = []
                if 'caixas' not in data:
                    data['caixas'] = {
                        'conta_corrente': 0.0,
                        'investimentos': {
                            'Ações': 0.0,
                            'Fundos Imobiliários': 0.0,
                            'ETF Internacional': 0.0,
                            'CDB': 0.0,
                            'Cofrinhos': 0.0,
                            'Tesouro Direto': 0.0,
                        }
                    }
                # Add 'Tesouro Direto' if it's missing from an old file
                if 'Tesouro Direto' not in data['caixas']['investimentos']:
                    data['caixas']['investimentos']['Tesouro Direto'] = 0.0
                return data
            except json.JSONDecodeError:
                return {
                    'entradas': [],
                    'despesas': [],
                    'investimentos': [],
                    'cartoes_parcelados': [],
                    'caixas': {
                        'conta_corrente': 0.0,
                        'investimentos': {
                            'Ações': 0.0,
                            'Fundos Imobiliários': 0.0,
                            'ETF Internacional': 0.0,
                            'CDB': 0.0,
                            'Cofrinhos': 0.0,
                            'Tesouro Direto': 0.0,
                        }
                    }
                }
    return {
        'entradas': [],
        'despesas': [],
        'investimentos': [],
        'cartoes_parcelados': [],
        'caixas': {
            'conta_corrente': 0.0,
            'investimentos': {
                'Ações': 0.0,
                'Fundos Imobiliários': 0.0,
                'ETF Internacional': 0.0,
                'CDB': 0.0,
                'Cofrinhos': 0.0,
                'Tesouro Direto': 0.0,
            }
        }
    }

# Função para salvar dados no arquivo JSON
def salvar_dados(dados, ano, mes):
    json_file = get_json_file(ano, mes)
    with open(json_file, 'w') as f:
        json.dump(dados, f, indent=4)
    # Removida a mensagem de sucesso para evitar pop-ups excessivos
    # messagebox.showinfo("Sucesso", f"Dados do mês {mes:02d}/{ano} salvos com sucesso!")

# Função para exibir mensagem de erro
def mostrar_erro(mensagem):
    messagebox.showerror("Erro", mensagem)

# Função para limpar campos
def limpar_campos(campos):
    for campo in campos:
        if isinstance(campo, ttk.Entry) or isinstance(campo, tk.Entry):
            campo.delete(0, tk.END)
        elif isinstance(campo, ttk.Combobox):
            campo.set("")

# Função de formatação de valores
def formatar_valor(event, entry):
    s = entry.get().replace('.', '').replace(',', '')
    if not s.isdigit():
        entry.delete(0, tk.END)
        return

    valor_int = int(s)
    valor_str = str(valor_int)

    if len(valor_str) < 3:
        valor_formatado = "0" * (3 - len(valor_str)) + valor_str
        valor_formatado = valor_formatado[:-2] + "," + valor_formatado[-2:]
    else:
        partes_inteiras = []
        parte_inteira = valor_str[:-2]
        parte_decimal = valor_str[-2:]
        while len(parte_inteira) > 3:
            partes_inteiras.append(parte_inteira[-3:])
            parte_inteira = parte_inteira[:-3]
        partes_inteiras.append(parte_inteira)
        partes_inteiras.reverse()
        valor_formatado = '.'.join(partes_inteiras) + "," + parte_decimal

    entry.delete(0, tk.END)
    entry.insert(0, valor_formatado)

def adicionar_transacao(tipo, descricao_widget, valor_entry, observacoes_entry, ano_combo, mes_combo):
    descricao = descricao_widget.get().strip()
    valor_str = valor_entry.get().strip().replace('.', '').replace(',', '.')
    observacoes = observacoes_entry.get().strip()
    mes_str = mes_combo.get()
    ano_str = ano_combo.get()
    
    if not descricao or not valor_str or not mes_str or not ano_str:
        mostrar_erro("Os campos 'Descrição', 'Valor', 'Mês' e 'Ano' devem ser preenchidos.")
        return
    
    try:
        valor = float(valor_str)
        mes = [m[1] for m in meses].index(mes_str) + 1
        ano = int(ano_str)
    except (ValueError, IndexError):
        mostrar_erro("Valores de entrada inválidos.")
        return

    dados = carregar_dados(ano, mes)
    
    if tipo == 'entradas':
        dados['entradas'].append({'descricao': descricao, 'valor': valor, 'observacoes': observacoes, 'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        if ano == ANO_ATUAL and mes == MES_ATUAL:
            dados['caixas']['conta_corrente'] += valor
    else: # despesas
        dados['despesas'].append({'descricao': descricao, 'valor': valor, 'observacoes': observacoes, 'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        if ano == ANO_ATUAL and mes == MES_ATUAL:
            dados['caixas']['conta_corrente'] -= valor
    
    salvar_dados(dados, ano, mes)
    # Removida a mensagem de sucesso para evitar pop-ups excessivos
    # messagebox.showinfo("Sucesso", f"{tipo.capitalize()} adicionada com sucesso!")
    limpar_campos([descricao_widget, valor_entry, observacoes_entry])
    atualizar_tabelas_e_resumo()

# Função para adicionar investimentos
def adicionar_investimento(combo_investimento, valor_entry, observacoes_entry, ano_combo, mes_combo):
    investimento_nome = combo_investimento.get()
    valor_str = valor_entry.get().strip().replace('.', '').replace(',', '.')
    observacoes = observacoes_entry.get().strip()
    mes_str = mes_combo.get()
    ano_str = ano_combo.get()

    if not investimento_nome or not valor_str or not mes_str or not ano_str:
        mostrar_erro("Por favor, selecione um investimento, insira um valor e preencha o mês e ano.")
        return

    try:
        valor = float(valor_str)
        mes = [m[1] for m in meses].index(mes_str) + 1
        ano = int(ano_str)
    except (ValueError, IndexError):
        mostrar_erro("Valores de entrada inválidos.")
        return
    
    dados = carregar_dados(ano, mes)
    
    # Adicionar o investimento
    dados['investimentos'].append({'descricao': investimento_nome, 'valor': valor, 'observacoes': observacoes, 'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
    
    # Atualizar caixas
    if ano == ANO_ATUAL and mes == MES_ATUAL:
        dados['caixas']['conta_corrente'] -= valor
        if investimento_nome in dados['caixas']['investimentos']:
            dados['caixas']['investimentos'][investimento_nome] += valor
        else:
            dados['caixas']['investimentos'][investimento_nome] = valor

    salvar_dados(dados, ano, mes)
    # Removida a mensagem de sucesso
    # messagebox.showinfo("Sucesso", f"Investimento em {investimento_nome} adicionado com sucesso!")
    limpar_campos([combo_investimento, valor_investimento_entry, observacoes_investimento_entry])
    atualizar_tabelas_e_resumo()

# Função para resgatar investimentos
def resgatar_investimento(combo_investimento, valor_entry):
    global ANO_ATUAL, MES_ATUAL
    
    investimento_nome = combo_investimento.get()
    valor_str = valor_entry.get().strip().replace('.', '').replace(',', '.')
    
    if not investimento_nome or not valor_str:
        mostrar_erro("Por favor, selecione um investimento e insira um valor para resgate.")
        return
    
    try:
        valor = float(valor_str)
    except ValueError:
        mostrar_erro("Valor de resgate inválido.")
        return
    
    dados = carregar_dados(ANO_ATUAL, MES_ATUAL)
    
    if investimento_nome not in dados['caixas']['investimentos']:
        mostrar_erro(f"O investimento '{investimento_nome}' não existe na sua caixa de investimentos.")
        return
    
    if dados['caixas']['investimentos'][investimento_nome] < valor:
        messagebox.showwarning("Aviso", "O valor de resgate é maior do que o saldo total do investimento.")
        
    resposta = messagebox.askyesno("Confirmar Resgate", f"Tem certeza que deseja resgatar R$ {valor:,.2f} de {investimento_nome}?")
    if resposta:
        # Subtrai do caixa de investimentos
        dados['caixas']['investimentos'][investimento_nome] -= valor
        
        # Adiciona ao caixa da conta corrente
        dados['caixas']['conta_corrente'] += valor
        
        salvar_dados(dados, ANO_ATUAL, MES_ATUAL)
        # Removida a mensagem de sucesso
        # messagebox.showinfo("Sucesso", f"Resgate de R$ {valor:,.2f} de {investimento_nome} realizado com sucesso!")
        limpar_campos([combo_investimento_resgate, valor_resgate_entry])
        atualizar_tabelas_e_resumo()

# Função para adicionar faturas parceladas
def adicionar_fatura_parcelada(cartao_combo, valor_entry, parcelas_entry, descricao_entry, mes_vencimento_combo, ano_vencimento_combo):
    cartao = cartao_combo.get()
    valor_str = valor_entry.get().strip().replace('.', '').replace(',', '.')
    parcelas_str = parcelas_entry.get().strip()
    descricao = descricao_entry.get().strip()
    mes_vencimento_str = mes_vencimento_combo.get()
    ano_vencimento_str = ano_vencimento_combo.get()

    if not cartao or not valor_str or not parcelas_str or not descricao or not mes_vencimento_str or not ano_vencimento_str:
        mostrar_erro("Todos os campos devem ser preenchidos.")
        return

    try:
        valor_total = float(valor_str)
        num_parcelas = int(parcelas_str)
        parcela_mensal = valor_total / num_parcelas
        mes_vencimento = [m[1] for m in meses].index(mes_vencimento_str) + 1
        ano_vencimento = int(ano_vencimento_str)
    except (ValueError, IndexError):
        mostrar_erro("Valores de entrada inválidos.")
        return
    
    # Adicionar o item à lista de parcelamentos
    dados = carregar_dados(ano_vencimento, mes_vencimento)
    dados['cartoes_parcelados'].append({
        'cartao': cartao,
        'descricao': descricao,
        'valor_total': valor_total,
        'valor_parcela': parcela_mensal,
        'num_parcelas': num_parcelas,
        'parcelas_restantes': num_parcelas,
        'ano_vencimento': ano_vencimento,
        'mes_vencimento': mes_vencimento,
        'data_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    salvar_dados(dados, ano_vencimento, mes_vencimento)

    # Lançar a primeira parcela como despesa
    dados_primeira_parcela = carregar_dados(ano_vencimento, mes_vencimento)
    dados_primeira_parcela['despesas'].append({
        'descricao': f"{cartao} - Parcela 1/{num_parcelas}: {descricao}",
        'valor': parcela_mensal,
        'observacoes': "", # Adicionado campo de observação vazio para a transação gerada
        'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    dados_primeira_parcela['caixas']['conta_corrente'] -= parcela_mensal
    salvar_dados(dados_primeira_parcela, ano_vencimento, mes_vencimento)

    # Projetar as parcelas futuras
    for i in range(1, num_parcelas):
        mes_futuro = mes_vencimento + i
        ano_futuro = ano_vencimento
        if mes_futuro > 12:
            mes_futuro -= 12
            ano_futuro += 1
        
        dados_futuros = carregar_dados(ano_futuro, mes_futuro)
        dados_futuros['despesas'].append({
            'descricao': f"{cartao} - Parcela {i+1}/{num_parcelas}: {descricao}",
            'valor': parcela_mensal,
            'observacoes': "", # Adicionado campo de observação vazio para a transação gerada
            'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        dados_futuros['caixas']['conta_corrente'] -= parcela_mensal
        salvar_dados(dados_futuros, ano_futuro, mes_futuro)

    messagebox.showinfo("Sucesso", "Compra parcelada adicionada e projetada com sucesso!")
    limpar_campos([cartao_combo, valor_compra_entry, parcelas_entry, descricao_compra_entry])
    atualizar_tabelas_e_resumo()

# Função para excluir transacao
def excluir_transacao(treeview, tipo_dados):
    global ANO_ATUAL, MES_ATUAL

    item_selecionado = treeview.selection()
    if not item_selecionado:
        messagebox.showwarning("Aviso", "Por favor, selecione uma transação para excluir.")
        return

    resposta = messagebox.askyesno("Confirmar Exclusão", "Tem certeza de que deseja excluir esta transação?")
    if resposta:
        item_para_excluir = treeview.item(item_selecionado[0])
        dados_item = item_para_excluir['values']
        descricao_excluir = dados_item[0]
        valor_excluir = float(str(dados_item[1]).replace('R$ ', '').replace('.', '').replace(',', '.'))
        
        dados = carregar_dados(ANO_ATUAL, MES_ATUAL)

        if tipo_dados == 'entradas':
            # Filtrar a lista de entradas para remover o item selecionado
            dados['entradas'] = [item for item in dados['entradas'] if not (item['descricao'] == descricao_excluir and item['valor'] == valor_excluir)]
            dados['caixas']['conta_corrente'] -= valor_excluir
        elif tipo_dados == 'despesas':
            # Filtrar a lista de despesas para remover o item selecionado
            dados['despesas'] = [item for item in dados['despesas'] if not (item['descricao'] == descricao_excluir and item['valor'] == valor_excluir)]
            dados['caixas']['conta_corrente'] += valor_excluir
        elif tipo_dados == 'investimentos':
            # Encontrar o item exato para remover
            encontrado = False
            for i, item in enumerate(dados['investimentos']):
                # Usar a data para garantir que estamos excluindo a transação correta, caso haja valores e descrições duplicadas.
                if item['descricao'] == descricao_excluir and item['valor'] == valor_excluir:
                    dados['investimentos'].pop(i)
                    
                    # LINHA CRÍTICA: DEVOLVE O DINHEIRO AO CAIXA DA CONTA CORRENTE
                    dados['caixas']['conta_corrente'] += valor_excluir
                    
                    # Subtrai também do saldo do investimento
                    if descricao_excluir in dados['caixas']['investimentos']:
                        dados['caixas']['investimentos'][descricao_excluir] -= valor_excluir
                    encontrado = True
                    break
            
            if not encontrado:
                messagebox.showerror("Erro", "Transação de investimento não encontrada.")
                return
                
        salvar_dados(dados, ANO_ATUAL, MES_ATUAL)
        messagebox.showinfo("Sucesso", "Transação excluída com sucesso!")
        atualizar_tabelas_e_resumo()

def excluir_fatura_parcelada(treeview):
    global ANO_ATUAL, MES_ATUAL

    item_selecionado = treeview.selection()
    if not item_selecionado:
        messagebox.showwarning("Aviso", "Por favor, selecione uma fatura parcelada para excluir.")
        return

    resposta = messagebox.askyesno("Confirmar Exclusão", "Tem certeza de que deseja excluir esta fatura parcelada? As despesas mensais já lançadas não serão removidas.")
    if resposta:
        item_para_excluir = treeview.item(item_selecionado[0])
        dados_item = item_para_excluir['values']
        
        # Obter a descrição original da fatura
        cartao = dados_item[0]
        descricao = dados_item[1]
        
        dados = carregar_dados(ANO_ATUAL, MES_ATUAL)

        faturas_mantidas = []
        for fatura in dados['cartoes_parcelados']:
            if not (fatura['cartao'] == cartao and fatura['descricao'] == descricao):
                faturas_mantidas.append(fatura)
        
        dados['cartoes_parcelados'] = faturas_mantidas
        
        salvar_dados(dados, ANO_ATUAL, MES_ATUAL)
        messagebox.showinfo("Sucesso", "Fatura parcelada excluída com sucesso!")
        atualizar_tabela_cartoes()

# Funções para atualizar a Treeview e totais
def atualizar_tabelas():
    global ANO_ATUAL, MES_ATUAL

    for i in tree_entradas.get_children():
        tree_entradas.delete(i)
    for i in tree_despesas.get_children():
        tree_despesas.delete(i)
    for i in tree_investimentos.get_children():
        tree_investimentos.delete(i)
    
    dados = carregar_dados(ANO_ATUAL, MES_ATUAL)
    
    total_entradas = 0
    for item in dados['entradas']:
        valor_str = f"R$ {item['valor']:,.2f}".replace('.', '#').replace(',', '.').replace('#', ',')
        data_formatada = datetime.strptime(item['data'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%y')
        tree_entradas.insert('', 'end', values=(item['descricao'], valor_str, item.get('observacoes', ''), data_formatada))
        total_entradas += item['valor']
        
    total_despesas = 0
    for item in dados['despesas']:
        valor_str = f"R$ {item['valor']:,.2f}".replace('.', '#').replace(',', '.').replace('#', ',')
        data_formatada = datetime.strptime(item['data'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%y')
        tree_despesas.insert('', 'end', values=(item['descricao'], valor_str, item.get('observacoes', ''), data_formatada))
        total_despesas += item['valor']
        
    total_investimentos = 0
    for item in dados['investimentos']:
        valor_str = f"R$ {item['valor']:,.2f}".replace('.', '#').replace(',', '.').replace('#', ',')
        data_formatada = datetime.strptime(item['data'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%y')
        tree_investimentos.insert('', 'end', values=(item['descricao'], valor_str, item.get('observacoes', ''), data_formatada))
        total_investimentos += item['valor']

    # Atualizar totais e porcentagens na aba de visualização
    total_receitas = total_entradas
    
    lbl_entradas_total.config(text=f"Total: R$ {total_entradas:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    
    lbl_despesas_total.config(text=f"Total: R$ {total_despesas:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    lbl_despesas_pct.config(text=f"({(total_despesas/total_receitas)*100:.2f}%)" if total_receitas > 0 else "(0,00%)")

    lbl_investimentos_total.config(text=f"Total: R$ {total_investimentos:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    lbl_investimentos_pct.config(text=f"({(total_investimentos/total_receitas)*100:.2f}%)" if total_receitas > 0 else "(0,00%)")

def atualizar_tabela_cartoes():
    global ANO_ATUAL, MES_ATUAL
    
    for i in tree_cartoes_parcelados.get_children():
        tree_cartoes_parcelados.delete(i)
    
    dados = carregar_dados(ANO_ATUAL, MES_ATUAL)
    
    for item in dados['cartoes_parcelados']:
        valor_parcela_str = f"R$ {item['valor_parcela']:,.2f}".replace('.', '#').replace(',', '.').replace('#', ',')
        data_registro_formatada = datetime.strptime(item['data_registro'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%y')
        tree_cartoes_parcelados.insert('', 'end', values=(
            item['cartao'],
            item['descricao'],
            valor_parcela_str,
            f"{item['parcelas_restantes']}/{item['num_parcelas']}",
            data_registro_formatada
        ))
        
# Função auxiliar para pegar dados de investimentos do mês anterior
def get_investimentos_mes_anterior(ano, mes):
    mes_anterior = mes - 1
    ano_anterior = ano
    if mes_anterior == 0:
        mes_anterior = 12
        ano_anterior -= 1
    
    dados_anterior = carregar_dados(ano_anterior, mes_anterior)
    return dados_anterior['caixas']['investimentos']


def atualizar_resumo():
    global ANO_ATUAL, MES_ATUAL

    dados_atual = carregar_dados(ANO_ATUAL, MES_ATUAL)
    dados_anterior_invest = get_investimentos_mes_anterior(ANO_ATUAL, MES_ATUAL)
    
    total_entradas = sum(item['valor'] for item in dados_atual['entradas'])
    total_despesas = sum(item['valor'] for item in dados_atual['despesas'])
    total_investimentos = sum(item['valor'] for item in dados_atual['investimentos'])

    saldo_total = total_entradas - total_despesas

    # Atualizar variáveis
    total_entradas_var.set(f"R$ {total_entradas:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    total_despesas_var.set(f"R$ {total_despesas:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    total_investimentos_var.set(f"R$ {total_investimentos:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    saldo_total_var.set(f"R$ {saldo_total:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    
    if total_entradas > 0:
        pct_investimento = (total_investimentos / total_entradas) * 100
        pct_investimento_var.set(f"{pct_investimento:,.2f}%".replace('.', '#').replace(',', '.').replace('#', ','))
    else:
        pct_investimento_var.set("0,00%")

    # Atualizar caixas
    caixa_cc_valor = dados_atual['caixas']['conta_corrente']
    caixa_invest_total = sum(dados_atual['caixas']['investimentos'].values())
    caixa_total = caixa_cc_valor + caixa_invest_total
    
    caixa_cc_var.set(f"R$ {caixa_cc_valor:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    caixa_invest_var.set(f"R$ {caixa_invest_total:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    caixa_total_var.set(f"R$ {caixa_total:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    
    # Atualizar lista de investimentos com a nova análise de variação
    for i in tree_caixa_investimentos.get_children():
        tree_caixa_investimentos.delete(i)
    
    for invest, valor_atual in dados_atual['caixas']['investimentos'].items():
        valor_anterior = dados_anterior_invest.get(invest, 0.0)
        
        if valor_anterior > 0:
            variacao_pct = ((valor_atual - valor_anterior) / valor_anterior) * 100
            variacao_str = f"{variacao_pct:,.2f}%".replace('.', '#').replace(',', '.').replace('#', ',')
        elif valor_atual > 0:
            variacao_str = "+ Inf."
        else:
            variacao_str = "0,00%"

        tree_caixa_investimentos.insert('', 'end', values=(
            invest, 
            f"R$ {valor_atual:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','), 
            variacao_str
        ))


def atualizar_tabelas_e_resumo():
    atualizar_tabelas()
    atualizar_resumo()
    atualizar_comparativo_despesas()
    atualizar_tabela_cartoes()

def forcar_atualizacao():
    atualizar_tabelas_e_resumo()
    messagebox.showinfo("Atualização Completa", "As tabelas e o resumo foram atualizados com sucesso.")

def carregar_mes_selecionado(event=None):
    global ANO_ATUAL, MES_ATUAL
    
    mes_str = combo_mes.get()
    ano_str = combo_ano.get()
    
    if mes_str and ano_str:
        mes_index = [m[1] for m in meses].index(mes_str) + 1
        ano = int(ano_str)

        MES_ATUAL = mes_index
        ANO_ATUAL = ano
        
        atualizar_tabelas_e_resumo()
        messagebox.showinfo("Sucesso", f"Dados de {mes_str}/{ano} carregados!")

# Função para gerar gráficos
def gerar_grafico_orcamento():
    global ANO_ATUAL, MES_ATUAL
    dados = carregar_dados(ANO_ATUAL, MES_ATUAL)
    
    total_entradas = sum(item['valor'] for item in dados['entradas'])
    total_despesas = sum(item['valor'] for item in dados['despesas'])
    total_investimentos = sum(item['valor'] for item in dados['investimentos'])

    labels = ['Receitas', 'Despesas', 'Investimentos']
    valores = [total_entradas, total_despesas, total_investimentos]
    cores = ['#4CAF50', '#F44336', '#2196F3']
    
    figura, ax = plt.subplots()
    ax.pie(valores, labels=labels, autopct='%1.1f%%', startangle=90, colors=cores, wedgeprops={'edgecolor': 'white'})
    ax.set_title(f'Resumo do Orçamento {combo_mes.get()}/{combo_ano.get()}')
    plt.show()

# FUNÇÃO `gerar_relatorio_pdf` ATUALIZADA
def gerar_relatorio_pdf():
    global ANO_ATUAL, MES_ATUAL
    dados = carregar_dados(ANO_ATUAL, MES_ATUAL)
    
    doc = SimpleDocTemplate(os.path.join(DATA_DIR, f"relatorio_orcamento_{ANO_ATUAL}_{MES_ATUAL:02d}.pdf"), pagesize=letter)
    story = []
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='TitleStyle', fontSize=24, alignment=1, spaceAfter=20, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='HeadingStyle', fontSize=14, alignment=0, spaceAfter=10, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='SubheadingStyle', fontSize=12, alignment=0, spaceAfter=8, fontName='Helvetica-Bold'))

    story.append(Paragraph(f"Relatório de Orçamento - {combo_mes.get()}/{combo_ano.get()}", styles['TitleStyle']))
    story.append(Spacer(1, 12))
    
    # Adicionar resumo
    total_entradas = sum(item['valor'] for item in dados['entradas'])
    total_despesas = sum(item['valor'] for item in dados['despesas'])
    total_investimentos = sum(item['valor'] for item in dados['investimentos'])
    total_saidas = total_despesas + total_investimentos
    saldo_final = total_entradas - total_saidas
    
    story.append(Paragraph("Resumo Geral", styles['HeadingStyle']))
    story.append(Paragraph(f"Total de Entradas: R$ {total_entradas:,.2f}".replace('.', '#').replace(',', '.').replace('#', ',')))
    story.append(Paragraph(f"Total de Saídas: R$ {total_saidas:,.2f}".replace('.', '#').replace(',', '.').replace('#', ',')))
    story.append(Paragraph(f"Saldo Final: R$ {saldo_final:,.2f}".replace('.', '#').replace(',', '.').replace('#', ',')))
    
    # Adicionar saldos dos caixas
    caixa_cc_valor = dados['caixas']['conta_corrente']
    caixa_invest_valor = sum(dados['caixas']['investimentos'].values())
    caixa_total_valor = caixa_cc_valor + caixa_invest_valor
    story.append(Spacer(1, 12))
    story.append(Paragraph("Saldos Atuais dos Caixas:", styles['SubheadingStyle']))
    story.append(Paragraph(f"Saldo Conta Corrente: R$ {caixa_cc_valor:,.2f}".replace('.', '#').replace(',', '.').replace('#', ',')))
    story.append(Paragraph(f"Saldo Total de Investimentos: R$ {caixa_invest_valor:,.2f}".replace('.', '#').replace(',', '.').replace('#', ',')))
    story.append(Paragraph(f"Saldo Total (CC + Investimentos): R$ {caixa_total_valor:,.2f}".replace('.', '#').replace(',', '.').replace('#', ',')))
    story.append(Spacer(1, 24))


    # Tabela de Receitas
    story.append(Paragraph("Detalhamento das Receitas", styles['HeadingStyle']))
    data_receitas = [['Descrição', 'Valor (R$)', 'Observações', 'Data']]
    for item in dados['entradas']:
        valor_str = f"R$ {item['valor']:,.2f}".replace('.', '#').replace(',', '.').replace('#', ',')
        data_formatada = datetime.strptime(item['data'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%y')
        data_receitas.append([item['descricao'], valor_str, item.get('observacoes', ''), data_formatada])
    t_receitas = Table(data_receitas, colWidths=[2.5*inch, 1*inch, 2*inch, 1*inch])
    t_receitas.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F5F5F5')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    story.append(t_receitas)
    story.append(Spacer(1, 12))

    # Tabela de Despesas AGRUPADA por categoria
    story.append(Paragraph("Resumo de Despesas por Categoria", styles['HeadingStyle']))
    despesas_agrupadas = {}
    for item in dados['despesas']:
        descricao = item['descricao']
        valor = item['valor']
        despesas_agrupadas[descricao] = despesas_agrupadas.get(descricao, 0) + valor

    data_despesas = [['Categoria', 'Valor Total (R$)']]
    for categoria, valor in sorted(despesas_agrupadas.items()):
        valor_str = f"R$ {valor:,.2f}".replace('.', '#').replace(',', '.').replace('#', ',')
        data_despesas.append([categoria, valor_str])

    t_despesas = Table(data_despesas, colWidths=[4*inch, 2.5*inch])
    t_despesas.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F5F5F5')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    story.append(t_despesas)
    story.append(Spacer(1, 12))


    # Tabela de Investimentos
    story.append(Paragraph("Detalhamento dos Investimentos", styles['HeadingStyle']))
    data_investimentos = [['Descrição', 'Valor (R$)', 'Observações', 'Data']]
    for item in dados['investimentos']:
        valor_str = f"R$ {item['valor']:,.2f}".replace('.', '#').replace(',', '.').replace('#', ',')
        data_formatada = datetime.strptime(item['data'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%y')
        data_investimentos.append([item['descricao'], valor_str, item.get('observacoes', ''), data_formatada])
    t_investimentos = Table(data_investimentos, colWidths=[2.5*inch, 1*inch, 2*inch, 1*inch])
    t_investimentos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F5F5F5')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    story.append(t_investimentos)
    story.append(Spacer(1, 24))

    # Comparativo de Faturas de Cartão de Crédito
    story.append(Paragraph("Comparativo de Faturas de Cartão de Crédito", styles['HeadingStyle']))
    meses_comparativos = []
    for i in range(12):
        mes_temp = MES_ATUAL - i
        ano_temp = ANO_ATUAL
        if mes_temp <= 0:
            mes_temp += 12
            ano_temp -= 1
        meses_comparativos.append((ano_temp, mes_temp))
    meses_comparativos.reverse()

    cartoes = ['Cartão de crédito Itaú', 'Cartão de crédito BVI', 'Cartão de crédito XP', 'Cartão credito ML', 'Cartão RCHLO']
    
    # Criar um dicionário para armazenar os valores mensais de cada cartão
    valores_mensais = {cartao: [] for cartao in cartoes}
    
    # Obter os dados de despesas de todos os meses para os cálculos
    for ano_comp, mes_comp in meses_comparativos:
        dados_mes = carregar_dados(ano_comp, mes_comp)
        for cartao in cartoes:
            valor_cartao = sum(d['valor'] for d in dados_mes['despesas'] if cartao in d['descricao'])
            valores_mensais[cartao].append(valor_cartao)

    # Preparar a tabela com cabeçalhos
    data_cartoes = [['Mês/Ano'] + cartoes]

    # Preencher a tabela com os dados, incluindo variação
    for i, (ano_comp, mes_comp) in enumerate(meses_comparativos):
        row = [f"{calendar.month_name[mes_comp].capitalize()}/{ano_comp}"]
        
        for cartao in cartoes:
            valor_atual = valores_mensais[cartao][i]
            
            if i > 0:
                valor_anterior = valores_mensais[cartao][i-1]
                variacao = valor_atual - valor_anterior
                if valor_anterior > 0:
                    pct_variacao = (variacao / valor_anterior) * 100
                else:
                    pct_variacao = 0 if valor_atual == 0 else 100
                
                variacao_str = f"R$ {variacao:,.2f}".replace('.', '#').replace(',', '.').replace('#', ',')
                pct_variacao_str = f"{pct_variacao:,.2f}%".replace('.', '#').replace(',', '.').replace('#', ',')
                
                row.append(f"R$ {valor_atual:,.2f} ({variacao_str}, {pct_variacao_str})".replace('.', '#').replace(',', '.').replace('#', ','))
            else:
                row.append(f"R$ {valor_atual:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
        
        data_cartoes.append(row)


    t_cartoes = Table(data_cartoes, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1*inch])
    t_cartoes.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F5F5F5')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    story.append(t_cartoes)

    doc.build(story)
    messagebox.showinfo("Sucesso", "Relatório PDF gerado com sucesso!")
    
    # --- Código para abrir o PDF automaticamente ---
    pdf_path = os.path.join(DATA_DIR, f"relatorio_orcamento_{ANO_ATUAL}_{MES_ATUAL:02d}.pdf")
    try:
        if sys.platform == 'win32':
            os.startfile(pdf_path)
        elif sys.platform == 'darwin': # macOS
            os.system(f"open {pdf_path}")
        else: # linux
            os.system(f"xdg-open {pdf_path}")
    except Exception as e:
        messagebox.showerror("Erro ao abrir PDF", f"Não foi possível abrir o arquivo PDF: {e}")

def atualizar_comparativo_despesas():
    global ANO_ATUAL, MES_ATUAL
    
    for item in tree_comparativo.get_children():
        tree_comparativo.delete(item)

    # Obter dados do mês atual
    dados_atual = carregar_dados(ANO_ATUAL, MES_ATUAL)
    despesas_atual_dict = {item['descricao']: sum(d['valor'] for d in dados_atual['despesas'] if d['descricao'] == item['descricao']) for item in dados_atual['despesas']}
    
    # Obter dados do mês anterior
    mes_anterior = MES_ATUAL - 1
    ano_anterior = ANO_ATUAL
    if mes_anterior == 0:
        mes_anterior = 12
        ano_anterior -= 1
    
    dados_anterior = carregar_dados(ano_anterior, mes_anterior)
    despesas_anterior_dict = {item['descricao']: sum(d['valor'] for d in dados_anterior['despesas'] if d['descricao'] == item['descricao']) for item in dados_anterior['despesas']}

    todas_categorias = set(despesas_atual_dict.keys()) | set(despesas_anterior_dict.keys())

    for categoria in sorted(list(todas_categorias)):
        valor_atual = despesas_atual_dict.get(categoria, 0)
        valor_anterior = despesas_anterior_dict.get(categoria, 0)
        
        variacao = valor_atual - valor_anterior
        
        if valor_anterior > 0:
            pct_variacao = (variacao / valor_anterior) * 100
        else:
            pct_variacao = 0 if valor_atual == 0 else 100

        # Formatar a variação
        if variacao > 0:
            variacao_str = f"+ R$ {variacao:,.2f}".replace('.', '#').replace(',', '.').replace('#', ',')
            pct_variacao_str = f"+{pct_variacao:,.2f}%".replace('.', '#').replace(',', '.').replace('#', ',')
        elif variacao < 0:
            variacao_str = f"R$ {variacao:,.2f}".replace('.', '#').replace(',', '.').replace('#', ',')
            pct_variacao_str = f"{pct_variacao:,.2f}%".replace('.', '#').replace(',', '.').replace('#', ',')
        else:
            variacao_str = "R$ 0,00"
            pct_variacao_str = "0,00%"

        tree_comparativo.insert('', 'end', values=(categoria, f"R$ {valor_atual:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','), variacao_str, pct_variacao_str))

# Função para definir o caixa inicial da conta corrente
def set_caixa_inicial():
    global ANO_ATUAL, MES_ATUAL
    
    dialog = tk.Toplevel(janela)
    dialog.title("Definir Saldo Inicial da Conta Corrente")
    dialog.grab_set()
    
    frame = ttk.Frame(dialog, padding="10")
    frame.pack()
    
    ttk.Label(frame, text="Insira o saldo inicial da conta corrente:").pack()
    valor_entry = ttk.Entry(frame, width=20)
    valor_entry.pack(pady=5)
    
    def salvar_valor(event=None):
        try:
            valor_str = valor_entry.get().strip().replace('.', '').replace(',', '.')
            valor = float(valor_str)
            dados = carregar_dados(ANO_ATUAL, MES_ATUAL)
            dados['caixas']['conta_corrente'] = valor
            salvar_dados(dados, ANO_ATUAL, MES_ATUAL)
            atualizar_resumo()
            dialog.destroy()
        except ValueError:
            mostrar_erro("Valor inválido. Por favor, insira um número.")
            
    ttk.Button(frame, text="Salvar", command=salvar_valor).pack(pady=10)
    valor_entry.bind('<Return>', salvar_valor)

# FUNÇÃO: Alterar valor de investimento na aba de resumo
def alterar_valor_investimento(tipo_investimento):
    global ANO_ATUAL, MES_ATUAL

    dialog = tk.Toplevel(janela)
    dialog.title(f"Alterar Saldo de '{tipo_investimento}'")
    dialog.grab_set()

    frame = ttk.Frame(dialog, padding="10")
    frame.pack()
    
    ttk.Label(frame, text="Insira o novo valor para este investimento:", font=FONTE_PADRAO).pack(pady=5)
    valor_entry = ttk.Entry(frame, width=20)
    valor_entry.pack(pady=5)
    valor_entry.bind("<KeyRelease>", lambda event: formatar_valor(event, valor_entry))

    dados = carregar_dados(ANO_ATUAL, MES_ATUAL)
    valor_atual = dados['caixas']['investimentos'].get(tipo_investimento, 0.0)
    valor_entry.insert(0, f"{valor_atual:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))


    def salvar_alteracao():
        try:
            valor_str = valor_entry.get().strip().replace('.', '').replace(',', '.')
            novo_valor = float(valor_str)

            dados = carregar_dados(ANO_ATUAL, MES_ATUAL)
            
            # Ajustar o saldo da conta corrente
            diferenca = novo_valor - dados['caixas']['investimentos'][tipo_investimento]
            dados['caixas']['conta_corrente'] -= diferenca
            
            # Alterar o valor do investimento
            dados['caixas']['investimentos'][tipo_investimento] = novo_valor
            
            salvar_dados(dados, ANO_ATUAL, MES_ATUAL)
            atualizar_tabelas_e_resumo()
            dialog.destroy()
            messagebox.showinfo("Sucesso", f"Saldo de '{tipo_investimento}' alterado para R$ {novo_valor:,.2f}.")
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido. Por favor, insira um número.")
    
    ttk.Button(frame, text="Salvar Novo Valor", command=salvar_alteracao).pack(pady=10)

# FUNÇÃO: Excluir valor de investimento na aba de resumo
def abrir_dialogo_excluir_investimento(tipo_investimento):
    global ANO_ATUAL, MES_ATUAL
    
    dialog = tk.Toplevel(janela)
    dialog.title("Excluir Valor do Investimento")
    dialog.grab_set()

    frame = ttk.Frame(dialog, padding="10")
    frame.pack()
    
    ttk.Label(frame, text=f"Insira o valor a ser excluído de '{tipo_investimento}':", font=FONTE_PADRAO).pack(pady=5)
    valor_entry = ttk.Entry(frame, width=20)
    valor_entry.pack(pady=5)
    valor_entry.bind("<KeyRelease>", lambda event: formatar_valor(event, valor_entry))

    def salvar_exclusao():
        try:
            valor_str = valor_entry.get().strip().replace('.', '').replace(',', '.')
            valor_excluir = float(valor_str)

            if valor_excluir <= 0:
                messagebox.showerror("Erro", "O valor a ser excluído deve ser maior que zero.")
                return

            dados = carregar_dados(ANO_ATUAL, MES_ATUAL)
            
            saldo_atual = dados['caixas']['investimentos'].get(tipo_investimento, 0.0)
            if valor_excluir > saldo_atual:
                resposta_aviso = messagebox.askyesno("Aviso", "O valor de exclusão é maior do que o saldo total do investimento. Continuar?")
                if not resposta_aviso:
                    return

            # Subtrai do caixa de investimentos
            dados['caixas']['investimentos'][tipo_investimento] -= valor_excluir
            
            # Adiciona ao caixa da conta corrente
            dados['caixas']['conta_corrente'] += valor_excluir
            
            salvar_dados(dados, ANO_ATUAL, MES_ATUAL)
            atualizar_tabelas_e_resumo()
            dialog.destroy()
            messagebox.showinfo("Sucesso", f"R$ {valor_excluir:,.2f} excluído de '{tipo_investimento}' e devolvido à Conta Corrente.")
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido. Por favor, insira um número.")
    
    ttk.Button(frame, text="Excluir Valor", command=salvar_exclusao).pack(pady=10)

# FUNÇÃO: Abrir menu de contexto
def show_context_menu(event):
    item_id = tree_caixa_investimentos.identify_row(event.y)
    if not item_id:
        return

    tree_caixa_investimentos.selection_set(item_id)
    item = tree_caixa_investimentos.item(item_id)
    tipo_investimento = item['values'][0]

    menu = tk.Menu(janela, tearoff=0)
    menu.add_command(label="Alterar Valor", command=lambda: alterar_valor_investimento(tipo_investimento))
    menu.add_command(label="Excluir Valor", command=lambda: abrir_dialogo_excluir_investimento(tipo_investimento))
    menu.post(event.x_root, event.y_root)

# Função para pedir confirmação ao fechar o programa
def on_closing():
    if messagebox.askyesno("Sair", "Tem certeza que deseja fechar o programa?"):
        janela.destroy()

# Função para adicionar scrollbar a uma aba
def add_scrollbar(frame):
    canvas = tk.Canvas(frame)
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )
    
    # Bind o mouse wheel ao canvas
    canvas.bind("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    return scrollable_frame

# --- Criação da Janela Principal ---
janela = tk.Tk()
janela.title(f"Gerenciador Financeiro - Versão {VERSAO}")
janela.state('zoomed')
janela.protocol("WM_DELETE_WINDOW", on_closing) # Adiciona a confirmação ao fechar

# Estilos
style = ttk.Style(janela)
style.theme_use(TEMA)
style.configure('TNotebook.Tab', font=('Helvetica', 10))
style.configure('TButton', font=FONTE_PADRAO)
style.configure('TLabel', font=FONTE_LABEL)
style.configure('Treeview.Heading', font=FONTE_TITULO)
style.configure('Treeview', rowheight=25)

# Notebook para abas
notebook = ttk.Notebook(janela)
notebook.pack(pady=10, expand=True, fill="both")

# Listas para os Comboboxes
meses = [('01', 'Janeiro'), ('02', 'Fevereiro'), ('03', 'Março'), ('04', 'Abril'), ('05', 'Maio'), ('06', 'Junho'), ('07', 'Julho'), ('08', 'Agosto'), ('09', 'Setembro'), ('10', 'Outubro'), ('11', 'Novembro'), ('12', 'Dezembro')]
meses_nomes = [m[1] for m in meses]
anos = [str(ano) for ano in range(2023, datetime.now().year + 5)]

# --- Aba de Cadastro ---
aba_cadastro = ttk.Frame(notebook)
notebook.add(aba_cadastro, text="Cadastro")
scrollable_cadastro = add_scrollbar(aba_cadastro)

# Frame para entradas
frame_entradas = ttk.LabelFrame(scrollable_cadastro, text="Adicionar Entradas", padding="10")
frame_entradas.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

ttk.Label(frame_entradas, text="Descrição:", font=FONTE_PADRAO).grid(row=0, column=0, padx=5, pady=5)
descricao_entrada_entry = ttk.Combobox(frame_entradas, values=CATEGORIAS_ENTRADAS_PREDEFINIDAS, state="readonly", width=38)
descricao_entrada_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_entradas, text="Valor (R$):", font=FONTE_PADRAO).grid(row=1, column=0, padx=5, pady=5)
valor_entrada_entry = ttk.Entry(frame_entradas, width=20)
valor_entrada_entry.grid(row=1, column=1, padx=5, pady=5)
valor_entrada_entry.bind("<KeyRelease>", lambda event: formatar_valor(event, valor_entrada_entry))

ttk.Label(frame_entradas, text="Observações:", font=FONTE_PADRAO).grid(row=2, column=0, padx=5, pady=5)
observacoes_entrada_entry = ttk.Entry(frame_entradas, width=40)
observacoes_entrada_entry.grid(row=2, column=1, padx=5, pady=5)

# Seletor de mês e ano para entradas
ttk.Label(frame_entradas, text="Mês:", font=FONTE_PADRAO).grid(row=3, column=0, padx=5, pady=5, sticky='w')
mes_combo_entrada = ttk.Combobox(frame_entradas, values=meses_nomes, state="readonly", width=15)
mes_combo_entrada.set(meses[MES_ATUAL-1][1])
mes_combo_entrada.grid(row=3, column=1, padx=5, pady=5, sticky='w')

ttk.Label(frame_entradas, text="Ano:", font=FONTE_PADRAO).grid(row=4, column=0, padx=5, pady=5, sticky='w')
ano_combo_entrada = ttk.Combobox(frame_entradas, values=anos, state="readonly", width=10)
ano_combo_entrada.set(ANO_ATUAL)
ano_combo_entrada.grid(row=4, column=1, padx=5, pady=5, sticky='w')


ttk.Button(frame_entradas, text="Adicionar Entrada", command=lambda: adicionar_transacao('entradas', descricao_entrada_entry, valor_entrada_entry, observacoes_entrada_entry, ano_combo_entrada, mes_combo_entrada)).grid(row=5, column=0, columnspan=2, pady=10)


# Frame para despesas
frame_despesas = ttk.LabelFrame(scrollable_cadastro, text="Adicionar Despesas", padding="10")
frame_despesas.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

ttk.Label(frame_despesas, text="Descrição:", font=FONTE_PADRAO).grid(row=0, column=0, padx=5, pady=5)
descricao_despesa_entry = ttk.Combobox(frame_despesas, values=CATEGORIAS_DESPESAS_PREDEFINIDAS, state="readonly", width=38)
descricao_despesa_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_despesas, text="Valor (R$):", font=FONTE_PADRAO).grid(row=1, column=0, padx=5, pady=5)
valor_despesa_entry = ttk.Entry(frame_despesas, width=20)
valor_despesa_entry.grid(row=1, column=1, padx=5, pady=5)
valor_despesa_entry.bind("<KeyRelease>", lambda event: formatar_valor(event, valor_despesa_entry))

ttk.Label(frame_despesas, text="Observações:", font=FONTE_PADRAO).grid(row=2, column=0, padx=5, pady=5)
observacoes_despesa_entry = ttk.Entry(frame_despesas, width=40)
observacoes_despesa_entry.grid(row=2, column=1, padx=5, pady=5)

# Seletor de mês e ano para despesas
ttk.Label(frame_despesas, text="Mês:", font=FONTE_PADRAO).grid(row=3, column=0, padx=5, pady=5, sticky='w')
mes_combo_despesa = ttk.Combobox(frame_despesas, values=meses_nomes, state="readonly", width=15)
mes_combo_despesa.set(meses[MES_ATUAL-1][1])
mes_combo_despesa.grid(row=3, column=1, padx=5, pady=5, sticky='w')

ttk.Label(frame_despesas, text="Ano:", font=FONTE_PADRAO).grid(row=4, column=0, padx=5, pady=5, sticky='w')
ano_combo_despesa = ttk.Combobox(frame_despesas, values=anos, state="readonly", width=10)
ano_combo_despesa.set(ANO_ATUAL)
ano_combo_despesa.grid(row=4, column=1, padx=5, pady=5, sticky='w')

ttk.Button(frame_despesas, text="Adicionar Despesa", command=lambda: adicionar_transacao('despesas', descricao_despesa_entry, valor_despesa_entry, observacoes_despesa_entry, ano_combo_despesa, mes_combo_despesa)).grid(row=5, column=0, columnspan=2, pady=10)


# Frame para investimentos
frame_investimentos = ttk.LabelFrame(scrollable_cadastro, text="Adicionar Investimento", padding="10")
frame_investimentos.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

tipos_investimentos = ['Ações', 'Fundos Imobiliários', 'ETF Internacional', 'CDB', 'Cofrinhos', 'Tesouro Direto']
ttk.Label(frame_investimentos, text="Tipo de Investimento:", font=FONTE_PADRAO).grid(row=0, column=0, padx=5, pady=5)
combo_investimento = ttk.Combobox(frame_investimentos, values=tipos_investimentos, state="readonly", width=30)
combo_investimento.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_investimentos, text="Valor (R$):", font=FONTE_PADRAO).grid(row=1, column=0, padx=5, pady=5)
valor_investimento_entry = ttk.Entry(frame_investimentos, width=20)
valor_investimento_entry.grid(row=1, column=1, padx=5, pady=5)
valor_investimento_entry.bind("<KeyRelease>", lambda event: formatar_valor(event, valor_investimento_entry))

ttk.Label(frame_investimentos, text="Observações:", font=FONTE_PADRAO).grid(row=2, column=0, padx=5, pady=5)
observacoes_investimento_entry = ttk.Entry(frame_investimentos, width=40)
observacoes_investimento_entry.grid(row=2, column=1, padx=5, pady=5)

# Seletor de mês e ano para investimentos
ttk.Label(frame_investimentos, text="Mês:", font=FONTE_PADRAO).grid(row=3, column=0, padx=5, pady=5, sticky='w')
mes_combo_investimento = ttk.Combobox(frame_investimentos, values=meses_nomes, state="readonly", width=15)
mes_combo_investimento.set(meses[MES_ATUAL-1][1])
mes_combo_investimento.grid(row=3, column=1, padx=5, pady=5, sticky='w')

ttk.Label(frame_investimentos, text="Ano:", font=FONTE_PADRAO).grid(row=4, column=0, padx=5, pady=5, sticky='w')
ano_combo_investimento = ttk.Combobox(frame_investimentos, values=anos, state="readonly", width=10)
ano_combo_investimento.set(ANO_ATUAL)
ano_combo_investimento.grid(row=4, column=1, padx=5, pady=5, sticky='w')

ttk.Button(frame_investimentos, text="Adicionar Investimento", command=lambda: adicionar_investimento(combo_investimento, valor_investimento_entry, observacoes_investimento_entry, ano_combo_investimento, mes_combo_investimento)).grid(row=5, column=0, columnspan=2, pady=10)

# Frame para resgate
frame_resgate = ttk.LabelFrame(scrollable_cadastro, text="Resgatar Investimento", padding="10")
frame_resgate.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

ttk.Label(frame_resgate, text="Tipo de Investimento:", font=FONTE_PADRAO).grid(row=0, column=0, padx=5, pady=5)
combo_investimento_resgate = ttk.Combobox(frame_resgate, values=tipos_investimentos, state="readonly", width=30)
combo_investimento_resgate.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_resgate, text="Valor (R$):", font=FONTE_PADRAO).grid(row=1, column=0, padx=5, pady=5)
valor_resgate_entry = ttk.Entry(frame_resgate, width=20)
valor_resgate_entry.grid(row=1, column=1, padx=5, pady=5)
valor_resgate_entry.bind("<KeyRelease>", lambda event: formatar_valor(event, valor_resgate_entry))

ttk.Button(frame_resgate, text="Resgatar Investimento", command=lambda: resgatar_investimento(combo_investimento_resgate, valor_resgate_entry)).grid(row=2, column=0, columnspan=2, pady=10)

# Frame para faturas parceladas
frame_faturas = ttk.LabelFrame(scrollable_cadastro, text="Adicionar Fatura Parcelada", padding="10")
frame_faturas.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

faturas = ['Cartão de crédito Itaú', 'Cartão de crédito BVI', 'Cartão de crédito XP', 'Cartão credito ML', 'Cartão RCHLO']
ttk.Label(frame_faturas, text="Cartão:", font=FONTE_PADRAO).grid(row=0, column=0, padx=5, pady=5)
cartao_combo = ttk.Combobox(frame_faturas, values=faturas, state="readonly", width=30)
cartao_combo.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_faturas, text="Descrição da Compra:", font=FONTE_PADRAO).grid(row=1, column=0, padx=5, pady=5)
descricao_compra_entry = ttk.Entry(frame_faturas, width=40)
descricao_compra_entry.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(frame_faturas, text="Valor Total:", font=FONTE_PADRAO).grid(row=0, column=2, padx=5, pady=5)
valor_compra_entry = ttk.Entry(frame_faturas, width=20)
valor_compra_entry.grid(row=0, column=3, padx=5, pady=5)
valor_compra_entry.bind("<KeyRelease>", lambda event: formatar_valor(event, valor_compra_entry))

ttk.Label(frame_faturas, text="Nº de Parcelas:", font=FONTE_PADRAO).grid(row=1, column=2, padx=5, pady=5)
parcelas_entry = ttk.Entry(frame_faturas, width=10)
parcelas_entry.grid(row=1, column=3, padx=5, pady=5)

ttk.Label(frame_faturas, text="Mês/Ano Vencimento:", font=FONTE_PADRAO).grid(row=2, column=0, padx=5, pady=5)
mes_vencimento_combo = ttk.Combobox(frame_faturas, values=meses_nomes, state="readonly", width=15)
mes_vencimento_combo.grid(row=2, column=1, padx=5, pady=5)

ano_atual_vencimento = datetime.now().year
anos_vencimento = [str(ano) for ano in range(ano_atual_vencimento, ano_atual_vencimento + 5)]
ano_vencimento_combo = ttk.Combobox(frame_faturas, values=anos_vencimento, state="readonly", width=10)
ano_vencimento_combo.grid(row=2, column=2, padx=5, pady=5)

ttk.Button(frame_faturas, text="Adicionar Fatura", command=lambda: adicionar_fatura_parcelada(cartao_combo, valor_compra_entry, parcelas_entry, descricao_compra_entry, mes_vencimento_combo, ano_vencimento_combo)).grid(row=3, column=0, columnspan=4, pady=10)


# --- Aba de Visualização ---
aba_visualizacao = ttk.Frame(notebook)
notebook.add(aba_visualizacao, text="Visualização")
scrollable_visualizacao = add_scrollbar(aba_visualizacao)

# Frame para seleção de mês e ano
frame_periodo = ttk.LabelFrame(scrollable_visualizacao, text="Seleção de Período", padding="10")
frame_periodo.pack(pady=10, padx=10, fill="x")

ttk.Label(frame_periodo, text="Mês:", font=FONTE_PADRAO).pack(side=tk.LEFT, padx=5)
combo_mes = ttk.Combobox(frame_periodo, values=meses_nomes, state="readonly", width=15)
combo_mes.set(meses[MES_ATUAL-1][1])
combo_mes.pack(side=tk.LEFT, padx=5)

ttk.Label(frame_periodo, text="Ano:", font=FONTE_PADRAO).pack(side=tk.LEFT, padx=5)
combo_ano = ttk.Combobox(frame_periodo, values=anos, state="readonly", width=10)
combo_ano.set(ANO_ATUAL)
combo_ano.pack(side=tk.LEFT, padx=5)

combo_mes.bind("<<ComboboxSelected>>", carregar_mes_selecionado)
combo_ano.bind("<<ComboboxSelected>>", carregar_mes_selecionado)

# Botões de ação
btn_refresh = ttk.Button(frame_periodo, text="Atualizar Dados", command=forcar_atualizacao)
btn_refresh.pack(side=tk.LEFT, padx=10)

btn_pdf = ttk.Button(frame_periodo, text="Gerar Relatório PDF", command=gerar_relatorio_pdf)
btn_pdf.pack(side=tk.LEFT, padx=10)

btn_chart = ttk.Button(frame_periodo, text="Gerar Gráfico", command=gerar_grafico_orcamento)
btn_chart.pack(side=tk.LEFT, padx=10)

btn_caixa_inicial = ttk.Button(frame_periodo, text="Definir Saldo Inicial CC", command=set_caixa_inicial)
btn_caixa_inicial.pack(side=tk.LEFT, padx=10)


# Treeview de Entradas
frame_tabela_entradas = ttk.LabelFrame(scrollable_visualizacao, text="Entradas", padding="10")
frame_tabela_entradas.pack(pady=5, padx=10, fill="both", expand=True)

tree_entradas = ttk.Treeview(frame_tabela_entradas, columns=('Descrição', 'Valor', 'Observações', 'Data'), show='headings')
tree_entradas.heading('Descrição', text='Descrição')
tree_entradas.heading('Valor', text='Valor')
tree_entradas.heading('Observações', text='Observações')
tree_entradas.heading('Data', text='Data')
tree_entradas.column('Descrição', width=200, anchor='w')
tree_entradas.column('Valor', width=100, anchor='e')
tree_entradas.column('Observações', width=200, anchor='w')
tree_entradas.column('Data', width=100, anchor='e')
tree_entradas.pack(fill="both", expand=True)

ttk.Label(frame_tabela_entradas, text="Total: R$ 0,00", font=FONTE_PADRAO).pack(anchor='e', pady=5)
lbl_entradas_total = ttk.Label(frame_tabela_entradas, text="Total: R$ 0,00", font=FONTE_PADRAO)
lbl_entradas_total.pack(anchor='e', pady=5)
btn_excluir_entrada = ttk.Button(frame_tabela_entradas, text="Excluir Entrada", command=lambda: excluir_transacao(tree_entradas, 'entradas'))
btn_excluir_entrada.pack(pady=5, padx=5, side='right')


# Treeview de Despesas
frame_tabela_despesas = ttk.LabelFrame(scrollable_visualizacao, text="Despesas", padding="10")
frame_tabela_despesas.pack(pady=5, padx=10, fill="both", expand=True)

tree_despesas = ttk.Treeview(frame_tabela_despesas, columns=('Descrição', 'Valor', 'Observações', 'Data'), show='headings')
tree_despesas.heading('Descrição', text='Descrição')
tree_despesas.heading('Valor', text='Valor')
tree_despesas.heading('Observações', text='Observações')
tree_despesas.heading('Data', text='Data')
tree_despesas.column('Descrição', width=200, anchor='w')
tree_despesas.column('Valor', width=100, anchor='e')
tree_despesas.column('Observações', width=200, anchor='w')
tree_despesas.column('Data', width=100, anchor='e')
tree_despesas.pack(fill="both", expand=True)

lbl_despesas_total = ttk.Label(frame_tabela_despesas, text="Total: R$ 0,00", font=FONTE_PADRAO)
lbl_despesas_pct = ttk.Label(frame_tabela_despesas, text="(0,00%)", font=FONTE_PADRAO)
lbl_despesas_total.pack(anchor='e', pady=5)
lbl_despesas_pct.pack(anchor='e', padx=5)
btn_excluir_despesa = ttk.Button(frame_tabela_despesas, text="Excluir Despesa", command=lambda: excluir_transacao(tree_despesas, 'despesas'))
btn_excluir_despesa.pack(pady=5, padx=5, side='right')

# Treeview de Investimentos
frame_tabela_investimentos = ttk.LabelFrame(scrollable_visualizacao, text="Investimentos", padding="10")
frame_tabela_investimentos.pack(pady=5, padx=10, fill="both", expand=True)

tree_investimentos = ttk.Treeview(frame_tabela_investimentos, columns=('Descrição', 'Valor', 'Observações', 'Data'), show='headings')
tree_investimentos.heading('Descrição', text='Descrição')
tree_investimentos.heading('Valor', text='Valor')
tree_investimentos.heading('Observações', text='Observações')
tree_investimentos.heading('Data', text='Data')
tree_investimentos.column('Descrição', width=200, anchor='w')
tree_investimentos.column('Valor', width=100, anchor='e')
tree_investimentos.column('Observações', width=200, anchor='w')
tree_investimentos.column('Data', width=100, anchor='e')
tree_investimentos.pack(fill="both", expand=True)

lbl_investimentos_total = ttk.Label(frame_tabela_investimentos, text="Total: R$ 0,00", font=FONTE_PADRAO)
lbl_investimentos_pct = ttk.Label(frame_tabela_investimentos, text="(0,00%)", font=FONTE_PADRAO)
lbl_investimentos_total.pack(anchor='e', pady=5)
lbl_investimentos_pct.pack(anchor='e', padx=5)
btn_excluir_investimento = ttk.Button(frame_tabela_investimentos, text="Excluir Investimento", command=lambda: excluir_transacao(tree_investimentos, 'investimentos'))
btn_excluir_investimento.pack(pady=5, padx=5, side='right')


# --- Aba de Resumo ---
aba_resumo = ttk.Frame(notebook)
notebook.add(aba_resumo, text="Resumo e Caixas")
scrollable_resumo = add_scrollbar(aba_resumo)

# Frame de totais
frame_resumo_geral = ttk.LabelFrame(scrollable_resumo, text="Resumo do Mês", padding="10")
frame_resumo_geral.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

total_entradas_var = tk.StringVar(value="R$ 0,00")
total_despesas_var = tk.StringVar(value="R$ 0,00")
total_investimentos_var = tk.StringVar(value="R$ 0,00")
saldo_total_var = tk.StringVar(value="R$ 0,00")
pct_investimento_var = tk.StringVar(value="0,00%")

ttk.Label(frame_resumo_geral, text="Total de Entradas:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
ttk.Label(frame_resumo_geral, textvariable=total_entradas_var, font=FONTE_TITULO).grid(row=0, column=1, sticky="e", padx=5, pady=2)

ttk.Label(frame_resumo_geral, text="Total de Despesas:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
ttk.Label(frame_resumo_geral, textvariable=total_despesas_var, font=FONTE_TITULO).grid(row=1, column=1, sticky="e", padx=5, pady=2)

ttk.Label(frame_resumo_geral, text="Total de Investimentos:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
ttk.Label(frame_resumo_geral, textvariable=total_investimentos_var, font=FONTE_TITULO).grid(row=2, column=1, sticky="e", padx=5, pady=2)

ttk.Label(frame_resumo_geral, text="Saldo do Mês (Entradas - Despesas):").grid(row=3, column=0, sticky="w", padx=5, pady=2)
ttk.Label(frame_resumo_geral, textvariable=saldo_total_var, font=FONTE_TITULO).grid(row=3, column=1, sticky="e", padx=5, pady=2)

ttk.Label(frame_resumo_geral, text="Pct. de Investimento sobre a Receita:").grid(row=4, column=0, sticky="w", padx=5, pady=2)
ttk.Label(frame_resumo_geral, textvariable=pct_investimento_var, font=FONTE_TITULO).grid(row=4, column=1, sticky="e", padx=5, pady=2)


# Frame de caixas
frame_caixas = ttk.LabelFrame(scrollable_resumo, text="Saldos das Contas", padding="10")
frame_caixas.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

caixa_cc_var = tk.StringVar(value="R$ 0,00")
caixa_invest_var = tk.StringVar(value="R$ 0,00")
caixa_total_var = tk.StringVar(value="R$ 0,00")

ttk.Label(frame_caixas, text="Saldo Conta Corrente:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
ttk.Label(frame_caixas, textvariable=caixa_cc_var, font=FONTE_TITULO).grid(row=0, column=1, sticky="e", padx=5, pady=2)

ttk.Label(frame_caixas, text="Saldo Total de Investimentos:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
ttk.Label(frame_caixas, textvariable=caixa_invest_var, font=FONTE_TITULO).grid(row=1, column=1, sticky="e", padx=5, pady=2)

ttk.Label(frame_caixas, text="Saldo Total (CC + Investimentos):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
ttk.Label(frame_caixas, textvariable=caixa_total_var, font=FONTE_TITULO).grid(row=2, column=1, sticky="e", padx=5, pady=2)


# Treeview do caixa de investimentos detalhado
frame_caixa_investimentos = ttk.LabelFrame(scrollable_resumo, text="Detalhe de Investimentos (Variação Mês a Mês)", padding="10")
frame_caixa_investimentos.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

tree_caixa_investimentos = ttk.Treeview(frame_caixa_investimentos, columns=('Tipo', 'Valor', 'Variação %'), show='headings')
tree_caixa_investimentos.heading('Tipo', text='Tipo de Investimento')
tree_caixa_investimentos.heading('Valor', text='Valor')
tree_caixa_investimentos.heading('Variação %', text='Variação %')
tree_caixa_investimentos.column('Tipo', width=200, anchor='w')
tree_caixa_investimentos.column('Valor', width=150, anchor='e')
tree_caixa_investimentos.column('Variação %', width=150, anchor='e')
tree_caixa_investimentos.pack(fill="both", expand=True)

# Ligar o evento de clique do botão direito
tree_caixa_investimentos.bind("<Button-3>", show_context_menu)

# --- Aba de Comparativos ---
aba_comparativos = ttk.Frame(notebook)
notebook.add(aba_comparativos, text="Comparativos")
scrollable_comparativos = add_scrollbar(aba_comparativos)

# Frame de Comparativo de Despesas
frame_comparativo_despesas = ttk.LabelFrame(scrollable_comparativos, text="Comparativo de Despesas (Mês Atual vs. Mês Anterior)", padding="10")
frame_comparativo_despesas.pack(pady=10, padx=10, fill="both", expand=True)

tree_comparativo = ttk.Treeview(frame_comparativo_despesas, columns=('Categoria', 'Valor Atual', 'Variação', '% Variação'), show='headings')
tree_comparativo.heading('Categoria', text='Categoria')
tree_comparativo.heading('Valor Atual', text='Valor Atual')
tree_comparativo.heading('Variação', text='Variação (R$)')
tree_comparativo.heading('% Variação', text='% Variação')
tree_comparativo.column('Categoria', width=250, anchor='w')
tree_comparativo.column('Valor Atual', width=150, anchor='e')
tree_comparativo.column('Variação', width=150, anchor='e')
tree_comparativo.column('% Variação', width=100, anchor='e')
tree_comparativo.pack(fill="both", expand=True)

# --- Aba de Parcelamentos ---
aba_parcelamentos = ttk.Frame(notebook)
notebook.add(aba_parcelamentos, text="Faturas Parceladas")
scrollable_parcelamentos = add_scrollbar(aba_parcelamentos)

frame_tabela_parcelamentos = ttk.LabelFrame(scrollable_parcelamentos, text="Faturas Parceladas", padding="10")
frame_tabela_parcelamentos.pack(pady=10, padx=10, fill="both", expand=True)

tree_cartoes_parcelados = ttk.Treeview(frame_tabela_parcelamentos, columns=('Cartão', 'Descrição', 'Valor Parcela', 'Parcelas Restantes', 'Data de Início'), show='headings')
tree_cartoes_parcelados.heading('Cartão', text='Cartão')
tree_cartoes_parcelados.heading('Descrição', text='Descrição')
tree_cartoes_parcelados.heading('Valor Parcela', text='Valor Parcela')
tree_cartoes_parcelados.heading('Parcelas Restantes', text='Parcelas Restantes')
tree_cartoes_parcelados.heading('Data de Início', text='Data de Início')
tree_cartoes_parcelados.pack(fill="both", expand=True)

btn_excluir_parcelada = ttk.Button(frame_tabela_parcelamentos, text="Excluir Fatura Parcelada", command=lambda: excluir_fatura_parcelada(tree_cartoes_parcelados))
btn_excluir_parcelada.pack(pady=5, padx=5, side='right')


# --- Inicialização ---
atualizar_tabelas_e_resumo()

# Rodapé
ttk.Label(janela, text="Criado por Gustavo Januzi Agosto 2025", font=('Helvetica', 9)).pack(side=tk.BOTTOM, pady=5)

janela.mainloop()