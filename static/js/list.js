// Execute the 'onLoad' function after the page has finished loading
$(onLoad)

function onLoad() {
    // Barre de recherche par nom de tâche
    $("#filter-task-by-name").on("input", filterRowsByName)

    //Cocher statut des tâches
    //$("#waiting").on("change", filterWaiting())
}

function filterRowsByName(){
    var filter_value = $("#filter-task-by-name").val().toLowerCase();
    $("#taches tbody tr").show();
    $("#taches tbody tr").filter(function () {
    return $(this).attr( "data-name-task" ).toLowerCase().indexOf(filter_value) === -1;
  }).hide();
}


function filterWaiting() {
    console.log("Dans la fonction");
    var checkBox = document.getElementById("waiting");
    if (checkBox.checked===true) {
        console.log("La case à cocher est cochée. Faites quelque chose ici.");
        $("#taches tbody tr[data-status='Waiting']").show();
    }
    else {
        console.log("La case à cocher n'est pas cochée. Faites quelque chose ici.");
        $("#taches tbody tr[data-status='Waiting']").hide();
    }
}

