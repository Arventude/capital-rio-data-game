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

## Validação pelo APK

`GameDataValidator.java` instala os dados em:

```text
Android/data/com.capitalrio.app/files/
```

A validação confere diretórios essenciais, arquivos de configuração, `gta3.img`
com tamanho mínimo, `SAMP/settings.ini` e `data/gta.dat`. O renderer ainda pode
exigir arquivos adicionais; um pacote aprovado pelo validator não substitui o
teste de boot em ARM32 e ARM64.

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
