function addDays(dateStr, days) {
    console.log(`Adding days: Date: ${dateStr}, Days: ${days}`);
    const date = new Date(dateStr);
    if (isNaN(date)) {
        throw new Error(`Invalid date: ${dateStr}`);
    }
    date.setDate(date.getDate() + days);
    return date.toISOString().split('T')[0];
}

function multiply(x, y) {
    console.log(`Multiplying: ${x} * ${y}`);
    return x * y;
}

function evaluateFormulas() {
    console.log("Evaluating formulas for each user card...");
    const cards = document.querySelectorAll('.user-card');
    for (let i = 0; i < cards.length; i++) {
        console.log(`Processing card ${i + 1}`);
        const card = cards[i];
        
        const fechaContratacionElem = card.querySelector('.fecha-contratacion');
        if (!fechaContratacionElem) {
            console.error('Fecha de Contratación element not found');
            continue;
        }
        
        const mesesElem = card.querySelector('.meses');
        if (!mesesElem) {
            console.error('Meses element not found');
            continue;
        }
        
        const subcripcionElem = card.querySelector('.subcripcion');
        if (!subcripcionElem) {
            console.error('Subcripción element not found');
            continue;
        }
        
        const fechaContratacion = fechaContratacionElem.textContent.split(': ')[1];
        const meses = parseInt(mesesElem.value, 10);
        const subcripcion = subcripcionElem.textContent.split(': ')[1];
        
        if (isNaN(meses)) {
            console.error(`Invalid months value: ${mesesElem.value}`);
            continue;
        }

        try {
            const fechaExpiracion = addDays(fechaContratacion, meses * 30);
            const precio = subcripcion === "Alta" ? multiply(meses, 9.99).toFixed(2) : "0";

            const fechaExpiracionElem = card.querySelector('.fecha-expiracion');
            const precioElem = card.querySelector('.precio');
            
            // Update only the relevant parts without removing the <strong> tags
            fechaExpiracionElem.innerHTML = `<strong>Fecha de Expiración:</strong> ${fechaExpiracion}`;
            precioElem.innerHTML = `<strong>Precio:</strong> ${precio}`;
            
            const button = card.querySelector('.action-button');
            if (button) {
                if (button.getAttribute('data-action') === 'unsubscribe') {
                    button.classList.add('unsubscribe-button');
                    button.classList.remove('subscribe-button');
                } else {
                    button.classList.add('subscribe-button');
                    button.classList.remove('unsubscribe-button');
                }
            }
        } catch (e) {
            console.error(e.message);
        }
    }
}

document.addEventListener('DOMContentLoaded', function () {
    console.log("DOM fully loaded and parsed");
    evaluateFormulas();
    
    // Add event listeners for the dropdown changes
    const dropdowns = document.querySelectorAll('.meses');
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('change', evaluateFormulas);
    });
});

function toggleSubscription(button) {
    var userId = button.getAttribute('data-user-id');
    var action = button.getAttribute('data-action');
    console.log(`Toggling subscription for user ${userId}: ${action}`);

    // Make an AJAX request to the server to update the subscription status
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/toggle_subscription', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
            console.log('Subscription status updated');

            // Parse the response
            var response = JSON.parse(xhr.responseText);

            if (response.message) {
                // Toggle button class and action
                if (action === 'unsubscribe') {
                    button.setAttribute('data-action', 'subscribe');
                    button.textContent = 'Subscribe';
                    button.classList.add('subscribe-button');
                    button.classList.remove('unsubscribe-button');
                } else {
                    button.setAttribute('data-action', 'unsubscribe');
                    button.textContent = 'Unsubscribe';
                    button.classList.add('unsubscribe-button');
                    button.classList.remove('subscribe-button');
                }

                // Reload the page to update the card data
                location.reload();
            } else {
                console.error('Failed to update subscription status');
            }
        } else if (xhr.readyState == 4) {
            console.error('Failed to update subscription status');
        }
    };
    xhr.send(`user_id=${userId}&action=${action}`);
}
