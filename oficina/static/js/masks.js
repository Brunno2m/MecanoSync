// Máscaras automáticas para campos de formulário

// Máscara de CPF: 000.000.000-00
function maskCPF(value) {
    return value
        .replace(/\D/g, '')
        .replace(/(\d{3})(\d)/, '$1.$2')
        .replace(/(\d{3})(\d)/, '$1.$2')
        .replace(/(\d{3})(\d{1,2})/, '$1-$2')
        .replace(/(-\d{2})\d+?$/, '$1');
}

// Máscara de CNPJ: 00.000.000/0000-00
function maskCNPJ(value) {
    return value
        .replace(/\D/g, '')
        .replace(/(\d{2})(\d)/, '$1.$2')
        .replace(/(\d{3})(\d)/, '$1.$2')
        .replace(/(\d{3})(\d)/, '$1/$2')
        .replace(/(\d{4})(\d)/, '$1-$2')
        .replace(/(-\d{2})\d+?$/, '$1');
}

// Máscara de CPF ou CNPJ (detecta automaticamente)
function maskCPFCNPJ(value) {
    const numbers = value.replace(/\D/g, '');
    
    if (numbers.length <= 11) {
        return maskCPF(value);
    } else {
        return maskCNPJ(value);
    }
}

// Máscara de Telefone: (00) 00000-0000 ou (00) 0000-0000
function maskPhone(value) {
    const numbers = value.replace(/\D/g, '');
    
    if (numbers.length <= 10) {
        // Telefone fixo: (00) 0000-0000
        return value
            .replace(/\D/g, '')
            .replace(/(\d{2})(\d)/, '($1) $2')
            .replace(/(\d{4})(\d)/, '$1-$2')
            .replace(/(-\d{4})\d+?$/, '$1');
    } else {
        // Celular: (00) 00000-0000
        return value
            .replace(/\D/g, '')
            .replace(/(\d{2})(\d)/, '($1) $2')
            .replace(/(\d{5})(\d)/, '$1-$2')
            .replace(/(-\d{4})\d+?$/, '$1');
    }
}

// Máscara de CEP: 00000-000
function maskCEP(value) {
    return value
        .replace(/\D/g, '')
        .replace(/(\d{5})(\d)/, '$1-$2')
        .replace(/(-\d{3})\d+?$/, '$1');
}

// Máscara de Placa de veículo: ABC-1234 ou ABC1D23 (Mercosul)
function maskPlaca(value) {
    value = value.replace(/[^a-zA-Z0-9]/g, '').toUpperCase();
    
    if (value.length <= 7) {
        // Formato antigo: ABC-1234
        return value
            .replace(/^([A-Z]{3})([0-9]{1,4})/, '$1-$2')
            .substring(0, 8);
    } else {
        // Formato Mercosul: ABC1D23
        return value.substring(0, 7);
    }
}

// Aplicar máscara em tempo real
function applyMask(input, maskFunction) {
    // Evitar aplicar máscara múltiplas vezes no mesmo input
    if (input.dataset.maskApplied) {
        return;
    }
    input.dataset.maskApplied = 'true';
    
    input.addEventListener('input', function(e) {
        const cursorPosition = this.selectionStart;
        const oldLength = this.value.length;
        
        this.value = maskFunction(this.value);
        
        const newLength = this.value.length;
        const diff = newLength - oldLength;
        
        // Ajustar posição do cursor
        this.setSelectionRange(cursorPosition + diff, cursorPosition + diff);
    });
    
    // Aplicar máscara no valor inicial se existir
    if (input.value) {
        input.value = maskFunction(input.value);
    }
}

// Inicializar máscaras automaticamente
document.addEventListener('DOMContentLoaded', function() {
    // Função auxiliar para aplicar máscara por identificadores múltiplos
    function applyMaskByIdentifiers(selectors, maskFunction) {
        selectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(input => {
                applyMask(input, maskFunction);
            });
        });
    }
    
    // CPF - busca por name, id, placeholder
    applyMaskByIdentifiers([
        'input[name="cpf"]',
        'input[id*="cpf"]',
        'input[placeholder*="CPF"]',
        'input[placeholder*="cpf"]',
        'input[placeholder*="000.000.000-00"]'
    ], maskCPF);
    
    // CNPJ - busca por name, id, placeholder
    applyMaskByIdentifiers([
        'input[name="cnpj"]',
        'input[id*="cnpj"]',
        'input[placeholder*="CNPJ"]',
        'input[placeholder*="cnpj"]',
        'input[placeholder*="00.000.000/0001-00"]'
    ], maskCNPJ);
    
    // CPF ou CNPJ - busca por name, id, placeholder
    applyMaskByIdentifiers([
        'input[name="cpf_cnpj"]',
        'input[id*="cpf_cnpj"]',
        'input[placeholder*="CPF/CNPJ"]',
        'input[placeholder*="cpf/cnpj"]'
    ], maskCPFCNPJ);
    
    // Telefone - busca por name, id, type, placeholder
    applyMaskByIdentifiers([
        'input[name="telefone"]',
        'input[id*="telefone"]',
        'input[type="tel"]',
        'input[placeholder*="telefone"]',
        'input[placeholder*="Telefone"]',
        'input[placeholder*="(00)"]',
        'input[placeholder*="0000-0000"]',
        'input[placeholder*="00000-0000"]'
    ], maskPhone);
    
    // CEP - busca por name, id, placeholder
    applyMaskByIdentifiers([
        'input[name="cep"]',
        'input[id*="cep"]',
        'input[placeholder*="CEP"]',
        'input[placeholder*="cep"]',
        'input[placeholder*="00000-000"]'
    ], maskCEP);
    
    // Placa de veículo - busca por name, id, placeholder
    applyMaskByIdentifiers([
        'input[name="placa"]',
        'input[id*="placa"]',
        'input[placeholder*="placa"]',
        'input[placeholder*="Placa"]',
        'input[placeholder*="ABC-1234"]'
    ], maskPlaca);
    
    // Observer para detectar novos campos adicionados dinamicamente
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) { // Element node
                    // Verificar se o próprio node é um input
                    if (node.tagName === 'INPUT') {
                        checkAndApplyMask(node);
                    }
                    // Verificar inputs dentro do node adicionado
                    node.querySelectorAll && node.querySelectorAll('input').forEach(checkAndApplyMask);
                }
            });
        });
    });
    
    // Função para verificar e aplicar máscara apropriada
    function checkAndApplyMask(input) {
        if (input.dataset.maskApplied) return;
        
        const name = input.name || '';
        const id = input.id || '';
        const placeholder = input.placeholder || '';
        const type = input.type || '';
        
        const lowerName = name.toLowerCase();
        const lowerId = id.toLowerCase();
        const lowerPlaceholder = placeholder.toLowerCase();
        
        // CPF
        if (lowerName.includes('cpf') && !lowerName.includes('cnpj') || 
            lowerId.includes('cpf') && !lowerId.includes('cnpj') ||
            lowerPlaceholder.includes('000.000.000-00')) {
            applyMask(input, maskCPF);
        }
        // CNPJ
        else if (lowerName.includes('cnpj') || lowerId.includes('cnpj') ||
                 lowerPlaceholder.includes('00.000.000/0001-00')) {
            applyMask(input, maskCNPJ);
        }
        // CPF/CNPJ
        else if (lowerName.includes('cpf_cnpj') || lowerId.includes('cpf_cnpj')) {
            applyMask(input, maskCPFCNPJ);
        }
        // Telefone
        else if (lowerName.includes('telefone') || lowerId.includes('telefone') || 
                 type === 'tel' || lowerPlaceholder.includes('(00)') ||
                 lowerPlaceholder.includes('0000-0000') || lowerPlaceholder.includes('00000-0000')) {
            applyMask(input, maskPhone);
        }
        // CEP
        else if (lowerName.includes('cep') || lowerId.includes('cep') ||
                 lowerPlaceholder.includes('00000-000')) {
            applyMask(input, maskCEP);
        }
        // Placa
        else if (lowerName.includes('placa') || lowerId.includes('placa') ||
                 lowerPlaceholder.includes('abc-1234')) {
            applyMask(input, maskPlaca);
        }
    }
    
    // Iniciar observação do DOM
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});

// Exportar funções para uso externo
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        maskCPF,
        maskCNPJ,
        maskCPFCNPJ,
        maskPhone,
        maskCEP,
        maskPlaca,
        applyMask
    };
}
