# MGS Integral — legendas pt-BR

Patch de legendas pt-BR para Metal Gear Solid Integral (PS1, disco 1, `SLPM_862.47`), para jogar no R36S via emulador.

## Regras
- Português do Brasil, natural e enxuto. Pode escrever com acentos: o injetor remove (a fonte do jogo não tem acentos).
- `" / "` = quebra de linha. Linhas com no máximo ~40 caracteres.
- Nomes próprios, codinomes e termos do jogo ficam como no original: Snake, Campbell, Meryl, Otacon, FOX-HOUND, Metal Gear, Rex, Codec, SOCOM, PAL, DARPA, ArmsTech, Hind D, Genome Soldier = "Soldado Genoma".
- Não mexer em `disc1/` (originais). Ferramentas: `tools/`.

## Pedido "traduza o próximo lote do codec"
1. `python3 -I tools/codec.py proximo` → mostra o arquivo `legendas/codec/lote_NN_en.txt`.
2. Ler esse arquivo (formato `ID<TAB>inglês`).
3. Escrever `legendas/codec/lote_NN_pt.txt` com as mesmas IDs (`ID<TAB>português`), uma por linha. Se o arquivo já existir com algumas linhas, manter e completar.
4. `tools/montar.sh` → remonta a imagem `patched/MGS Integral PT-BR (Disc 1).cue`.
   Se uma chamada passar do espaço, ele avisa "passou N bytes": encurtar falas daquela chamada e rodar de novo.
5. `python3 -I tools/codec.py status` e responder com uma linha de progresso.
Não reler outros lotes nem o código-fonte: o processo acima basta.

## Pedido "traduza o próximo lote do vox"
Igual ao do codec, trocando `tools/codec.py` por `tools/vox.py` e `legendas/codec/` por `legendas/vox/`.
Lote 99 (encurtar): cada linha traz `[atual: ...]` e `[max N letras]`. Escrever em `lote_99_pt.txt` só a nova versão em português, com no máximo N letras (contando espaços), mantendo o sentido.

## Pedido "traduza o próximo lote do disco2"
Igual ao do codec, trocando `tools/codec.py` por `tools/disco2.py`, a pasta por `legendas/disc2/lotes/` e `tools/montar.sh` por `tools/montar2.sh`.

## Estrutura (referência)
- Cutscenes: `DEMO.DAT`, blocos tipo 6 → traduções em `legendas/lote01-03.py` (completas, 81/81).
- Codec: `RADIO.DAT` (script de chamadas, formato em `tools/radio.py`), 3482 falas únicas em 24 lotes.
- Codec: completo (24/24 lotes).
- Vídeos: `ZMOVIE.STR`, 4 vídeos / 48 falas em `legendas/movie_pt.json` (`tools/movie.py`, grava direto na imagem). Completo.
- Executável: `tools/exe_patch.py` força inglês a cada quadro (5 instruções em gamed.c Act, 0x8002adfc-0x8002ae10), mantendo a lógica de vibração original (a 1ª versão quebrava isso; suspeita de travar save/load).
- `tools/montar.sh` remonta tudo (cutscenes + codec + vídeos) a partir do original.
- Vozes: `VOX.DAT` (abertura, briefing), mesmo formato das cutscenes. `tools/vox.py` reaproveita traduções das cutscenes/codec e põe só as falas novas em `legendas/vox/` (7 lotes). Blocos sem espaço ficam em inglês (listados pelo aplicar).
- PS1 no RG35XX (Knulli/PCSX-ReARMed) precisa de BIOS real em `/userdata/bios/scph1001.bin`: com a BIOS HLE o save/load trava.
- Mission Log: só existe em japonês (strings GCL no STAGE.DIR, codificação própria; kanji = índice da fonte, sem tabela pronta). Adiado.
- Disco 2: `disc2/` (original), executável idêntico ao do disco 1. `tools/disco2.py` reaproveita todas as traduções do disco 1 (codec 100% igual) e põe só as falas novas em `legendas/disc2/lotes/`. `tools/montar2.sh` gera a imagem + `patched/MGS Integral PT-BR.m3u`.
- Ainda não feito: itens/menus, disco 2, revisão no jogo.
