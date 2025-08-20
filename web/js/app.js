// Configurações globais
const API_BASE_URL = 'http://localhost:5000/api';
let currentArea = null;
let allEvents = [];
let filteredEvents = [];
let updateInterval = null;
let currentDateFilter = {
    startDate: null,
    endDate: null
};

// Inicialização da aplicação
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupFormListeners();
});

async function initializeApp() {
    showLoading();
    
    try {
        await loadAreas();
        await loadUncategorizedEvents();
        updateLastUpdateTime();
        
        // Configurar atualização automática
        setupAutoUpdate();
        
        hideLoading();
    } catch (error) {
        console.error('Erro ao inicializar aplicação:', error);
        hideLoading();
        showError('Erro ao carregar dados. Tente novamente.');
    }
}

// Configurar listeners do formulário
function setupFormListeners() {
    const observacaoTextarea = document.getElementById('observacao');
    const charCount = document.getElementById('charCount');
    
    if (observacaoTextarea && charCount) {
        observacaoTextarea.addEventListener('input', function() {
            const length = this.value.length;
            charCount.textContent = `${length}/1500`;
            
            if (length > 1500) {
                this.value = this.value.substring(0, 1500);
                charCount.textContent = '1500/1500';
            }
        });
    }
    
    const proposicaoForm = document.getElementById('proposicaoForm');
    if (proposicaoForm) {
        proposicaoForm.addEventListener('submit', handleProposicaoSubmit);
    }
}

// Carregar áreas técnicas
async function loadAreas() {
    try {
        const response = await fetch(`${API_BASE_URL}/areas`);
        const areas = await response.json();
        
        const areaGrid = document.getElementById('areaGrid');
        areaGrid.innerHTML = '';
        
        areas.forEach(area => {
            const areaCard = createAreaCard(area);
            areaGrid.appendChild(areaCard);
        });
        
        // Adicionar card para eventos não categorizados
        const uncategorizedCard = createUncategorizedCard();
        areaGrid.appendChild(uncategorizedCard);
        
        // Atualizar contadores
        await updateEventCounts();
        
    } catch (error) {
        console.error('Erro ao carregar áreas:', error);
        throw error;
    }
}

// Criar card de área técnica
function createAreaCard(area) {
    const card = document.createElement('div');
    card.className = 'area-card';
    card.onclick = () => selectArea(area.nome);
    
    card.innerHTML = `
        <h3>${area.nome}</h3>
        <p>${area.descricao || 'Área técnica do municipalismo'}</p>
        <span class="event-count" id="count-${area.nome.replace(/\s+/g, '-')}">0</span>
    `;
    
    return card;
}

// Criar card para eventos não categorizados
function createUncategorizedCard() {
    const card = document.createElement('div');
    card.className = 'area-card';
    card.onclick = () => showUncategorizedEvents();
    
    card.innerHTML = `
        <h3>Eventos Não Categorizados</h3>
        <p>Eventos que ainda não foram classificados em áreas técnicas</p>
        <span class="event-count" id="count-uncategorized">0</span>
    `;
    
    return card;
}

// Selecionar área técnica
async function selectArea(areaName) {
    showLoading();
    currentArea = areaName;
    
    try {
        await loadAreaData(areaName);
        showDashboard();
        hideLoading();
    } catch (error) {
        console.error('Erro ao carregar área:', error);
        hideLoading();
        showError('Erro ao carregar dados da área. Tente novamente.');
    }
}

// Carregar dados da área
async function loadAreaData(areaName) {
    try {
        // Carregar eventos
        const eventsResponse = await fetch(`${API_BASE_URL}/eventos?area=${encodeURIComponent(areaName)}`);
        const events = await eventsResponse.json();
        
        // Carregar estatísticas
        const statsResponse = await fetch(`${API_BASE_URL}/estatisticas?area=${encodeURIComponent(areaName)}`);
        const stats = await statsResponse.json();
        
        // Carregar proposições
        const proposicoesResponse = await fetch(`${API_BASE_URL}/proposicoes?area=${encodeURIComponent(areaName)}`);
        const proposicoes = await proposicoesResponse.json();
        
        updateDashboard(areaName, events, stats, proposicoes);
        
    } catch (error) {
        console.error('Erro ao carregar dados da área:', error);
        throw error;
    }
}

// Atualizar dashboard
function updateDashboard(areaName, events, stats, proposicoes) {
    // Atualizar título
    document.getElementById('currentAreaTitle').textContent = areaName;
    
    // Atualizar estatísticas de eventos
    const totalEvents = events.length;
    const ongoingEvents = events.filter(e => e.situacao === 'Em Andamento').length;
    const completedEvents = events.filter(e => e.situacao === 'Encerrada').length;
    
    document.getElementById('totalEvents').textContent = totalEvents;
    document.getElementById('ongoingEvents').textContent = ongoingEvents;
    document.getElementById('completedEvents').textContent = completedEvents;
    
    // Atualizar estatísticas de proposições
    updateStatisticsTable(stats);
    
    // Atualizar tabela de proposições
    updateProposicoesTable(proposicoes);
    
    // Atualizar eventos
    allEvents = events;
    filteredEvents = events;
    renderEvents(events);
}

// Atualizar tabela de estatísticas
function updateStatisticsTable(stats) {
    // Posicionamento CNM
    document.getElementById('cnmFavoravel').textContent = stats.cnm_favoravel || 0;
    document.getElementById('cnmDesfavoravel').textContent = stats.cnm_desfavoravel || 0;
    document.getElementById('cnmNeutro').textContent = stats.cnm_neutro || 0;
    
    // Aprovação na Câmara
    document.getElementById('camaraCnmFavoravel').textContent = stats.camara_cnm_favoravel || 0;
    document.getElementById('camaraCnmDesfavoravel').textContent = stats.camara_cnm_desfavoravel || 0;
    document.getElementById('camaraCnmNeutro').textContent = stats.camara_cnm_neutro || 0;
    
    // Aprovação no Senado
    document.getElementById('senadoCnmFavoravel').textContent = stats.senado_cnm_favoravel || 0;
    document.getElementById('senadoCnmDesfavoravel').textContent = stats.senado_cnm_desfavoravel || 0;
    document.getElementById('senadoCnmNeutro').textContent = stats.senado_cnm_neutro || 0;
    
    // Sancionado pela Presidência
    document.getElementById('presidenciaCnmFavoravel').textContent = stats.presidencia_cnm_favoravel || 0;
    document.getElementById('presidenciaCnmDesfavoravel').textContent = stats.presidencia_cnm_desfavoravel || 0;
    document.getElementById('presidenciaCnmNeutro').textContent = stats.presidencia_cnm_neutro || 0;
}

// Atualizar tabela de proposições
function updateProposicoesTable(proposicoes) {
    const tbody = document.getElementById('proposicoesTableBody');
    tbody.innerHTML = '';
    
    proposicoes.forEach(proposicao => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${proposicao.numero_projeto || '-'}</td>
            <td>${proposicao.ementa || '-'}</td>
            <td>${proposicao.casa_iniciadora || '-'}</td>
            <td>${proposicao.forma_apreciacao || '-'}</td>
            <td>${proposicao.eixo_tematico || '-'}</td>
            <td>${proposicao.situacao || '-'}</td>
            <td>${proposicao.cabe_analise || '-'}</td>
            <td>${proposicao.prazo_analise || '-'}</td>
            <td>${proposicao.analise_realizada || '-'}</td>
            <td>${proposicao.documento_analise ? '<i class="fas fa-file-alt"></i>' : '-'}</td>
            <td>${proposicao.posicionamento_cnm || '-'}</td>
            <td>${proposicao.prioridade || '-'}</td>
            <td>${proposicao.observacao ? proposicao.observacao.substring(0, 50) + '...' : '-'}</td>
            <td class="actions">
                <button class="action-btn edit" onclick="editProposicao(${proposicao.id})" title="Editar">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="action-btn delete" onclick="deleteProposicao(${proposicao.id})" title="Excluir">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Renderizar eventos
function renderEvents(events) {
    const eventsGrid = document.getElementById('eventsGrid');
    eventsGrid.innerHTML = '';
    
    if (events.length === 0) {
        eventsGrid.innerHTML = '<p class="no-events">Nenhum evento encontrado para o período selecionado.</p>';
        return;
    }
    
    events.forEach(event => {
        const eventCard = createEventCard(event);
        eventsGrid.appendChild(eventCard);
    });
}

// Criar card de evento
function createEventCard(event) {
    const card = document.createElement('div');
    card.className = 'event-card';
    
    const statusClass = event.situacao.toLowerCase().replace(' ', '-');
    
    card.innerHTML = `
        <div class="event-header">
            <h4 class="event-title">${event.nome}</h4>
            <span class="event-status ${statusClass}">${event.situacao}</span>
        </div>
        <div class="event-details">
            <div class="event-detail">
                <i class="fas fa-calendar"></i>
                <span><strong>Início:</strong> ${event.data_inicio}</span>
            </div>
            <div class="event-detail">
                <i class="fas fa-calendar-check"></i>
                <span><strong>Fim:</strong> ${event.data_fim}</span>
            </div>
            <div class="event-detail">
                <i class="fas fa-tag"></i>
                <span><strong>Tema:</strong> ${event.tema}</span>
            </div>
            <div class="event-detail">
                <i class="fas fa-map-marker-alt"></i>
                <span><strong>Local:</strong> ${event.local_evento}</span>
            </div>
            <div class="event-detail">
                <i class="fas fa-info-circle"></i>
                <span><strong>Tipo:</strong> ${event.tipo_evento}</span>
            </div>
        </div>
        <div class="event-link">
            <a href="${event.link_evento}" target="_blank">
                <i class="fas fa-external-link-alt"></i>
                Ver detalhes do evento
            </a>
        </div>
    `;
    
    return card;
}

// Filtrar eventos
function filterEvents() {
    const statusFilter = document.getElementById('statusFilter').value;
    const typeFilter = document.getElementById('typeFilter').value;
    
    filteredEvents = allEvents.filter(event => {
        const statusMatch = !statusFilter || event.situacao === statusFilter;
        const typeMatch = !typeFilter || event.tipo_evento === typeFilter;
        return statusMatch && typeMatch;
    });
    
    renderEvents(filteredEvents);
}

// Atualizar contadores de eventos
async function updateEventCounts() {
    try {
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;
        
        // Atualizar contadores para cada área
        const areas = await fetch(`${API_BASE_URL}/areas`).then(r => r.json());
        
        for (const area of areas) {
            const countElement = document.getElementById(`count-${area.nome.replace(/\s+/g, '-')}`);
            if (countElement) {
                const params = new URLSearchParams({
                    area: area.nome,
                    ...(startDate && { start_date: startDate }),
                    ...(endDate && { end_date: endDate })
                });
                
                const response = await fetch(`${API_BASE_URL}/eventos?${params}`);
                const events = await response.json();
                countElement.textContent = events.length;
            }
        }
        
        // Atualizar contador de não categorizados
        const uncategorizedCount = document.getElementById('count-uncategorized');
        if (uncategorizedCount) {
            const params = new URLSearchParams({
                ...(startDate && { start_date: startDate }),
                ...(endDate && { end_date: endDate })
            });
            
            const response = await fetch(`${API_BASE_URL}/eventos/nao-categorizados?${params}`);
            const events = await response.json();
            uncategorizedCount.textContent = events.length;
        }
        
    } catch (error) {
        console.error('Erro ao atualizar contadores:', error);
    }
}

// Aplicar filtro de data
function applyDateFilter() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    
    if (startDate && endDate && startDate > endDate) {
        showError('A data de início deve ser anterior à data de fim.');
        return;
    }
    
    currentDateFilter = { startDate, endDate };
    updateEventCounts();
    
    if (currentArea) {
        loadAreaData(currentArea);
    }
    
    showSuccess('Filtro de período aplicado com sucesso!');
}

// Mostrar dashboard
function showDashboard() {
    document.querySelector('.area-selection').style.display = 'none';
    document.getElementById('dashboardContent').style.display = 'block';
    document.getElementById('uncategorizedSection').style.display = 'none';
}

// Mostrar seleção de áreas
function showAreaSelection() {
    document.querySelector('.area-selection').style.display = 'block';
    document.getElementById('dashboardContent').style.display = 'none';
    document.getElementById('uncategorizedSection').style.display = 'none';
}

// Mostrar eventos não categorizados
async function showUncategorizedEvents() {
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/eventos/nao-categorizados`);
        const events = await response.json();
        
        const eventsGrid = document.getElementById('uncategorizedEventsGrid');
        eventsGrid.innerHTML = '';
        
        events.forEach(event => {
            const eventCard = createEventCard(event);
            eventsGrid.appendChild(eventCard);
        });
        
        document.querySelector('.area-selection').style.display = 'none';
        document.getElementById('dashboardContent').style.display = 'none';
        document.getElementById('uncategorizedSection').style.display = 'block';
        
        hideLoading();
    } catch (error) {
        console.error('Erro ao carregar eventos não categorizados:', error);
        hideLoading();
        showError('Erro ao carregar eventos não categorizados.');
    }
}

// Carregar eventos não categorizados
async function loadUncategorizedEvents() {
    try {
        const response = await fetch(`${API_BASE_URL}/eventos/nao-categorizados`);
        const events = await response.json();
        
        const countElement = document.getElementById('count-uncategorized');
        if (countElement) {
            countElement.textContent = events.length;
        }
    } catch (error) {
        console.error('Erro ao carregar eventos não categorizados:', error);
    }
}

// Atualizar dados
async function refreshData() {
    showLoading();
    
    try {
        await loadAreas();
        await loadUncategorizedEvents();
        
        if (currentArea) {
            await loadAreaData(currentArea);
        }
        
        updateLastUpdateTime();
        showSuccess('Dados atualizados com sucesso!');
        
        hideLoading();
    } catch (error) {
        console.error('Erro ao atualizar dados:', error);
        hideLoading();
        showError('Erro ao atualizar dados. Tente novamente.');
    }
}

// Configurar atualização automática
function setupAutoUpdate() {
    // Atualizar a cada hora
    updateInterval = setInterval(async () => {
        await checkForNewEvents();
    }, 3600000); // 1 hora
}

// Verificar novos eventos
async function checkForNewEvents() {
    try {
        const response = await fetch(`${API_BASE_URL}/eventos/novos`);
        const newEvents = await response.json();
        
        if (newEvents.length > 0) {
            newEvents.forEach(event => {
                showNewEventNotification(event);
            });
        }
        
        updateLastUpdateTime();
    } catch (error) {
        console.error('Erro ao verificar novos eventos:', error);
    }
}

// Mostrar notificação de novo evento
function showNewEventNotification(event) {
    const modal = document.getElementById('notificationModal');
    const content = document.getElementById('notificationContent');
    
    content.innerHTML = `
        <div class="new-event-notification">
            <h4>${event.nome}</h4>
            <p><strong>Data:</strong> ${event.data_inicio}</p>
            <p><strong>Local:</strong> ${event.local_evento}</p>
            <p><strong>Área:</strong> ${event.area_tecnica || 'Não categorizado'}</p>
        </div>
    `;
    
    modal.style.display = 'flex';
}

// Fechar notificação
function closeNotification() {
    document.getElementById('notificationModal').style.display = 'none';
}

// Mostrar modal de adicionar proposição
function showAddProposicaoModal() {
    document.getElementById('addProposicaoModal').style.display = 'flex';
}

// Fechar modal de adicionar proposição
function closeAddProposicaoModal() {
    document.getElementById('addProposicaoModal').style.display = 'none';
    document.getElementById('proposicaoForm').reset();
    document.getElementById('charCount').textContent = '0/1500';
}

// Manipular envio do formulário de proposição
async function handleProposicaoSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const proposicaoData = {
        numero_projeto: formData.get('numeroProjeto'),
        ementa: formData.get('ementa'),
        casa_iniciadora: formData.get('casaIniciadora'),
        forma_apreciacao: formData.get('formaApreciacao'),
        situacao: formData.get('situacao'),
        cabe_analise: formData.get('cabeAnalise'),
        prazo_analise: formData.get('prazoAnalise'),
        analise_realizada: formData.get('analiseRealizada'),
        posicionamento_cnm: formData.get('posicionamentoCnm'),
        prioridade: formData.get('prioridade'),
        observacao: formData.get('observacao'),
        area_tecnica: currentArea
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/proposicoes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(proposicaoData)
        });
        
        if (response.ok) {
            showSuccess('Proposição adicionada com sucesso!');
            closeAddProposicaoModal();
            
            // Recarregar dados da área
            if (currentArea) {
                await loadAreaData(currentArea);
            }
        } else {
            throw new Error('Erro ao adicionar proposição');
        }
    } catch (error) {
        console.error('Erro ao adicionar proposição:', error);
        showError('Erro ao adicionar proposição. Tente novamente.');
    }
}

// Editar proposição
function editProposicao(id) {
    // Implementar edição de proposição
    console.log('Editar proposição:', id);
}

// Excluir proposição
async function deleteProposicao(id) {
    if (!confirm('Tem certeza que deseja excluir esta proposição?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/proposicoes/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showSuccess('Proposição excluída com sucesso!');
            
            // Recarregar dados da área
            if (currentArea) {
                await loadAreaData(currentArea);
            }
        } else {
            throw new Error('Erro ao excluir proposição');
        }
    } catch (error) {
        console.error('Erro ao excluir proposição:', error);
        showError('Erro ao excluir proposição. Tente novamente.');
    }
}

// Atualizar horário da última atualização
function updateLastUpdateTime() {
    const now = new Date();
    const timeString = now.toLocaleString('pt-BR');
    document.getElementById('lastUpdate').textContent = `Última atualização: ${timeString}`;
}

// Funções de UI
function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

function showError(message) {
    // Implementar notificação de erro
    alert('Erro: ' + message);
}

function showSuccess(message) {
    // Implementar notificação de sucesso
    alert('Sucesso: ' + message);
}

// Limpar intervalo ao sair da página
window.addEventListener('beforeunload', () => {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
});
