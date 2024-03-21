document.addEventListener("DOMContentLoaded", function() {
    const openModalButtons = document.querySelectorAll('[data-modal-target]')
    const closeModalButtons = document.querySelectorAll('[date-close-button]')
    const overlay = document.getElementById('overlay')
    const plus = document.getElementById('addproject')

    console.log('tata')
    console.log(openModalButtons)


    openModalButtons.forEach(button => {
        console.log('toto')
        button.addEventListener("click", () => {
            console.log("test")
            const form = document.querySelector(button.dataset.modalTarget)
            console.log(form)
            openForm(form)
        })
    })

    closeModalButtons.forEach(button => {
        button.addEventListener("click", () => {
            const form = button.closest('.newproject')
            closeForm(form)
        })
    })


    function openForm(form) {
        if (form==null) return
        form.classList.add('active')
        overlay.classList.add('active')

    }

    function closeForm(form) {
        if (form==null) return
        form.classList.remove('active')
        overlay.classList.remove('active')

}});