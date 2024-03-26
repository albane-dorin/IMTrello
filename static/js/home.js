document.addEventListener("DOMContentLoaded", function() {
    const openModalButtons = document.querySelectorAll('[data-modal-target]')
    const closeModalButtons = document.querySelectorAll('[date-close-button]')
    const overlay = document.getElementById('overlay')
    const boutonsSupprimerNotif = document.querySelectorAll('.supprimer-notif');


    //Permet pour tous les boutons "data-modal-target" d'ouvrir le formulaire associer quand on clique dessus
    openModalButtons.forEach(button => {
        button.addEventListener("click", () => {
            const form = document.querySelector(button.dataset.modalTarget)
            console.log(form)
            openForm(form)

        })
    })

    // Permet au formulaire de se fermer en cliquant sur la croix
    closeModalButtons.forEach(button => {
        button.addEventListener("click", () => {
            const form = button.closest('.new');
            console.log(form)
            closeForm(form);
        })
    })

    boutonsSupprimerNotif.forEach(bouton => {
            bouton.addEventListener('click', function() {
                // Obtenez l'ID de la notification à partir de l'ID du bouton
                const idNotif = bouton.id.split('_')[1];
                // Appelez la fonction de suppression avec l'élément bouton et l'ID de la notification
                supprimerNotif(bouton, idNotif);
            });
    });





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

    function supprimerNotif(element, notif) {
        var NotifASupprimer = element.parentElement;
        NotifASupprimer.remove();
        //database.db.session.delete(notif)
        //database.db.session.commit()
    }


});