function removeQuestion(btn) {
    if (confirm("Czy na pewno chcesz usunąć to pytanie? Te zmiany są nieodwracalne przed zapisem.")) {
        const card = btn.closest('.question-card');
        card.remove();
        reindexQuestions();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const addBtn = document.getElementById('add-question-btn');
    const container = document.querySelector('.questions-list');

    if (addBtn) {
        addBtn.addEventListener('click', function() {
            const techId = Date.now();
            
            const newCardHTML = `
                <div class="panel question-card">
                    <div class="q-header">
                        <h3>Pytanie <span class="q-index"></span></h3>
                        <button type="button" class="btn-delete" onclick="removeQuestion(this)">Usuń</button>
                    </div>
                    
                    <textarea name="q_new_${techId}_text" class="edit-q" 
                              placeholder="Wpisz treść nowego pytania..." required></textarea>
                    
                    <div class="options-grid">
                        <div class="opt-row">
                            <input type="radio" name="q_new_${techId}_correct" value="0" required>
                            <input type="text" name="q_new_${techId}_opt_0" placeholder="Opcja 1" class="edit-opt" required>
                        </div>
                        <div class="opt-row">
                            <input type="radio" name="q_new_${techId}_correct" value="1" required>
                            <input type="text" name="q_new_${techId}_opt_1" placeholder="Opcja 2" class="edit-opt" required>
                        </div>
                        <div class="opt-row">
                            <input type="radio" name="q_new_${techId}_correct" value="2" required>
                            <input type="text" name="q_new_${techId}_opt_2" placeholder="Opcja 3" class="edit-opt" required>
                        </div>
                        <div class="opt-row">
                            <input type="radio" name="q_new_${techId}_correct" value="3" required>
                            <input type="text" name="q_new_${techId}_opt_3" placeholder="Opcja 4" class="edit-opt" required>
                        </div>
                    </div>
                </div>
            `;
            
            container.insertAdjacentHTML('beforeend', newCardHTML);
            
            reindexQuestions();
            
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
        });
    }

    reindexQuestions();
});

function reindexQuestions() {
    const indices = document.querySelectorAll('.q-index');
    indices.forEach((span, index) => {
        span.innerText = index + 1;
    });
}