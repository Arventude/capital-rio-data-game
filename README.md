# Capital Rio — game-data

## Estado auditado em 2026-10-21

Este repositório representa a versão dos dados externos usados pelo launcher. A
release `game-data-v2` está publicada e a URL configurada no APK responde HTTP 200
com aproximadamente 1,07 GB:

```text
https://github.com/Arventude/capital-rio-data-game/releases/download/game-data-v2/capitalrio-game-data-v2.zip
```

O clone Git contém apenas a documentação e as tags da release; o ZIP grande não é
versionado diretamente neste repositório. A release precisa continuar pública e
ser validada antes de qualquer publicação do APK.

## Estrutura esperada dentro do ZIP

O arquivo pode ter uma pasta superior `files/`, que o launcher remove durante a
extração, ou pode trazer as pastas diretamente na raiz:

```text
files/ ou raiz/
├── CINFO.BIN
├── gtasatelem.set
├── gta_sa.set
├── samp_log.txt
├── stream.ini
├── anim/
├── audio/
│   ├── SFX/*.osw e *.osw.idx
│   └── STREAMS/*.osw e *.osw.idx
├── crashhandler/
├── data/
│   └── gta.dat
├── fonts/
├── models/
├── SAMP/
│   └── settings.ini
├── storage/
└── texdb/
    └── gta3.img
```

Os arquivos `.idx` de áudio são obrigatórios quando referenciados pelo pacote. Não
criar índices vazios para esconder erro de instalação: todos os arquivos de áudio,
texturas, `gta.dat`, modelos, colisões e índices precisam pertencer à mesma versão.

## Diagnóstico do ZIP `game-data-v2`

O ZIP auditado em 2026-10-23 foi rejeitado para o cliente Capital Rio. Ele contém
`loader/blackrussia_client.log`, 57 entradas com nomes cirílicos/cópias e mapas
alternativos como `PORTLAND`, `PORTLAND1`, `M_CITY`, `LIBERTY`, `MOTOR`, `STAUNTON`
e `vcsa`. Além disso, `data/gta.dat` e `SAMP/gta.dat` carregam `rip*.IPL`,
`vcsa.ipl` e `trees_map.IPL`. Isso explica o mapa russo/estranho no aparelho; não
é causado pelo open.mp, pelo CMake ou pelo WebView.

Esse pacote não deve ser "corrigido" apagando arquivos isolados: os arquivos IMG,
IDE, IPL, colisões e `gta.dat` precisam ser gerados como um conjunto compatível.
Gere a próxima release a partir de uma instalação limpa e licenciada do GTA San
Andreas e aplique somente os assets Capital Rio planejados.

Antes de publicar qualquer ZIP, execute:

```bash
python3 tools/audit_game_data.py /caminho/capitalrio-game-data.zip
```

O comando deve terminar com `status=PASS`. O APK também rejeita esse perfil de
data antes da extração e volta a rejeitar uma instalação antiga que contenha os
mesmos marcadores.

## Validação pelo APK

`GameDataValidator.java` instala os dados em:

```text
Android/data/com.capitalrio.app/files/
```

A validação confere diretórios essenciais, arquivos de configuração, `gta3.img`
com tamanho mínimo, `SAMP/settings.ini` e `data/gta.dat`. O renderer ainda pode
exigir arquivos adicionais; um pacote aprovado pelo validator não substitui o
teste de boot em ARM32 e ARM64.

### Origem do mapa exibido

O mapa carregado pelo cliente vem dos arquivos binários extraídos do ZIP,
principalmente `texdb/gta3.img`, `data/gta.dat`, modelos, colisões e texturas.
O código CMake, o componente WebView e as includes Pawn não substituem o mapa.
Se o jogo mostrar um mapa russo ou outro mapa que não seja o mapa original do
GTA San Andreas, o ZIP instalado no aparelho não é uma data original compatível
ou contém um mod de mapa. É necessário gerar uma nova release a partir de uma
instalação limpa e licenciada do GTA SA, mantendo modelos, texturas, colisões e
índices da mesma versão; não basta renomear `gta3.img`.

## Checklist de publicação

1. Gerar o ZIP a partir de uma instalação limpa.
2. Conferir maiúsculas/minúsculas dos caminhos.
3. Conferir todos os `.idx` junto dos `.osw` correspondentes.
4. Gerar e publicar SHA-256/manifesto da release.
5. Testar download interrompido, ZIP corrompido e armazenamento insuficiente.
6. Extrair em staging e iniciar o APK em aparelho real.
7. Confirmar ausência de `SIGSEGV`, `ANR` e arquivos ausentes no logcat.
8. Atualizar a tag somente quando os dados forem compatíveis com o APK publicado.

Os dados do jogo não incluem login, credenciais, banco de personagens ou código do
servidor. Esses itens pertencem aos repositórios e serviços correspondentes.
