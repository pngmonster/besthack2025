// Глобальные переменные для карты
let map;
let markers = [];

// Инициализация карты при загрузке страницы
function initMap() {
    map = L.map('map', {
        attributionControl: false  // Полностью отключаем контроль атрибуции
    }).setView([55.7558, 37.6173], 10);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
}

// Очистка маркеров
function clearMarkers() {
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
}

// Добавление маркеров на карту
function addMarkersToMap(objects) {
    clearMarkers();

    if (!objects || objects.length === 0) return;

    const bounds = [];

    objects.forEach((object, index) => {
        const marker = L.marker([object.lat, object.lon])
            .addTo(map)
            .bindPopup(`
                <b>Результат ${index + 1}</b><br>
                ${object.locality}, ${object.street} ${object.number}<br>
                Score: ${Math.round(object.score * 100)}%
            `);

        markers.push(marker);
        bounds.push([object.lat, object.lon]);
    });

    // Подгоняем карту чтобы показать все маркеры
    if (bounds.length > 0) {
        map.fitBounds(bounds);
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const searchBtn = document.getElementById('searchBtn');
    const addressInput = document.getElementById('addressInput');
    const outputSection = document.querySelector('.output-section');

    initMap();

    searchBtn.addEventListener('click', function () {
        const address = addressInput.value.trim();

        if (!address) {
            alert('Пожалуйста, введите адрес для поиска');
            return;
        }

        searchBtn.classList.add('loading');

        // Запрос к бекенду
        searchAddress(address)
            .then(data => {
                // Обновляем интерфейс с полученными данными
                updateUI(data);
            })
            .catch(error => {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при поиске адреса');
            })
            .finally(() => {
                searchBtn.classList.remove('loading');
            });
    });

    async function searchAddress(address) {
        const baseUrl = 'http://81.200.145.134:8000';
        const url = `${baseUrl}/api/search?address=${encodeURIComponent(address)}`;

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) {
            throw new Error(`Ошибка HTTP: ${response.status}`);
        }

        return await response.json();
    }

    // Функция для обновления интерфейса
    function updateUI(data) {
        const outputLabel = outputSection.querySelector('.input-label');
        outputSection.innerHTML = '';
        outputSection.appendChild(outputLabel);

        if (data.objects && data.objects.length > 0) {
            const resultsContainer = document.createElement('div');
            resultsContainer.className = 'results-container';

            data.objects.forEach((object, index) => {
                const outputBox = createOutputBox(object, index + 1);
                resultsContainer.appendChild(outputBox);
            });

            outputSection.appendChild(resultsContainer);
        } else {
            // Если объекты не найдены
            const noResultsBox = document.createElement('div');
            noResultsBox.className = 'output-box';
            noResultsBox.innerHTML = `
                <div class="score-badge">0%</div>
                <div class="output-content">
                    <div class="output-field">
                        <span class="field-label">Адрес:</span>
                        <span class="field-value">Адрес не найден</span>
                    </div>
                    <div class="output-field">
                        <span class="field-label">Координаты:</span>
                        <span class="field-value">Нет координат</span>
                    </div>
                </div>
            `;
            outputSection.appendChild(noResultsBox);
        }

        if (data.objects && data.objects.length > 0) {
            addMarkersToMap(data.objects);
        }
    }

    // Функция для создания блока результата
    function createOutputBox(object, number) {
        const outputBox = document.createElement('div');
        outputBox.className = 'output-box';

        // Формируем адрес
        const addressParts = [
            object.locality,
            object.street,
            object.number
        ].filter(part => part && part.trim() !== '');

        const address = addressParts.join(', ');

        outputBox.innerHTML = `
            <div class="result-number">${number}</div>
            <div class="score-badge">${Math.round(object.score * 100)}%</div>
            <div class="output-content">
                <div class="output-field">
                    <span class="field-label">Адрес:</span>
                    <span class="field-value">${address}</span>
                </div>
                <div class="output-field">
                    <span class="field-label">Координаты:</span>
                    <span class="field-value">${object.lat}, ${object.lon}</span>
                </div>
            </div>
        `;

        return outputBox;
    }
});