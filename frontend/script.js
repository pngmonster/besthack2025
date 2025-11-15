class AddressSearch {
    constructor() {
        this.searchBtn = document.getElementById('searchBtn');
        this.addressInput = document.getElementById('addressInput');
        this.outputAddress = document.getElementById('outputAddress');
        this.outputCoordinates = document.getElementById('outputCoordinates');

        this.init();
    }

    init() {
        this.searchBtn.addEventListener('click', () => this.handleSearch());
        this.addressInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.handleSearch();
            }
        });
    }

    async handleSearch() {
        const address = this.addressInput.value.trim();

        if (!address) {
            this.showMessage('Введите адрес для поиска', 'info');
            return;
        }

        this.setLoading(true);
        this.clearOutput();

        try {
            // Здесь будет вызов к Python бекенду
            const result = await this.searchAddress(address);

            if (result) {
                this.updateOutput(result);
                this.showMessage('Адрес успешно найден', 'success');
            } else {
                this.showMessage('Адрес не найден', 'error');
            }
        } catch (error) {
            console.error('Search error:', error);
            this.showMessage('Ошибка при поиске', 'error');
        } finally {
            this.setLoading(false);
        }
    }

    // Функция для вызова Python бекенда
    async searchAddress(address) {
        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ address: address })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;

        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    }

    updateOutput(result) {
        this.outputAddress.textContent = result.formattedAddress || result.address;
        this.outputCoordinates.textContent = result.formattedCoordinates ||
            `${result.coordinates.lat}, ${result.coordinates.lng}`;
    }

    clearOutput() {
        this.outputAddress.textContent = '—';
        this.outputCoordinates.textContent = '—';
    }

    setLoading(loading) {
        if (loading) {
            this.searchBtn.classList.add('loading');
            this.searchBtn.disabled = true;
        } else {
            this.searchBtn.classList.remove('loading');
            this.searchBtn.disabled = false;
        }
    }

    showMessage(message, type) {
        const existingNotification = document.querySelector('.notification');
        if (existingNotification) {
            existingNotification.remove();
        }

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;

        notification.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%) translateY(100%);
            padding: 0.75rem 1.25rem;
            border-radius: 6px;
            color: white;
            font-size: 0.9rem;
            font-weight: 500;
            z-index: 1000;
            transition: transform 0.3s ease;
            ${type === 'error' ? 'background: #dc2626;' :
                type === 'success' ? 'background: #059669;' :
                    'background: #4b5563;'}
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.transform = 'translateX(-50%) translateY(0)';
        }, 100);

        setTimeout(() => {
            notification.style.transform = 'translateX(-50%) translateY(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Инициализация приложения
document.addEventListener('DOMContentLoaded', () => {
    new AddressSearch();
});