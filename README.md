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
├── mods/
│   └── customdrop/
└── texdb/
    └── gta3.img
```

Os arquivos `.idx` de áudio são obrigatórios quando referenciados pelo pacote. Não
criar índices vazios para esconder erro de instalação: todos os arquivos de áudio,
texturas, `gta.dat`, modelos, colisões e índices precisam pertencer à mesma versão.

## Diagnóstico do ZIP `game-data-v2`

O ZIP auditado em 2026-10-23 contém
`loader/blackrussia_client.log`, 57 entradas com nomes cirílicos/cópias e mapas
alternativos como `PORTLAND`, `PORTLAND1`, `M_CITY`, `LIBERTY`, `MOTOR`, `STAUNTON`
e `vcsa`. Além disso, `data/gta.dat` e `SAMP/gta.dat` carregam `rip*.IPL`,
`vcsa.ipl` e `trees_map.IPL`. Isso explica o mapa russo/estranho no aparelho; não
é causado pelo open.mp, pelo CMake ou pelo WebView. Esse conteúdo agora é
permitido pelo APK; o auditor apenas emite avisos para facilitar o diagnóstico.

Esse pacote não deve ser "corrigido" apagando arquivos isolados: os arquivos IMG,
IDE, IPL, colisões e `gta.dat` precisam ser gerados como um conjunto compatível.
Gere a próxima release a partir de uma instalação limpa e licenciada do GTA San
Andreas e aplique somente os assets Capital Rio planejados.

Antes de publicar qualquer ZIP, execute:

```bash
python3 tools/audit_game_data.py /caminho/capitalrio-game-data.zip
```

O comando deve terminar com `status=PASS`. Referências a mapas alternativos podem
aparecer como `warning=...`, mas não bloqueiam a instalação. O APK também aceita
essa data normalmente, desde que os arquivos estruturais mínimos estejam presentes.

## Crash no carregamento do mundo — 2026-10-23

O logcat enviado após a troca da data mostra `SIGSEGV` em ARM64 nesta sequência:

```text
CBaseModelInfo::SetColModel
CColAccel::cacheLoadCol
CFileLoader::LoadLevel
CGame::Initialise
```

Isso ocorre antes da conexão com o servidor e indica problema no conjunto de
colisões/cache do mundo, não no WebView ou no RPC. O ZIP analisado contém somente
`models/coll/peds.col`, `vehicles.col` e `weapons.col`, além de `CINFO.BIN`,
`gta3.img` e mapas alternativos. Esses arquivos precisam ter sido gerados para a
mesma versão; um `CINFO.BIN` ou cache de colisão de outra instalação pode derrubar
o renderer nativo mesmo que o ZIP passe na validação estrutural.

Ao trocar de data, não mescle os arquivos sobre a instalação anterior. Remova ou
substitua toda a data como conjunto, mantendo apenas as preferências necessárias.
O APK corrigido extrai em staging, valida e limpa a data antiga antes de copiar a
nova, evitando a mistura silenciosa de colisões e mapas.

## Manifesto opcional de assets do Capital Rio

Para assets próprios pequenos, o pacote pode conter `capitalrio/asset_manifest.v1`.
O arquivo usa uma linha por asset, separada por `|`, nesta ordem:

```text
# key|relativePath|sha256|version|sizeBytes|required
ui.logo|capitalrio/ui/logo.bin|0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef|1|4096|1
```

O cliente valida caminho relativo, SHA-256, versão e tamanho antes de carregar o
arquivo no cache nativo. Assets obrigatórios que falharem ficam fora do runtime;
o cliente retorna ao fallback legado e registra o motivo no logcat. Na ausência
do manifesto, o jogo também usa o fallback legado, portanto a instalação não
depende de um arquivo que a release ainda não possua.

## CustomDrop: mods de personagem

A base recebida em `CustomDrop.zip` é um recurso Lua do MTA. Os arquivos Lua usam
`engineLoadDFF`, `engineLoadTXD`, `engineReplaceModel` e shaders do MTA, portanto
não são executados diretamente pelo APK Android. O importador
`tools/import_customdrop.py` extrai os assets de personagem suportados (`.dff`,
`.txd` e `.png`) para `mods/customdrop/` e gera `asset_manifest.v1` com tamanho e
SHA-256.

Uso:

```bash
python3 tools/import_customdrop.py /caminho/CustomDrop.zip .
```

a importação atual contém 585 assets e aproximadamente 100 MB, separados por
`maleskin`, `femaleskin` e `textures`. O Lua original permanece como referência da lógica MTA;
a aplicação no APK será feita pelo `CapitalRioModLoader` nativo/RenderWare.
Não chamamos isso de conversão para ACL: o equivalente no nosso cliente é um
loader C++ controlado pelo manifesto, com validação de caminhos, tamanho e hash.

## Pickup 1239

O servidor usa o pickup GTA padrão `1239` como ponto interativo. A ação é
registrada no gamemode em `gamemodes/modules/src/global/global_world.inc` e, ao
encostar/interagir, abre o painel WebView Capital Rio. O evento touch nativo deve
validar a mesma chave no servidor antes de disparar a ação.

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


## Atualização do manifesto para o CapitalRioModLoader — 2026-10-27

As chaves do `asset_manifest.v1` agora incluem a extensão do arquivo. Assim, `male.dff` e `male.txd` não colidem no parser. O manifesto atual possui 585 entradas únicas e foi validado pelo parser C++ do APK.

O Android carrega inicialmente somente os quatro assets base marcados como obrigatórios. O `CapitalRioModLoader` busca sob demanda o DFF/TXD do gênero escolhido e as variantes de camisa, calça, tênis e face. A seleção é transportada pelos campos `shirtId`, `pantsId`, `shoesId` e `faceId` do snapshot `character`.

Os arquivos são preparados e validados no cache nativo antes de qualquer tentativa de troca visual. Enquanto o registro standalone de clump/TXD não estiver confirmado para a versão exata do RenderWare do APK, o ped original permanece como fallback para evitar crash.
