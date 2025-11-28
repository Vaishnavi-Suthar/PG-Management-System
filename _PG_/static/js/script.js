// Common JavaScript functions
document.addEventListener('DOMContentLoaded', function() {
    initializeFormFields();
    setupRoomTypeHandler();
    setupSecurityDepositCalculator();
    setupPhoneNumberFormatting();
});

// Initialize form fields with default values
function initializeFormFields() {
    // Auto-fill current date in date fields
    const dateFields = document.querySelectorAll('input[type="date"]');
    dateFields.forEach(field => {
        if (!field.value) {
            const today = new Date();
            const yyyy = today.getFullYear();
            const mm = String(today.getMonth() + 1).padStart(2, '0');
            const dd = String(today.getDate()).padStart(2, '0');
            field.value = `${yyyy}-${mm}-${dd}`;
        }
    });
}

// Room type change handler
function setupRoomTypeHandler() {
    const roomTypeSelect = document.getElementById('room_type');
    const sharingTypeSelect = document.getElementById('sharing_type');
    
    if (roomTypeSelect && sharingTypeSelect) {
        roomTypeSelect.addEventListener('change', function() {
            if (this.value === 'Single') {
                sharingTypeSelect.value = '1';
                sharingTypeSelect.disabled = true;
            } else {
                sharingTypeSelect.disabled = false;
            }
        });
        
        // Trigger change event on page load if Single is selected
        if (roomTypeSelect.value === 'Single') {
            roomTypeSelect.dispatchEvent(new Event('change'));
        }
    }
}

// Auto-calculate security deposit based on rent
function setupSecurityDepositCalculator() {
    const rentAmountInput = document.getElementById('rent_amount');
    const securityDepositInput = document.getElementById('security_deposit');
    
    if (rentAmountInput && securityDepositInput) {
        rentAmountInput.addEventListener('blur', function() {
            if (this.value && !securityDepositInput.value) {
                securityDepositInput.value = (parseFloat(this.value) * 2).toFixed(2);
            }
        });
        
        rentAmountInput.addEventListener('input', function() {
            if (this.value && securityDepositInput.value === (parseFloat(this.value) * 2).toFixed(2)) {
                securityDepositInput.value = (parseFloat(this.value) * 2).toFixed(2);
            }
        });
    }
}

// Auto-format phone numbers
function setupPhoneNumberFormatting() {
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function() {
            formatPhoneNumber(this);
        });
        
        input.addEventListener('blur', function() {
            formatPhoneNumber(this);
        });
    });
}

// Format phone number as Indian format
function formatPhoneNumber(input) {
    // Remove all non-digit characters
    let phone = input.value.replace(/\D/g, '');
    
    // Format as Indian phone number (10 digits)
    if (phone.length > 10) {
        phone = phone.substring(0, 10);
    }
    
    if (phone.length >= 6) {
        phone = phone.replace(/(\d{5})(\d{0,5})/, '$1 $2');
    } else if (phone.length >= 5) {
        phone = phone.replace(/(\d{5})/, '$1 ');
    }
    
    input.value = phone.trim();
}

// Show loading state on buttons
function showLoading(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    button.disabled = true;
    
    // Re-enable after 3 seconds (safety timeout)
    setTimeout(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    }, 3000);
}

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// Auto-fill tenant details when tenant is selected (for payments)
function setupTenantAutoFill() {
    const tenantSelect = document.getElementById('tenant_id');
    const amountInput = document.getElementById('amount');
    const tenantDetails = document.getElementById('tenantDetails');
    
    if (tenantSelect && amountInput) {
        tenantSelect.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            const rentAmount = selectedOption.getAttribute('data-rent');
            
            if (rentAmount && selectedOption.value) {
                amountInput.value = rentAmount;
                
                // Show tenant details if container exists
                if (tenantDetails) {
                    tenantDetails.classList.remove('d-none');
                    const tenantName = document.getElementById('tenantName');
                    const tenantRoom = document.getElementById('tenantRoom');
                    const tenantRent = document.getElementById('tenantRent');
                    
                    if (tenantName) tenantName.textContent = 'Name: ' + selectedOption.text.split(' - ')[0];
                    if (tenantRoom) tenantRoom.textContent = 'Room: ' + selectedOption.text.split(' - ')[1];
                    if (tenantRent) tenantRent.textContent = 'Monthly Rent: ₹' + rentAmount;
                }
            } else if (tenantDetails) {
                tenantDetails.classList.add('d-none');
            }
        });
    }
}

// Quick amount buttons handler (for payments page)
function setupQuickAmountButtons() {
    document.querySelectorAll('.amount-btn').forEach(button => {
        button.addEventListener('click', function() {
            const amountInput = document.getElementById('amount');
            if (amountInput) {
                amountInput.value = this.getAttribute('data-amount');
            }
        });
    });
}

// Quick method buttons handler (for payments page)
function setupQuickMethodButtons() {
    document.querySelectorAll('.method-btn').forEach(button => {
        button.addEventListener('click', function() {
            const methodSelect = document.getElementById('payment_method');
            if (methodSelect) {
                methodSelect.value = this.getAttribute('data-method');
            }
        });
    });
}

// Auto-show login modal on errors (for home page)
function setupLoginModalAutoShow() {
    const errorAlerts = document.querySelectorAll('.alert-danger');
    if (errorAlerts.length > 0) {
        const loginModal = document.getElementById('loginModal');
        if (loginModal) {
            const bootstrapModal = new bootstrap.Modal(loginModal);
            bootstrapModal.show();
        }
    }
}

// Room auto-fill when tenant selected (for complaints page)
function setupRoomAutoFill() {
    const tenantSelect = document.getElementById('tenant_id');
    const roomSelect = document.getElementById('room_id');
    
    if (tenantSelect && roomSelect) {
        tenantSelect.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            const roomId = selectedOption.getAttribute('data-room');
            
            if (roomId) {
                roomSelect.value = roomId;
            }
        });
    }
}

// Quick category buttons (for complaints page)
function setupQuickCategoryButtons() {
    document.querySelectorAll('.category-btn').forEach(button => {
        button.addEventListener('click', function() {
            const categorySelect = document.getElementById('category');
            if (categorySelect) {
                categorySelect.value = this.getAttribute('data-category');
            }
        });
    });
}

// Quick priority buttons (for complaints page)
function setupQuickPriorityButtons() {
    document.querySelectorAll('.priority-btn').forEach(button => {
        button.addEventListener('click', function() {
            const prioritySelect = document.getElementById('priority');
            if (prioritySelect) {
                prioritySelect.value = this.getAttribute('data-priority');
            }
        });
    });
}

// Initialize all page-specific handlers
function initializePageSpecificHandlers() {
    // Payments page handlers
    if (document.getElementById('tenant_id')) {
        setupTenantAutoFill();
        setupQuickAmountButtons();
        setupQuickMethodButtons();
    }
    
    // Complaints page handlers
    if (document.getElementById('complaint_category')) {
        setupRoomAutoFill();
        setupQuickCategoryButtons();
        setupQuickPriorityButtons();
    }
    
    // Home page handlers
    if (document.getElementById('loginModal')) {
        setupLoginModalAutoShow();
    }
}

// Re-initialize when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeFormFields();
    setupRoomTypeHandler();
    setupSecurityDepositCalculator();
    setupPhoneNumberFormatting();
    initializePageSpecificHandlers();
});

// Utility function to format currency
function formatCurrency(amount) {
    return '₹' + parseFloat(amount).toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Utility function to validate email
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Utility function to validate Indian phone number
function validateIndianPhone(phone) {
    const phoneRegex = /^[6-9]\d{9}$/;
    return phoneRegex.test(phone.replace(/\D/g, ''));
}

// Export functions for global use (if needed)
window.PGManager = {
    showLoading,
    validateForm,
    formatCurrency,
    validateEmail,
    validateIndianPhone
};

// Handle "Select All" checkbox
document.getElementById('selectAll').addEventListener('change', function() {
    const checked = this.checked;
    document.querySelectorAll('.room-checkbox').forEach(cb => cb.checked = checked);
});

