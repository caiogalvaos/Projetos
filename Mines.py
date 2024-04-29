import tkinter as tk
from random import shuffle
from tkinter.messagebox import showinfo, showerror
from PIL import ImageTk, Image

cores = {
    1: '#0000FF',
    2: '#008200',
    3: '#FF0000',
    4: '#000084',
    5: '#840000',
    6: '#008284',
    7: '#840084',
    8: '#800020'
}

class MeuBotao(tk.Button):
    def __init__(self, master, x, y, number=0, *args, **kwargs):
        super(MeuBotao, self).__init__(
                master, *args, **kwargs, width=3, font='Calibri 15 bold')
        self.x = x
        self.y = y
        self.numero = number
        self.e_bomba = False
        self.contagem_bomba = 0
        self.foi_aberto = False
    
    def __repr__(self):
        return f'MeuBotao{self.x} {self.y} {self.numero} {self.e_bomba}'

class CampoMinado:
    
    janela = tk.Tk()
    LINHAS = 10
    COLUNAS = 7
    BOMBAS = 7
    FIM_DE_JOGO = False
    PRIMEIRO_CLIQUE = True
    janela.geometry('+800+200')

    img_band = ImageTk.PhotoImage(Image.open("img/flag.png"))
    img_bomba = ImageTk.PhotoImage(Image.open("img/mine.png"))
  
    def __init__(self):
        self.botoes = []
        for i in range(CampoMinado.LINHAS+2):
            temp = []
            for j in range(CampoMinado.COLUNAS+2):
                btn = MeuBotao(CampoMinado.janela, x=i, y=j)
                btn.config(command=lambda button=btn: self.clicar(button))
                btn.bind('<Button-3>', self.clique_direito)
                temp.append(btn)
            self.botoes.append(temp)
  
    def clique_direito(self, event):
        if CampoMinado.FIM_DE_JOGO:
            return
        cur_btn = event.widget
        if cur_btn['state'] == 'normal':
            cur_btn['state'] = 'disabled'
            cur_btn['image'] = self.img_band
        elif cur_btn['state'] == 'disabled':
            cur_btn['image'] = ''
            cur_btn['state'] = 'normal'
 
    def clicar(self, botao_clicado: MeuBotao):
        if CampoMinado.FIM_DE_JOGO:
            return
        if CampoMinado.PRIMEIRO_CLIQUE:
            self.inserir_bombas(botao_clicado.numero)
            self.contar_bomba_em_botoes()
            self.imprimir_botoes()
            CampoMinado.PRIMEIRO_CLIQUE = False
        if botao_clicado.e_bomba:
            botao_clicado.config(image=self.img_bomba, background='red',
                                  disabledforeground='black')
            botao_clicado.foi_aberto = True
            CampoMinado.FIM_DE_JOGO = True
            showinfo('Fim de Jogo', 'Você perdeu!')
            for i in range(1, CampoMinado.LINHAS+1):
                for j in range(1, CampoMinado.COLUNAS+1):
                    btn = self.botoes[i][j]
                    if btn.e_bomba:
                        btn['image'] = self.img_bomba
        else:
            cor = cores.get(botao_clicado.contagem_bomba, 'black')
            if botao_clicado.contagem_bomba:
                botao_clicado.config(text=botao_clicado.contagem_bomba,
                                      disabledforeground=cor)
                botao_clicado.foi_aberto = True
            else:
                self.busca_em_largura(botao_clicado)
        botao_clicado.config(state='disabled')
        botao_clicado.config(relief=tk.SUNKEN)
    
    def busca_em_largura(self, btn: MeuBotao):
        fila = [btn]
        while fila:
            
            btn_atual = fila.pop()
            cor = cores.get(btn_atual.contagem_bomba, 'black')
            if btn_atual.contagem_bomba:
                btn_atual.config(text=btn_atual.contagem_bomba,
                               disabledforeground=cor)
            else:
                btn_atual.config(text='', disabledforeground=cor)
            btn_atual.foi_aberto = True
            btn_atual.config(state='disabled')
            btn_atual.config(relief=tk.SUNKEN)
            if btn_atual.contagem_bomba == 0:
                x, y = btn_atual.x, btn_atual.y
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        proximo_btn = self.botoes[x+dx][y+dy]
                        if not proximo_btn.foi_aberto and 1<=proximo_btn.x<=CampoMinado.LINHAS and \
                                1<=proximo_btn.y<=CampoMinado.COLUNAS and proximo_btn not in fila:
                            fila.append(proximo_btn)
            
    def recarregar(self):
        [child.destroy() for child in self.janela.winfo_children()]
        self.__init__()
        self.criar_widgets()
        CampoMinado.PRIMEIRO_CLIQUE = True
        CampoMinado.FIM_DE_JOGO = False
    
    def criar_janela_de_configuracoes(self):
        janela_configuracoes = tk.Toplevel(self.janela)
        janela_configuracoes.wm_title('Configurações')
        tk.Label(janela_configuracoes, text='Linhas').grid(row=0, column=0)
        linha_entrada = tk.Entry(janela_configuracoes)
        linha_entrada.insert(0, CampoMinado.LINHAS)
        linha_entrada.grid(row=0, column=1, padx=20, pady=20)
        tk.Label(janela_configuracoes, text='Colunas').grid(row=1, column=0)
        coluna_entrada = tk.Entry(janela_configuracoes)
        coluna_entrada.insert(0, CampoMinado.COLUNAS)
        coluna_entrada.grid(row=1, column=1, padx=20, pady=20)
        tk.Label(janela_configuracoes, text='Bombas').grid(row=2, column=0)
        bomba_entrada = tk.Entry(janela_configuracoes)
        bomba_entrada.insert(0, CampoMinado.BOMBAS)
        bomba_entrada.grid(row=2, column=1, padx=20, pady=20)
        salvar_btn = tk.Button(janela_configuracoes, text='Aplicar', 
                  command=lambda: self.mudar_configuracoes(linha_entrada, coluna_entrada, bomba_entrada))
        salvar_btn.grid(row=3, column=8, columnspan=2, padx=20, pady=20)
        janela_configuracoes.geometry('+790+300')
    
    def mudar_configuracoes(self, linha: tk.Entry, coluna: tk.Entry, bomba: tk.Entry):
        try:
            int(linha.get()), int(coluna.get()), int(bomba.get())
        except ValueError:
            showerror('Erro', 'Entrada incorreta')
            return
        CampoMinado.LINHAS = int(linha.get())
        CampoMinado.COLUNAS = int(coluna.get())
        CampoMinado.BOMBAS = int(bomba.get())
        self.recarregar()
    
    def criar_widgets(self):
        barra_de_menu = tk.Menu(self.janela)
        self.janela.config(menu=barra_de_menu)
        menu_de_configuracoes = tk.Menu(barra_de_menu, tearoff=0)
        menu_de_configuracoes.add_command(label='Jogo', command=self.recarregar)
        menu_de_configuracoes.add_command(label='Configurações', command=self.criar_janela_de_configuracoes)
        menu_de_configuracoes.add_command(label='Sair', command=self.janela.destroy)
        barra_de_menu.add_cascade(label='Arquivo', menu=menu_de_configuracoes)
        contador = 1
        for i in range(1, CampoMinado.LINHAS+1):
            for j in range(1, CampoMinado.COLUNAS+1):
                btn = self.botoes[i][j]
                btn.numero = contador
                btn.grid(row=i, column=j, stick='NWES')
                contador += 1
        for i in range(1, CampoMinado.LINHAS+1):
            tk.Grid.rowconfigure(self.janela, i, weight=1)
        for i in range(1, CampoMinado.COLUNAS+1):
            tk.Grid.columnconfigure(self.janela, i, weight=1)
    
    def abrir_todos_os_botoes(self):
        for i in range(CampoMinado.LINHAS+2):
            for j in range(CampoMinado.COLUNAS+2):
                btn = self.botoes[i][j]
                if btn.e_bomba:
                    btn.config(image=self.img_bomba, background='red', disabledforeground='black')
                elif btn.contagem_bomba in cores:
                    cor = cores.get(btn.contagem_bomba, 'black')
                    btn.config(text=btn.contagem_bomba, fg=cor)
                
    def iniciar(self):
        self.criar_widgets()
        CampoMinado.janela.mainloop()
    
    def imprimir_botoes(self):
        for i in range(1, CampoMinado.LINHAS+1):
            for j in range(1, CampoMinado.COLUNAS+1):
                btn = self.botoes[i][j]
                if btn.e_bomba:
                    print('B', end='')
                else:
                    print(btn.contagem_bomba, end='')
            print()

    def inserir_bombas(self, numero: int):
        indices_bombas = self.obter_posicoes_das_bombas(numero)
        print(indices_bombas)
        for i in range(1, CampoMinado.LINHAS+1):
            for j in range(1, CampoMinado.COLUNAS+1):
                btn = self.botoes[i][j]
                if btn.numero in indices_bombas:
                    btn.e_bomba = True
    
    def contar_bomba_em_botoes(self):
        for i in range(1, CampoMinado.LINHAS+1):
            for j in range(1, CampoMinado.COLUNAS+1):
                btn = self.botoes[i][j]
                contagem_bomba = 0
                if not btn.e_bomba:
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            vizinho = self.botoes[i+dx][j+dy]
                            if vizinho.e_bomba:
                                contagem_bomba += 1
                btn.contagem_bomba = contagem_bomba
    
    @staticmethod
    def obter_posicoes_das_bombas(excluir_numero: int):
        indices = list(range(1, CampoMinado.COLUNAS * CampoMinado.LINHAS + 1))
        print(f'Excluir número {excluir_numero}')
        indices.remove(excluir_numero)
        shuffle(indices)
        return indices[:CampoMinado.BOMBAS]

jogo = CampoMinado()
jogo.iniciar()
