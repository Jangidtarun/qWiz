console.log('script is loaded');

function adjustTextareaHeight(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';  

}

const textarea = document.getElementById('quiz_description');
textarea.addEventListener('input', () => {
    console.log('text area is getting input');
    adjustTextareaHeight(textarea);
});