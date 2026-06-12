// Check everything when page loads 
window.addEventListener('DOMContentLoaded', () => {
    const savedDarkMode = localStorage.getItem('darkMode');
    
    if (savedDarkMode === 'true') {
        toggleDark();
    }

    const predictForm = document.getElementById('predictForm');

    // dont allow same team to be selected for both home and away
    if (predictForm) {
        const homeSelect = document.getElementById('homeTeam');
        const awaySelect = document.getElementById('awayTeam');
        const submit = document.getElementById('predictSubmit');
        submit.disabled = true;
        submit.style.backgroundColor = "red";

        predictForm.addEventListener('change', () => {
            const selectedHomeTeam = homeSelect.value;
            const selectedAwayTeam = awaySelect.value;

            
            Array.from(awaySelect.options).forEach(option => {
                if (option.value === selectedHomeTeam) {
                    option.disabled = true;
                } else {
                    option.disabled = false;
                }
            });
            Array.from(homeSelect.options).forEach(option => {
                option.disabled = option.value === selectedAwayTeam;
            });

            if (homeSelect.value === awaySelect.value || homeSelect.value === 'none' || awaySelect.value === 'none') {
                submit.disabled = true;
                submit.style.backgroundColor = "red";
            } else { 
                submit.disabled = false;
                submit.style.backgroundColor = "";
            }
        });
    }

    function toggleDark() {
        // Determine the new theme based on current background
        const isNowDark = document.body.style.backgroundColor !== 'black';
        const bgColor = isNowDark ? 'black' : 'white';
        const textColor = isNowDark ? 'white' : 'black';

        // Apply to body
        document.body.style.backgroundColor = bgColor;
        document.body.style.color = textColor;

        // Apply to all cards
        document.querySelectorAll('.card').forEach(function(link) {
            link.style.backgroundColor = bgColor;
            link.style.color = textColor;
        });

        // Save to storage
        localStorage.setItem('darkMode', isNowDark);
    }

    const password = document.getElementById('new_password');
    const confirmPass = document.getElementById('confirm_password');
    const submitBtn = document.getElementById('submitBtn');

    function validatePasswords() {
        // Only validate if the user has actually typed something in the confirmation box
        if (confirmPass.value.length > 0) {
            if (password.value === confirmPass.value) {
                confirmPass.classList.remove('is-invalid');
                confirmPass.classList.add('is-valid');
                submitBtn.disabled = false;
            } else {
                confirmPass.classList.remove('is-valid');
                confirmPass.classList.add('is-invalid');
                submitBtn.disabled = true;
            }
        } else {
            // Reset if confirm is empty
            confirmPass.classList.remove('is-invalid', 'is-valid');
            submitBtn.disabled = false;
        }
    }

    // Listen for typing events on both fields
    if (password && confirmPass && submitBtn) {
        password.addEventListener('input', validatePasswords);
        confirmPass.addEventListener('input', validatePasswords);
    }

});

window.addEventListener('pageshow', (event) => {
    if (event.persisted) {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.add('d-none');
        }
    }
});

function scrollToSpot(spot) {
    // Determine where to scroll then do it
    var where = (spot === 'bottom') ? document.body.scrollHeight : 0;
    window.scrollTo({
        top: where,
        behavior: 'smooth'
    });
}

function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.remove('d-none');
    }
}