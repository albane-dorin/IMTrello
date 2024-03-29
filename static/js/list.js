// Execute the 'onLoad' function after the page has finished loading
$(onLoad)

function onLoad() {
    var today = new Date();
    var year = today.getFullYear();
    var month = String(today.getMonth() + 1).padStart(2, '0'); // Les mois sont indexés de 0 à 11, alors ajoutez 1 et remplissez avec des zéros si nécessaire
    var day = String(today.getDate()).padStart(2, '0');
    var today = year+"-"+month+"-"+day;
    $("#taches tbody tr").show();
    $("#taches tbody tr").filter(function () {
    var date = $(this).attr("data-date");
    return date < today;})
        .hide();
    // Barre de recherche par nom de tâche
    $("#filter-task-by-name").on("input", filterRowsByName)
}

function reapplyAlternanceCouleurs() {
    var tableau = document.getElementById("taches");
    var tbody = tableau.querySelector("tbody");
    var lignes = Array.from(tbody.getElementsByTagName("tr"));
    var rowCount = lignes.length;

    for (var i = 0; i < rowCount; i++) {
        if (i % 2 === 0) {
            lignes[i].classList.remove("odd");
            lignes[i].classList.add("even");
        } else {
            lignes[i].classList.remove("even");
            lignes[i].classList.add("odd");
        }
    }
}

function updateRows() {
        $("table.TFtable tr:visible:odd").addClass("odd");
        $("table.TFtable tr:visible:even").addClass("even");
}

function filterByProject(n){
    var checkBox = document.getElementById("p_" + n);
    if (checkBox.checked===true) {
        $("#taches tbody tr[data-project='" + n + "']").show();
    }
    else {
        console.log(n)
        console.log($("#taches tbody tr[data-project='" + n + "']"))
        $("#taches tbody tr[data-project='" + n + "']").hide();
    }
    updateRows()
}




function filterRowsByName(){
    var filter_value = $("#filter-task-by-name").val().toLowerCase();
    $("#taches tbody tr").show();
    $("#taches tbody tr").filter(function () {
    return $(this).attr( "data-name-task" ).toLowerCase().indexOf(filter_value) === -1;
  }).hide();
}


function filterWaiting() {
    var checkBox = document.getElementById("waiting");
    if (checkBox.checked===true) {
        $("#taches tbody tr[data-status='En attente']").show();
    }
    else {
        $("#taches tbody tr[data-status='En attente']").hide();
    }
    updateRows()
}

function filterCompleted() {
    var checkBox = document.getElementById("completed");
    if (checkBox.checked===true) {
        $("#taches tbody tr[data-status='Completée']").show();
    }
    else {
        $("#taches tbody tr[data-status='Completée']").hide();
    }
}

function filterInProgress() {
    var checkBox = document.getElementById("in_progress");
    if (checkBox.checked===true) {
        $("#taches tbody tr[data-status='En cours']").show();
    }
    else {
        $("#taches tbody tr[data-status='En cours']").hide();
    }
}

function filterCancelled() {
    var checkBox = document.getElementById("cancelled");
    if (checkBox.checked===true) {
        $("#taches tbody tr[data-status='Annulée']").show();
    }
    else {
        $("#taches tbody tr[data-status='Annulée']").hide();
    }
}

function filterBlocked() {
    var checkBox = document.getElementById("blocked");
    if (checkBox.checked===true) {
        $("#taches tbody tr[data-status='En pause']").show();
    }
    else {
        $("#taches tbody tr[data-status='En pause']").hide();
    }
}

function filterByTime() {
    var checkBox = document.getElementById("chronology");
    if (checkBox.checked===true) {
        var checkBox = document.getElementById("priority");
        checkBox.checked = false;
        filterChronology()
    }
}

function filterChronology() {
    var tableau = document.getElementById("taches");
    var tbody = tableau.querySelector("tbody");
    var lignes = Array.from(tbody.getElementsByTagName("tr"));

    lignes.sort(function(a, b) {
        var dateA = new Date(a.getAttribute("data-date"));
        var dateB = new Date(b.getAttribute("data-date"));
        return dateA - dateB;
    });

    // Retirer les lignes actuelles du tbody
    while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
    }

    // Réinsérer les lignes triées
    lignes.forEach(function(ligne) {
        tbody.appendChild(ligne);
    });
}

function filterByPrio(){
    var checkBox = document.getElementById("priority");
    if (checkBox.checked===true) {
        var checkBox = document.getElementById("chronology");
        checkBox.checked = false;
        filterPrio();
    }
}

function filterPrio(){
    var tableau = document.getElementById("taches");
    var tbody = tableau.querySelector("tbody");
    var lignes = Array.from(tbody.getElementsByTagName("tr"));

    lignes.sort(function(a, b) {
        function attributeNumber(x) {
            var n;
            if (x.getAttribute("data-prio")=='Facultative') {
                n=0;
            }
            if (x.getAttribute("data-prio")=='Faible') {
                n=1;
            }
            if (x.getAttribute("data-prio")=='Moyenne') {
                n=2;
            }
            if (x.getAttribute("data-prio")=='Forte') {
                n=3;
            }
            if (x.getAttribute("data-prio")=='Importante') {
                n=4;
            }
            return n;
        }
        var prioA = attributeNumber(a);
        var prioB = attributeNumber(b);
        return prioB - prioA;
    });

    // Retirer les lignes actuelles du tbody
    while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
    }

    // Réinsérer les lignes triées
    lignes.forEach(function(ligne) {
        tbody.appendChild(ligne);
    });
}

function printAll() {
    var checkBox = document.getElementById("all");
    if (checkBox.checked===true) {
        $("#taches tbody tr").show();
    }
    else {
        var today = new Date();
        var year = today.getFullYear();
        var month = String(today.getMonth() + 1).padStart(2, '0'); // Les mois sont indexés de 0 à 11, alors ajoutez 1 et remplissez avec des zéros si nécessaire
        var day = String(today.getDate()).padStart(2, '0');
        var today = year+"-"+month+"-"+day;
        $("#taches tbody tr").show();
        $("#taches tbody tr").filter(function () {
            var date = $(this).attr("data-date");
            return date < today;})
        .hide();
    }
}