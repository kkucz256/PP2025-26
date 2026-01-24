document.querySelectorAll(".drop-zone__input").forEach((inputElement) => {
  const dropZoneElement = inputElement.closest(".drop-zone");

  dropZoneElement.addEventListener("click", (e) => {
    inputElement.click();
  });

  inputElement.addEventListener("change", (e) => {
    if (inputElement.files.length) {
      updateThumbnail(dropZoneElement, inputElement.files[0]);
    }
  });

  dropZoneElement.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZoneElement.classList.add("drop-zone--over");
  });

  ["dragleave", "dragend"].forEach((type) => {
    dropZoneElement.addEventListener(type, (e) => {
      dropZoneElement.classList.remove("drop-zone--over");
    });
  });

  dropZoneElement.addEventListener("drop", (e) => {
    e.preventDefault();
    if (e.dataTransfer.files.length) {
      inputElement.files = e.dataTransfer.files;
      updateThumbnail(dropZoneElement, e.dataTransfer.files[0]);
    }
    dropZoneElement.classList.remove("drop-zone--over");
  });
});

function updateThumbnail(dropZoneElement, file) {
  let promptElement = dropZoneElement.querySelector(".drop-zone__prompt");
  promptElement.textContent = `Wybrano: ${file.name}`;
  promptElement.style.fontWeight = "bold";
  promptElement.style.color = "#2563eb";
}
const slider = document.getElementById('question_count');
const output = document.getElementById('rangeValue');

if (slider && output) {
    slider.oninput = function() {
        output.innerHTML = this.value;
    }
}

// Obsługa przesłania formularza - przechowaj pytania w sessionStorage
document.addEventListener('DOMContentLoaded', function() {
    const generateForm = document.querySelector('form[action*="upload"]');
    
    if (generateForm) {
        const generateBtn = generateForm.querySelector('button[name="action"][value="generate"]');
        
        if (generateBtn) {
            generateBtn.addEventListener('click', function(e) {
                // Po wciśnięciu przycisku "Generuj" - dane będą przesłane z sessionu
                // Pytania zostaną dostarczone z backendu jako JSON
            });
        }
    }
});

/**
 * Funkcja do ręcznego przechowywania pytań w sessionStorage
 * (może być użyta jeśli backend przesyła pytania jako JSON)
 */
function storeQuestionsInSession(questions) {
    if (questions && Array.isArray(questions)) {
        sessionStorage.setItem('temp_questions', JSON.stringify(questions));
    }
}