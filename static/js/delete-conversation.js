document.addEventListener('DOMContentLoaded', () => {
    const deleteButtons = document.querySelectorAll('.delete-conversation');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function () {
            const userId = this.dataset.userId;
            const row = this.closest('.list-group-item');

            if (confirm('Are you sure you want to delete this conversation?')) {
                fetch(`/delete-conversation/${userId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                        'Content-Type': 'application/json'
                    },
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert(data.message);
                            row.remove(); // Remove the conversation from the list
                        } else {
                            alert('Error: ' + data.message);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('An unexpected error occurred.');
                    });
            }
        });
    });
});