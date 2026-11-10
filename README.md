# RBM — landing page do Quake RBM

Site institucional estático da **RBM**, com o **Quake RBM** como projeto em destaque.
Três idiomas: **日本語** (`/`), **English** (`/en/`) e **Português (Brasil)** (`/pt/`).
Sem dependências de runtime, sem framework, sem etapa de build obrigatória.

**Marca:** RBM · **Projeto:** Quake RBM · **Domínio indicado:** `financeself.jp`.
O conteúdo continua sendo o conceito de dispositivo de informação sobre terremotos.
O nome do repositório GitHub permanece `andrebauru/byte-tsc-site`; ele não é o domínio do site.

> ⚠️ **Status:** projeto em planejamento. O Quake RBM é um **conceito**, antes da prototipagem.
> Nenhum produto, data, certificação, parceiro ou depoimento foi publicado — por design.

## Preview da página inicial

![Preview da página inicial japonesa da RBM, com o projeto Quake RBM em destaque](docs/homepage-preview.png)

Captura real da primeira dobra de `/` (japonês), em viewport desktop de **1440 × 1000 px**, gerada com Chrome Headless. É uma preview estática; o site ainda não foi publicado.

[Ver imagem em tamanho original](docs/homepage-preview.png).

## Estrutura

```
.
├── index.html                # 日本語 (raiz, funciona sem JavaScript)
├── en/index.html             # English
├── pt/index.html             # Português (Brasil)
├── site.webmanifest         # PWA manifest (nome, ícones, cor)
├── robots.txt               # robots + sitemap
├── sitemap.xml               # sitemap com hreflang (ja/en/pt/x-default)
└── assets/
    ├── css/style.css         # todo o estilo (design system em :root)
    ├── js/lang.js            # detecção/persistência de idioma + menu móvel
    ├── favicon.svg           # favicon vetorial
    ├── favicon-16.png        # favicon 16×16 (PNG)
    ├── favicon-32.png        # favicon 32×32 (PNG)
    ├── apple-touch-icon.png  # ícone de toque 180×180
    ├── brand/
    │   ├── symbol.svg            # símbolo isolado (claro)
    │   ├── symbol-dark.svg       # símbolo para fundos escuros
    │   ├── symbol-mono.svg       # símbolo monocromático (currentColor)
    │   ├── logo-horizontal.svg  # logotipo horizontal (claro)
    │   ├── logo-horizontal-dark.svg
    │   └── logo-horizontal-mono.svg
    └── img/
        ├── hero-device.svg   # ilustração conceitual do dispositivo (hero)
        ├── og-share.png      # imagem de compartilhamento 1200×630 (PNG)
        └── og-share.webp     # mesma imagem em WebP
scripts/
├── make_raster_assets.py     # regenera os PNG/WebP (Pillow)
├── test_lang.js              # testes unitários da detecção de idioma (Node)
├── test_dom.js               # integração em DOM/storage simulados (Node)
├── test_site.py              # marca, metadados, links e assets (Python 3)
└── configure_deployment.py   # configura metadados para a origem HTTPS indicada
```

## Rodar localmente

Qualquer servidor estático serve. Exemplos:

```bash
python3 -m http.server 8080     # → http://localhost:8080/
npx serve .                     # alternativa via Node
```

Abra `http://localhost:8080/` (日本語), `/en/` (English) e `/pt/` (Português).

> Nota: em `file://` a página também funciona, mas o redirecionamento automático
> da raiz pode não acontecer em todos os navegadores (limitação de `localStorage`
> em `file://`). Prefira um servidor local para testes.

## Regenerar os assets raster (ícones / OG)

Requisito: Pillow (`pip install pillow`). Depois:

```bash
python3 scripts/make_raster_assets.py
```

Isso recria `favicon-16.png`, `favicon-32.png`, `apple-touch-icon.png`,
`og-share.png` e `og-share.webp`. As cores e o desenho são editados
**no próprio script** (`NAVY`, `AMBER`, as funções de desenho).

## Testes

```bash
node scripts/test_lang.js      # 19 testes da seleção de idioma
node scripts/test_dom.js       # 17 testes de DOM/storage simulados, incluindo migração
python3 scripts/test_site.py   # marca, domínio, links, SVG/XML e dimensões dos PNGs
```

Cobre: variantes regionais (`en-US` → `en`, `pt-BR` → `pt`), primeira
correspondência suportada, fallback para 日本語 sem correspondência
ou entrada inutilizável, e formas incomuns de entrada.

## Comportamento de idiomas

- **`/` é a versão 日本語 por padrão**, mesmo com JavaScript desativado.
- Na primeira visita a `/`, **sem preferência salva**, o script lê
  `navigator.languages` e escolhe o primeiro idioma suportado, ignorando
  variantes regionais; sem correspondência (ou sem detecção), fica em 日本語.
- Escolha manual (clique no seletor 日本語 · English · Português) é salva em
  `localStorage` (`rbm-pref-lang`) e **tem prioridade** na próxima visita à raiz.
  A chave antiga é migrada na mesma origem. Preferências não podem ser transferidas
  automaticamente entre domínios diferentes.
- Páginas localizadas (`/en/`, `/pt/`) **nunca** redirecionam automaticamente,
  então não há loop de redirecionamento (a raiz só redireciona *para fora*).
- Trocar de idioma **mantém a seção atual** (`#development` etc.): as três
  páginas usam os mesmos `id`s de âncora.
- O idioma ativo é marcado no seletor com estilo próprio e `aria-current="true"`.

## Onde editar

| O quê | Onde |
| --- | --- |
| Textos 日本語 | `index.html` |
| Textos English | `en/index.html` |
| Textos Português | `pt/index.html` |
| Cores, tipografia, espaçamento | `assets/css/style.css` (tokens em `:root`) |
| Lógica de idioma / menu | `assets/js/lang.js` |
| Marca (símbolo/logotipo) | `assets/brand/*.svg` |
| Ilustração do hero | `assets/img/hero-device.svg` |
| Imagem de compartilhamento | `scripts/make_raster_assets.py` → rodar de novo |
| Metadados/OG/canônica | bloco `<head>` de cada `index.html` |

Os três arquivos HTML são **traduções um-a-um** (mesmas seções, mesmos
`id`s). Ao acrescentar/remover uma seção, replique nos três idiomas.

### Contatos e campanha (pendências)

- `index.html`, seção `#participate`: o bloco `TODO` marca onde entra o
  **link real de inscrição/contato** — só publicar com destino confirmado.
- Seção `#development`: o bloco `TODO` marca onde entra o **botão de apoio**
  — só exibir quando houver campanha ativa com URL confirmada.
- `og-share.png` não contém frases (marca + ilustração), então a tradução
  dos textos **não exige** reexportar o visual.

## ✅ Itens que precisam de confirmação antes da publicação

1. **Domínio indicado:** `financeself.jp`. Canonical, hreflang, OG, robots e sitemap
   estão configurados para `https://financeself.jp`.
   Isso não registra o domínio, comprova sua titularidade, configura DNS/TLS nem publica o site.
   Antes de publicar, confirme o controle do domínio e a hospedagem.
   Para regenerar: `python3 scripts/configure_deployment.py https://financeself.jp`.
2. **URL da campanha de apoio** (botão desabilitado até existir campanha ativa).
3. **Destinos reais de contato/inscrição** da RBM Community Contributors.
4. **Revisão de conteúdo pelo responsável pela RBM** — em especial os
   números preliminares: meta de ¥3.000.000 e estimativa de ~10 meses
   (ambos identificados na página como "preliminar", da proposta).
5. **Revisão jurídica** (se aplicável) das advertências: avisos podem chegar
   tarde ou não chegar; o dispositivo complementa (não substitui) os canais
   oficiais.
6. **Verificação de acessibilidade** com leitores de tela (NVDA/VoiceOver) —
   a base (HTML semântico, foco visível, ícone de toque 180×180 px) já está pronta.
7. Hospedagem: qualquer host estático (GitHub Pages, Netlify, S3…).
   A publicação fica **vinculada à aprovação do responsável pela RBM**.

## Publicar (build)

Não há build: os arquivos são servidos como estão (`index.html`, `en/`,
`pt/`, `assets/`). Se quiser minificar/optimize, os únicos alvos são o CSS
e o JS — ambos são pequenos o suficiente para dispensar.

---

© RBM — projeto em planejamento. Conteúdo sujeito a mudanças.
## Verificações desta entrega

```sh
node scripts/test_lang.js   # 19 casos da seleção de idioma
node scripts/test_dom.js    # 17 casos de integração, DOM/storage simulados
python3 scripts/test_site.py
```

Foram verificados também SVG/XML, tamanhos dos ícones e imagem social,
URLs locais HTTP 200 e geração idempotente dos metadados de implantação.
O teste do gerador usa uma cópia temporária e `https://example.com`, sem
alterar a configuração real `https://financeself.jp` do site entregue.

**Validação da mudança de marca:** captura desktop atualizada com Chrome Headless,
marca RBM e canonical `https://financeself.jp/` confirmados no DOM real.
Na viewport de 390 × 844 px, não foi detectada rolagem horizontal e o menu
móvel abriu com `aria-expanded` consistente. As três versões passam pelas
verificações de marca, metadados, âncoras e assets locais. O gerador de
implantação foi reexecutado com a origem indicada e permaneceu idempotente.

**Limitações:** os 17 testes de detecção/persistência/menu usam DOM/storage
simulados; não equivalem a uma auditoria completa de acessibilidade.
Revisão visual manual, navegação por teclado, leitores de tela, controle do
domínio, DNS/TLS e hospedagem ainda precisam de verificação antes da publicação.
Nenhum build é necessário: o site continua em HTML/CSS/JS estático nesta etapa.
