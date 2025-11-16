document.addEventListener('DOMContentLoaded', function () {
    const searchBtn = document.getElementById('searchBtn');
    const addressInput = document.getElementById('addressInput');
    const outputSection = document.querySelector('.output-section');

    searchBtn.addEventListener('click', function () {
        const address = addressInput.value.trim();

        if (!address) {
            alert('Пожалуйста, введите адрес для поиска');
            return;
        }

        // Показываем спиннер загрузки
        searchBtn.classList.add('loading');

        // Имитируем запрос к бекенду (замените на реальный fetch)
        simulateBackendRequest(address)
            .then(data => {
                // Обновляем интерфейс с полученными данными
                updateUI(data);
            })
            .catch(error => {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при поиске адреса');
            })
            .finally(() => {
                // Скрываем спиннер загрузки
                searchBtn.classList.remove('loading');
            });
    });

    // Функция для имитации запроса к бекенду
    function simulateBackendRequest(address) {
        return new Promise((resolve) => {
            setTimeout(() => {
                // Заглушка с тестовыми данными (3 объекта)
                resolve({
                    "searched_address": address,
                    "objects": [
                        {
                            "locality": "Москва",
                            "street": "Центральный проезд Хорошёвского Серебряного Бора",
                            "number": "15",
                            "lon": 37.5238,
                            "lat": 55.7738,
                            "score": 94
                        },
                        {
                            "locality": "Москва",
                            "street": "Ленинский проспект",
                            "number": "42",
                            "lon": 37.5738,
                            "lat": 55.6938,
                            "score": 87
                        },
                        {
                            "locality": "Москва",
                            "street": "Тверская улица",
                            "number": "25",
                            "lon": 37.6038,
                            "lat": 55.7638,
                            "score": 76
                        }
                    ]
                });
            }, 0); // Имитация задержки сети
        });
    }

    // Функция для обновления интерфейса
    function updateUI(data) {
        // Удаляем старые результаты (оставляем только заголовок)
        const outputLabel = outputSection.querySelector('.input-label');
        outputSection.innerHTML = '';
        outputSection.appendChild(outputLabel);

        if (data.objects && data.objects.length > 0) {
            // Создаем контейнер для всех результатов
            const resultsContainer = document.createElement('div');
            resultsContainer.className = 'results-container';

            // Создаем блок для каждого объекта
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
            <div class="score-badge">${object.score}%</div>
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