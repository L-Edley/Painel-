const MAX_ITENS = Number(document.body.dataset.maxItens) || 500;

const EXEMPLOS = [
    "4111 1111 1111 1111",
    "4012 0010 2345 6789",
    "5555 5555 5555 4444",
    "4532 1598 7654 3210",
];

const formatadorNumero = new Intl.NumberFormat("pt-BR", {
    maximumFractionDigits: 1,
});

const elementos = {
    lista: document.querySelector("#input-lista"),
    contador: document.querySelector("#contador-itens"),
    btnValidar: document.querySelector("#btn-validar"),
    btnExemplo: document.querySelector("#btn-exemplo"),
    btnLimpar: document.querySelector("#btn-limpar"),
    alerta: document.querySelector("#alerta"),
    total: document.querySelector("#stat-total"),
    aprovados: document.querySelector("#stat-aprovados"),
    reprovados: document.querySelector("#stat-reprovados"),
    taxa: document.querySelector("#stat-taxa"),
    corpoTabela: document.querySelector("#tabela-resultados"),
    formGateway: document.querySelector("#form-gateway"),
    cartaoGateway: document.querySelector("#input-cartao-gateway"),
    valorGateway: document.querySelector("#input-valor-gateway"),
    btnGateway: document.querySelector("#btn-gateway"),
    statusGateway: document.querySelector("#status-gateway"),
    respostaGateway: document.querySelector("#resposta-gateway"),
};

function iniciar() {
    elementos.lista.addEventListener("input", atualizarContador);
    elementos.btnValidar.addEventListener("click", validarLote);
    elementos.btnExemplo.addEventListener("click", carregarExemplo);
    elementos.btnLimpar.addEventListener("click", limparPainel);
    elementos.formGateway.addEventListener("submit", testarGateway);

    elementos.lista.addEventListener("keydown", (evento) => {
        if (evento.key === "Enter" && (evento.ctrlKey || evento.metaKey)) {
            evento.preventDefault();
            validarLote();
        }
    });

    atualizarContador();
}

function extrairLinhas() {
    return elementos.lista.value
        .split(/\r?\n/)
        .map((linha) => linha.trim())
        .filter((linha) => linha !== "");
}

function atualizarContador() {
    const total = extrairLinhas().length;
    elementos.contador.textContent = `${total} ${total === 1 ? "item" : "itens"}`;
}

async function validarLote() {
    const linhas = extrairLinhas();

    if (linhas.length === 0) {
        mostrarAlerta("Insira pelo menos um item para validar.", "erro");
        elementos.lista.focus();
        return;
    }

    if (linhas.length > MAX_ITENS) {
        mostrarAlerta(`Envie no máximo ${MAX_ITENS} itens por lote.`, "erro");
        return;
    }

    definirCarregando(true);
    esconderAlerta();

    try {
        const dados = await requisitar("/api/checar", {
            method: "POST",
            body: JSON.stringify({ itens: linhas }),
        });

        atualizarEstatisticas(dados);
        renderizarResultados(dados.resultados);
        mostrarAlerta(
            `Validação concluída: ${dados.total} item(ns) processado(s).`,
            "sucesso",
        );
    } catch (erro) {
        mostrarAlerta(erro.message, "erro");
    } finally {
        definirCarregando(false);
    }
}

function definirCarregando(carregando) {
    elementos.btnValidar.disabled = carregando;
    elementos.btnExemplo.disabled = carregando;
    elementos.btnLimpar.disabled = carregando;
    elementos.btnValidar.textContent = carregando ? "Validando..." : "Validar lote";
}

function atualizarEstatisticas(dados) {
    const total = Number(dados?.total) || 0;
    const aprovados = Number(dados?.aprovados) || 0;
    const reprovados = Number(dados?.reprovados) || 0;
    const taxa = dados?.taxa_aprovacao != null
        ? Number(dados.taxa_aprovacao)
        : total
            ? (aprovados / total) * 100
            : 0;

    elementos.total.textContent = total;
    elementos.aprovados.textContent = aprovados;
    elementos.reprovados.textContent = reprovados;
    elementos.taxa.textContent = `${formatadorNumero.format(taxa)}%`;
}

function renderizarResultados(resultados) {
    elementos.corpoTabela.replaceChildren();

    if (!Array.isArray(resultados) || resultados.length === 0) {
        elementos.corpoTabela.append(
            criarLinhaVazia("Nenhum dado processado ainda."),
        );
        return;
    }

    for (const resultado of resultados) {
        const linha = document.createElement("tr");

        const celulaItem = document.createElement("td");
        celulaItem.className = "cell-mono";
        celulaItem.textContent = resultado.item;

        const celulaStatus = document.createElement("td");
        celulaStatus.append(criarBadgeStatus(resultado.status));

        const celulaDetalhe = document.createElement("td");
        celulaDetalhe.className = "muted";
        celulaDetalhe.textContent = resultado.motivo;

        linha.append(celulaItem, celulaStatus, celulaDetalhe);
        elementos.corpoTabela.append(linha);
    }
}

function criarLinhaVazia(mensagem) {
    const linha = document.createElement("tr");
    const celula = document.createElement("td");
    celula.colSpan = 3;
    celula.className = "empty";
    celula.textContent = mensagem;
    linha.append(celula);
    return linha;
}

function criarBadgeStatus(status) {
    const badge = document.createElement("span");
    badge.className = `badge ${status === "Aprovado" ? "badge--ok" : "badge--error"}`;
    badge.textContent = status;
    return badge;
}

function carregarExemplo() {
    elementos.lista.value = EXEMPLOS.join("\n");
    atualizarContador();
    esconderAlerta();
    elementos.lista.focus();
}

function limparPainel() {
    elementos.lista.value = "";
    atualizarContador();
    atualizarEstatisticas({ total: 0, aprovados: 0, reprovados: 0, taxa_aprovacao: 0 });
    renderizarResultados([]);
    esconderAlerta();
    elementos.lista.focus();
}

function mostrarAlerta(mensagem, tipo) {
    elementos.alerta.textContent = mensagem;
    elementos.alerta.className = `alert alert--${tipo}`;
    elementos.alerta.hidden = false;
}

function esconderAlerta() {
    elementos.alerta.hidden = true;
    elementos.alerta.textContent = "";
}

async function testarGateway(evento) {
    evento.preventDefault();

    const cartao = elementos.cartaoGateway.value.trim();
    const valor = Number(elementos.valorGateway.value);

    if (!cartao) {
        elementos.statusGateway.textContent = "Erro";
        elementos.statusGateway.className = "badge badge--error";
        elementos.respostaGateway.textContent = "Informe um número de cartão.";
        return;
    }

    if (!Number.isFinite(valor) || valor <= 0) {
        elementos.statusGateway.textContent = "Erro";
        elementos.statusGateway.className = "badge badge--error";
        elementos.respostaGateway.textContent = "Informe um valor maior que zero.";
        return;
    }

    elementos.btnGateway.disabled = true;
    elementos.btnGateway.textContent = "Consultando...";
    elementos.statusGateway.textContent = "Aguardando";
    elementos.statusGateway.className = "badge badge--neutral";
    elementos.respostaGateway.textContent = "Consultando gateway simulado...";

    try {
        const dados = await requisitar("/api/gateway/pagar", {
            method: "POST",
            body: JSON.stringify({ cartao, valor }),
        });

        const aprovado = dados.status === "Aprovado";
        elementos.statusGateway.textContent = dados.status;
        elementos.statusGateway.className =
            `badge ${aprovado ? "badge--ok" : "badge--error"}`;
        elementos.respostaGateway.textContent = JSON.stringify(dados, null, 2);
    } catch (erro) {
        elementos.statusGateway.textContent = "Erro";
        elementos.statusGateway.className = "badge badge--error";
        elementos.respostaGateway.textContent = erro.message;
    } finally {
        elementos.btnGateway.disabled = false;
        elementos.btnGateway.textContent = "Enviar ao gateway";
    }
}

async function requisitar(url, opcoes = {}) {
    const { headers, ...resto } = opcoes;
    const controlador = new AbortController();
    const temporizador = setTimeout(() => controlador.abort(), 30000);

    let resposta;

    try {
        resposta = await fetch(url, {
            ...resto,
            signal: controlador.signal,
            headers: {
                "Content-Type": "application/json",
                ...(headers || {}),
            },
        });
    } catch (erro) {
        if (erro.name === "AbortError") {
            throw new Error("Tempo limite excedido ao consultar o servidor.");
        }
        throw new Error("Não foi possível conectar ao servidor.");
    } finally {
        clearTimeout(temporizador);
    }

    const dados = await resposta.json().catch(() => null);

    if (!resposta.ok) {
        throw new Error(extrairMensagemErro(dados, resposta.status));
    }

    return dados;
}

function extrairMensagemErro(dados, status) {
    if (dados && typeof dados.detail === "string") {
        return dados.detail;
    }

    if (dados && Array.isArray(dados.detail)) {
        return dados.detail
            .map((item) => item.msg || String(item))
            .join("; ");
    }

    return `Falha na requisição (HTTP ${status}).`;
}

document.addEventListener("DOMContentLoaded", iniciar);
