function toggleAccess(studentId, isChecked) {
    // Отправка данных на сервер
    fetch(`/update-access/${studentId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken, // CSRF-токен для безопасности
        },
        body: JSON.stringify({
            access: isChecked,
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Изменение сохранено!');
        } else {
            alert('Ошибка при сохранении изменений.');
        }
    })
    .catch(error => console.error('Ошибка:', error));
}

// Получение CSRF-токена из куки
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrfToken = getCookie('csrftoken');
