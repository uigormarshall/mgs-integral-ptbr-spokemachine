# Metal Gear Solid Integral: legendas em português (pt-BR)

Tradução feita por fãs das legendas de **Metal Gear Solid Integral** (PlayStation 1, versão japonesa com áudio em inglês) para o português do Brasil.

Um projeto do **Spoke Machine**: veja os bastidores da tradução e outros projetos de jogos retrô no [blog](https://spokemachine.com.br) e no [canal do YouTube](https://www.youtube.com/channel/UCOvPz1-OJJXjhsHDjIE_oZA).

O que fica em português:

- **Cutscenes**: todas as cenas do jogo.
- **Codec**: todas as conversas por rádio.
- **Vozes durante o jogo**: a conversa de abertura, o briefing e as falas nas fases.
- **Vídeos**: as legendas dos vídeos (FMV).
- **Discos 1 e 2**: o jogo inteiro.

Também deixamos o jogo **em inglês desde a primeira vez que ele liga**. Assim você não precisa mudar o idioma no menu.

> **Importante:** este projeto **não distribui o jogo** e nenhum arquivo dele. Você precisa ter sua própria cópia do Metal Gear Solid Integral. O que está aqui são as traduções e as ferramentas que aplicam essas traduções na sua cópia e geram uma imagem nova, já traduzida.

---

## Sumário

1. [O que você precisa](#1-o-que-você-precisa)
2. [Preparando o computador](#2-preparando-o-computador)
3. [Baixando este projeto](#3-baixando-este-projeto)
4. [Colocando os discos do jogo na pasta certa](#4-colocando-os-discos-do-jogo-na-pasta-certa)
5. [Gerando a ROM traduzida](#5-gerando-a-rom-traduzida)
6. [Jogando](#6-jogando)
7. [Problemas comuns](#7-problemas-comuns)
8. [Limitações conhecidas](#8-limitações-conhecidas)
9. [Como contribuir](#9-como-contribuir)
10. [Créditos](#10-créditos)

---

## 1. O que você precisa

| Item | Detalhes |
|---|---|
| Sua cópia do jogo | *Metal Gear Solid - Integral (Japan) (En,Ja)*, **Disco 1** e **Disco 2**, no formato `.bin` + `.cue` (veja abaixo) |
| Um computador | Linux, macOS ou Windows (no Windows, com WSL; veja o passo 2) |
| Python 3.8 ou mais novo | Gratuito. Não precisa instalar nenhuma biblioteca extra |
| Cerca de 3 GB livres | Para as imagens originais e as traduzidas |

### Que versão do jogo serve?

Só serve a versão **japonesa Integral** com inglês e japonês (código `SLPM-86247` no disco 1 e `SLPM-86248` no disco 2). **Não** funciona com o Metal Gear Solid americano, europeu ou brasileiro, porque os arquivos internos são diferentes.

A imagem de cada disco precisa ser **um único arquivo `.bin`** (uma faixa só, `MODE2/2352`). É o formato normal das cópias feitas com programas de cópia de CD, como o padrão Redump. Se o seu jogo está em `.chd`, `.pbp`, `.iso` ou `.7z`, veja [Problemas comuns](#7-problemas-comuns).

Para conferir se a sua cópia é igual à que usamos para testar, calcule o MD5 dos arquivos `.bin`:

| Disco | MD5 do `.bin` original |
|---|---|
| Disco 1 | `b96cef584013df491246513c6b39a186` |
| Disco 2 | `7421e5bf758bd921f7ac39d8f4584f76` |

Se for diferente, o processo ainda pode funcionar, mas não é garantido.

> **Como calcular o MD5?** No Linux ou no macOS, abra o terminal e digite `md5sum arquivo.bin` (no macOS, `md5 arquivo.bin`). No Windows, abra o PowerShell e digite `Get-FileHash arquivo.bin -Algorithm MD5`.

---

## 2. Preparando o computador

Todo o processo roda por **comandos no terminal**. Não se assuste: você só vai copiar e colar três ou quatro comandos.

### Linux

Quase sempre o Python 3 já vem instalado. Para conferir, abra o **Terminal** e digite:

```bash
python3 --version
```

Se aparecer `Python 3.8` ou um número maior, está pronto. Se não aparecer, instale o Python:

- Ubuntu, Debian, Mint: `sudo apt install python3 git`
- Fedora: `sudo dnf install python3 git`
- Arch, Manjaro: `sudo pacman -S python git`

### macOS

Abra o **Terminal** (em Aplicativos > Utilitários) e digite `python3 --version`. Se o macOS oferecer instalar as "ferramentas de linha de comando", aceite. Isso instala o Python e o git.

### Windows

As ferramentas usam scripts do Linux. O jeito mais simples de rodar esses scripts no Windows é o **WSL**, um Linux que roda dentro do Windows, é gratuito e é oficial da Microsoft.

1. Clique no menu Iniciar, digite **PowerShell**, clique com o botão direito e escolha **Executar como administrador**.
2. Digite `wsl --install` e aperte Enter.
3. Reinicie o computador quando ele pedir.
4. Depois de reiniciar, abra o **Ubuntu** pelo menu Iniciar. Na primeira vez, ele pede para você criar um usuário e uma senha. Pode ser qualquer um.
5. Na janela do Ubuntu, digite:
   ```bash
   sudo apt update && sudo apt install -y python3 git
   ```

A partir daqui, **todos os comandos deste guia devem ser digitados na janela do Ubuntu**.

> **Dica para o Windows:** dentro do Ubuntu, o seu disco `C:` aparece como `/mnt/c`. Por exemplo, a pasta Downloads fica em `/mnt/c/Users/SEU_USUARIO/Downloads`. Para abrir a pasta atual do Ubuntu no Explorador de Arquivos, digite `explorer.exe .` (com o ponto no final).

---

## 3. Baixando este projeto

Escolha **uma** das duas opções.

**Opção A, com git (recomendada, porque facilita atualizar depois):**

```bash
cd ~
git clone https://github.com/uigormarshall/mgs-integral-ptbr-spokemachine.git MGS-Integral
cd MGS-Integral
```

**Opção B, sem git:**

1. Na página do projeto no GitHub, clique no botão verde **Code** e depois em **Download ZIP**.
2. Extraia o ZIP.
3. No terminal, entre na pasta extraída com o `cd`. Por exemplo:
   ```bash
   cd ~/Downloads/MGS-Integral-main
   ```

Para conferir se você está na pasta certa, digite `ls`. Devem aparecer as pastas `legendas` e `tools` e o arquivo `README.md`.

---

## 4. Colocando os discos do jogo na pasta certa

Dentro da pasta do projeto, crie as pastas `disc1` e `disc2`:

```bash
mkdir -p disc1 disc2
```

Copie os arquivos `.bin` do jogo para elas e **renomeie os arquivos exatamente assim**, com maiúsculas, espaços e parênteses:

```
MGS-Integral/
├── disc1/
│   └── Metal Gear Solid - Integral (Japan) (En,Ja) (Disc 1).bin
├── disc2/
│   └── Metal Gear Solid - Integral (Japan) (En,Ja) (Disc 2).bin
├── legendas/
└── tools/
```

Os arquivos `.cue` originais **não são necessários**, porque as ferramentas criam arquivos novos. Se quiser, pode copiar os `.cue` também, que não atrapalha.

> Se você baixou uma cópia no padrão Redump, os nomes provavelmente já estão certos.

> **No Windows (WSL):** você pode copiar os arquivos pelo Explorador de Arquivos. Na janela do Ubuntu, dentro da pasta do projeto, digite `explorer.exe .` e arraste os arquivos para as pastas `disc1` e `disc2`.

---

## 5. Gerando a ROM traduzida

Ainda dentro da pasta do projeto, rode **primeiro o disco 1 e depois o disco 2** (o disco 2 usa traduções do disco 1):

```bash
bash tools/montar.sh
bash tools/montar2.sh
```

Cada comando leva de alguns segundos a poucos minutos. Ele vai mostrando o que está fazendo: cutscenes, codec, vozes, vídeos. Se tudo der certo, a última linha de cada um é:

```
OK -> patched/MGS Integral PT-BR (Disc 1).cue
OK -> patched/MGS Integral PT-BR (Disc 2).cue (+ .m3u)
```

Os arquivos prontos ficam na pasta **`patched/`**:

| Arquivo | Para que serve |
|---|---|
| `MGS Integral PT-BR (Disc 1).bin` e `.cue` | Disco 1 traduzido |
| `MGS Integral PT-BR (Disc 2).bin` e `.cue` | Disco 2 traduzido |
| `MGS Integral PT-BR.m3u` | Lista dos dois discos, para o emulador trocar de disco sozinho |

Os seus arquivos originais **não são alterados**.

---

## 6. Jogando

### Copiando para o emulador ou portátil

Copie os **5 arquivos** da pasta `patched/` para a pasta de jogos de PS1 do emulador. Em portáteis com Knulli, Batocera, ArkOS, ROCKNIX e sistemas parecidos, a pasta costuma ser `roms/psx`.

**Abra o jogo pelo arquivo `.m3u`.** Assim, quando o jogo pedir o disco 2, o emulador troca de disco sozinho. No RetroArch, use o menu rápido: *Controle de Disco* > *Ejetar*, escolha o *Disco 2* e depois *Inserir*.

> Muitos sistemas mostram o jogo duas ou três vezes na lista (`.m3u` e os dois `.cue`). Para esconder as entradas repetidas, você pode colocar os `.bin` e os `.cue` numa subpasta (por exemplo, `roms/psx/.mgs/`) e ajustar os caminhos dentro do `.m3u`.

### BIOS (muito importante)

O emulador precisa da **BIOS original do PlayStation** (por exemplo, `scph1001.bin` ou `scph5501.bin`) na pasta de BIOS do sistema. Sem ela, o emulador usa uma BIOS "de mentira" (HLE), e o **Metal Gear Solid trava ao salvar ou carregar o jogo**.

- Knulli e Batocera: a BIOS fica em `/userdata/bios/`.
- RetroArch no PC: a BIOS fica na pasta `system`.

A BIOS também não é distribuída aqui. Use a do seu console.

### Emuladores testados

| Emulador | Situação |
|---|---|
| PCSX-ReARMed (RetroArch), no Anbernic RG35XX H com Knulli | Funciona (com BIOS) |

Testou em outro emulador? Conte para a gente (veja [Como contribuir](#9-como-contribuir)).

### Saves

Os saves (memory card) do jogo original **também funcionam** na versão traduzida, porque o jogo é o mesmo por dentro. Para continuar um save antigo, copie o arquivo de memory card (por exemplo, `.srm` no RetroArch) e dê a ele o mesmo nome do jogo traduzido.

---

## 7. Problemas comuns

**`No such file or directory` e o nome do disco.**
O arquivo `.bin` não está na pasta certa ou o nome está diferente. Confira o [passo 4](#4-colocando-os-discos-do-jogo-na-pasta-certa) letra por letra. No terminal, `ls disc1 disc2` mostra o que está lá.

**`python3: command not found`.**
O Python não está instalado. Volte ao [passo 2](#2-preparando-o-computador).

**`monte o disco 1 primeiro`.**
Rode o `bash tools/montar.sh` antes do `bash tools/montar2.sh`.

**`cmp: ... differ` ou outro erro no meio da montagem.**
Provavelmente a sua imagem é diferente da que usamos. Confira o MD5 do [passo 1](#que-versão-do-jogo-serve) e abra uma *issue* com a mensagem de erro completa.

**O jogo está em `.chd`.**
Converta para `.bin` + `.cue` com o `chdman` (vem com o MAME):
```bash
chdman extractcd -i jogo.chd -o "Metal Gear Solid - Integral (Japan) (En,Ja) (Disc 1).cue"
```

**O jogo está em `.pbp` (formato do PSP) ou `.iso`.**
Esses formatos não servem diretamente. É preciso partir da imagem `.bin` + `.cue` original.

**O jogo trava ao salvar ou carregar.**
Falta a BIOS. Veja [BIOS](#bios-muito-importante).

**O jogo abriu em japonês.**
Você abriu a imagem original, não a da pasta `patched/`. Ou então o memory card tem uma configuração antiga salva em japonês. Nesse caso, mude o idioma no menu *Options* do jogo.

**As letras aparecem sem acento.**
Isso é de propósito. A fonte do jogo não tem letras acentuadas, então "ação" aparece como "acao".

---

## 8. Limitações conhecidas

- **Sem acentos e sem ç.** A fonte original do jogo não tem esses caracteres.
- **Menus, nomes de itens e armas continuam em inglês.** Isso inclui os textos de "ITEM", "WEAPON" e as telas de opções.
- **O "Mission Log" (o resumo ao carregar o jogo) continua em japonês.** Esse texto fica em outro formato, que ainda não conseguimos editar.
- **Algumas falas foram encurtadas.** O espaço de cada legenda no disco é fixo. Quando a tradução não cabia, ela foi resumida, mas mantendo o sentido.
- **Algumas linhas longas do codec** podem ficar perto da borda da tela.
- **O disco 3 (VR Missions)** não foi traduzido.

---

## 9. Como contribuir

Achou um erro de tradução, uma fala estranha ou um texto cortado? Contribuições são muito bem-vindas!

### Só quer avisar um problema

Abra uma **Issue** aqui no GitHub e diga:

- em que parte do jogo aconteceu (fase, cena, quem estava falando no codec);
- o texto que aparece;
- se possível, uma foto ou captura de tela.

### Quer corrigir você mesmo

As traduções ficam em arquivos de texto simples:

| Parte | Onde fica a tradução |
|---|---|
| Codec (disco 1 e 2) | `legendas/codec/lote_NN_pt.txt` |
| Vozes do disco 1 | `legendas/vox/lote_NN_pt.txt` |
| Falas novas do disco 2 | `legendas/disc2/lotes/lote_NN_pt.txt` |
| Cutscenes do disco 1 | `legendas/demo_cena1.json` e `legendas/lote0N.py` |
| Vídeos do disco 1 | `legendas/movie_tr.json` |

Nos arquivos `lote_NN_pt.txt`, cada linha tem um **número**, uma **tabulação** e o **texto em português**. O texto original em inglês fica no arquivo `lote_NN_en.txt` correspondente, com o mesmo número. Esse arquivo **não vem no repositório**, porque é texto da Konami. Ele é criado na sua máquina, a partir do seu disco, quando você roda o [passo 5](#5-gerando-a-rom-traduzida). As regras são estas:

- `" / "` (espaço, barra, espaço) **quebra a linha** na tela;
- cada linha deve ter **no máximo cerca de 40 letras**;
- não use acentos (eles são removidos automaticamente, mas assim você já vê como vai ficar);
- não apague nem mude o número no começo da linha;
- códigos entre chaves, como `{9C01}`, são símbolos especiais (aspas, botões) e devem ser mantidos.

Depois de editar, gere a ROM de novo com o [passo 5](#5-gerando-a-rom-traduzida) e teste no jogo. Se a fala não couber no espaço, a montagem avisa ("nao couberam") e o trecho volta para o inglês. Nesse caso, encurte o texto.

As regras de estilo e o glossário (Snake, Coronel Campbell, Soldado Genoma, FOX-HOUND…) estão no arquivo [`CLAUDE.md`](CLAUDE.md).

Para enviar a sua correção, faça um *fork* do projeto, edite os arquivos e abra um *Pull Request*.

---

## 10. Créditos

- **Engenharia reversa do jogo:** este projeto só foi possível graças ao [FoxdieTeam/mgs_reversing](https://github.com/FoxdieTeam/mgs_reversing), que reconstruiu o código do Metal Gear Solid de PS1 e documentou os formatos dos arquivos do jogo.
- **Tradução e ferramentas:** Spoke Machine ([blog](https://spokemachine.com.br) · [YouTube](https://www.youtube.com/channel/UCOvPz1-OJJXjhsHDjIE_oZA)) e a comunidade, com a ajuda do Claude (Anthropic).
- *Metal Gear Solid* é uma marca da Konami. Este é um projeto de fãs, sem fins lucrativos e sem ligação com a Konami.
