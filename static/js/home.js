document.addEventListener("DOMContentLoaded", function() {
    const openModalButtons = document.querySelectorAll('[data-modal-target]')
    const closeModalButtons = document.querySelectorAll('[date-close-button]')
    const overlay = document.getElementById('overlay')





    openModalButtons.forEach(button => {
        button.addEventListener("click", () => {
            const form = document.querySelector(button.dataset.modalTarget)
            console.log(form)
            openForm(form)

        })
    })

    closeModalButtons.forEach(button => {
        button.addEventListener("click", () => {
            const form = button.closest('.new');
            console.log(form)
            closeForm(form);
        })
    })





    function openForm(form) {
        if (form==null) return
        form.classList.add('active')
        overlay.classList.add('active')

    }

    function closeForm(form) {
        if (form == null) return
        form.classList.remove('active')
        overlay.classList.remove('active')

    }


});