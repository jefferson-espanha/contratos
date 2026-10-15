import os
import psycopg2
from psycopg2.extras import RealDictCursor
from nicegui import app, ui

# Libera arquivos estáticos
app.add_static_files('/static', '.')

# String de Conexão do PostgreSQL (Neon)
DATABASE_URL = "postgresql://neondb_owner:npg_a1JMVwqSUdK6@ep-dawn-recipe-b8arzc2o-pooler.c-14.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Helper para obter conexão com o BD
def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# Inicializa a tabela no PostgreSQL se não existir
def inicializar_banco():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS contratos_aditivos (
                id SERIAL PRIMARY KEY,
                num_contrato VARCHAR(100) NOT NULL,
                num_aditivo VARCHAR(100),
                objeto TEXT NOT NULL,
                empresa VARCHAR(255) NOT NULL,
                data_inicio DATE,
                data_termino DATE,
                gestor VARCHAR(255),
                fiscal VARCHAR(255),
                link_contrato TEXT
            );
        """)
        
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {e}")

# Executa a inicialização do banco ao carregar o script
inicializar_banco()

@ui.page('/')
def contratos_page():
    ui.colors(primary='#1e3a8a')

    # Cabeçalho da Página
    with ui.header().classes('bg-blue-950 text-white p-4 flex justify-between items-center shadow-lg'):
        with ui.row().classes('items-center gap-3'):
            ui.icon('assignment', size='32px').classes('text-blue-300')
            ui.label('Procuradoria do Município').classes('text-2xl font-bold tracking-wide')
        
        ui.button(
            'Voltar ao Portal', 
            on_click=lambda: ui.open('https://portal-sistemas-procuradoria.onrender.com')
        ).classes('bg-blue-800 text-white text-sm')

    # Container Principal
    with ui.column().classes('w-full p-6 max-w-7xl mx-auto items-center'):
        
        # Título
        with ui.column().classes('text-center my-2 w-full items-center'):
            ui.label('Módulo de Contratos e Aditivos').classes('text-3xl font-extrabold text-gray-800 mb-1')
            ui.label('Cadastre e acompanhe os contratos, aditivos, gestores e vigências:').classes('text-base text-gray-600')

        # Form de Cadastro de Novo Contrato
        with ui.card().classes('w-full p-6 shadow-md rounded-xl border border-gray-200 bg-white my-4'):
            ui.label('Novo Contrato / Aditivo').classes('text-lg font-bold text-gray-800 mb-2')
            
            with ui.column().classes('w-full gap-4'):
                
                # Linha 1: Nº Contrato + Nº Aditivo + Empresa Contratada
                with ui.row().classes('w-full gap-4 flex-col sm:flex-row'):
                    num_contrato = ui.input(
                        label='Nº do Contrato:', 
                        placeholder='Ex: 045/2026'
                    ).classes('w-full sm:w-1/3').props('outlined dense')
                    
                    num_aditivo = ui.input(
                        label='Nº do Aditivo:', 
                        placeholder='Ex: 01/2026 (opcional)'
                    ).classes('w-full sm:w-1/3').props('outlined dense')
                    
                    empresa = ui.input(
                        label='Empresa Contratada:', 
                        placeholder='Ex: Construtora Exemplo LTDA'
                    ).classes('w-full sm:w-1/3').props('outlined dense')

                # Linha 2: Objeto do Contrato (Autogrow)
                objeto = ui.textarea(
                    label='Objeto do Contrato:', 
                    placeholder='Descrição detalhada do objeto contratado...'
                ).classes('w-full').props('outlined dense autogrow rows=1')

                # Linha 3: Vigência (Início e Término)
                with ui.row().classes('w-full gap-4 flex-col sm:flex-row'):
                    data_inicio = ui.input(
                        label='Data de Início:'
                    ).classes('w-full sm:w-1/2').props('outlined dense type="date"')
                    
                    data_termino = ui.input(
                        label='Data de Término:'
                    ).classes('w-full sm:w-1/2').props('outlined dense type="date"')

                # Linha 4: Gestor + Fiscal + Link do Contrato
                with ui.row().classes('w-full gap-4 flex-col sm:flex-row'):
                    gestor = ui.input(
                        label='Gestor do Contrato:', 
                        placeholder='Ex: João da Silva'
                    ).classes('w-full sm:w-1/3').props('outlined dense')
                    
                    fiscal = ui.input(
                        label='Fiscal do Contrato:', 
                        placeholder='Ex: Maria Oliveira'
                    ).classes('w-full sm:w-1/3').props('outlined dense')
                    
                    link_contrato = ui.input(
                        label='Link do Contrato (URL):', 
                        placeholder='https://...'
                    ).classes('w-full sm:w-1/3').props('outlined dense')

                # Cadastrar Contrato no PostgreSQL
                def salvar_contrato():
                    if not num_contrato.value or not objeto.value or not empresa.value:
                        ui.notify('Preencha os campos obrigatórios: Nº do Contrato, Objeto e Empresa!', type='warning')
                        return
                    
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute("""
                            INSERT INTO contratos_aditivos 
                            (num_contrato, num_aditivo, objeto, empresa, data_inicio, data_termino, gestor, fiscal, link_contrato)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                        """, (
                            num_contrato.value,
                            num_aditivo.value or '-',
                            objeto.value,
                            empresa.value,
                            data_inicio.value or None,
                            data_termino.value or None,
                            gestor.value or '-',
                            fiscal.value or '-',
                            link_contrato.value or ''
                        ))
                        conn.commit()
                        cur.close()
                        conn.close()

                        atualizar_tabela()
                        
                        # Limpeza dos campos
                        num_contrato.value = ''
                        num_aditivo.value = ''
                        objeto.value = ''
                        empresa.value = ''
                        data_inicio.value = ''
                        data_termino.value = ''
                        gestor.value = ''
                        fiscal.value = ''
                        link_contrato.value = ''
                        
                        ui.notify('Contrato cadastrado e salvo no PostgreSQL!', type='positive')
                    except Exception as err:
                        ui.notify(f'Erro ao salvar contrato: {err}', type='negative')

                with ui.row().classes('w-full justify-end mt-2'):
                    ui.button(
                        'Adicionar Contrato', 
                        icon='add', 
                        on_click=salvar_contrato
                    ).classes('bg-blue-900 text-white font-bold py-2 px-6 rounded-lg shadow-md')

        # Seção de Tabela de Informações
        with ui.column().classes('w-full mt-4'):
            with ui.row().classes('w-full justify-between items-center mb-2'):
                ui.label('Contratos Cadastrados (Duplo clique para Alterar / Excluir)').classes('text-lg font-bold text-gray-800')
                ui.button(
                    'Gerar Relatório PDF 🖨️', 
                    on_click=gerar_pdf_relatorio
                ).classes('bg-emerald-800 text-white text-xs font-bold py-2 px-4 rounded-lg shadow-sm')

            colunas = [
                {'name': 'num_contrato', 'label': 'Nº Contrato', 'field': 'num_contrato', 'align': 'left', 'sortable': True},
                {'name': 'num_aditivo', 'label': 'Nº Aditivo', 'field': 'num_aditivo', 'align': 'left', 'sortable': True},
                {'name': 'empresa', 'label': 'Empresa Contratada', 'field': 'empresa', 'align': 'left', 'sortable': True},
                {'name': 'objeto', 'label': 'Objeto', 'field': 'objeto', 'align': 'left'},
                {'name': 'vigencia', 'label': 'Vigência (Início - Término)', 'field': 'vigencia', 'align': 'center'},
                {'name': 'gestor', 'label': 'Gestor', 'field': 'gestor', 'align': 'left'},
                {'name': 'fiscal', 'label': 'Fiscal', 'field': 'fiscal', 'align': 'left'},
                {'name': 'link_contrato', 'label': 'Documento', 'field': 'link_contrato', 'align': 'center'},
            ]

            tabela = ui.table(columns=colunas, rows=[], row_key='id').classes('w-full shadow-md rounded-xl border border-gray-100 bg-white cursor-pointer')
            
            # Formatação da coluna do link do documento na tabela
            tabela.add_slot('body-cell-link_contrato', '''
                <q-td :props="props">
                    <a v-if="props.value" :href="props.value" target="_blank" class="text-blue-700 font-bold underline">Acessar Link ↗</a>
                    <span v-else class="text-gray-400">-</span>
                </q-td>
            ''')

            # Modal de Alteração / Exclusão por duplo clique
            with ui.dialog() as modal_edicao, ui.card().classes('w-full max-w-lg p-6'):
                ui.label('Editar / Excluir Contrato').classes('text-xl font-bold mb-4 text-gray-800')
                
                edit_id = ui.input('ID').classes('hidden')
                edit_num_contrato = ui.input('Nº do Contrato').classes('w-full').props('outlined dense')
                edit_num_aditivo = ui.input('Nº do Aditivo').classes('w-full').props('outlined dense')
                edit_empresa = ui.input('Empresa Contratada').classes('w-full').props('outlined dense')
                edit_objeto = ui.textarea('Objeto do Contrato').classes('w-full').props('outlined dense autogrow rows=1')
                
                with ui.row().classes('w-full gap-2'):
                    edit_inicio = ui.input('Data Início').classes('w-1/2').props('outlined dense type="date"')
                    edit_termino = ui.input('Data Término').classes('w-1/2').props('outlined dense type="date"')
                
                with ui.row().classes('w-full gap-2'):
                    edit_gestor = ui.input('Gestor').classes('w-1/2').props('outlined dense')
                    edit_fiscal = ui.input('Fiscal').classes('w-1/2').props('outlined dense')
                    
                edit_link = ui.input('Link do Contrato').classes('w-full').props('outlined dense')

                def salvar_edicao():
                    if not edit_num_contrato.value or not edit_objeto.value or not edit_empresa.value:
                        ui.notify('Campos obrigatórios não podem ficar vazios!', type='warning')
                        return

                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute("""
                            UPDATE contratos_aditivos
                            SET num_contrato = %s, num_aditivo = %s, empresa = %s, objeto = %s, 
                                data_inicio = %s, data_termino = %s, gestor = %s, fiscal = %s, link_contrato = %s
                            WHERE id = %s;
                        """, (
                            edit_num_contrato.value,
                            edit_num_aditivo.value or '-',
                            edit_empresa.value,
                            edit_objeto.value,
                            edit_inicio.value or None,
                            edit_termino.value or None,
                            edit_gestor.value or '-',
                            edit_fiscal.value or '-',
                            edit_link.value or '',
                            int(edit_id.value)
                        ))
                        conn.commit()
                        cur.close()
                        conn.close()

                        atualizar_tabela()
                        modal_edicao.close()
                        ui.notify('Contrato atualizado no PostgreSQL!', type='positive')
                    except Exception as err:
                        ui.notify(f'Erro ao atualizar contrato: {err}', type='negative')

                def excluir_contrato():
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute("DELETE FROM contratos_aditivos WHERE id = %s;", (int(edit_id.value),))
                        conn.commit()
                        cur.close()
                        conn.close()

                        atualizar_tabela()
                        modal_edicao.close()
                        ui.notify('Contrato excluído do PostgreSQL!', type='negative')
                    except Exception as err:
                        ui.notify(f'Erro ao excluir contrato: {err}', type='negative')

                with ui.row().classes('w-full justify-between mt-4'):
                    ui.button('Excluir Contrato', color='red', on_click=excluir_contrato).classes('text-white')
                    with ui.row().classes('gap-2'):
                        ui.button('Cancelar', on_click=modal_edicao.close).props('flat')
                        ui.button('Salvar Alterações', color='primary', on_click=salvar_edicao)

            # Ação de Duplo Clique na linha da tabela
            def on_row_dblclick(e):
                row = e.args[1]
                edit_id.value = str(row['id'])
                edit_num_contrato.value = row['num_contrato']
                edit_num_aditivo.value = row.get('num_aditivo', '')
                edit_empresa.value = row['empresa']
                edit_objeto.value = row['objeto']
                edit_inicio.value = str(row.get('raw_inicio', '')) if row.get('raw_inicio') else ''
                edit_termino.value = str(row.get('raw_termino', '')) if row.get('raw_termino') else ''
                edit_gestor.value = row.get('gestor', '')
                edit_fiscal.value = row.get('fiscal', '')
                edit_link.value = row.get('link_contrato', '')
                modal_edicao.open()

            tabela.on('row-dblclick', on_row_dblclick)

    # Consulta e Atualização da Tabela
    def atualizar_tabela():
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT id, num_contrato, num_aditivo, objeto, empresa, 
                       data_inicio, data_termino, gestor, fiscal, link_contrato
                FROM contratos_aditivos
                ORDER BY id DESC;
            """)
            contratos = cur.fetchall()
            cur.close()
            conn.close()

            rows = []
            for c in contratos:
                inicio_str = c['data_inicio'].strftime('%d/%m/%Y') if c['data_inicio'] else '-'
                termino_str = c['data_termino'].strftime('%d/%m/%Y') if c['data_termino'] else '-'
                vigencia = f"{inicio_str} a {termino_str}"
                
                rows.append({
                    'id': c['id'],
                    'num_contrato': c['num_contrato'],
                    'num_aditivo': c['num_aditivo'] or '-',
                    'empresa': c['empresa'],
                    'objeto': c['objeto'],
                    'vigencia': vigencia,
                    'raw_inicio': c['data_inicio'],
                    'raw_termino': c['data_termino'],
                    'gestor': c['gestor'] or '-',
                    'fiscal': c['fiscal'] or '-',
                    'link_contrato': c['link_contrato'] or ''
                })

            tabela.rows = rows
            tabela.update()
        except Exception as err:
            ui.notify(f'Erro ao carregar contratos: {err}', type='negative')

    # Carrega os dados na inicialização
    atualizar_tabela()

    # Rodapé
    with ui.footer().classes('bg-gray-100 text-gray-600 p-4 text-center text-sm border-t mt-12'):
        ui.label('Prefeitura Municipal de Francisco Morato — Procuradoria do Município © 2026')

# Gerador do Relatório em PDF
def gerar_pdf_relatorio():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT num_contrato, num_aditivo, empresa, objeto, data_inicio, data_termino, gestor, fiscal
            FROM contratos_aditivos
            ORDER BY id DESC;
        """)
        contratos = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as err:
        ui.notify(f'Erro ao buscar contratos para o relatório: {err}', type='negative')
        return

    linhas_html = ""
    for c in contratos:
        inicio_str = c['data_inicio'].strftime('%d/%m/%Y') if c['data_inicio'] else '-'
        termino_str = c['data_termino'].strftime('%d/%m/%Y') if c['data_termino'] else '-'
        
        linhas_html += f"""
        <tr>
            <td>{c['num_contrato']}</td>
            <td>{c['num_aditivo'] or '-'}</td>
            <td>{c['empresa']}</td>
            <td>{c['objeto']}</td>
            <td>{inicio_str} a {termino_str}</td>
            <td>{c['gestor'] or '-'}</td>
            <td>{c['fiscal'] or '-'}</td>
        </tr>
        """
        
    html_relatorio = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Relatório de Contratos - Procuradoria</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; color: #333; }}
            h1 {{ text-align: center; color: #1e3a8a; margin-bottom: 5px; }}
            h3 {{ text-align: center; color: #555; font-weight: normal; margin-top: 0; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 11px; }}
            th, td {{ border: 1px solid #ccc; padding: 6px; text-align: left; }}
            th {{ background-color: #1e3a8a; color: white; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
        </style>
    </head>
    <body onload="window.print()">
        <h1>PREFEITURA MUNICIPAL DE FRANCISCO MORATO</h1>
        <h3>Procuradoria do Município — Relatório de Contratos e Aditivos</h3>
        <hr>
        <table>
            <thead>
                <tr>
                    <th>Nº Contrato</th>
                    <th>Nº Aditivo</th>
                    <th>Empresa</th>
                    <th>Objeto</th>
                    <th>Vigência</th>
                    <th>Gestor</th>
                    <th>Fiscal</th>
                </tr>
            </thead>
            <tbody>
                {linhas_html if linhas_html else '<tr><td colspan="7" style="text-align:center;">Nenhum contrato cadastrado.</td></tr>'}
            </tbody>
        </table>
    </body>
    </html>
    """
    
    ui.run_javascript(f"""
        var win = window.open("", "_blank");
        win.document.write(`{html_relatorio}`);
        win.document.close();
    """)

if __name__ in {"__main__", "__mp_main__"}:
    PORT = int(os.environ.get('PORT', 8080))
    ui.run(host='0.0.0.0', port=PORT, reload=False)
