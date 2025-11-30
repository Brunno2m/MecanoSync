// Navigation
const navItems = document.querySelectorAll('.nav-item');
const pages = document.querySelectorAll('.page');

navItems.forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Remove active class from all nav items
        navItems.forEach(nav => nav.classList.remove('active'));
        
        // Add active class to clicked item
        item.classList.add('active');
        
        // Hide all pages
        pages.forEach(page => page.classList.remove('active'));
        
        // Show selected page
        const pageId = item.getAttribute('data-page');
        if (pageId) {
            const targetPage = document.getElementById(pageId);
            if (targetPage) {
                targetPage.classList.add('active');
            }
        }
    });
});

// Mobile Menu Toggle
const menuToggle = document.querySelector('.menu-toggle');
const sidebar = document.querySelector('.sidebar');

if (menuToggle) {
    menuToggle.addEventListener('click', () => {
        sidebar.classList.toggle('active');
    });
}

// Close sidebar when clicking outside on mobile
document.addEventListener('click', (e) => {
    if (window.innerWidth <= 768) {
        if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
            sidebar.classList.remove('active');
        }
    }
});

// Modal Functions
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
}

// Close modal when clicking outside
document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
            document.body.style.overflow = 'auto';
        }
    });
});

// Close modal with Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal.active').forEach(modal => {
            modal.classList.remove('active');
            document.body.style.overflow = 'auto';
        });
    }
});

// Form Handlers
const clienteForm = document.getElementById('clienteForm');
if (clienteForm) {
    clienteForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Get form data
        const formData = new FormData(clienteForm);
        
        // Here you would typically send data to a server
        console.log('Cliente data:', Object.fromEntries(formData));
        
        // Show success message
        alert('Cliente cadastrado com sucesso!');
        
        // Close modal and reset form
        closeModal('clienteModal');
        clienteForm.reset();
        
        // Refresh table (in a real app, this would update with server data)
        addClienteToTable(formData);
    });
}

const ordemForm = document.getElementById('ordemForm');
if (ordemForm) {
    ordemForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Get form data
        const formData = new FormData(ordemForm);
        
        // Here you would typically send data to a server
        console.log('Ordem data:', Object.fromEntries(formData));
        
        // Show success message
        alert('Ordem de serviço criada com sucesso!');
        
        // Close modal and reset form
        closeModal('ordemModal');
        ordemForm.reset();
        
        // Refresh table
        addOrdemToTable(formData);
    });
}

// Add Cliente to Table
function addClienteToTable(formData) {
    const tbody = document.getElementById('clientesTable');
    if (!tbody) return;
    
    const newRow = tbody.insertRow(0);
    const clienteId = '#' + String(Math.floor(Math.random() * 1000)).padStart(3, '0');
    const today = new Date().toLocaleDateString('pt-BR');
    
    newRow.innerHTML = `
        <td>${clienteId}</td>
        <td>${formData.get('nome') || 'Novo Cliente'}</td>
        <td>${formData.get('telefone') || '-'}</td>
        <td>${formData.get('email') || '-'}</td>
        <td>${formData.get('veiculo') || '-'}</td>
        <td>${today}</td>
        <td>
            <button class="btn-icon" title="Editar" onclick="editCliente('${clienteId}')">
                <i class="fas fa-edit"></i>
            </button>
            <button class="btn-icon" title="Excluir" onclick="deleteCliente('${clienteId}')">
                <i class="fas fa-trash"></i>
            </button>
        </td>
    `;
    
    // Animate new row
    newRow.style.animation = 'fadeIn 0.5s ease';
}

// Add Ordem to Table
function addOrdemToTable(formData) {
    const tbody = document.getElementById('ordensTable');
    if (!tbody) return;
    
    const newRow = tbody.insertRow(0);
    const ordemId = '#' + String(1234 + tbody.rows.length);
    
    newRow.innerHTML = `
        <td>${ordemId}</td>
        <td>${formData.get('cliente') || '-'}</td>
        <td>${formData.get('veiculo') || '-'}</td>
        <td>${formData.get('servicos') || '-'}</td>
        <td>${formData.get('dataEntrada') || '-'}</td>
        <td>${formData.get('previsao') || '-'}</td>
        <td><span class="badge-status em-andamento">${formData.get('status') || 'Em Andamento'}</span></td>
        <td>R$ ${formData.get('valor') || '0,00'}</td>
        <td>
            <button class="btn-icon" title="Visualizar" onclick="viewOrdem('${ordemId}')">
                <i class="fas fa-eye"></i>
            </button>
            <button class="btn-icon" title="Editar" onclick="editOrdem('${ordemId}')">
                <i class="fas fa-edit"></i>
            </button>
        </td>
    `;
    
    // Animate new row
    newRow.style.animation = 'fadeIn 0.5s ease';
}

// CRUD Functions (placeholders)
function editCliente(id) {
    alert(`Editar cliente ${id}`);
    // In a real app, this would open the modal with pre-filled data
}

function deleteCliente(id) {
    if (confirm(`Deseja realmente excluir o cliente ${id}?`)) {
        alert(`Cliente ${id} excluído`);
        // In a real app, this would send a delete request to the server
    }
}

function viewOrdem(id) {
    alert(`Visualizar ordem ${id}`);
    // In a real app, this would show detailed order information
}

function editOrdem(id) {
    alert(`Editar ordem ${id}`);
    // In a real app, this would open the modal with pre-filled data
}

// Search Functionality
const searchInputs = document.querySelectorAll('.search-bar input, .search-box input');
searchInputs.forEach(input => {
    input.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const table = e.target.closest('.card')?.querySelector('table tbody');
        
        if (table) {
            const rows = table.querySelectorAll('tr');
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        }
    });
});

// Filter Functionality
const filterSelects = document.querySelectorAll('.filter-select');
filterSelects.forEach(select => {
    select.addEventListener('change', (e) => {
        const filterValue = e.target.value.toLowerCase();
        const table = e.target.closest('.card')?.querySelector('table tbody');
        
        if (table) {
            const rows = table.querySelectorAll('tr');
            rows.forEach(row => {
                if (filterValue === 'todos' || filterValue === 'todas') {
                    row.style.display = '';
                } else {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(filterValue) ? '' : 'none';
                }
            });
        }
    });
});

// Chart.js Configuration (if Chart.js is loaded)
if (typeof Chart !== 'undefined') {
    const ctx = document.getElementById('revenueChart');
    if (ctx) {
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov'],
                datasets: [{
                    label: 'Faturamento',
                    data: [32000, 38000, 35000, 42000, 39000, 45890],
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return 'R$ ' + value.toLocaleString('pt-BR');
                            }
                        }
                    }
                }
            }
        });
    }
}

// Real-time Clock
function updateClock() {
    const now = new Date();
    const options = { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    const dateString = now.toLocaleDateString('pt-BR', options);
    
    // Update if there's a clock element
    const clockElement = document.querySelector('.clock');
    if (clockElement) {
        clockElement.textContent = dateString;
    }
}

// Update clock every minute
setInterval(updateClock, 60000);
updateClock();

// Notification Handler
const notificationBtn = document.querySelector('.notification-btn');
if (notificationBtn) {
    notificationBtn.addEventListener('click', () => {
        alert('Você tem 3 notificações:\n\n1. Nova ordem de serviço criada\n2. Pagamento recebido\n3. Estoque baixo: Óleo 5W30');
    });
}

// Auto-save form data to localStorage (optional feature)
function autoSaveForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const inputs = form.querySelectorAll('input, select, textarea');
    
    // Load saved data
    inputs.forEach(input => {
        const savedValue = localStorage.getItem(`${formId}_${input.name}`);
        if (savedValue && input.type !== 'password') {
            input.value = savedValue;
        }
    });
    
    // Save on input
    inputs.forEach(input => {
        input.addEventListener('input', () => {
            if (input.name) {
                localStorage.setItem(`${formId}_${input.name}`, input.value);
            }
        });
    });
    
    // Clear on submit
    form.addEventListener('submit', () => {
        inputs.forEach(input => {
            if (input.name) {
                localStorage.removeItem(`${formId}_${input.name}`);
            }
        });
    });
}

// Initialize auto-save for forms
autoSaveForm('clienteForm');
autoSaveForm('ordemForm');

// Format currency inputs
document.querySelectorAll('input[type="number"]').forEach(input => {
    if (input.step === '0.01') {
        input.addEventListener('blur', (e) => {
            if (e.target.value) {
                const value = parseFloat(e.target.value);
                e.target.value = value.toFixed(2);
            }
        });
    }
});

// Print functionality
function printPage() {
    window.print();
}

// Export to CSV (simple implementation)
function exportToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const rowData = Array.from(cols).map(col => {
            return '"' + col.textContent.trim().replace(/"/g, '""') + '"';
        });
        csv.push(rowData.join(','));
    });
    
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || 'export.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}

// Initialize tooltips
document.querySelectorAll('[title]').forEach(element => {
    element.addEventListener('mouseenter', (e) => {
        const title = e.target.getAttribute('title');
        if (title) {
            e.target.setAttribute('data-title', title);
            e.target.removeAttribute('title');
        }
    });
});

// Smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href !== '#') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        }
    });
});

// Console welcome message
console.log('%cMecanoSync Dashboard', 'color: #2563eb; font-size: 24px; font-weight: bold;');
console.log('%cSistema de Gestão para Oficinas Mecânicas', 'color: #64748b; font-size: 14px;');
console.log('%cVersão 1.0.0', 'color: #64748b; font-size: 12px;');

// Check for updates (placeholder)
function checkForUpdates() {
    // In a real app, this would check with a server
    console.log('Verificando atualizações...');
}

// Run on load
document.addEventListener('DOMContentLoaded', () => {
    checkForUpdates();
    
    // Set current date in date inputs
    const today = new Date().toISOString().split('T')[0];
    document.querySelectorAll('input[type="date"]').forEach(input => {
        if (!input.value) {
            input.value = today;
        }
    });
});
