// Dados iniciais
const initialData = [
    {
        id: 1,
        assunto: "Solicitação de status de atendimento",
        categoria: "Não categorizado",
        data: "2025-10-02",
        corpo: `Olá, equipe de suporte. Poderiam, por gentileza, me informar o status atualizado do ticket #4821? 
            Abri esta solicitação na última sexta-feira e preciso do retorno para dar continuidade ao processo interno aqui na empresa. 
            Aguardo a atualização. Obrigado, Carlos Andrade`,
        possivel_resposta: ""
    },
    {
        id: 1763215245549,
        assunto: "🎉 Boas Festas e Agradecimento pela Parceria em 2025!",
        categoria: "Não categorizado",
        data: "2025-11-02",
        corpo: `Prezada Equipe,
            Em nome de toda a nossa divisão, gostaríamos de expressar nossa profunda gratidão pela parceria de sucesso que tivemos ao longo deste ano.
            O trabalho em conjunto no projeto de otimização de custos foi fundamental, e agradecemos imensamente a dedicação de todos.
            Desejamos a vocês e suas famílias um Natal muito feliz e um excelente começo de 2026!
            Atenciosamente,
            João Silva Gerente de Relacionamento`,
        possivel_resposta: ""
    }
];

// Procura dados locais -> Os dados estão sendo salvos localmente 
function loadData() {
    const saved = localStorage.getItem("emails");

    if (saved) return JSON.parse(saved);

    localStorage.setItem("emails", JSON.stringify(initialData));
    return initialData;
}

function saveData(data) {
    localStorage.setItem("emails", JSON.stringify(data));
}

let emails = loadData();


// Itens listados em uma tabela
// Renderizar a cada modificação
function renderTable(data) {
    const tbody = document.querySelector(".items-table tbody");
    tbody.innerHTML = "";

    data.forEach(item => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${item.id}</td>
            <td>${item.assunto}</td>
            <td>
                <span class="${item.categoria === "Produtivo" ? "tag produtivo" : "tag improdutivo"}">
                    ${item.categoria}
                </span>
            </td>
            <td>${item.data}</td>
            <td class="actions-cell">
                <button class="view-btn" data-id="${item.id}">Ver</button>
                <button class="delete-btn">Excluir</button>
            </td>
        `;

        // Botão Excluir
        tr.querySelector(".delete-btn").addEventListener("click", () => {
            if (!confirm("Tem certeza que deseja excluir este email?")) return;

            emails = emails.filter(e => e.id !== item.id);
            saveData(emails);
            renderTable(emails);
        });

        tbody.appendChild(tr);
    });

    // Botão Ver
    tbody.querySelectorAll(".view-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const id = btn.dataset.id;
            const item = emails.find(e => e.id == id);
            openModal(item);
        });
    });
}

renderTable(emails);

function addEmail(email) {
    emails.push(email);
    saveData(emails);
    renderTable(emails);
}

function deleteEmail(id) {
    emails = emails.filter(item => item.id !== id);
    saveData(emails);
    renderTable(emails);
}

// Visualização de Item
function openModal(item) {
    document.getElementById("modal-id").textContent = item.id;
    document.getElementById("modal-assunto").textContent = item.assunto;
    document.getElementById("modal-categoria").textContent = item.categoria;
    document.getElementById("modal-data").textContent = item.data;
    document.getElementById("modal-corpo").textContent = item.corpo;
    document.getElementById("modal-possivel_resposta").textContent = item.possivel_resposta;

    document.getElementById("modal-overlay").classList.remove("hidden");
}

// Fechar modal
document.getElementById("close-modal").addEventListener("click", () => {
    document.getElementById("modal-overlay").classList.add("hidden");
});

document.getElementById("modal-overlay").addEventListener("click", (e) => {
    if (e.target.id === "modal-overlay") {
        document.getElementById("modal-overlay").classList.add("hidden");
    }
});


// Limpa conteúdos extras na resposta
function limparResposta(texto) {
    const regex = /(atenciosamente|att\.?|atte\.?|cordialmente|obrigado[,\.]?|abraços)[\s\S]*$/i;
    return texto.replace(regex, "").trim();
}

// Requisição para resposta e classificação
document.getElementById("generate-response").addEventListener("click", () => {
    const id = document.getElementById("modal-id").textContent;
    const email = emails.find(e => e.id == id);
    if (!email) return;

    showLoading();

    fetch("/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(email)
    })
        .then(res => res.json())
        .then(data => {
            const resposta = data.resposta;
            const categoria = data.categoria;

            // Atualiza item
            emails = emails.map(item =>
                item.id === email.id
                    ? {
                        ...item,
                        categoria,
                        possivel_resposta: resposta
                    }
                    : item
            );

            saveData(emails);
            renderTable(emails);

            document.getElementById("modal-possivel_resposta").textContent = resposta;
        })
        .finally(() => hideLoading());

    alert("Gerando resposta para: " + email.assunto);
});


const modalAdd = document.getElementById("modal-add");
const btnAddEmail = document.querySelector(".add-item");
const btnCloseAdd = document.getElementById("btn-add-close");

btnAddEmail.addEventListener("click", () => modalAdd.classList.remove("hidden"));
btnCloseAdd.addEventListener("click", () => modalAdd.classList.add("hidden"));

// Inputs novo e-mail
const inputAssunto = document.getElementById("add-assunto");
const inputCorpo = document.getElementById("add-corpo");
const fileInput = document.getElementById("file-upload");

let fileContent = "";


// leitura de arquivos
function readTxt(file) {
    return new Promise(resolve => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.readAsText(file);
    });
}

async function readPdf(file) {
    const arrayBuffer = await file.arrayBuffer();
    const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;

    let text = "";
    for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const content = await page.getTextContent();
        text += content.items.map(i => i.str).join(" ") + "\n";
    }

    return text;
}

// Upload
fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) return;

    if (file.type === "text/plain") fileContent = await readTxt(file);
    if (file.type === "application/pdf") fileContent = await readPdf(file);

    inputCorpo.value = fileContent;
});


document.getElementById("btn-add-confirm").addEventListener("click", () => {
    const newEmail = {
        id: Date.now(),
        assunto: inputAssunto.value,
        categoria: "Não classificado",
        data: new Date().toISOString().slice(0, 10),
        corpo: inputCorpo.value,
        possivel_resposta: null
    };

    addEmail(newEmail);

    modalAdd.classList.add("hidden");
    inputAssunto.value = "";
    inputCorpo.value = "";
    fileInput.value = "";
});

function showLoading() {
    document.getElementById("loading-overlay").classList.remove("hidden");
}

function hideLoading() {
    document.getElementById("loading-overlay").classList.add("hidden");
}
