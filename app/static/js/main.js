// password validation for the signup form
document.addEventListener('DOMContentLoaded', function() {
    const signupForm = document.querySelector('form');
    
    if (signupForm && signupForm.action.includes('signup')) {
        const passwordField = document.getElementById('password');
        const confirmPasswordField = document.getElementById('confirm_password');
        const phoneField = document.getElementById('phone');

        
        passwordField.addEventListener('keyup', validatePassword);
        confirmPasswordField.addEventListener('keyup', validateConfirmPassword);
        phoneField.addEventListener('keyup', validatePhone);

        
        signupForm.addEventListener('submit', function(event) {
            if (!isPasswordValid(passwordField.value)) {
                event.preventDefault();
                alert('Password must be at least 8 characters long and contain at least one number and one special character.');
            } else if (passwordField.value !== confirmPasswordField.value) {
                event.preventDefault();
                alert('Passwords do not match.');
            }
            else if (!validatePhone(phoneField.value)) {
                event.preventDefault();
                alert('Phone number must be 10 digits.');
            }    
        });
    }
    
    // add animation to flash messages
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.transition = 'opacity 1s';
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 1000);
        }, 5000);
    });
});

// balidate password requirements
function isPasswordValid(password) {
    const regex = /^(?=.*[0-9])(?=.*[!@#$%^&*])[a-zA-Z0-9!@#$%^&*]{8,}$/;
    return regex.test(password);
}

function validatePassword() {
    const password = this.value;
    const messageElement = this.nextElementSibling;
    
    if (password.length < 8) {
        this.classList.add('is-invalid');
        messageElement.innerHTML = 'Password must be at least 8 characters long.';
        messageElement.classList.add('text-danger');
    } else if (!/\d/.test(password)) {
        this.classList.add('is-invalid');
        messageElement.innerHTML = 'Password must contain at least one number.';
        messageElement.classList.add('text-danger');
    } else if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
        this.classList.add('is-invalid');
        messageElement.innerHTML = 'Password must contain at least one special character.';
        messageElement.classList.add('text-danger');
    } else {
        this.classList.remove('is-invalid');
        this.classList.add('is-valid');
        messageElement.innerHTML = 'Password meets requirements.';
        messageElement.classList.remove('text-danger');
        messageElement.classList.add('text-success');
    }
}

function validateConfirmPassword() {
    const confirmPassword = this.value;
    const password = document.getElementById('password').value;
    
    if (confirmPassword !== password) {
        this.classList.add('is-invalid');
        this.classList.remove('is-valid');
    } else {
        this.classList.remove('is-invalid');
        this.classList.add('is-valid');
    }
}

function validatePhone() {
    const phone = this.value;
    const phoneRegex = /^\d{10}$/;

    if (!phoneRegex.test(phone)) {
        this.classList.add('is-invalid');
        this.classList.remove('is-valid');
    } else {
        this.classList.remove('is-invalid');
        this.classList.add('is-valid');
    }
}