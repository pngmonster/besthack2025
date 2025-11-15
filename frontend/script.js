class AddressSearch {
    constructor() {
        this.searchBtn = document.getElementById('searchBtn');
        this.addressInput = document.getElementById('addressInput');
        this.outputAddress = document.getElementById('outputAddress');
        this.outputCoordinates = document.getElementById('outputCoordinates');
        this.marker = document.getElementById('marker');

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
            // Временная заглушка для демонстрации
            const result = await this.mockSearch(address);

            if (result) {
                this.updateOutput(result);
                this.showMarker(result.coordinates);
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

    // Временная функция-заглушка
    async mockSearch(address) {
        // Имитация задержки сети
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Для демонстрации возвращаем тестовые данные
        return {
            address: `г. Москва, ул. Тверская, д. 7 (по запросу: "${address}")`,
            coordinates: {
                lat: 55.7602,
                lng: 37.6085
            },
            formattedAddress: `г. Москва, ул. Тверская, дом 7`,
            formattedCoordinates: `55.7602, 37.6085`
        };
    }

    updateOutput(result) {
        this.outputAddress.textContent = result.formattedAddress || result.address;
        this.outputCoordinates.textContent = result.formattedCoordinates ||
            `${result.coordinates.lat}, ${result.coordinates.lng}`;
    }

    clearOutput() {
        this.outputAddress.textContent = '—';
        this.outputCoordinates.textContent = '—';
        this.marker.classList.add('hidden');
    }

    showMarker(coordinates) {
        this.marker.classList.remove('hidden');

        // Здесь будет логика для реальной карты
        console.log('Показываем маркер на координатах:', coordinates);
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
        // Удаляем предыдущие уведомления
        const existingNotification = document.querySelector('.notification');
        if (existingNotification) {
            existingNotification.remove();
        }

        // Создаем уведомление
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;

        // Стили для уведомления
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

        // Анимация появления
        setTimeout(() => {
            notification.style.transform = 'translateX(-50%) translateY(0)';
        }, 100);

        // Автоматическое скрытие
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