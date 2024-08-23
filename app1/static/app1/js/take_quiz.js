function startTimer(timeLimit) {
    var minutes_field = document.getElementById('minutes');
    var seconds_field = document.getElementById('seconds');
    var progressbar = document.getElementById('progress-bar');
    var minutes = Math.floor(timeLimit / 60);
    var seconds = timeLimit % 60;
    
    var timerInterval = setInterval(function() {
        // console.log(timerElement.textContent)
        seconds--;
        if (seconds < 0) {
            minutes--;
            seconds = 59;
        }
        
        minutes_field.textContent = minutes
        seconds_field.textContent = seconds
        var timeleft = minutes*60 + seconds;
        var timeleftpercent = (timeleft/timeLimit)*100
        if(timeleftpercent < 20){
            progressbar.className = 'progress-bar text-bg-danger'
        } else if(timeleftpercent < 50){
            progressbar.className = 'progress-bar text-bg-warning'
        }
        progressbar.style.width = `${timeleftpercent}%`
        
        if (minutes === 0 && seconds === 0) {
            clearInterval(timerInterval);
            console.log('quiz is over')
            submitquiz();
        }
    }, 1000);
}

window.onload = function() {
    console.log('script is loading')
    const timelimit = document.getElementById('time-limit').value
    startTimer(timelimit)
};

function submitquiz() {
    var toastcontainer = document.getElementById("toast-container");
    var toast = document.getElementById('toast');
    var countdown = document.getElementById("countdown");
    const submitbutton = document.getElementById('submit-button')
    var timer = 3;
    
    toastcontainer.style.display = 'flex'
    toast.classList.add('show');

    var interval = setInterval(function() {
        timer--;
        
        countdown.textContent = timer;

        if (timer === 0) {
            clearInterval(interval);
            toastcontainer.style.display = 'none';
            toast.classList.remove('show');
            console.log('submit now');
            submitbutton.click();
        }
    }, 1000);
}